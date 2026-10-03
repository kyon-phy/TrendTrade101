import unittest
from trendtrade101.indicators import Reading
from trendtrade101.signals import SignalRules, SignalState, target_notional

RULES=SignalRules(True,True,True,True,True)
def reading(sma, macd, hist, adx=30):
    return Reading(sma,10,macd,0,hist,adx,1)

def state(arm="FULL"):
    return SignalState(arm,rules=RULES,adx_threshold=25,cross_window=5,hist_drawdown=.4,increments=3)

class SignalTests(unittest.TestCase):
    def test_ma_only_has_no_histogram_or_adx_entry_gate(self):
        s=state("MA_ONLY")
        s.update(reading(9,-2,-2,0))
        self.assertTrue(s.update(reading(11,-3,-3,0))["entry"])

    def test_adx_gate_is_strict(self):
        s=state("MA_ADX")
        s.update(reading(9,-2,-2,25))
        self.assertFalse(s.update(reading(11,-2,-2,25))["entry"])

    def test_cross_pair_triggers_once_with_sequential_crosses(self):
        s=state()
        values=[reading(9,-3,-3),reading(11,-2,-2),reading(11,-1,-1),reading(11,1,1),reading(11,2,2)]
        events=[s.update(r)["entry"] for r in values]
        self.assertEqual(events,[False,False,False,True,False])

    def test_old_cross_falls_out_of_inclusive_window(self):
        s=state()
        values=[reading(9,-6,-6),reading(11,-5,-5),reading(11,-4,-4),reading(11,-3,-3),
                reading(11,-2,-2),reading(11,-1,-1),reading(11,1,1)]
        self.assertFalse(any(s.update(r)["entry"] for r in values))

    def test_zero_does_not_swallow_exit_and_resets_peak(self):
        s=state("MA_ONLY")
        s.update(reading(9,1,1))
        s.update(reading(9,2,2))
        result=s.update(reading(9,0,0))
        self.assertTrue(result["exit"])
        self.assertIsNone(result["histogram_peak"])
        self.assertFalse(s.update(reading(9,.1,.1))["exit"])

    def test_drawdown_boundary_includes_equality(self):
        s=state()
        s.update(reading(9,10,10))
        self.assertTrue(s.update(reading(9,6,6))["exit"])

    def test_nonpositive_exit_does_not_require_a_previous_positive_peak(self):
        s=state("MA_ONLY")
        self.assertTrue(s.update(reading(9,-2,-2))["exit"])
        self.assertTrue(s.update(reading(9,-1,-1))["exit"])
        self.assertTrue(s.update(reading(9,0,0))["exit"])
        self.assertTrue(s.update(reading(9,0,0))["exit"])

    def test_fixed_sizing_independent_of_adx(self):
        args=dict(initial_capital=100000,allocation="fixed",adx_threshold=25,arm="MA_ONLY",base=None)
        self.assertEqual(target_notional(adx=0,**args),target_notional(adx=100,**args))

    def test_weighted_nonpositive_budget_does_not_add_gate(self):
        args=dict(initial_capital=100000,allocation="adx_scaled",adx_threshold=30,arm="MA_ONLY",base=10000)
        self.assertEqual(target_notional(adx=10,**args),0)
        self.assertEqual(target_notional(adx=25,**args),5000)
