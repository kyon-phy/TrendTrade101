import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime,timedelta,timezone
from pathlib import Path
from trendtrade101.engine import Bar,replay
from trendtrade101.portfolio import Ledger,LedgerPolicy
from trendtrade101.signals import SignalRules
from trendtrade101.inputs import verify
from trendtrade101.server import make_server
from trendtrade101.readiness import require_ready

class IntegrationTests(unittest.TestCase):
    def test_missing_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.assertEqual(verify(root)["status"],"blocked")
            with self.assertRaises(RuntimeError):require_ready(root)

    def test_dashboard_exposes_status_not_private_files(self):
        with tempfile.TemporaryDirectory() as d:
            server=make_server(Path(d),port=0)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                base=f"http://127.0.0.1:{server.server_port}"
                with urllib.request.urlopen(base+"/api/status") as r:
                    result=json.load(r)
                self.assertEqual(result["results"],[])
                self.assertEqual(result["stages"][-1]["status"],"sealed")
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(base+"/.private/inputs/file.json")
                self.assertEqual(error.exception.code,404)
                with urllib.request.urlopen(base) as r:
                    self.assertIn(b"No backtest results yet",r.read())
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_synthetic_replay_is_causal_and_uses_actual_opens(self):
        start=datetime(2026,1,5,9,tzinfo=timezone.utc)
        prices=[100]*20+[80]*5+[120]*15
        bars=[Bar("AAA",start+timedelta(minutes=5*i),start+timedelta(minutes=5*(i+1)),
                  p,p,p,p,1000,start+timedelta(hours=10)) for i,p in enumerate(prices)]
        ledger=Ledger(capital=100000,position_cap=100000,fee_rate=.00495,fee_cap=22,tax_rate=.20315,
                      lots={"AAA":1},policy=LedgerPolicy("market_value",True,"realization_accrual",False))
        args=dict(ledger=ledger,start=start,end=bars[-1].end,frequency="5m",market_timezone="UTC",
            arm="MA_ONLY",allocation="fixed",signal_rules=SignalRules(True,True,True,True,True),
            seed_method="sma_seed",adx_threshold=25,cross_window=5,hist_drawdown=.4,increments=3,
            delay_minutes=20,scaled_base=None,planned_exits=[],dataset_kind="synthetic")
        result=replay(bars,**args)
        fills=[x for x in result["orders"] if x["status"]=="filled"]
        self.assertTrue(fills)
        for f in fills:
            self.assertGreaterEqual(datetime.fromisoformat(f["time"]),datetime.fromisoformat(f["due_time"]))
            bar=next(b for b in bars if b.start.isoformat()==f["time"])
            self.assertEqual(f["price"],bar.open)
        self.assertEqual(result["status"],"synthetic_test_only")
        args["dataset_kind"]="real"
        with self.assertRaises(ValueError):replay(bars,**args)

    def test_overlapping_bars_are_rejected(self):
        t=datetime(2026,1,5,tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            Bar("AAA",t,t,1,1,1,1,1)
