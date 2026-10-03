# Execution definitions reconciled with canonical v0.13

The designated configuration writer saved these accepted definitions in authoritative v0.13. That entire source (1,031 lines) was read and reconciled with the local machine configuration, explicit policy objects and synthetic tests. Its expected SHA256 is 707cf2472d97d535061395a439fbe81764e9fec53b303edb88419d90c5553bce. Exact source-byte validation and market-data audit remain prerequisites for historical execution.

| Area | Accepted definition |
|---|---|
| Cross window | Current bar plus previous N-1 bars: [t-N+1, t] |
| Independent FULL event | One order for each distinct most-recent SMA/MACD cross pair |
| Histogram exit | H <= 0 independently triggers exit before resetting the hump; otherwise require decline and include equality at 60% of running peak |
| Reservation | Signal-price target amount plus estimated buy fee, including the lot-rounding remainder; fill-time quantity can shrink but cannot increase |
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

The replay implementation deliberately rejects real datasets. This guard must remain until exact input verification and audited orchestration are complete.
