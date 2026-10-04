"""Yahoo-shaped synthetic payloads test normalization; no vendor data is used."""
import tempfile,unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from trendtrade101.audit_package import audit_local_charts
from trendtrade101.dataset import REQUIRED_AUDITS,load_dataset
from trendtrade101.storage import write_json,read_json,sha256

class AuditPackageTests(unittest.TestCase):
    def test_audit_requires_evidence_before_reading_price_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_json(root/"capture.json",{"provider":"Yahoo","review":{}})
            with self.assertRaisesRegex(ValueError,"evidence-backed"):
                audit_local_charts(root,root/"capture.json",root/"output")
            self.assertFalse((root/"output").exists())

    def test_each_capture_timestamp_limits_observable_bars_and_splits_restore_units(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=[{"ticker":"TEST","market":"US","frequency":"5m"}]
            times=["2026-06-30T09:30:00-04:00","2026-07-01T09:30:00-04:00"]
            payload={"chart":{"result":[{"meta":{"exchangeTimezoneName":"America/New_York","currency":"USD"},
                "timestamp":[int(datetime.fromisoformat(t).timestamp()) for t in times],
                "indicators":{"quote":[{"open":[10,11],"high":[10,11],"low":[10,11],
                                         "close":[10,11],"volume":[100,200]}]}}]}}
            write_json(root/"synthetic.json",payload)
            write_json(root/"calendar.json",{"complete_from":"2026-06-29","complete_through":"2026-07-05","sessions":[
                {"start":times[0],"end":"2026-06-30T09:35:00-04:00","breaks":[]},
                {"start":times[1],"end":"2026-07-01T09:35:00-04:00","breaks":[]}]})
            capture={"provider":"Yahoo","market":"US","frequency":"5m","timezone":"America/New_York",
                "study_start":times[0],
                "as_of":"2026-07-01T09:35:00-04:00","calendar_file":"calendar.json",
                "calendar_sha256":sha256(root/"calendar.json"),"vendor_ohlc_basis":"split_adjusted_only",
                "review":{k:{"status":"verified","evidence":"Synthetic test fixture, not a real audit."} for k in REQUIRED_AUDITS},
                "members":{"TEST":{"lot":1,"availability":"available","first_trade_date":"2020-01-01",
                    "file":"synthetic.json","sha256":sha256(root/"synthetic.json"),
                    "retrieved_at":"2026-07-01T09:32:00-04:00","request":{"fixture":True}}},
                "splits":[{"ticker":"TEST","at":"2026-07-01T09:30:00-04:00","ratio":2}],
                "unresolved_corporate_actions":[{"ticker":"TEST","type":"unverified_distribution"}]}
            write_json(root/"capture.json",capture)
            with patch("trendtrade101.audit_package.project_members",return_value=rows),patch("trendtrade101.dataset.project_members",return_value=rows):
                result=audit_local_charts(root,root/"capture.json",root/"output")
                ds=load_dataset(root,Path(result["dataset"]))
            self.assertEqual(len(ds.bars),1)
            self.assertEqual(ds.bars[0].open,20)
            self.assertEqual(len(ds.open_quotes),2)
            self.assertEqual(ds.open_quotes[1].open,11)
            self.assertEqual(ds.manifest["per_symbol_audit"]["TEST"]["counts"]["incomplete_at_retrieval"],1)
            self.assertEqual(ds.manifest["complete_period_ends"],[])
            self.assertEqual(result["unresolved_action_symbols"],["TEST"])
            self.assertEqual(ds.manifest["unresolved_corporate_actions"],capture["unresolved_corporate_actions"])
