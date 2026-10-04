import unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from trendtrade101.audit import audit_chart
from trendtrade101.engine import Bar,OpenQuote,replay
from trendtrade101.indicators import Reading
from trendtrade101.portfolio import Ledger,LedgerPolicy,Position
from trendtrade101.signals import SignalRules
from trendtrade101.timing import Session

T=datetime(2026,1,5,9,30,tzinfo=timezone.utc)

def account():
    return Ledger(capital=100000,position_cap=100000,fee_rate=.00495,fee_cap=22,tax_rate=.20315,
                  lots={"AAA":1},policy=LedgerPolicy("market_value",True,"realization_accrual",False))

def replay_args(ledger):
    return dict(ledger=ledger,frequency="5m",market_timezone="UTC",market="US",arm="FULL",allocation="fixed",
        signal_rules=SignalRules(True,True,True,True,True),seed_method="sma_seed",adx_threshold=25,
        cross_window=5,hist_drawdown=.4,increments=3,delay_minutes=20,scaled_base=None,
        planned_exits=[],dataset_kind="synthetic")

class ExecutionAuditTests(unittest.TestCase):
    def test_completed_close_is_valued_before_the_next_simultaneous_open(self):
        ledger=account()
        ledger.cash=0
        ledger.positions["AAA"]=Position(1000,100000,100000,T)
        ledger.mark("AAA",100)
        boundary=T+timedelta(minutes=5)
        bars=[Bar("AAA",T,boundary,100,100,80,80,1000)]
        result=replay(bars,start=T,end=T+timedelta(minutes=10),allow_entries=False,
            open_quotes=[OpenQuote("AAA",T,100),OpenQuote("AAA",boundary,100)],
            **replay_args(ledger))
        marks=[p["equity"] for p in result["equity"] if p["time"]==boundary.isoformat()]
        self.assertEqual(marks,[80000,100000])
        self.assertAlmostEqual(result["metrics"]["max_drawdown"],.2)
        self.assertEqual(ledger.equity,100000)

    def test_null_future_close_does_not_remove_an_observed_open(self):
        payload={"chart":{"result":[{"timestamp":[int(T.timestamp())],"indicators":{"quote":[
            {"open":[100],"high":[None],"low":[None],"close":[None],"volume":[None]}]}}]}}
        audit=audit_chart(payload,[Session("US",T,T+timedelta(minutes=5))],frequency="5m")
        self.assertEqual(audit["bars"],[])
        self.assertEqual(audit["opens"],[{"start":T.isoformat(),"open":100}])
        ledger=account()
        ledger.queue_buy(event_id="prior-signal",ticker="AAA",signal_time=T-timedelta(minutes=20),
                         due_time=T,slope=1,adx=30,target=1000,signal_price=100)
        result=replay([],start=T,end=T+timedelta(minutes=5),
                      open_quotes=[OpenQuote("AAA",T,100)],allow_entries=False,**replay_args(ledger))
        self.assertEqual(result["orders"][0]["status"],"filled")
        self.assertEqual(ledger.positions["AAA"].quantity,10)

    def test_daily_quote_must_match_the_session_open(self):
        at=T+timedelta(minutes=1)
        payload={"chart":{"result":[{"timestamp":[int(at.timestamp())],"indicators":{"quote":[
            {"open":[100],"high":[100],"low":[100],"close":[100],"volume":[100]}]}}]}}
        result=audit_chart(payload,[Session("US",T,T+timedelta(hours=6))],frequency="daily")
        self.assertFalse(result["opens"])
        self.assertEqual(result["counts"]["outside_audited_session"],1)

    def test_parameter_change_cannot_emit_the_same_cross_pair_twice(self):
        class DeterministicReadings:
            def __init__(self,**_):pass
            def update(self,high,low,close):
                i=round(close)-100
                h=[-3,-2,-1,1,2,3][i] if i<6 else i-2
                adx=[20,20,20,26,29,31][i] if i<6 else 31
                return Reading(9 if i==0 else 11,10,h,0,h,adx,1)
        bars=[Bar("AAA",T+timedelta(minutes=5*i),T+timedelta(minutes=5*(i+1)),
                  100+i,100+i,100+i,100+i,1000,T+timedelta(hours=10)) for i in range(12)]
        ledger=account();args=replay_args(ledger)
        with patch("trendtrade101.engine.Indicators",DeterministicReadings):
            replay(bars,start=T,end=T+timedelta(minutes=25),**args)
            args.update(adx_threshold=30,cross_window=8)
            replay(bars,start=T+timedelta(minutes=25),end=T+timedelta(minutes=60),**args)
        entries=[e for e in ledger.events if e.get("side")=="buy" and e["status"]=="queued"]
        fills=[e for e in ledger.events if e.get("side")=="buy" and e["status"]=="filled"]
        self.assertEqual(len(entries),1)
        self.assertEqual(len(fills),1)
        self.assertIn("entry:US:5m:FULL:AAA",entries[0]["event_id"])
