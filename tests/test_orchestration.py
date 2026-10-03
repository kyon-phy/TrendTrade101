import json,tempfile,unittest
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from pathlib import Path
from fixture_support import ROOT,build_fixture
from trendtrade101.dataset import load_dataset
from trendtrade101.inputs import verify,verify_project_inputs,PUBLIC_EXPECTED
from trendtrade101.orchestration import freeze_plan,run_baseline,run_walk_forward,freeze_final_selection,run_final_holdout,consume_holdout
from trendtrade101.schedule import liquidation_schedule
from trendtrade101.storage import read_json
from trendtrade101.dashboard import result_catalog,export_dashboard
from trendtrade101.indicators import Indicators
from trendtrade101.signals import SignalState,SignalRules
from trendtrade101.portfolio import Ledger,LedgerPolicy
from trendtrade101.engine import Bar,replay

class OrchestrationTests(unittest.TestCase):
    def test_public_derivatives_are_verified_without_claiming_original_bytes(self):
        r=verify_project_inputs(ROOT)
        self.assertEqual(r["status"],"verified")
        self.assertEqual(r["verification_kind"],"public_derived")
        self.assertFalse(r["original_bytes_verified"])
        self.assertEqual((r["membership_count"],r["unique_securities"]),(201,127))
        self.assertEqual(verify(ROOT/"config/inputs")["status"],"blocked")

    def test_provenance_tampering_is_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"inputs";shutil.copytree(ROOT/"config/inputs",target)
            p=target/"public_input_provenance.json";p.write_text(p.read_text()+" ")
            self.assertEqual(verify(target,kind="public_derived")["status"],"blocked")

    def test_a_complete_synthetic_pipeline_and_once_only_holdout(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);ds=build_fixture(directory/"data")
            runs=directory/"run"
            plan=freeze_plan(ROOT,ds,"existing_25",runs)
            self.assertEqual(plan["holdout"]["start"],"2026-01-26")
            with self.assertRaises(ValueError):run_walk_forward(ROOT,ds,runs,arms=["MA_ONLY"])
            baseline=run_baseline(ROOT,ds,runs,arms=["MA_ONLY"])
            self.assertIn("MA_ONLY",baseline)
            results=run_walk_forward(ROOT,ds,runs,arms=["MA_ONLY"])
            self.assertEqual(len(results["MA_ONLY"]["folds"]),1)
            frozen=freeze_final_selection(ROOT,ds,runs,arms=["MA_ONLY"])
            self.assertEqual(frozen["training"]["end"],plan["holdout"]["start"])
            outputs=run_final_holdout(ROOT,ds,runs)
            self.assertEqual(outputs["MA_ONLY"]["baseline"]["status"],"synthetic_test_only")
            with self.assertRaises(FileExistsError):run_final_holdout(ROOT,ds,runs)

    def test_holdout_price_changes_cannot_change_development_scores(self):
        with tempfile.TemporaryDirectory() as d:
            out=[]
            for name,multiplier in [("a",1),("b",20)]:
                directory=Path(d)/name
                ds=build_fixture(directory/"data",holdout_multiplier=multiplier)
                freeze_plan(ROOT,ds,"existing_25",directory/"run")
                run_baseline(ROOT,ds,directory/"run",arms=["MA_ONLY"])
                out.append(run_walk_forward(ROOT,ds,directory/"run",arms=["MA_ONLY"])["MA_ONLY"])
            self.assertEqual(out[0]["after_tax_return"],out[1]["after_tax_return"])
            self.assertEqual(out[0]["folds"],out[1]["folds"])

    def test_frozen_plan_cannot_be_replaced_after_data_change(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            ds=build_fixture(directory/"data")
            freeze_plan(ROOT,ds,"existing_25",directory/"run")
            changed=build_fixture(directory/"other",holdout_multiplier=2)
            with self.assertRaises(ValueError):freeze_plan(ROOT,changed,"existing_25",directory/"run")

    def test_daily_folds_carry_account_equity_without_capital_reset(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);ds=build_fixture(directory/"data",frequency="daily")
            run=directory/"run"
            freeze_plan(ROOT,ds,"existing_25",run)
            run_baseline(ROOT,ds,run,arms=["MA_ONLY"])
            result=run_walk_forward(ROOT,ds,run,arms=["MA_ONLY"])["MA_ONLY"]
            first,second=result["folds"]
            self.assertEqual(first["end_equity"],second["metrics"]["initial_equity"])
            self.assertAlmostEqual(second["end_equity"]/100000-1,result["after_tax_return"])

    def test_a_bar_before_known_ipo_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ds=build_fixture(Path(d))
            manifest=json.loads(ds.source_path.read_text())
            manifest["members"]["NVDA"]["first_trade_date"]="2026-01-20"
            ds.source_path.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):load_dataset(ROOT,ds.source_path,allow_synthetic=True)

    def test_duplicate_split_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ds=build_fixture(Path(d))
            manifest=json.loads(ds.source_path.read_text())
            split={"ticker":"NVDA","ratio":2,"at":"2026-01-20T09:30:00-05:00"}
            manifest["splits"]=[split,split]
            ds.source_path.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):load_dataset(ROOT,ds.source_path,allow_synthetic=True)

    def test_synthetic_fixture_requires_explicit_route(self):
        with tempfile.TemporaryDirectory() as d:
            ds=build_fixture(Path(d))
            with self.assertRaises(ValueError):load_dataset(ROOT,ds.source_path)

    def test_final_sample_cannot_be_reused_in_another_run_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            a,b=root/"a",root/"b";a.mkdir();b.mkdir()
            plan={"dataset_kind":"yahoo_audited","market":"US","frequency":"5m","universe":"test",
                  "members":["TEST"],"holdout":{"start":"2026-01-26","end":"2026-02-02"}}
            consume_holdout(root,plan,a)
            with self.assertRaises(FileExistsError):consume_holdout(root,plan,b)

    def test_synthetic_results_never_enter_historical_dashboard(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=root/".private/runs/demo";run.mkdir(parents=True)
            (run/"plan.json").write_text(json.dumps({"dataset_kind":"synthetic_fixture"}))
            self.assertEqual(result_catalog(root),[])

    def test_exported_dashboard_is_self_contained_and_identifies_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            destination=Path(d)/"dashboard.html"
            export_dashboard(ROOT,destination)
            html=destination.read_text()
            self.assertIn("TRENDTRADE_SNAPSHOT",html)
            self.assertNotIn('src="/app.js"',html)
            self.assertNotIn('href="/style.css"',html)

    def test_daily_month_end_plan_bans_buys_at_open(self):
        with tempfile.TemporaryDirectory() as d:
            ds=build_fixture(Path(d),frequency="daily")
            events=liquidation_schedule(ds.sessions,["AAPL"],frequency="daily",delay_minutes=20)
            self.assertEqual(len(events),9)
            self.assertTrue(all(e.signal_time==e.due_time for e in events))
            self.assertTrue(all(e.prohibit_buys_until>e.due_time for e in events))

    def test_split_preserves_indicator_history_and_portfolio_equity(self):
        old=Indicators(seed_method="sma_seed");normalized=Indicators(seed_method="sma_seed")
        for i in range(50):
            p=100+i
            old.update(p+1,p-1,p);normalized.update((p+1)/2,(p-1)/2,p/2)
        old.apply_split(2)
        self.assertEqual(old.update(76,74,75),normalized.update(76,74,75))
        ledger=Ledger(capital=100000,position_cap=100000,fee_rate=0,fee_cap=0,tax_rate=.20315,
                      lots={"AAPL":1},policy=LedgerPolicy("market_value",True,"realization_accrual",False))
        t=datetime(2026,1,1,tzinfo=timezone.utc)
        ledger.queue_buy(event_id="a",ticker="AAPL",signal_time=t,due_time=t,slope=1,adx=30,target=1000,signal_price=100)
        ledger.execute(t,{"AAPL":100},tax_year=2026)
        before=ledger.equity
        ledger.apply_split("AAPL",2,t+timedelta(days=1))
        self.assertEqual(ledger.positions["AAPL"].quantity,20)
        self.assertEqual(ledger.equity,before)

    def test_fractional_split_entitlement_is_not_fabricated(self):
        from trendtrade101.portfolio import Position
        ledger=Ledger(capital=100000,position_cap=100000,fee_rate=0,fee_cap=0,tax_rate=.20315,
                      lots={"AAPL":1},policy=LedgerPolicy("market_value",True,"realization_accrual",False))
        ledger.positions["AAPL"]=Position(quantity=1,cost=100,gross_cost=100)
        with self.assertRaises(ValueError):ledger.apply_split("AAPL",.5,datetime.now(timezone.utc))
