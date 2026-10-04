"""Approved account semantics tested on synthetic data only."""
import copy
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from fixture_support import ROOT, build_fixture
from trendtrade101 import orchestration
from trendtrade101.audit_package import audit_local_charts
from trendtrade101.dataset import REQUIRED_AUDITS, load_dataset
from trendtrade101.indicators import Indicators, Reading
from trendtrade101.portfolio import Ledger, LedgerPolicy
from trendtrade101.signals import SignalRules, SignalState
from trendtrade101.storage import read_json, write_json, sha256

T = datetime(2026, 1, 5, 9, 30, tzinfo=timezone.utc)


def account():
    return Ledger(capital=100000, position_cap=100000, fee_rate=.00495,
                  fee_cap=22, tax_rate=.20315, lots={"TEST": 1},
                  policy=LedgerPolicy("market_value", True, "realization_accrual", False))


def snapshot(ledger):
    return copy.deepcopy({key: getattr(ledger, key) for key in (
        "initial_capital", "cash", "positions", "marks", "orders", "ids",
        "realized", "tax_paid", "fees", "taxes")})


class ApprovedAccountingTests(unittest.TestCase):
    def test_split_preserves_total_cost_cash_tax_and_round_trip_pnl(self):
        outcomes=[]
        for ratio in (1, 2, .5):
            ledger=account()
            ledger.queue_buy(event_id="entry", ticker="TEST", signal_time=T,
                due_time=T, slope=1, adx=30, target=10000, signal_price=100)
            ledger.execute(T, {"TEST": 100}, tax_year=2026)
            p=ledger.positions["TEST"]
            before=(ledger.cash, ledger.equity, p.cost, p.gross_cost, ledger.fees, ledger.taxes)
            old_unit_cost=p.cost/p.quantity
            ledger.apply_split("TEST", ratio, T+timedelta(days=1))
            self.assertEqual(p.quantity, 100*ratio)
            self.assertAlmostEqual(p.average_cost, old_unit_cost/ratio)
            self.assertEqual(before, (ledger.cash, ledger.equity, p.cost, p.gross_cost,
                                      ledger.fees, ledger.taxes))
            split=ledger.events[-1]
            self.assertEqual(split["quantity_before"],100)
            self.assertEqual(split["quantity_after"],100*ratio)
            self.assertEqual(split["total_cost"],p.cost)
            at=T+timedelta(days=2)
            ledger.queue_exit(event_id="exit", ticker="TEST", signal_time=at,
                              due_time=at, reason="test")
            ledger.execute(at, {"TEST": 110/ratio}, tax_year=2026)
            outcomes.append((ledger.cash, ledger.fees, ledger.taxes,
                             ledger.trades[-1]["after_tax_pnl"]))
        self.assertEqual(outcomes[0], outcomes[1])
        self.assertEqual(outcomes[0], outcomes[2])

    def test_split_rescales_partial_seeds_and_initialized_indicators(self):
        for count in (10, 27, 45):
            with self.subTest(warmup=count):
                actual=Indicators(seed_method="sma_seed")
                reference=Indicators(seed_method="sma_seed")
                for i in range(count):
                    price=100+i+(i%3)
                    actual.update(price+2,price-1,price)
                    reference.update((price+2)/2,(price-1)/2,price/2)
                actual.apply_split(2)
                for i in range(count, count+40):
                    price=(100+i+(i%3))/2
                    self.assertEqual(actual.update(price+1,price-.5,price),
                                     reference.update(price+1,price-.5,price))

    def test_split_preserves_hump_exit_and_cross_identity(self):
        actual=SignalState("FULL",rules=SignalRules(True,True,True,True,True),
                           adx_threshold=25,cross_window=5,hist_drawdown=.4,increments=3)
        reference=copy.deepcopy(actual)
        for h in (-3,-2,-1,2,4):
            actual.update(Reading(110,100,h,0,h,30,1))
            reference.update(Reading(55,50,h/2,0,h/2,30,1))
        actual.apply_split(2)
        value=Reading(55,50,1,0,1,30,1)
        self.assertEqual(actual.update(value),reference.update(value))
        self.assertTrue(actual.update(Reading(55,50,0,0,0,30,1))["exit"])

    def test_nonfinite_split_is_rejected_before_indicator_state_changes(self):
        indicator=Indicators(seed_method="sma_seed")
        for i in range(40):indicator.update(102+i,99+i,100+i)
        signal=SignalState("FULL",rules=SignalRules(True,True,True,True,True),
                          adx_threshold=25,cross_window=5,hist_drawdown=.4,increments=3)
        signal.update(Reading(110,100,2,1,1,30,1))
        for obj in (indicator, signal):
            for ratio in (float("nan"),float("inf"),0,-1):
                with self.subTest(component=type(obj).__name__,ratio=ratio):
                    before=repr(obj.__dict__)
                    with self.assertRaisesRegex(ValueError,"split"):
                        obj.apply_split(ratio)
                    self.assertEqual(repr(obj.__dict__),before)

    def test_split_inside_a_bar_cannot_mix_price_units(self):
        with tempfile.TemporaryDirectory() as d:
            ds=build_fixture(Path(d))
            manifest=read_json(ds.source_path)
            manifest["splits"]=[{"ticker":"NVDA","ratio":2,"at":"2026-01-20T09:32:00-05:00"}]
            write_json(ds.source_path,manifest)
            with self.assertRaisesRegex(ValueError,"inside.*bar"):
                load_dataset(ROOT,ds.source_path,allow_synthetic=True)

    def test_unidentified_distribution_stops_before_price_processing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            write_json(root/"capture.json",{"provider":"Yahoo",
                "review":{k:{"status":"verified","evidence":"Synthetic fixture"} for k in REQUIRED_AUDITS},
                "members":{"TEST":{}},
                "unresolved_corporate_actions":[{"ticker":"UNKNOWN","type":"unverified_distribution"}]})
            with self.assertRaisesRegex(ValueError,"must identify a frozen ticker"):
                audit_local_charts(root,root/"capture.json",root/"output")
            self.assertFalse((root/"output").exists())

    def test_unresolved_distribution_blocks_affected_run_without_removing_member(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);ds=build_fixture(directory/"data",frequency="daily")
            manifest=read_json(ds.source_path)
            manifest["unresolved_corporate_actions"]=[{"ticker":"AIG","type":"unverified_distribution"}]
            write_json(ds.source_path,manifest)
            ds=load_dataset(ROOT,ds.source_path,allow_synthetic=True)
            unaffected=orchestration.freeze_plan(ROOT,ds,"existing_25",directory/"unaffected")
            self.assertEqual(len(unaffected["members"]),12)
            self.assertEqual(unaffected["unresolved_action_symbols_outside_run"],["AIG"])
            self.assertIn("AIG",ds.manifest["members"])
            with self.assertRaisesRegex(ValueError,"block this run: AIG"):
                orchestration.freeze_plan(ROOT,ds,"sector_28",directory/"affected")
            self.assertFalse((directory/"affected").exists())

    def test_unsupported_account_policy_cannot_silently_change_a_research_plan(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);ds=build_fixture(directory/"data")
            root=directory/"project";shutil.copytree(ROOT/"config",root/"config")
            config=read_json(root/"config/baseline.json")
            config["account_state"]["training"]="continuous"
            write_json(root/"config/baseline.json",config)
            with self.assertRaisesRegex(ValueError,"Accounting policies"):
                orchestration.freeze_plan(root,ds,"existing_25",directory/"run")
            self.assertFalse((directory/"run").exists())

    def test_training_isolated_oos_carries_risk_and_final_accounts_are_fresh(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            ds=build_fixture(directory/"data",frequency="daily")
            manifest=read_json(ds.source_path)
            bars_path=ds.source_path.parent/manifest["bars_file"]
            # One unavailable month-end quote leaves an actual residual holding
            # and exit order; another security closes and accrues tax that month.
            rows=[b for b in read_json(bars_path) if not
                  (b["ticker"]=="AMD" and b["start"].startswith("2025-07-31"))]
            write_json(bars_path,rows);manifest["bars_sha256"]=sha256(bars_path)
            write_json(ds.source_path,manifest)
            ds=load_dataset(ROOT,ds.source_path,allow_synthetic=True)
            run=directory/"run"
            plan=orchestration.freeze_plan(ROOT,ds,"existing_25",run)
            orchestration.run_baseline(ROOT,ds,run,arms=["MA_ONLY"])
            observations=[]
            real_replay=orchestration.replay
            def observe(bars,**kwargs):
                ledger=kwargs["ledger"]
                row={"ledger":ledger,"start":kwargs["start"].date().isoformat(),
                     "end":kwargs["end"].date().isoformat(),"before":snapshot(ledger),
                     "prior_bars":sum(b.end<kwargs["start"] for b in bars)}
                result=real_replay(bars,**kwargs)
                row.update(after=snapshot(ledger),result=result)
                observations.append(row)
                return result
            with patch.object(orchestration,"replay",side_effect=observe):
                orchestration.run_walk_forward(ROOT,ds,run,arms=["MA_ONLY"])
                orchestration.freeze_final_selection(ROOT,ds,run,arms=["MA_ONLY"])
                orchestration.run_final_holdout(ROOT,ds,run)
            windows={(w["test"]["start"],w["test"]["end"]) for w in plan["folds"]}
            oos=[r for r in observations if (r["start"],r["end"]) in windows]
            self.assertEqual(len(oos),2)
            self.assertTrue(oos[0]["after"]["positions"]["AMD"].quantity)
            self.assertTrue(any(o.status=="queued" for o in oos[0]["after"]["orders"]))
            self.assertGreater(oos[0]["after"]["taxes"],0)
            self.assertEqual(oos[0]["after"],oos[1]["before"])
            self.assertIs(oos[0]["ledger"],oos[1]["ledger"])
            fresh=[r for r in observations if (r["start"],r["end"]) not in windows]
            for row in fresh:
                before=row["before"]
                self.assertEqual(before["cash"],100000)
                self.assertEqual(before["positions"],{})
                self.assertEqual(before["orders"],[])
                self.assertEqual(before["realized"],{})
                self.assertEqual(before["tax_paid"],{})
                self.assertEqual((before["fees"],before["taxes"]),(0,0))
            self.assertEqual(len({id(r["ledger"]) for r in fresh}),len(fresh))
            final=[r for r in observations if r["start"]==plan["holdout"]["start"]]
            self.assertEqual(len(final),2)
            for row in final:
                self.assertGreater(row["prior_bars"],0)
                self.assertEqual(row["result"]["metrics"]["undefined_histogram_bars"],0)
                self.assertTrue(all(t["entry_time"]>=row["start"] for t in row["result"]["trades"]))
                self.assertEqual(row["result"]["equity"][0]["equity"],100000)
                self.assertEqual(row["result"]["equity"][0]["exposure"],0)
            pairs=read_json(run/"final_holdout/MA_ONLY.json")
            self.assertEqual(pairs["baseline"]["account_initialization"],"fresh_initial_flat")
            self.assertEqual(pairs["selected"]["account_initialization"],"fresh_initial_flat")
