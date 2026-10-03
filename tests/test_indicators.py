import unittest
from trendtrade101.indicators import Indicators, Smoother, bullish_cross, positive_histogram

class IndicatorTests(unittest.TestCase):
    def test_macd_signal_startup_uses_nine_available_macd_values(self):
        state=Indicators(seed_method="sma_seed")
        result=[state.update(101+i,99+i,100+i) for i in range(40)]
        self.assertTrue(all(r.macd is None for r in result[:25]))
        self.assertIsNotNone(result[25].macd)
        self.assertTrue(all(r.histogram is None for r in result[:33]))
        self.assertAlmostEqual(result[33].signal,sum(r.macd for r in result[25:34])/9)
        self.assertAlmostEqual(result[33].histogram,result[33].macd-result[33].signal)

    def test_ema_seed_and_recursive_reference(self):
        ema = Smoother(3,0.5)
        self.assertEqual([ema.update(x) for x in [1,2,3,8,4]],[None,None,2,5,4.5])

    def test_streaming_is_prefix_causal(self):
        def calculate(count):
            state=Indicators(seed_method="sma_seed")
            return [state.update(101+i,99+i,100+i) for i in range(count)]
        self.assertEqual(calculate(60),calculate(100)[:60])

    def test_wilder_adx_on_monotone_prices(self):
        state=Indicators(seed_method="sma_seed")
        result=[state.update(101+i,99+i,100+i) for i in range(80)]
        self.assertIsNone(result[26].adx)
        self.assertAlmostEqual(result[27].adx,100)
        self.assertAlmostEqual(result[-1].adx,100)

    def test_constant_price_does_not_generate_adx_trend(self):
        state=Indicators(seed_method="sma_seed")
        result=[state.update(100,100,100) for _ in range(60)]
        self.assertEqual(result[-1].adx,0)
        self.assertEqual(result[-1].histogram,0)

    def test_histogram_requires_three_increments_not_acceleration(self):
        self.assertTrue(positive_histogram([-.2,-.1,.02,.03]))
        self.assertTrue(positive_histogram([.01,.03,.04,.045]))
        self.assertFalse(positive_histogram([.01,.02,.03]))
        self.assertFalse(positive_histogram([.01,.02,.02,.04]))
        self.assertFalse(positive_histogram([-.4,-.3,-.2,-.1]))

    def test_cross_includes_previous_equality(self):
        self.assertTrue(bullish_cross(2,2,3,2))
        self.assertFalse(bullish_cross(1,2,2,2))
        self.assertFalse(bullish_cross(None,2,3,2))

    def test_bad_bar_rejected(self):
        state=Indicators(seed_method="sma_seed")
        with self.assertRaises(ValueError):
            state.update(100,101,100)
