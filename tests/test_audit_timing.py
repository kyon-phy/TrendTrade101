import unittest
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from trendtrade101.timing import Session,eligible_open,daily_due,entry_allowed
from trendtrade101.audit import audit_chart

TZ=ZoneInfo("Asia/Tokyo")
def t(hour,minute=0):
    return datetime(2026,7,6,hour,minute,tzinfo=TZ)
def session():
    return Session("JP",t(9),t(15,25),((t(11,30),t(12,30)),))

class AuditTests(unittest.TestCase):
    def test_lunch_not_concatenated_and_auction_excluded(self):
        intervals=list(session().expected_bars())
        starts=[a for a,b in intervals]
        self.assertNotIn(t(11,30),starts)
        self.assertNotIn(t(12),starts)
        self.assertNotIn(t(15,25),starts)
        self.assertIn(t(12,30),starts)

    def test_non_aligned_due_never_rounds_backwards(self):
        self.assertEqual(eligible_open(t(10),[t(10,20),t(10,25)],delay_minutes=21),t(10,25))

    def test_lunch_delayed_fill_uses_next_observed_open(self):
        self.assertEqual(eligible_open(t(11,20),[t(11,25),t(12,30)],delay_minutes=20),t(12,30))

    def test_cutoff_is_signal_time_not_fill_time(self):
        self.assertTrue(entry_allowed(t(14,20),session(),20))
        self.assertFalse(entry_allowed(t(14,25),session(),20))

    def test_daily_has_no_intraday_delay(self):
        us=Session("US",t(9),t(15))
        tomorrow=Session("US",t(9)+timedelta(days=1),t(15)+timedelta(days=1))
        self.assertEqual(daily_due(t(15),[us,tomorrow]),tomorrow.start)

    def test_short_tail_retained(self):
        s=Session("TEST",t(9),t(9,12))
        self.assertEqual(list(s.expected_bars())[-1],(t(9,10),t(9,12)))

    def test_null_terminal_duplicate_and_gap_are_flagged(self):
        stamps=[t(9),t(9,5),t(9,5),t(9,15),t(15,25)]
        quote={k:[100,100,100,None,100] for k in ["open","high","low","close"]}
        quote["volume"]=[1]*5
        payload={"chart":{"result":[{"timestamp":[int(x.timestamp()) for x in stamps],
                                    "indicators":{"quote":[quote]}}],"error":None}}
        report=audit_chart(payload,[session()],frequency="5m")
        self.assertEqual(report["counts"]["usable"],2)
        self.assertEqual(report["counts"]["duplicate_timestamp"],1)
        self.assertEqual(report["counts"]["null_or_nonfinite"],1)
        self.assertEqual(report["counts"]["terminal_observation"],1)
        self.assertGreater(report["counts"]["missing_expected_intervals"],0)

    def test_provider_failure_is_not_empty_success(self):
        report=audit_chart({"chart":{"error":{"code":"Not Found"}}},[],frequency="5m")
        self.assertEqual(report["status"],"unavailable")
