import unittest
from trendtrade101.reporting import summarize

class ReportingTests(unittest.TestCase):
    def test_time_weighting_cost_views_and_unique_failure_counts(self):
        curve=[{"time":"2026-01-01T00:00:00+00:00","equity":100,"capital_utilization":0,
                "largest_position_equity_share":0,"position_hhi":0},
               {"time":"2026-01-01T01:00:00+00:00","equity":90,"capital_utilization":.5,
                "largest_position_equity_share":.3,"position_hhi":.52},
               {"time":"2026-01-01T04:00:00+00:00","equity":110,"capital_utilization":0,
                "largest_position_equity_share":0,"position_hhi":0}]
        events=[{"event_id":"exit","reason":"scheduled_daily_flatten","status":status}
                for status in ("missing_price","missing_price","unfilled_at_end")]
        metrics=summarize(curve,100,2,3,[],events)
        self.assertAlmostEqual(metrics["calendar_time_weighted_capital_utilization"],.375)
        self.assertAlmostEqual(metrics["max_drawdown"],.1)
        self.assertAlmostEqual(metrics["gross_return"],.15)
        self.assertAlmostEqual(metrics["after_fee_return"],.13)
        self.assertEqual(metrics["orders_with_missing_price"],1)
        self.assertEqual(metrics["unsuccessful_scheduled_liquidations"],1)
        self.assertEqual(metrics["maximum_single_position_equity_share"],.3)
        self.assertTrue(metrics["sparse"])
