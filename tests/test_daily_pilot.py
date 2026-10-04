"""Synthetic pilot isolation tests; never a cache audit or historical result."""
from dataclasses import replace
from datetime import datetime
import json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from fixture_support import ROOT,build_fixture
from trendtrade101.audit_package import audit_local_charts
from trendtrade101.dataset import PILOT_SCOPE,PILOT_KIND,PILOT_AUDITS,load_dataset,fingerprint
from trendtrade101.dashboard import result_catalog,pilot_progress,research_progress
from trendtrade101.inputs import EXPECTED,project_members,symbols_for
from trendtrade101.orchestration import freeze_plan,run_walk_forward,consume_holdout
from trendtrade101.pilot import PILOT_CONVENTIONS,freeze_pilot,run_pilot
from trendtrade101.readiness import status
from trendtrade101.storage import read_json,write_json,sha256

def setup_fixture(root,multiplier=1):
    shutil.copytree(ROOT/"config",root/"config")
    dataset=build_fixture(root/"data",frequency="daily",holdout_multiplier=multiplier)
    manifest=dataset.manifest.copy()
    members=symbols_for(project_members(ROOT),"US","existing_25","daily")
    bars=[b for b in read_json(root/"data/bars.json") if b["ticker"] in members]
    write_json(root/"data/bars.json",bars)
    manifest.update(kind="synthetic_pilot_fixture",research_scope=PILOT_SCOPE,
        study_start="2025-01-01T00:00:00-05:00",calendar_complete_from="2025-01-01",
        members={t:manifest["members"][t] for t in members},bars_sha256=sha256(root/"data/bars.json"))
    write_json(root/"data/dataset.json",manifest)
    config=read_json(root/"config/baseline.json")
    write_json(root/"config/daily_pilot.json",dict(schema_version=1,research_scope=PILOT_SCOPE,
        source_version=config["source_version"],source_sha256=config["source_sha256"],
        scope_approval="recorded",execution_ready=True,interval={"start":"2025-01-01","end":"2025-09-01"},
        protected_from="2025-09-01",technical_conventions=PILOT_CONVENTIONS))
    return load_dataset(root,root/"data/dataset.json",allow_synthetic=True,allow_pilot=True)

class DailyPilotTests(unittest.TestCase):
    def test_pilot_cannot_enter_formal_load_plan_optimization_or_holdout(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root)
            with self.assertRaisesRegex(ValueError,"isolated pilot"):
                load_dataset(root,dataset.source_path,allow_synthetic=True)
            with self.assertRaisesRegex(ValueError,"formal research"):
                freeze_plan(root,dataset,"existing_25",root/".private/runs/formal")
            run=root/".private/pilots/test";plan=freeze_pilot(root,dataset,run)
            with self.assertRaisesRegex(ValueError,"formal research"):
                run_walk_forward(root,dataset,run)
            with self.assertRaisesRegex(ValueError,"formal holdout"):
                consume_holdout(root,plan,run)
            self.assertFalse((root/".private/holdout_registry").exists())

    def test_canonical_scope_and_execution_lock_are_required(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root)
            config=read_json(root/"config/daily_pilot.json")
            config["scope_approval"]="pending_canonical_record"
            write_json(root/"config/daily_pilot.json",config)
            with self.assertRaisesRegex(ValueError,"canonical pilot scope"):
                freeze_pilot(root,dataset,root/".private/pilots/test")
            config["scope_approval"]="recorded";config["execution_ready"]=False
            write_json(root/"config/daily_pilot.json",config)
            with self.assertRaisesRegex(ValueError,"locked"):
                freeze_pilot(root,dataset,root/".private/pilots/test")

    def test_protected_prices_do_not_change_any_baseline_and_no_formal_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            outputs=[]
            for name,multiplier in (("a",1),("b",20)):
                root=Path(d)/name;dataset=setup_fixture(root,multiplier)
                run=root/".private/pilots/test";freeze_pilot(root,dataset,run)
                outputs.append(run_pilot(root,dataset,run))
                result=read_json(run/"baseline/FULL.json")
                self.assertEqual(result["phase"],"exploratory_daily_pilot")
                self.assertEqual(result["status"],"synthetic_test_only")
                self.assertEqual(result["metrics"]["initial_equity"],100000)
                self.assertIsNone(result["scope"]["delay_minutes"])
                self.assertFalse(result["formal_holdout_consumed"])
                self.assertFalse((root/".private/runs").exists())
                self.assertFalse((root/".private/holdout_registry").exists())
                self.assertEqual(result_catalog(root),[])
                self.assertEqual(pilot_progress(root),[])
                with self.assertRaisesRegex(ValueError,"already complete"):run_pilot(root,dataset,run)
            self.assertEqual(outputs[0],outputs[1])
            self.assertEqual(list(outputs[0]),["FULL"])

    def test_unknown_actions_block_market_without_removing_members(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root)
            dataset.manifest["unresolved_corporate_actions"]=[{"ticker":"NVDA","type":"unknown_distribution"}]
            with self.assertRaisesRegex(ValueError,"NVDA"):
                freeze_pilot(root,dataset,root/".private/pilots/test")
            self.assertEqual(len(dataset.manifest["members"]),12)

    def test_boundary_and_private_destination_are_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root)
            with self.assertRaisesRegex(ValueError,"child of"):
                freeze_pilot(root,dataset,root/".private/runs/test")
            config=read_json(root/"config/daily_pilot.json")
            config["interval"]["end"]="2025-10-01"
            write_json(root/"config/daily_pilot.json",config)
            with self.assertRaisesRegex(ValueError,"protected boundary"):
                freeze_pilot(root,dataset,root/".private/pilots/test")

    def test_plan_edits_cannot_change_the_predeclared_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root);run=root/".private/pilots/test"
            plan=freeze_pilot(root,dataset,run);plan["baseline"]["adx_threshold"]=20
            write_json(run/"plan.json",plan)
            with self.assertRaisesRegex(ValueError,"plan differs"):run_pilot(root,dataset,run)

    def test_pilot_display_does_not_advance_formal_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root);run=root/".private/pilots/test"
            plan=freeze_pilot(root,dataset,run);run_pilot(root,dataset,run)
            # Only this isolated temporary display fixture receives a real-kind label.
            plan["dataset_kind"]=PILOT_KIND;write_json(run/"plan.json",plan)
            for path in (run/"baseline").glob("*.json"):
                result=read_json(path);result["dataset_kind"]=PILOT_KIND;write_json(path,result)
            self.assertEqual(len(result_catalog(root)),1)
            self.assertEqual(len(pilot_progress(root)),1)
            self.assertEqual(research_progress(root),[])
            stages={s["id"]:s["status"] for s in status(root)["stages"]}
            self.assertEqual(stages["baseline"],"not_started")
            self.assertEqual(stages["final_holdout"],"sealed")

    def test_cache_scope_is_not_formal_maximum_history_certification(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(ROOT/"config",root/"config")
            tickers=symbols_for(project_members(root),"US","existing_25","daily")
            at="2025-01-02T09:30:00-05:00"
            payload={"chart":{"result":[{"meta":{"exchangeTimezoneName":"America/New_York","currency":"USD"},
                "timestamp":[int(datetime.fromisoformat(at).timestamp())],
                "indicators":{"quote":[{"open":[100],"high":[101],"low":[99],"close":[100],"volume":[100]}]}}]}}
            write_json(root/"synthetic.json",payload)
            write_json(root/"calendar.json",{"complete_from":"2025-01-01","complete_through":"2025-01-31",
                "sessions":[{"start":at,"end":"2025-01-02T16:00:00-05:00","breaks":[]}]})
            capture={"research_scope":PILOT_SCOPE,"configuration_source_sha256":EXPECTED["TrendTrade101_Backtest_Configuration.md"],
                "provider":"Yahoo","market":"US","frequency":"daily","timezone":"America/New_York",
                "as_of":"2025-02-01T00:00:00-05:00","study_start":"2025-01-01T00:00:00-05:00",
                "calendar_file":"calendar.json","calendar_sha256":sha256(root/"calendar.json"),
                "vendor_ohlc_basis":"historical_unadjusted","splits":[],
                "review":{k:{"status":"verified","evidence":"Synthetic test only"} for k in PILOT_AUDITS},
                "members":{t:{"file":"synthetic.json","sha256":sha256(root/"synthetic.json"),"lot":1,
                    "availability":"available","first_trade_date":"2020-01-01",
                    "retrieved_at":"2025-02-01T00:00:00-05:00","request":{"fixture":True}} for t in tickers}}
            write_json(root/"capture.json",capture)
            output=root/".private/data"
            with self.assertRaisesRegex(ValueError,"audit-pilot-local"):
                audit_local_charts(root,root/"capture.json",output)
            result=audit_local_charts(root,root/"capture.json",output,pilot=True)
            dataset=load_dataset(root,Path(result["dataset"]),allow_pilot=True)
            self.assertEqual(dataset.kind,PILOT_KIND)
            self.assertNotIn("maximum_history",dataset.manifest["audit"])
            self.assertEqual(len(dataset.manifest["members"]),12)
            with self.assertRaisesRegex(ValueError,"isolated pilot"):
                load_dataset(root,Path(result["dataset"]))

    def test_an_existing_formal_reservation_prevents_pilot_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);dataset=setup_fixture(root)
            write_json(root/".private/runs/formal/plan.json",{"market":"US","frequency":"daily",
                "holdout":{"start":"2025-08-01","end":"2025-09-01"}})
            with self.assertRaisesRegex(ValueError,"already reserved"):
                freeze_pilot(root,dataset,root/".private/pilots/test")
