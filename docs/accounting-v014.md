# v0.14 accounting synchronization

The [canonical public projection](../config/inputs/TrendTrade101_Backtest_Configuration.md) and [source/public provenance](../config/inputs/public_input_provenance.json) record the approved historical executable price/share basis and account-state policies. Only `split_lot_basis`, `fold_account_state` and `final_account_state` changed approval status. All 201 memberships, execution/scoring parameters and other pending technical conventions remain unchanged. The real execution flag remains false.

## Price and share units

The machine policy uses historical executable units with explicit split events. A ratio of new shares to old shares multiplies the filled quantity, divides its per-share book cost and rescales price-dimensional indicator state at the effective event. Aggregate cost, cash and tax are unchanged by the mechanical split. `Position.average_cost` derives the fee-inclusive per-share cost from the aggregate ledger rather than storing a second mutable basis. Split events log quantities before/after and preserved total cost.

Vendor fields must be evidenced as historical unadjusted or split-adjusted-only before reconstruction. The audit preserves original source bytes and hashes; it does not assume Yahoo's field basis. Nonfinite split ratios are rejected before indicator mutation. A split inside an observed bar is rejected because a single OHLC record cannot silently mix price units. Actual fractional/odd-lot holdings remain blocked without an evidenced entitlement/execution model.

An unresolved special action must identify a frozen ticker and event type. The dataset keeps the original member, observations and unresolved event. Freezing or executing a run that includes that ticker fails before replay. A different basket that does not contain it may be prepared; the frozen plan lists unresolved symbols outside that run. This scope does not skip an event inside an affected run, imply that its economic treatment is verified, or permit replacing the member. Malformed/unidentified actions fail the package check.

The audit package's `audited_local_package` status describes captured-data checks, not execution eligibility. Corporate-action receipts establish the reviewed event inventory; unresolved economic treatments stay explicit in `unresolved_corporate_actions`. The per-run action guard and the separate configuration/readiness gates must pass before real replay.

## Account state

| Phase | Account policy |
| --- | --- |
| Each candidate in each training fold | Fresh initial capital, flat holdings, no earlier fees, tax, reservations or orders |
| Ordinary rolling OOS | One continuous account per stream, including cash, costs, holdings, current-year tax, pending orders and reservations |
| Final baseline | Fresh initial-capital flat account, separate from all development accounts |
| Final selected strategy | Another fresh initial-capital flat account, separate from the final baseline |

Earlier observations warm up indicator state only for fresh accounts. They cannot generate pre-interval trades or import earlier P&L. The plan stores both accounting policies; unsupported policy edits fail before plan creation. Results identify account initialization alongside starting equity, interval and configuration. Final results must not be appended as a continuation of ordinary OOS equity.

## Verification and remaining gates

[Accounting regression tests](../tests/test_approved_accounting.py) cover equivalent forward/reverse-split round trips; aggregate cost, cash, tax and fees; partially seeded and initialized indicators; histogram/cross continuity; nonfinite and intra-bar split rejection; affected/unaffected basket handling; unsupported policy rejection; independent training candidates; continuous OOS positions/orders/tax; and separate warmed final accounts.

The OOS fixture omits one synthetic month-end quote, retaining an actual position and exit order while another symbol closes and accrues tax. The following fold must inherit the complete account unchanged. These are synthetic software checks, not historical return validation. The full local suite passed 109 tests, including nine focused accounting regressions; input verification and continuity lint also passed.

Public v0.14 configuration and provenance bytes were verified against the supplied hashes. Original-source materialization failed after one bounded retry; the original-byte hash remains a source attribution, not an independent original-byte verification here. No Yahoo requests were made. Remaining indicator/gap/valuation/window conventions, actual provider coverage, actions/units and holdout-date audits still prevent real execution. JP ADX sizing remains an optional inactive branch.
