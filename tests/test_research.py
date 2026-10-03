import unittest
from datetime import date
from trendtrade101.research import Interval,folds,guard_training,candidates,select_candidate,maximum_drawdown,holdout_from_complete_sessions

class ResearchTests(unittest.TestCase):
    def test_no_redundant_grid_axes(self):
        self.assertEqual([len(candidates(a)) for a in ["MA_ONLY","MACD_HIST","MA_ADX","MACD_HIST_ADX","FULL"]],[3,3,9,9,27])

    def test_minute_folds_never_touch_final_holdout(self):
        h=Interval(date(2026,9,28),date(2026,10,5))
        fs=list(folds(date(2026,7,10),h,frequency="5m"))
        self.assertEqual(fs[0][0].start,date(2026,7,13))
        for train,test in fs:
            self.assertLessEqual(test.end,h.start)
            self.assertEqual((train.end-train.start).days,14)
            self.assertEqual((test.end-test.start).days,7)
            guard_training(train,h)

    def test_daily_six_month_windows_and_one_month_steps(self):
        h=Interval(date(2026,9,1),date(2026,10,1))
        fs=list(folds(date(2021,10,4),h,frequency="daily"))
        self.assertEqual(fs[0][0],Interval(date(2021,11,1),date(2022,5,1)))
        self.assertEqual(fs[-1][1].end,h.start)

    def test_holdout_reuse_rejected(self):
        h=Interval(date(2026,9,1),date(2026,10,1))
        with self.assertRaises(ValueError):guard_training(h,h)

    def test_calendar_completeness_required(self):
        with self.assertRaises(ValueError):
            holdout_from_complete_sessions([date(2026,10,2)],frequency="5m",
                                           as_of=date(2026,10,3),audited_period_ends=set())

    def test_holiday_week_final_period_uses_calendar(self):
        h=holdout_from_complete_sessions([date(2026,9,24)],frequency="5m",
                    as_of=date(2026,9,27),audited_period_ends={date(2026,9,24)})
        self.assertEqual(h,Interval(date(2026,9,21),date(2026,9,28)))

    def test_constraint_and_sparse_flag_do_not_fabricate_winner(self):
        args=dict(objective="after_tax_return",neighborhood="axis_adjacent_median",
                  minimum_trades=5,sparse_is_filter=False,max_drawdown=.3)
        row=dict(scope="training",parameters=candidates("FULL")[0],after_tax_return=.1,max_drawdown=.31,trades=10)
        self.assertIsNone(select_candidate([row],**args))
        row.update(max_drawdown=.1,trades=1)
        self.assertTrue(select_candidate([row],**args)["sparse"])
        row["scope"]="holdout"
        with self.assertRaises(ValueError):select_candidate([row],**args)

    def test_neighbor_region_beats_isolated_peak(self):
        params=candidates("MA_ONLY")
        rows=[dict(scope="training",parameters=p,after_tax_return=r,max_drawdown=.1,trades=10)
              for p,r in zip(params,[.01,.02,.9])]
        winner=select_candidate(rows,objective="after_tax_return",neighborhood="axis_adjacent_median",
                                minimum_trades=5,sparse_is_filter=False,max_drawdown=.3)
        self.assertEqual(winner["neighbor_count"],2)

    def test_drawdown_includes_unrealized_decline(self):
        self.assertAlmostEqual(maximum_drawdown([100,120,80,110]),1/3)
