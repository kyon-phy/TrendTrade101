"""Status evidence is independent from local software-test timestamps."""
import tempfile
import unittest
from pathlib import Path
from trendtrade101.readiness import status
from trendtrade101.storage import write_json


class StatusObservationTests(unittest.TestCase):
    def test_new_public_observation_is_not_hidden_by_old_private_test_state(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            write_json(root/"config/project_status.json",{
                "reported_at":"2026-10-04T06:15:27Z","scope":"Parent-observed preflight",
                "provider_preflight":{"status":"blocked","message":"HTTP 429"}})
            write_json(root/".private/status.json",{
                "reported_at":"2026-10-03T13:47:06Z",
                "provider_preflight":{"status":"blocked","message":"CONNECT 403"},
                "verification":{"checked_at":"2026-10-05T00:00:00Z","tests_passed":93}})
            report=status(root)
            self.assertEqual(report["stages"][2]["detail"],"HTTP 429")
            self.assertEqual(report["provider_preflight"]["observed_at"],"2026-10-04T06:15:27Z")
            self.assertEqual(report["verification"]["tests_passed"],93)

    def test_preflight_success_is_not_a_completed_market_data_audit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            write_json(root/"config/project_status.json",{
                "reported_at":"2026-10-03T00:00:00Z",
                "provider_preflight":{"status":"blocked","message":"Old error"}})
            write_json(root/".private/status.json",{
                "provider_preflight":{"status":"complete","message":"Preflight succeeded",
                    "observed_at":"2026-10-04T00:00:00Z"}})
            report=status(root)
            self.assertEqual(report["provider_preflight"]["message"],"Preflight succeeded")
            self.assertEqual(report["stages"][2]["status"],"not_started")
            self.assertIn("No complete verified-data audit",report["stages"][2]["detail"])

    def test_invalid_observation_date_cannot_supersede_dated_evidence(self):
        for stamp in ("not-a-date","2026-10-05T00:00:00",None):
            with self.subTest(stamp=stamp),tempfile.TemporaryDirectory() as d:
                root=Path(d)
                write_json(root/"config/project_status.json",{
                    "reported_at":"2026-10-04T06:15:27Z",
                    "provider_preflight":{"status":"blocked","message":"HTTP 429"}})
                write_json(root/".private/status.json",{
                    "provider_preflight":{"status":"complete","observed_at":stamp,"message":"Undated"}})
                self.assertEqual(status(root)["stages"][2]["detail"],"HTTP 429")
