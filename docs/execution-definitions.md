# Accepted definitions awaiting canonical synchronization

These definitions were accepted during implementation. They are represented by explicit policy objects and synthetic tests. They do not become effective for historical research until saved to the authoritative configuration under its existing identity and version guard. The supplied source remains v0.12.

| Area | Accepted definition |
|---|---|
| Cross window | Current bar plus previous N-1 bars: [t-N+1, t] |
| Independent FULL event | One order for each distinct most-recent SMA/MACD cross pair |
| Histogram exit | During decline, include equality at 60% of running peak; evaluate zero/negative before resetting the hump |
| Reservation | Signal-price target quantity plus buy fee; fill-time quantity can shrink but cannot increase |
| Position caps | Then-known market value; fees and reservations also constrain cash |
| Priority tie | Stable ticker, then event ID, following stored signal-time SMA slope |
| Minute flatten | Last calendar-scheduled continuous-session bar Open; queue 20 minutes earlier |
| Daily flatten | Preplanned last trading-day Open of each month; prohibit buys that day |
| Tax | Realization-time annual net-profit accrual, current-year refund on offsetting losses; no cross-year carry |
| Calendar boundaries | Monday weeks, first-of-month months, half-open score intervals |
| Objective | After-tax training return with maximum drawdown at most 30% |
| Neighborhood | Candidate plus one-axis adjacent candidates, median eligible neighborhood return |
| Score tie | Lower drawdown, then stable parameter order |
| Sparse trades | Fewer than five complete aggregate exits is a reporting flag, not an exclusion filter |

A last observed bar discovered retrospectively is not an acceptable flattening target. The scheduled target must come from the calendar before replay. If it is missing, keep the pending sell and residual position, and report failure.

The accepted definitions do not resolve every data interpretation. Indicator seeding is available as an explicit SMA-seed technical convention but remains unsynchronized. JP ADX-scaled base, actual legal lots, split normalization, corporate distributions, exact complete holdout dates and coverage remain pending. Primary experiments retain fixed 1/15 sizing; a fully crossed weighted ten-arm experiment is not enabled.

The replay implementation deliberately rejects real datasets. This guard must remain until the canonical update and audited orchestration are complete.
