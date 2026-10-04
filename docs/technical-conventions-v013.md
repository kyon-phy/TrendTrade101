# Implementation audit and remaining conventions

Status: this memo began with the v0.13 audit. Canonical v0.14 now approves the split/share basis and account-state rows; see [the synchronization record](accounting-v014.md). Other proposals remain pending and no historical result is claimed. This memo does not replace the canonical record. The real execution flag remains false.

## Already approved: do not reopen these decisions

- All 201 memberships, 127 distinct market/security pairs and the single US daily NKE-to-PYPL replacement. Earlier minute observations retain the disclosed selection look-ahead bias. No new ranking or replacement is required.
- Separate USD 100,000 and JPY 16,000,000 accounts; five entry arms with fixed initial-capital 1/15 sizing for the primary comparison. The ADX formula remains an alternative capability; a ten-arm experiment is not selected.
- SMA 5/20, EMA MACD 12/26/9, ADX 14, strict ADX > threshold, N5 baseline and the inclusive [t-N+1,t] window. A distinct double-cross pair emits at most once.
- Current positive-hump peak, nonpositive exit before reset, and the declining inclusive 60%-height branch at the 40% baseline drawdown.
- Fixed minute D20, signal cutoff 63 minutes before session close, delayed observed Open fills; daily next-session Open without an intraday delay.
- Minute calendar-planned last continuous-bar Open liquidation; daily calendar-planned last-trading-day Open liquidation and whole-day buy ban. Missing fills retain actual residual risk.
- Fee-inclusive cash reservations, shrink-only queued quantities, held-market-value-plus-proposed-fill caps, sell-first ordering and stored slope/ticker/event-ID priority.
- The specified commissions, annual realized-net-profit tax accrual and bounded current-year refunds, with no loss carry across years. These remain simulation assumptions, not verified brokerage/tax advice.
- Monday/month-start windows, two-week/one-week and six-month/one-month walk-forward periods, last complete week/month holdouts, training-only after-tax eligible-neighborhood median selection, MDD <= 30% and sparse-closure reporting without a new exclusion filter.

## Narrow technical convention bundle for canonical synchronization

The following conventions are explicit in code and synthetic fixtures. They are not silently promoted to effective real-run defaults. Rows marked "verification" elaborate an already disclosed implementation assumption; they are not requests to reselect the strategy.

| Topic | Precise proposed convention | Status and impact |
|---|---|---|
| Indicator inputs and scale | Completed Close for SMA/EMA/MACD; completed High/Low/previous Close for ADX. H = MACD minus signal, without a factor of two. | Technical verification and canonical freeze. Provider field basis still requires evidence. |
| EMA startup | Seed each EMA with the arithmetic mean of its first period-length valid observations; then alpha = 2/(period+1). EMA12 begins on observation 12, EMA26/MACD on 26, EMA9 of available MACD and H on 34. | Material startup convention to confirm. Do not substitute first-price seeding or zero padding. |
| Wilder ADX startup | First OHLC establishes previous values only. Seed TR, +DM and -DM with the mean of 14 transitions (observations 2-15), then alpha = 1/14. Seed ADX with 14 available DX values (observations 15-28), then alpha = 1/14. Equal directional moves give both DM values zero; zero TR/DI denominator gives zero DI/DX. | Material startup convention to confirm; synthetic reference tests cover the recurrence. |
| Crosses, histogram and slope | Previous fast <= slow and current fast > slow; three positive differences across four H values, only the last H required positive; slope = 100 * (SMA5[t]/SMA5[t-1]-1). | Already disclosed implementation assumptions in sections 4/9; verify and freeze, not a new optimization axis. |
| Missing bars and startup readiness | Count N and smoothing observations on valid completed bars only; never fabricate gap bars. Preserve recursive/cross/hump state through lunch, overnight and flat positions. Keep per-arm indicator availability; do not add a common ADX filter or an arbitrary burn-in count. If H is still undefined, its exit cannot trigger; disclose that startup limitation. Flag an initial positive hump whose preceding nonpositive boundary is unavailable. | Gap/startup convention needs confirmation. A common exit-ready warmup gate would change early/IPO entries and needs a separate decision; it is not enabled. |
| Event identity | Market, frequency, entry arm, ticker and underlying cross indices in the immutable ticker history form the entry ID. Signal/due/fill times are separate fields. Ledger deduplication survives fold parameter changes. | Serialization is an implementation detail requested for verification; fixed and tested without changing the approved once-per-pair rule. |
| Valuation | After-tax account equity marked at observed Opens, completed Closes and planned events; a missing observation retains its last known mark. Drawdown includes unrealized exposure. Utilization is weighted by calendar elapsed time, including overnight/weekend periods. | Valuation/reporting convention to confirm. No future Close marks an earlier Open. |
| Fold account state | Each training candidate starts flat at original capital. Ordinary OOS folds carry cash, tax state, pending orders and residual positions; sizing still uses original capital. No eligible candidate means no new entries while existing risk remains managed. | Approved in v0.14; synchronized and covered by synthetic account-state regressions. |
| Final account state | The final baseline and selected strategy use separate fresh accounts at original capital, warmed only by earlier indicator/event history. They do not inherit development-trial positions. | Approved in v0.14: separate fresh final accounts. Final returns do not continue the OOS account. |
| Partial windows and study boundary | Score only full calendar windows. An audited holiday/weekend at the period start is compatible with a full window; a partially available first trading session is not. Record the study-start boundary separately from earlier warmup. Daily target remains five years; minute scope remains maximum actually accessible history. | Partial-window policy needs confirmation; exact boundaries require data evidence. Code requires an explicit real-data study start and calendar coverage start. |

Only the account-state and split/share-unit rows were approved in v0.14. Do not promote the rest of this technical bundle to approved by association. Remaining startup, gap, valuation and window conventions still need verification/freeze; no extra parameter grid or common warmup gate is introduced.

## JP sizing, legal units and corporate actions

| Topic | Already selected | Narrow recommendation / required evidence | Blocking scope |
|---|---|---|---|
| JP ADX base | JPY 16m initial account; fixed target JPY 16m/15. ADX mode remains an alternative. | Keep JPY 1.6m (10% of initial capital) as the proposed ADX base, with scale 1. Only adopt it when the JP weighted branch is selected. For ADX-gated arms use the candidate threshold as denominator; without the gate retain the disclosed reference 25 and log nonpositive targets. | Does not block the fixed 1/15 primary study. JP weighted execution remains disabled without its explicit base. |
| Legal lot size | Whole legal units, no fractional buys; US 1 and JP ordinary-stock 100 are baseline descriptions. | Verify each frozen security and effective historical interval, including instrument type/ADR units and lot changes. These are evidence questions, not values a user approval can make legally true. Use a constant per-security unit only when the audit supports it across the sample. | Real data audit. The current loader rejects dated lot-change metadata; a dated execution model must be implemented if such changes are found. |
| Split quantity basis | Splits must not manufacture losses, crosses or inconsistent P&L. | Approved historical executable share units: restore historical prices only from an evidenced split-only vendor basis, adjust actual shares at the effective split and rescale past indicator state at that instant. Preserve source fields, split events and hashes. Do not assume Yahoo's basis. | Basis approved in v0.14; vendor/action evidence and execution guards still apply. |
| Pending versus held split quantities | Filled shares and pending order intentions are different states. | Pending quantities may shrink to legal units after a split. A fractional or non-lot actual holding needs an evidenced entitlement/odd-lot execution model; stop the affected run rather than round away property or invent cash. | Only affected securities/runs; no silent member removal. Current code blocks unsupported held entitlements. |
| Ordinary cash dividends | Dividend income is excluded. | Retain executable price changes and record dividend events, but do not add dividend cash or use dividend-reinvested adjusted Close. Verify the selected OHLC basis. | Data-field verification; no need to reopen the already selected exclusion. |
| Spin-offs, rights, stock/special distributions, mergers, ADR changes | No general economic treatment is selected. | The approved v0.14 policy pauses affected runs until quantities, cost basis, tradability, cash and tax treatment are evidenced. Do not treat an unexplained discontinuity as strategy loss, mechanically apply a split ratio, manufacture proceeds or replace the ticker. | The affected dataset/run remains blocked. User decisions may be needed after concrete events are identified. |

## Fixes from this audit

1. Separate cash reservations (including fees) from pending market-value reservations. At fill, capacity uses actual held market value plus that fill. Fees no longer incorrectly remove a legal unit from the position cap, and lower-priority reservations do not reverse fill priority.
2. Store executable Open observations independently from signal bars. A later missing High/Low/Close/volume cannot retroactively remove a valid Open. Real packages hash both streams and verify matching prices where a completed bar exists.
3. Remove evaluation time from entry identity. The same cross pair cannot emit again merely because a new fold changes its threshold/window and recognizes it later.
4. Distinguish pending split rounding from actual entitlements, retain unsupported holdings intact on failure, and reject silently ignored time-varying lot metadata.
5. Flag inadequate positive-hump history, distinguish cash/lot/cap shortfalls, require a real-data study boundary, and use calendar evidence for holiday and partial-session window starts.

These fixes enforce selected rules or expose missing evidence. They do not select new constituents, costs, thresholds, latency, account sizes or allocation experiments.

## Evidence still required before historical execution

See the dated [network evidence](network-access.md) for the current parent-observed HTTP 429; this executor issued no additional Yahoo requests for the implementation reviews. Full-universe capture, maximum-history verification, missing/null/terminal observations, lunch/auction/short sessions, all IPO identities, delistings/actions, legal units and exact holdout dates remain unaudited. A review receipt must identify actual evidence; setting a boolean does not create it. Daily study-start audit must demonstrate the five-year target rather than treating arbitrary downloaded history as the approved scoring horizon.

A positive finite Open remains an execution proxy, not proof of liquidity during a halt. Eventual bar volume cannot filter an earlier fill. Zero/missing-volume reporting is available; a broader low-liquidity threshold remains unselected and must not become a hidden trade filter.

Real research remains locked until the designated configuration writer synchronizes accepted conventions and the actual data audit is complete. The pending JP weighted base and inactive finite price exits/FX do not require resolution to run the selected fixed-allocation study. Finite price exits remain disabled and unoptimized; enabling them would require the already documented trigger/reference rules.

## Dashboard access

The saved cloud environment serves the read-only console on local port 8765. That address is local, and no public live URL has been configured or verified. A platform-provided authenticated port preview may be used if the environment exposes one; do not guess its URL or assume it exists.

The successful Tests workflow publishes a self-contained `research-dashboard` HTML artifact. Download, unzip and open it to view a timestamped snapshot without a server. The existing Library HTML is also a snapshot. Neither route is a public real-time feed. GitHub Pages or another hosting deployment would be separate hosting setup; it is not necessary to unblock data research and must not be claimed as already configured.

## Offline troubleshooting update: 2026-10-04

Current authorization permits ordinary reversible implementation fixes and verification. It does not approve unresolved strategy definitions. The latest canonical document was read as v0.13; its configuration, universe and real-execution lock remain unchanged.

- Completed Close marks were overwritten when the next bar opened at the same timestamp. The engine now records the Close valuation before processing that Open. A synthetic held-position case with Close 80 followed by Open 100 now retains the 20% drawdown instead of reporting zero. This repairs the already documented valuation implementation; it does not select a new valuation convention or publish a historical result. Equal timestamps have deterministic event order and zero elapsed time between them for utilization weighting.
- Provider-status selection uses the observation's own aware timestamp, independently of software-test timestamps. Invalid/naive timestamps cannot supersede dated evidence. Connectivity success remains separate from completed data auditing. These are evidence-display conventions, not trading rules.
- HTTP response diagnostics distinguish a received 429 from a connection-stage denial, retain bounded response evidence, and stop without automatic retry. Transport tests are mocked, preserving the original endpoint, user agent and request parameters.

The two previously consolidated material questions were subsequently approved and recorded in v0.14: historical executable units with evidence-backed action handling; flat training accounts, continuous ordinary OOS accounts, and separate fresh final accounts. [Synchronization and regressions](accounting-v014.md) preserve remaining technical proposals. Unsupported fractional/odd-lot entitlements and non-split distributions remain blocked pending concrete evidence and treatment.

Existing deterministic EMA/ADX initialization, valid-bar gap handling, per-arm readiness, event serialization and full-window checks can be inspected and tested offline without another routine permission request. They remain explicitly described implementation conventions, with canonical synchronization required before dependent real execution. No new common warmup gate, gap filling, parameter axis, eligibility filter or data interpretation is enabled by this troubleshooting update. JP ADX sizing remains an inactive alternative and does not block fixed-1/15 research.
