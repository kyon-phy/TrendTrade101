# TrendTrade101 Backtest Configuration

Version: v0.18  
Publication: sanitized public projection; strategy definitions and membership match canonical v0.18  
Source configuration SHA256: 900ea310774e2540f8571dca5a075567542423d3fd1c34cfc6c38e0b0d7c2126  
Updated: 2026-10-04 JST  
Project: TrendTrade101  
Status: The original25 daily pilot now has a separate approved in-sample entry-arm and parameter-grid experiment: 51 distinct candidates per market, 102 total, using fixed1/15 allocation and the same assumption-based data/window. Record each market/arm's highest after-tax-return candidate subject to maximum drawdown<=30%, with all trials and sparse-trade flags visible. The fixed v0.16 and ADX-scaled v0.17 run snapshots remain historical artifacts. New grid execution is not yet established by this record. Formal walk-forward/holdout rules and benchmark distribution restrictions remain unchanged.

This public project configuration is derived from the authoritative v0.18 configuration record for the US and Japan historical trend-backtest project. Publication provenance and original-versus-public file hashes are recorded in public_input_provenance.json. It records selected parameters, execution assumptions, experiment design, unresolved definitions, evidence and biases. Every strategy, universe, data, cost or parameter change must update this record and its version history.

Project documents, configuration, UI, code comments and commit messages use English. This document contains no return results and does not claim that an engine, live monitor or trading system has been deployed.

## 1 Status conventions and open decisions

| Status | Meaning |
|---|---|
| Approved | Explicitly selected by the user or explicitly accepted from a proposal |
| Principle approved | Direction is selected, but implementation details still need to be frozen |
| Pending | Must not silently become an executable default |
| Implementation assumption | A disclosed technical convention, distinct from a user-selected parameter |
| Proposed | A recommendation that has not been selected |
| Source verified | Source content was opened and checked; this does not establish implementation or adoption |
| Verification required | Actual data, calendar, coverage or source evidence must be checked |
| Blocked | Evidence is insufficient to complete the stated scope; do not silently substitute a narrower one |

An adjustable field is not automatically an optimization axis. The documented first-round grid is now also approved for the separate in-sample original25 pilot experiment defined in Section2; its formal walk-forward use remains governed by Section13. Delay, position scale and histogram drawdown have separate parameter names rather than sharing an ambiguous x.

### Remaining decisions and verification

1. The N window, one-order-per-cross-pair rule, histogram zero/reset ordering, cash reservation, fill-time quantity reduction, market-value caps and deterministic order tie-breaks are approved below. Implementation must verify these definitions rather than retain them as inactive suggestions.
2. Scheduled minute liquidation and the separate daily month-end Open liquidation are approved. Calendar alignment, missing quotations, partial sessions and residual positions still require audit.
3. After-tax training scoring, eligible-neighborhood medians, the 30% drawdown constraint, tie-breaking and the fewer-than-five-completed-trades reporting flag are approved. Exact final-holdout dates and partial-window treatment still require actual data/calendar audit.
4. Indicator initialization, Wilder ADX/EMA startup, histogram scale, the disclosed rising-count interpretation and complete event serialization still require implementation verification. They must not create future-data leakage or duplicate a cross pair.
5. All 201 membership rows remain frozen, including the approved US daily NKE-to-PYPL replacement. Full-US historical Top30 certification is incomplete and is not a prerequisite for the selected fixed-basket study. Preserve actual coverage, selection-date and look-ahead-bias disclosures.
6. Historical executable prices/share units, effective-date split adjustments and the training/OOS/final account-state policies are now approved. Affected real runs must pause for unverified special corporate actions; implementation synchronization and focused verification remain pending.
7. Five fixed-amount entry comparisons remain selected for formal research. The separate v0.17 FULL ADX-scaled pilot retains its approved bases and historical run configuration. The new Section2 in-sample grid uses only fixed1/15 across the five entry arms, avoiding an ADX-sizing confound. A fully crossed weighted grid remains outside this extension.
8. The original25 pilot and its approved allocation comparison use [2024-11-01, 2026-09-01), October2024 warmup and late-IPO/readiness constraints. The named assumptions permit qualified simulation despite incomplete external economic verification; formal verified-data readiness remains unchanged. Mechanical validity, exact input hashes, causal boundaries and clear labels remain required. Benchmark source availability and permitted distribution are pending verification.

## 2 Data and market configuration

| Parameter | Current value | Units or adjustment scope | Status |
|---|---|---|---|
| data_provider | Yahoo for price history | Current source | Approved |
| data_budget | Free | This project | Approved |
| market_set | US and JP, tested independently | Markets | Approved |
| data_1m_window | Maximum history actually available from the free endpoint | Actual coverage | Principle approved |
| data_5m_window | Maximum history actually available from the free endpoint | Actual coverage | Principle approved |
| data_1h_window | 1 year | Years | Approved |
| data_daily_window | 5 years | Years | Approved |
| minute_test_window | Maximum actually accessible five-minute history | Audit-based window, not a fixed60-calendar-day cut | Approved |
| minute_window_selection | max_actual_available_5m | Selected over an explicit60-calendar-day alternative | Approved |
| minute_data_start_anchor | Actual audited start, separately by market | Exact dates remain provisional; does not trigger member reselection | Verification required |
| minute_historical_rerank_required | false | Keep exactly the delivered review members even when data start earlier | Approved latest override |
| daily_test_window | 5 years | Total dataset target | Approved |
| minute_signal_bar | 5 minutes | Bar interval | Approved |
| daily_signal_bar | Daily | Trading-day bar | Approved |
| minute_sma_fast / minute_sma_slow | 5 / 20 | Bars | Approved |
| daily_sma_fast / daily_sma_slow | 5 / 20 | Bars | Approved |
| market_currency | USD for US; JPY for JP | Local currency | Approved |
| session_anchor | Opening of each continuous trading session | Session | Approved |
| lunch_handling | Anchor morning and afternoon separately; do not concatenate lunch | Session | Approved |
| session_tail_bar | Retain a short final bar | Boolean | Principle approved |

On five-minute bars, SMA5/SMA20 represent nominal spans of 25/100 trading minutes. They do not mean 20-minute signal bars, and the spans are not uninterrupted wall-clock time through lunch or overnight closures.

The maximum-available-history minute study and five-year daily study have separate reports. Retaining one-minute and hourly data categories does not add another primary strategy or authorize mixing their return series.

Requested windows are not Yahoo availability guarantees. No OHLCV coverage audit has been completed. Preserve requests, retrieval timestamps, per-symbol first/last bars, gaps, timezones, fields, adjustment flags and raw-snapshot hashes. Missing prices must not become invented fills.

The inherited requirement to retain short session-end bars also applies when appropriate to special short sessions and interruptions. Verify it against the exchange calendar and the actual bar construction.

### Minute-window audit update

The user selected maximum actually accessible five-minute history on 2026-10-03 at 21:45 JST. This supersedes the prior60-day target; do not truncate returned data to60 calendar days merely to preserve an old formation date. The five-year daily study is unchanged. Minute training remains2 weeks, the next test1 week, and the untouched final holdout1 complete week.

Two representative read-only probes made at 2026-10-03 12:43:51 UTC returned the following summaries for range=60d and interval=5m:

| Symbol | First returned timestamp in exchange time | Last returned timestamp in exchange time | Returned points | Non-null Close points |
|---|---|---|---:|---:|
| NVDA | 2026-07-10 09:30 America/New_York | 2026-10-02 16:00 America/New_York | 4,681 | 4,681 |
| 6857.T | 2026-07-06 09:00 Asia/Tokyo | 2026-10-02 15:30 Asia/Tokyo | 4,681 | 3,916 |

Sources: [NVDA representative chart request](https://query1.finance.yahoo.com/v8/finance/chart/NVDA?range=60d&interval=5m&events=div%2Csplits), [Advantest representative chart request](https://query1.finance.yahoo.com/v8/finance/chart/6857.T?range=60d&interval=5m&events=div%2Csplits). These are request URLs, not immutable historical snapshots.

Only summaries and response hashes were retained for these probes, not full bar payloads. NVDA response SHA256: e4ebb7bd9eec29fce6382e3ad107bafb851dffe2a8ad9e9aa63061b49b3bcf64. Advantest response SHA256: 834f9f1f1323278db007fd80959816d19ed2860aa34993e93d8714b3752db5ed.

The returned windows do not match an assumed60-calendar-day span. Do not infer a universal duration or a proven maximum from the label60d or these two symbols. Full-universe first/last usable bars, continuity, intraday sessions and provider limits still require audit.

Advantest has765 null Close entries in this summary; their cause has not been classified. Do not automatically label them lunch, suspension or missing trading data without the actual payload/calendar audit. A terminal point stamped exactly at the exchange close is not automatically a complete five-minute interval. Distinguish interval bars from closing/terminal observations before constructing signals, fills or the final holdout.

The subsequent 21:57 JST instruction freezes the previously delivered members and cancels the re-ranking requirement introduced in v0.10. Retain the July31/early-August selection provenance even when the audited price window begins earlier in July. This intentionally creates look-ahead selection bias in the affected earlier observations and must be disclosed; do not claim those members were selected using only information available at the earlier start. Data-start timestamps and selection-information dates are separate fields. The probe dates above do not establish full-universe dates. No signals, returns or backtest scores were calculated by this audit.

### Separately authorized assumption-based cached-daily pilot

The user first authorized an original25 cached-daily baseline pilot on 2026-10-04 at 18:36 JST. At 19:48 JST, the user approved continuing under the specific price, split-record and trading-unit assumptions below, with a fixed November2024-through-August2026 test interval. This is a scoped hypothetical simulation, not a certification that those assumptions are historically true. It does not replace the formal five-year daily study, maximum-available-minute study, 201 frozen membership assignments or 127 unique market/ticker universe.

| Pilot parameter | Selected scope | Status |
|---|---|---|
| pilot_id | original25_cached_daily_assumption_baseline | Separate qualified simulation |
| pilot_data_source | Existing daily cache only | Approved; no fresh price fetch |
| pilot_universe | existing_25: US12 and JP13 as frozen in Section12 | Approved; no reselection or substitution |
| pilot_frequency | Daily | Approved |
| pilot_strategy | Current FULL baseline with existing indicator/entry/exit parameters | Baseline only; no parameter search |
| pilot_allocation | Primary fixed initial-capital 1/15 | Approved rules retained |
| pilot_accounts | Separate fresh US and JP accounts at their approved initial capital, flat at scored start | Baseline initialization retained |
| pilot_scored_start_inclusive | 2024-11-01 | Market-local trading dates; no earlier trades |
| pilot_scored_end_exclusive | 2026-09-01 | Last permitted scored date is 2026-08-31 |
| pilot_warmup | Available October2024 observations before the scored start | Indicator warmup only; never earlier P&L or trades |
| pilot_late_ipo_readiness | Wait for each security's actual available post-listing observations and required indicators | No pre-IPO backfill or assumed ready state |
| pilot_optimization | false | No grid, training selection or tuning |
| pilot_formal_holdout_evaluation | false | September2026 and later price observations excluded from pilot evaluation |
| pilot_evidence_mode | Explicitly assumption-based | Does not satisfy formal verified-data readiness |
| pilot_result_label | Assumption-based original25 daily FULL baseline pilot | Not a formal strategy conclusion or holdout result |

#### Economic assumption register

| ID | Assumption used only for this pilot | Authority/status | Not established by the assumption |
|---|---|---|---|
| PA01 | Cached OHLC is adjusted for splits only, without dividend adjustment | Explicitly approved simulation assumption | Yahoo/vendor field basis is not externally certified |
| PA02 | Split records in the cache are complete for the reconstruction/model | Explicitly approved simulation assumption | Complete historical corporate-action coverage is not verified |
| PA03 | US order unit is 1 share; JP order unit is 100 shares | Explicitly approved simulation assumption | Every security's effective historical legal unit is not verified |
| PA04 | Each cached ticker series represents one continuously mapped issuer over its available observations | Disclosed operational assumption for this limited simulation | Issuer/ADR continuity and all historical identity events are not independently certified |

Use PA01/PA02 to reconstruct the model's historical executable-price/share basis and apply effective split adjustments consistently with Section11, preserving total position cost and indicator dimensions. Retain the original cache and action records, exact hashes and transformation log. Mark the corresponding evidence fields as assumed/unverified, never as verified merely because execution is allowed. A source assumption can materially alter returns even when the arithmetic is correct.

PA02 concerns the split records, not a blanket finding that all spin-offs, rights, mergers, ADR conversions or special distributions are absent or correctly handled. PA04 is a disclosed operational simplification, not a newly approved formal identity rule. If observed records contradict these assumptions or expose a concrete unsupported special action, malformed price, impossible split ratio, lost entitlement or invalid account state, stop the affected simulation and report it. Do not fabricate prices or proceeds, round away actual property, silently remove a frozen member, or turn an invalid run into an apparently successful all-cash return.

The available-cache inventory has reported US original12 bounds of 2024-10-02 through 2026-10-01, JP original13 bounds of 2024-10-02 through 2026-10-02, and a later first observation for Kioxia285A.T on 2024-12-18. These describe cached coverage, not the scored interval or independently verified historical tradability. Use only the selected original25 series; preserve per-symbol omissions, startup status, source metadata and hashes. The approved simulation interval does not imply that every stock can trade on its first day.

#### Technical conventions and mechanical checks

Reuse consistent, documented implementation conventions for this limited simulation, with their implementation version and diagnostics recorded. These are disclosed technical choices, not additional source-verification claims or blanket approval of all pending formal-study proposals:

- Completed Close inputs for SMA/EMA/MACD; completed High/Low/previous Close for ADX; H equals MACD minus signal without a factor of two.
- The existing SMA-seeded EMA and Wilder ADX recurrences, as documented in the project's technical convention record. Preserve their actual valid-observation startup and required readiness; do not replace missing startup values with zeros.
- Use valid observed completed bars without fabricated gap bars. Carry legitimate indicator state across calendar gaps, while keeping missing-data and readiness flags explicit. Do not add a common extra entry filter or alter the approved cross/histogram rules.
- Use observed Open and completed-Close valuation in causal event order. A future Close cannot mark an earlier Open. Any last-known mark used during a gap must remain flagged and must not turn an undefined valuation into a verified price.

The qualified simulation has its own execution mode, input manifest and result namespace. Validate hashes, schema, selected members, finite and structurally consistent observations, dates, split arithmetic, indicator causality, account conservation and end-date isolation. The allowance for PA01–PA04 replaces external certainty only for this named hypothesis mode; it does not disable formal audit/readiness checks or set a generic verified-audit flag. Keep formal baseline, optimization and final-holdout execution behind their existing gates. This version approves no new technical parameter sweep or eligibility filter.

#### Trading rules, interval and interpretation

All current baseline rules remain: independent USD/JPY markets; approved initial capital and fixed1/15 sizing; the assumed whole units above; fees and current-year tax; completed-bar signals; daily next-tradable-session Open for ordinary orders; preplanned last-trading-day Open monthly liquidation and its full-day buy ban; pyramiding and cross-pair deduplication; reservations, caps and signal-time priority; and disabled price-stop/target modules. No minute D20 simulation is added to the daily pilot. Each account starts flat at the selected scored start; October observations cannot produce inherited orders, positions, tax or profits.

For a late IPO such as Kioxia, begin its warmup only when its actual cached post-listing observations exist and permit entries only after the existing FULL-rule readiness is met. An evidenced pre-IPO period, insufficient startup state or genuine absence of signals can produce cash holdings with explicit reasons. A cash-only result caused by those valid rules is distinct from an audit/error state. Do not replace an unavailable member.

Score only market-local dates from 2024-11-01 inclusive to 2026-09-01 exclusive. Sequester September2026 and later OHLC from pilot signal calculation, fill selection, valuation, return summaries and exploratory performance charts; do not let an August signal execute using a September Open. Preserve any boundary residual or unfilled order with its actual state instead of inventing a liquidation. The existing monthly schedule should be applied on the last eligible August trading day under its ordinary rules.

The formal final holdout is neither evaluated nor relabeled by this simulation. Its formal date/coverage audit remains separate. No pilot outcome may select parameters, trigger optimization or be represented as an untouched final test. The cache's later observations remain outside this pilot regardless of their presence in the source package.

Every output must identify the assumption-based label, PA01–PA04, actual code/configuration/cache hashes, input transformations, exact scored/warmup windows, readiness and missing-data flags, account initialization and any unresolved action limitations. Report hypothetical simulated returns only as conditional on these inputs. Do not describe them as verified market execution, a five-year/full-universe result, an optimized strategy or a formal investment conclusion. No fresh price fetch, optimization, grid comparison, parameter retuning or formal-holdout performance is authorized by this extension.

### Approved ADX-scaled pilot comparison and benchmark reporting

On 2026-10-04 at 20:23 JST, the user explicitly selected the Japanese base of JPY1,600,000 with scale1, alongside the established USD10,000 US formula, and requested Nikkei225 and S&P500 curves in the result comparison. This extends the qualified pilot to one additional allocation mode. It does not select a formal five-arm weighted grid or promote an observed result into a new strategy default.

| Comparison parameter | Selected value | Scope/status |
|---|---|---|
| comparison_id | original25_cached_daily_assumption_adx_scaled | Separate authorized run; completed hypothetical result recorded in its preserved artifacts |
| comparison_strategy | FULL | Same entry, exit and readiness conditions as the fixed pilot |
| comparison_allocation | ADX-scaled target notional | Only the allocation branch changes |
| comparison_position_base_us | 10,000 USD | Approved |
| comparison_position_base_jp | 1,600,000 JPY | Explicitly approved for the ADX branch |
| comparison_position_scale | 1 | Approved; not optimized |
| comparison_adx_denominator | 25 | Same fixed baseline threshold; not optimized |
| comparison_adx_observation | Stored signal-time ADX | No later indicator value used for sizing |
| comparison_us_target | 10,000 USD × 1 × (signal-time ADX / 25 - 0.5) | Before fees, reservation, lot and cap constraints |
| comparison_jp_target | 1,600,000 JPY × 1 × (signal-time ADX / 25 - 0.5) | Before fees, reservation, lot and cap constraints |
| comparison_accounts | Separate fresh USD100,000 and JPY16,000,000 accounts, flat at scored start | Do not carry the fixed-run ledger or its profits into this run |
| comparison_interval | [2024-11-01, 2026-09-01) in market-local dates | Same October warmup and late-IPO/readiness rules |
| comparison_inputs | Same original25 cached equity data and PA01–PA04 | No new equity price fetch or substitution |
| comparison_other_rules | Unchanged baseline indicators, fees, tax, fills, whole units, caps, reservations and order priorities | Preserve the actual inherited parameter semantics |
| comparison_optimization / comparison_formal_holdout | false / false | No tuning, ranking search or holdout consumption |
| comparison_sequence | Publish completed fixed-run result, exact runtime configuration and PDF; then execute the ADX comparison | Record publication and run completion separately |
| comparison_result_label | Assumption-based original25 daily FULL ADX-scaled pilot | Conditional result; no verified-source or formal-strategy conclusion |

Keep the completed fixed-1/15 pilot as an immutable comparison baseline. Its authorization source is v0.16, SHA256 b727826e136611f31822915375903c88967243e43e791cb5c52d89c613f8fe6b. Preserve that run's actual machine configuration, code/data hashes and historical inactive settings, including its unused JP ADX-base field. Do not relabel or overwrite the completed run with v0.17 merely because a later branch now has an approved JP base. The new run must have its own configuration snapshot, input/run manifest, output namespace and exact hashes.

Use Section8's fee-inclusive reservation, cap checks, whole-share/whole-lot rounding and shrink-only fill rules. Scaling changes intended exposure; through cash competition and unit rounding it can also change fills, trade counts and subsequent portfolio paths. Compare after-tax/after-fee returns, drawdowns, exposure, fees, trade counts and skipped-order reasons. Do not claim equal exposure, change parameters from observed outcomes, or treat either pilot as untouched validation.

#### Requested reference-index curves

| Reporting field | Selected convention | Status |
|---|---|---|
| us_reference_index | S&P500 price index | Requested reporting reference; source not yet selected |
| jp_reference_index | Nikkei225 price index | Requested reporting reference; source not yet selected |
| benchmark_role | Reporting curves only | No index trades, strategy signals or allocation input |
| benchmark_window | Same scored interval as the pilot | Exclude September2026 and later observations |
| benchmark_normalization | Rebase to100 at the first common valid scored observation for each market panel | Disclosed display convention; report the actual base date |
| benchmark_strategy_basis | After-fee/after-tax account equity, rebased on the same panel base date | Preserve separately reported full-interval account returns |
| benchmark_index_basis | Price index, without reinvested dividends or simulated strategy fees/taxes | Label its different return basis explicitly |
| benchmark_source_status | Pending availability, field and rights verification | No approved price-provider migration |
| benchmark_public_distribution | Conditional on verified permission for the actual source and use | Do not publish source bars or derived curves to public Git before this check |

Use actual observed index dates and market-local calendars. Preserve missing dates, base dates and source metadata; do not fabricate data or use a future observation to fill an earlier date. If a common base observation is delayed, label the reduced displayed span and retain the strategy's original full-interval result separately. The reference indices are different universes from the selected stocks, and their price-only curves are not directly cost/tax-matched investable strategies. Any permitted private comparison must still follow the selected source's terms. Missing or restricted benchmark data must be reported as unavailable rather than silently replaced with an ETF, another index or an unverified curve. The curve request does not authorize changing the equity data provider or distributing raw market-data caches.

The preserved ADX run summary records hypothetical completion on 2026-10-04, using canonical v0.17 source SHA256 b0a5a25e4e7ad7ae813c0fc40a75bc21a4ff796a30e5e0262e0921fcd2a542ba and unchanged normalized inputs. Its summary SHA256 is b1e61a3c9170eab91f8128165070a044171f3de66e5a8c0d0508ec3f6cc36559. This is an execution-artifact observation, not approval of different parameters, verification of assumed economic inputs, or permission to distribute benchmark data. The new grid below has not been executed by this configuration save.

### Approved in-sample entry-arm and parameter-grid experiment

On 2026-10-04 at 21:41 JST, the user requested every existing condition combination followed by different parameter values and each group's best historical result. At 21:42 JST, the user approved beginning the bounded fixed-1/15 experiment described below. This is an explicitly in-sample, assumption-based exploration of data already examined in the fixed and ADX pilots. It permits the specified grid despite the earlier pilots' no-optimization limits; those older run snapshots and the separate formal walk-forward/holdout plan are unchanged.

| Experiment field | Frozen scope or convention | Status |
|---|---|---|
| experiment_id | original25_daily_in_sample_entry_grid | Separately approved experiment; execution pending |
| experiment_data | Same cached original25 daily equity observations and normalization inputs | No fresh prices, member changes or provider migration |
| experiment_interval | [2024-11-01, 2026-09-01), market-local scored dates | September2026 and later prices excluded from signals, fills, valuation and scoring |
| experiment_warmup | Same available October2024 history and late-IPO/readiness policy | Past indicator state only; no inherited positions or orders |
| experiment_evidence_mode | Same PA01–PA04 qualified hypotheses and disclosed technical conventions | Economic assumptions remain unverified; mechanical validity still required |
| experiment_markets | US and JP, separately | Independent result/ranking groups |
| experiment_allocation | Fixed initial-capital1/15 | US100,000/15 USD and JP16,000,000/15 JPY before whole-unit/fee/cash constraints |
| experiment_accounts | Every candidate starts fresh, flat and independent at the approved market capital | No candidate inherits another candidate's profits, tax, reservations or orders |
| experiment_phase | In-sample full-interval replay | No rolling OOS result or untouched-holdout claim |
| experiment_primary_score | Individual candidate's full-interval after-tax return | Rank separately for each market and entry arm |
| experiment_eligibility | Completed valid replay and maximum drawdown<=30% | Constraint on ranking; never a trading stop or curve truncation |
| experiment_ties | Lower maximum drawdown, then ascending active parameter tuple | Tuple order: ADX threshold, cross-window N, histogram drawdown; omit inactive axes |
| experiment_sparse_flag | Fewer than5 complete aggregate stock-position closures | Report only; no minimum-trade exclusion |
| experiment_optional_secondary | Eligible-neighborhood median after-tax return using Section13's one-active-axis-step neighbors | Label as secondary in-sample robustness; never replace the requested individual-best column |
| experiment_formal_holdout | Not consumed | Formal selection and final-test policies remain unchanged |
| experiment_result_label | Assumption-based in-sample original25 daily entry-arm grid | Historical best among tested candidates; no out-of-sample superiority claim |

The five existing entry arms and their exact grid are frozen as follows. All arms share the approved MACD-histogram peak exit, monthly liquidation, slope-based cash priority, fees, taxes, whole units, reservations, caps and daily next-session Open execution. An arm's name describes its entry conditions, not a whole strategy using that indicator alone.

| Canonical arm | Runtime alias, if used | Entry conditions | Active grid axes | Candidates per market |
|---|---|---|---|---:|
| MA_ONLY | SMA_ONLY | SMA5/SMA20 bullish cross | Histogram peak drawdown30/40/50% | 3 |
| MACD_HIST | MACD_HIST_ONLY | MACD bullish cross and approved histogram condition | Histogram peak drawdown30/40/50% | 3 |
| MA_ADX | SMA_ADX | SMA bullish cross and ADX strictly above candidate threshold | ADX20/25/30; histogram drawdown30/40/50% | 9 |
| MACD_HIST_ADX | Same as canonical | MACD bullish cross, histogram condition and ADX strictly above candidate threshold | ADX20/25/30; histogram drawdown30/40/50% | 9 |
| FULL | Same as canonical | Both bullish crosses within candidate N, histogram condition and ADX strictly above candidate threshold | ADX20/25/30; N3/5/8; histogram drawdown30/40/50% | 27 |
| Total | Five arms | Per market | Inapplicable axes omitted | 51 |

There are 102 distinct market/arm/parameter candidates across the two markets, producing ten market-by-arm groups. Each arm's applicable baseline tuple (ADX25, N5, drawdown40%) is already included in its grid. Run/report the five baseline combinations first, then complete the remaining grid; any baseline validation replay does not create an additional distinct candidate. Inactive fields may remain in a machine snapshot for compatibility but must not change signals, sizing, readiness or candidate identity through an unintended entry filter. In particular, no-ADX arms must not inherit an ADX entry gate or ADX-scaled budgets; N does not vary outside FULL.

Keep SMA5/20, MACD12/26/9, ADX14, three strictly positive histogram increments with a positive final histogram value, all fee/tax/execution rules and disabled price-stop/target modules fixed. The drawdown values30/40/50% mean retained peak heights70/60/50%. The positive-hump boundary, declining-histogram trigger, nonpositive exit/reset order and cross-pair deduplication stay unchanged. This authorization is the listed bounded grid, not an open-ended period search, additional indicators, weighted-allocation grid or adaptive refinement after seeing results.

For each market and arm, show the valid eligible candidate with highest individual after-tax return. If no candidate meets the 30% maximum-drawdown constraint, report no eligible best; retain all valid ineligible and failed/blocked candidates with their reasons. Sparse or zero-trade valid candidates remain visible and eligible under the existing rule. A software/data failure is not a zero-return candidate. Resolve genuine numerical ties with the predeclared lower-drawdown and ascending-tuple order, not a favorable ordering chosen after inspecting results.

Publish/report all candidate configurations, completion status, returns, maximum drawdown, complete closures, sparse flag, costs, exposure and ranking eligibility, alongside the ten-group best-result summary and each baseline. If computed, identify the separate neighborhood-stability choice and its eligible-neighbor count; the formal neighborhood selector is not replaced by this experiment's individual-best reporting rule. Freeze code/configuration/input hashes and enumeration before replay. Preserve the prior v0.16/v0.17 artifacts rather than overwriting them with grid outcomes.

This grid explicitly reuses an already inspected historical interval and selects among many trials. The highest observed result is subject to look-back selection, multiple comparisons and overfitting. It cannot establish future profitability, a causal benefit of an entry indicator, or a formal out-of-sample winner. Retain the existing source, corporate-action, membership, execution and tax assumptions. Requested benchmark curves are reporting references only and cannot influence eligibility or ranking; their source/distribution restrictions still apply.

## 3 Indicators and baseline parameters

| Parameter | Baseline | Units or current-round treatment | Status |
|---|---|---|---|
| sma_fast_period | 5 | Bars; fixed in the first grid | Approved |
| sma_slow_period | 20 | Bars; fixed in the first grid | Approved |
| macd_fast_period | 12 | Bars; fixed this round | Approved |
| macd_slow_period | 26 | Bars; fixed this round | Approved |
| macd_signal_period | 9 | Bars; fixed this round | Approved |
| macd_ma_type | EMA | Fixed this round | Approved |
| macd_in_optimization_grid | false | Do not optimize 12/26/9 this round | Approved |
| adx_period | 14 | Bars; fixed in the first grid | Approved |
| adx_threshold | 25 | Indicator points; grid below | Approved |
| adx_entry_operator | Strictly greater than threshold | Comparison | Approved |
| cross_mode | double | Single/double architecture; explicit arms below | Approved |
| cross_window_bars | 5 | N bars; grid below | Approved |
| hist_positive_increments | 3 | Consecutive positive changes | Principle approved |
| hist_positive_at_entry | true | Signal-time condition | Approved |
| hist_acceleration_required | false | No increasing-increment requirement | Approved |
| indicator_warmup | Use all legitimate prior history and carry recursive state | Past-only state | Principle approved |

MACD line = EMA12 minus EMA26. Signal line = EMA9 of MACD. Histogram H = MACD minus signal line. A chart may display 2H; choose and preserve one convention throughout. Freeze the price input, EMA initialization, Wilder ADX smoothing and startup behavior so library differences do not change boundary signals.

Start with the fixed baseline. Optimization cannot retroactively change completed test trades or apply a full-sample optimum to earlier periods.

## 4 Entry rules

The full strategy is long-only and unlevered. It requires the SMA and MACD bullish crosses within N bars, ADX above its threshold, and a positive/rising histogram at signal confirmation. Independent subsequent signals may create additional orders in the same stock, including pyramiding; the earlier no-pyramiding restriction is superseded.

The two crosses may occur sequentially within N bars rather than on the same bar. N = 5 replaces the earlier unapproved N = 3 suggestion. At completed signal bar t, the approved inclusive window is [t - N + 1, t]. Both cross events must fall in that window, and each distinct pair of cross events may emit an order only once. Re-evaluating the same pair on later bars does not create a new event. A new independent pair may still add to an existing position.

Negative starting histogram values are allowed in the rising sequence. Only the final signal-time value must be positive, and each increment must be positive; increments do not have to accelerate.

### Rising histogram count

The current explicit implementation interpretation is three positive increments using four values:

- H[t] - H[t-1] > 0
- H[t-1] - H[t-2] > 0
- H[t-2] - H[t-3] > 0
- H[t] > 0

Examples that satisfy this interpretation are (-0.2, -0.1, 0.02, 0.03) and (0.01, 0.03, 0.04, 0.045). The second sequence has shrinking increments and still qualifies.

Earlier wording referred to three rising bars. If that meant three total values, it would mean two increments. The four-value interpretation remains visible for verification rather than hiding the counting distinction.

| Definition | Current treatment | Status |
|---|---|---|
| SMA bullish cross | Previous fast SMA <= slow SMA; current fast SMA > slow SMA | Implementation assumption |
| MACD bullish cross | Previous MACD <= signal; current MACD > signal | Implementation assumption |
| N-bar window | Both cross events in inclusive [t - N + 1, t] | Approved |
| Double-cross event deduplication | Each distinct cross-event pair emits at most once | Approved |
| Single-cross experiments | Use the explicit SMA and MACD arms in Section 13; no additional “either cross” arm is selected | Approved arms |
| Signal confirmation | Completed bar only; never use its final Close before completion | Implementation assumption |
| Signal invalidation during delay | Do not use later price information to cancel an already confirmed event | Principle approved |
| Repeated orders | Independent events may create orders and add to a position; due sells precede buys | Approved |

Histogram positivity is assessed at the historical signal time. Once confirmed, the minute signal is frozen and queued; later observations are not used to retroactively invalidate it.

## 5 Histogram peak exit and optional price exits

The user confirmed the current positive hump after the most recent nonpositive histogram value H <= 0. Track its largest value observed so far. The selected exit is a 40% drawdown from that running peak, equivalent to retaining 60% of peak height.

| Parameter | Current value | Units or definition | Status |
|---|---|---|---|
| hist_exit_model | Relative geometric peak-height exit | Model | Approved |
| hist_exit_drawdown_pct | 40 | Percent decline from running peak | Approved |
| hist_exit_retained_pct | 60 = 100 - hist_exit_drawdown_pct | Derived percent remaining | Derived from approved value |
| hist_peak_boundary | Current positive hump after the latest H <= 0 | Interval | Approved |
| hist_peak_tracking | Running maximum using information available by t | Causal rule | Principle approved |
| hist_declining_required | H[t] < H[t-1] for the positive-hump threshold branch | Strict decline | Approved |
| hist_zero_or_negative_exit | Evaluate H[t] <= 0 exit before resetting the hump peak | Rule | Approved |
| hist_peak_reset | Nonpositive exit check precedes reset; verify entry/session state continuity | Rule | Ordering approved; implementation audit |

Let b be the most recent location with H[b] <= 0. Within the current positive hump:

P[t] = max(H[b+1], ..., H[t])

The approved positive-hump branch requires H[t] < H[t-1] and H[t] <= 0.60 × P[t] at the baseline. Equality at the retained-height threshold is included; equal consecutive histogram values do not satisfy decline. For another approved grid drawdown d, the threshold is (1 - d/100) × P[t]. Minute exits use the delayed queue; daily indicator exits use the separate next-session-Open model.

First evaluate an exit when H[t] <= 0; only then reset the hump peak. This branch must not lose a sell signal because the peak was cleared too early. Otherwise evaluate the declining positive-hump threshold. When data begin inside a positive hump, use legitimate earlier history to restore its running maximum and flag inadequate history.

Never identify the completed future hump's maximum and backfill it into earlier decisions.

### Gaussian analogy

For exp(-z²/2), z = 1 has a relative height of about 60.65%, or a 39.35% decline. A 40% decline/60% remainder is close to that geometry but is not identical.

This is a shape analogy, not evidence that MACD values are normally distributed, a sample standard deviation or a tail probability. Whether an exit is late depends on price behavior and the minute delay. On the same declining hump, 60% remaining is crossed earlier than the previous 13.5% remaining rule; actual execution still needs testing.

The percentage applies to MACD histogram height, not to a 40% stock-price or account loss.

### Price stop-loss and take-profit parameters

Both thresholds remain modeled and configurable, including finite extremes or an explicit unbounded mode. They currently impose no additional limit and do not participate in optimization.

Represent the current nontriggering state with enabled = false and threshold = null. Null means disabled/unbounded, not 0%. Do not invent an arbitrary huge number that can overflow or trigger unexpectedly. A later finite extreme must state its units and trigger direction.

| Parameter | Current value | Meaning | Status |
|---|---|---|---|
| price_stop_loss_enabled | false | Configurable module | Currently nontriggering |
| price_stop_loss_pct | null | Disabled/unbounded percentage parameter | Approved no current limit |
| price_take_profit_enabled | false | Configurable module | Currently nontriggering |
| price_take_profit_pct | null | Disabled/unbounded percentage parameter | Approved no current limit |
| price_exit_extreme_mode_supported | true | Support extremes or explicit unbounded mode | Approved model capability |
| price_exit_in_optimization_grid | false | Excluded this round | Approved |
| price_exit_reference | Not set | Weighted cost or another reference | Define before finite activation |
| price_exit_ordering | Not set | Priority against indicator/scheduled exits | Define before finite activation |

Disabled price exits do not disable histogram exits, daily liquidation or monthly liquidation. Before finite activation, define the reference price, its change after additions, gaps, same-bar simultaneous triggers and minute/daily fill treatment. OHLC alone cannot establish which intrabar stop or target happened first.

## 6 Delay and fills

| Parameter | Current value | Scope | Status |
|---|---|---|---|
| execution_delay_minutes | 20 | Minute strategy; change only before a new complete round | Approved |
| delay_fixed_within_run | true | Entire backtest-plus-optimization round | Approved |
| delay_in_optimization_grid | false | Excluded from current search | Approved |
| delay_applies_to | Same D for minute buys and sells | Directions | Approved |
| minute_execution_policy | Confirm, queue, execute after D | Rule | Approved |
| signal_recheck_before_fill | No cancellation based on later price information | Rule | Principle approved |
| signal_cutoff_buffer_minutes | 3 × (D + 1) | Minute entry signals only | Approved |
| signal_cutoff_default | 63 minutes before close | Signal time, not fill time | Approved |
| minute_fill_source | First tradable five-minute bar with start >= signal-bar close + D | Open proxy | Approved |
| minute_fill_price_field | Open | Never that bar's eventual Close | Approved |
| minute_bar_timestamp_semantics | Bar start; signal time is the actual signal-bar end | Model convention | Approved; audit provider fields |
| buy_order_type | market | Minute Open proxy | Approved model |
| sell_order_type | market | Minute Open proxy | Approved model |
| unfilled_order_log | Preserve every unfilled order and reason | Audit log | Approved |
| daily_fill_model | Next tradable session Open after signal confirmation | Separate simplified model | Approved |
| daily_intraday_delay_simulation | false | No daily 20-minute simulation | Approved |
| spread_bps | 0 | Basis points | Current simplification |
| slippage_bps | 0 | Basis points | Current simplification |

### Round-level delay and entry cutoff

D = 20 stays fixed across all training, candidates, folds and controls in one entire round. A later round may choose another D and must receive a new configuration/run record. Do not optimize a shorter delay to improve the current round.

The last minute entry signal time is session close minus 3 × (D + 1) minutes. At D = 20, it is 63 minutes before close. Do not reinterpret this as a fill cutoff or move the signal cutoff to 83 minutes. Exit and scheduled liquidation signals are not blocked by the entry cutoff.

Daily signals use their separate completed-day/next-Open model and do not inherit a 63-minute-before-close rule.

### Information-time model

At historical signal-bar end t, evaluate only information through t. Freeze the resulting event and release its order at t + D. An offline calculation at t is a simulation device, not a claim that the live user would already possess delayed API information at t.

If the data feed itself releases the t observation at t + D, do not add another D after reception. Record event_time, available_time and fill_time so a 20-minute model does not accidentally become 40 minutes.

The execution-time price and then-current simulated cash/position can be used at execution. They must not be inspected early to cancel losing queued signals. Approved stock-level exit cancellation is a separate state transition with an auditable time and reason.

### Exact minute price proxy

Normalize timestamps to bar starts. Set:

- signal_time = actual signal-bar end
- due_time = signal_time + D
- execution bar = first tradable, observed bar whose bar_start >= due_time
- fill price = that bar's Open

A signal confirmed at 10:00 with D = 20 therefore uses the Open of the 10:20 bar, not the 10:00 signal price or the eventual Close of the 10:20 bar.

For a future round with D not aligned to five minutes, move forward to the first eligible start and record additional granularity delay. Never round backward to a pre-due price. Audit provider timestamps, timezone, calendar and actual short-bar endings.

Market-order modeling does not guarantee execution during a halt, lunch, closed session or missing quotation. Retain pending/unfilled state and record the reason; execution may occur only when an eligible observation becomes available. Do not fabricate a price to satisfy a flattening deadline or mark an unfilled sell as completed.

An Open proxy is not a verified executable bid/ask, depth or second-level price. Spread, impact and liquidity limitations remain biases even when the order is labeled market.

### Daily fills

A completed daily signal fills at the next tradable session's Open. No 20-minute intraday delay is simulated. This applies to ordinary entry and indicator exit. The separately approved scheduled exit liquidates at the Open of the month's last trading day and prohibits buys for that entire day; it is preplanned from the calendar rather than triggered by that day's final Close.

Label results “five-year daily / next-session-Open simplified fills.” Do not describe this as validation of historical 20-minute execution or splice it into the minute strategy's asset curve as if execution precision were identical.

## 7 Positions, order lifecycle and scheduled liquidation

| Parameter | Current value | Meaning | Status |
|---|---|---|---|
| direction | long_only | Direction | Approved |
| leverage | 1 | No leverage | Approved |
| repeat_orders_same_symbol | true | New independent signals can create orders | Approved |
| pyramiding_while_held | true | Additions to an existing position allowed | Approved |
| cancel_pending_after_flat | Cancel the stock's pending buys on aggregate exit | Rule | Approved |
| position_exit_scope | all_filled_shares_by_symbol | Exit all filled shares of the stock | Approved |
| same_time_order_priority | Due sells before due buys | Ordering | Approved |
| pending_cash_reservation | true | Reserve cash on queue entry | Approved |
| order_decision_snapshot | Signal-time ADX and percentage SMA5 slope | Information snapshot | Approved |
| duplicate_event_dedup | One event, including a double-cross pair, emits once | Idempotence | Approved |
| minute_flatten_frequency | Every trading day | Holding limit | Approved |
| daily_flatten_frequency | Every calendar month | Holding limit | Approved |
| minute_scheduled_flatten | Last valid continuous-session bar Open of the day | Queue D=20 minutes before the planned Open | Approved |
| daily_scheduled_flatten | Last trading day of the month, at Open | Preplanned calendar event; no D | Approved |
| daily_month_end_buy_ban | true | No buys on the scheduled monthly liquidation day | Approved |
| reservation_basis | Signal-price target amount plus estimated buy fees | Cash reserved at queue entry | Approved |
| fill_quantity_policy | Reduce only; never increase the queued quantity | Fill-price/cash/lot adjustment | Approved |
| position_cap_measure | Market value of held positions plus the proposed fill | Cap check | Approved |

Preplan the minute scheduled liquidation for the Open of the last valid continuous-trading bar and queue it D minutes earlier, with D=20 for this round. The scheduled calendar, short-session rules and bar semantics determine the target before execution. Do not inspect the eventual missing-data pattern and retroactively queue an earlier order at the last observed good price. If the planned price is unavailable, retain the unfilled/residual position and log the failure.

For daily data, preplan liquidation at the Open of the last exchange trading day of each calendar month, with no intraday D. Prohibit all buys on that day, including previously queued buys that would otherwise fill at its Open; record their cancellation/non-execution. Holidays require the actual last trading session, not the last calendar date. A missing Open or halt does not authorize an invented fill or a retrospective alternative date.

This daily simplification leaves the strategy out of the final trading day's intraday move and postpones new exposure until a later eligible session. Its timing differs from month-end Close liquidation and creates an exposure/timing comparison bias. Minute liquidation at a pre-close bar Open also omits the remaining part of that session. Report both schedules and any failed liquidation explicitly.

Record scheduled and indicator exits as distinct triggers. On aggregate exit, sell all filled shares and cancel pending buys for that symbol. If the order does not fully execute, retain the actual residual position instead of zeroing it prematurely.

### Repeated events and cash

Do not deduplicate permanently by ticker: the user permits new independent signals and pyramiding. Conversely, duplicate data, retries or repeated evaluation of the same cross are not new events.

A stable signal_id should retain market, security, arm and underlying cross-event identities. For the full arm, deduplication is keyed to the distinct SMA-cross/MACD-cross pair, not merely the current evaluation timestamp. Once that pair emits, a sustained N-bar condition cannot emit it again. Preserve signal time separately and make retries idempotent. Exact serialization is an implementation detail to record and test.

At a shared due time, process sells first, then buys ranked by the stored signal-time relative SMA5 slope. Resolve equal priority by ticker, then event ID in a stable order. ADX-scaled targets use the stored signal-time ADX. Later indicator values cannot retroactively reprioritize those historical events.

Reserve the signal-price target amount together with estimated buy fees when orders enter the queue so pending orders cannot spend the same cash. At execution, recompute affordability, fees, whole-share/lot rounding and market-value caps. The executed quantity may be reduced but never increased above the queued quantity when prices change. Release unused reservations on completion or cancellation and preserve any non-executed quantity/reason in the audit log. Keep each fill's quantity, price, fees and realized P&L, with a stock-level weighted-average cost ledger and a consistent tax basis.

Fee-inclusive signal-price reservation, shrink-only fill adjustment, ticker/event-ID tie-breaking and market-value cap checks are now approved. Reservation cannot evade total/single-stock limits or create negative cash. Audit same-time aggregate-exit/new-event handling against the approved sell-first and cancel-pending-buy rules; a still-pending canceled event is not silently revived.

Keep queued, filled, cash-shortfall, missing-price, below-lot and canceled states separately. Never delete failed orders to improve apparent results.

## 8 Capital and sizing

| Parameter | US | JP | Status |
|---|---:|---:|---|
| initial_capital | 100,000 USD | 16,000,000 JPY | Approved |
| account_position_cap | 100,000 USD | 16,000,000 JPY | Principle approved |
| single_stock_cap | Entire account position cap | Entire account position cap | Approved |
| position_scale | 1 | 1 | Approved; fixed in first grid |
| position_base | 10,000 USD | 1,600,000 JPY | Approved for the ADX-scaled branch; JP explicitly selected 2026-10-04 |
| lot_size | 1 share | 100 shares for ordinary-stock baseline | Whole lots approved; verify each security |
| fractional_shares | Not used | Not used | Principle approved |
| borrow_cash | Not allowed | Not allowed | Approved |

The markets have separate local-currency accounts, not one shared USD100,000 pool. JPY16,000,000 supersedes the earlier JPY1,600,000 typo.

### ADX-scaled mode

US target_notional = 10,000 USD × position_scale × (ADX / adx_threshold - 0.5)

JP target_notional = 1,600,000 JPY × position_scale × (ADX / adx_threshold - 0.5)

The JP base is 10% of initial capital, matching the US ratio. It was an implementation proposal through v0.16 and was explicitly selected for the ADX-scaled pilot branch on 2026-10-04. The formal fixed-1/15 primary comparison remains selected; approval of this base does not authorize the optional full five-arm weighted grid.

At threshold 25 and scale 1, ADX values 25/50/100 yield US targets 5,000/15,000/35,000 USD and JP targets 800,000/2,400,000/5,600,000 JPY. The ADX25 example illustrates the formula only; arms with an ADX entry gate require strictly more than their threshold.

### Fixed-amount comparison

| Parameter | US | JP | Status |
|---|---:|---:|---|
| fixed_allocation_fraction | 1/15 | 1/15 | Approved |
| fixed_allocation_capital_basis | 100,000 USD | 16,000,000 JPY | Fixed account-capital basis |
| fixed_target_notional | 6,666.6667 USD | 1,066,666.6667 JPY | Derived display values |
| allocation_comparison | Fixed-amount primary comparison; retain ADX scale | Same | Approved |
| adx_scale_mode_available | true | true | Approved retained capability |

Targets use the fixed initial account cap, not fluctuating NAV. Quantities round down to legal shares/lots, including cash and fee constraints. Targets are not promises to invest that exact decimal amount. Do not use fractional shares or overbuy to reach 1/15.

The fixed mode does not change sizing with ADX. Arms with an ADX gate keep it; arms without one do not inherit it.

For an ADX-gated weighted arm, preserve the original formula's candidate entry threshold as the denominator. For an arm without that gate, use the disclosed fixed reference below. It is not an added optimization axis or an implicit ADX>25 entry test.

| Parameter | Value | Scope and status |
|---|---:|---|
| adx_scale_reference_without_filter | 25 | Fixed normalization in no-ADX-gate arms; implementation assumption |
| nonpositive_target_budget | No buy; record the reason | Never submit zero/negative buy quantities |

A low ADX can produce nonpositive target capital and therefore no buy. Weighted mode can change the trade set even without an explicit ADX gate. It is not a clean same-entry comparison with fixed mode. The primary five-arm fixed-1/15 comparison avoids this confounding.

### Execution constraints

1. Bound the target by single-stock cap, total cap and available unreserved cash.
2. Round quantities down; skip orders below one legal unit.
3. Include buy fees in cash checks; no negative cash or hidden borrowing.
4. Verify nonstandard Japanese units rather than assuming every instrument trades in 100 shares.
5. Never sell more than the actual filled position.
6. Measure held positions at current market value for cap checks, not historical cost; retain the fixed account and single-stock ceilings when considering a new fill.
7. Reserve the signal-price target plus fees, process same-time sells first, reduce quantities if necessary and release unused reservation; never increase a queued quantity merely because the price falls.

A stock may consume the entire account cap. Preserve and report this concentration risk rather than silently adding diversification limits.

## 9 Simultaneous-signal priority

| Parameter | Current value | Units | Status |
|---|---|---|---|
| priority_metric | Relative short-SMA slope | Percent | Approved |
| priority_ma_period | SMA5 | Follows short-SMA setting | Principle approved |
| priority_lookback | Previous 1 bar | Bars | Implementation assumption |
| priority_direction | Larger positive slope first | Descending | Principle approved |
| priority_information_time | Each order's signal time | Timestamp | Approved |
| priority_tie_break | Ticker, then event ID | Stable ordering after slope priority | Approved |

Proposed exact calculation:

slope_pct[t] = 100 × (SMA_fast[t] / SMA_fast[t-1] - 1)

Use relative change so a high nominal share price does not receive an artificial advantage. Use completed information at signal time and save the value with the order.

The user's short-term movement preference means short-SMA slope, not ATR, standard deviation or another volatility metric. Apply the selected ticker/event-ID tie-break without re-ranking from future ADX or slope values.

## 10 Fees, tax and currency

These are accepted modeling assumptions, not a judgment about the user's brokerage eligibility or personal tax position. Actual account fees, discounts, market levies and tax status have not been reverified for this version.

| Parameter | Value | Units or treatment | Status |
|---|---|---|---|
| us_commission_rate | 0.495% | Traded notional | Accepted SBI reference model |
| us_commission_cap | 22 | USD per side | Accepted SBI reference model |
| jp_commission | 0 | JPY | Conditional simplification |
| annual_realized_tax_rate | 20.315% | Annual net realized profit | Accepted simulation rate |
| annual_loss_refund | Reverse excess current-year tax after each realized loss | Bounded by tax deducted in the same year | Approved |
| tax_accrual_timing | After each realized trade, on cumulative current-year net realized P&L | Incremental liability/refund | Approved |
| cross_year_loss_carry | false | No loss carryforward to another year | Approved |
| dividend_income | Excluded | Cash dividends | Approved |
| fx_variation_enabled | false | Local-currency accounting | Approved |
| fx_reporting_model | Define source, reporting currency and conversion costs if enabled | Model | Pending |

US fee per buy or sell = min(notional × 0.00495, USD22), charged independently on each side.

Japan's zero fee assumes the relevant eligibility conditions. Do not describe it as universally free for all accounts and orders.

Tax applies to annual net realized P&L, not gross sales or the sum of winning trades. After each realized trade, recompute current-year liability as max(cumulative current-year net realized profit, 0) × 20.315% and book the difference from tax already accrued in that year. A loss can refund only tax deducted in the same year; negative annual net P&L generates no subsidy. Losses do not carry into another year. Preserve the per-trade tax ledger and reset the annual accumulation consistently at the year boundary.

Excluding dividends, spread, slippage and FX changes creates differences from real account returns. Report USD and JPY separately; with FX disabled, do not claim one combined cross-currency asset curve.

## 11 Corporate actions and historical executable units

The user approved historical actual executable prices and share units on 2026-10-04 at 15:35 JST. This resolves the earlier unspecified choice between normalized quantity units and historical tradable units. The original requirement to avoid artificial split losses or indicator jumps remains.

| Parameter | Current value | Meaning | Status |
|---|---|---|---|
| execution_price_basis | Historical actual executable-price basis | Price at the simulated trading time | Approved; vendor basis requires evidence |
| position_quantity_basis | Historical actual share/instrument units | Legal executable units at each time | Approved; historical units require evidence |
| split_effective_time | Verified effective date/time before affected trading observations | Corporate-action event | Approved principle; event metadata audit |
| split_quantity_update | Multiply filled quantity by the new-shares/old-shares ratio | Actual position ledger | Approved |
| split_cost_per_share_update | Divide per-share cost by the same ratio | Preserve total position cost | Approved |
| split_indicator_update | Rescale price-dimensional indicator state consistently at the effective split | Avoid a mechanical signal discontinuity | Approved |
| split_total_cost_preserved | true | Quantity times per-share cost remains unchanged by the split itself | Approved |
| unverified_special_corporate_action | Pause the affected run | No guessed economic treatment or silent member deletion | Approved |
| dividend_model | No cash dividend income | Return model | Approved; unchanged |
| adjustment_metadata | Preserve vendor fields, split events, effective timestamps and hashes | Audit record | Verification required |

For a new-to-old split ratio r, the filled quantity becomes q × r and per-share book cost becomes c / r. Total book cost q × c is preserved. For a two-for-one split, 100 shares become 200 while total cost stays the same. The executable price is expressed in the post-split units from the event's effective time; a matching mechanical price change must not create profit, loss, a cross or a histogram collapse.

At that same effective event, translate retained price-dimensional histories and recursive indicator state to the matching scale, including the price-dimensional components underlying the indicators. Dimensionless quantities such as ADX and percentage slope must remain dimensionally consistent rather than being blindly divided by r. Apply transformations causally at the effective event, without using a later split to rewrite the simulated earlier account or making the same adjustment twice.

Vendor prices may already be retrospectively adjusted. Verify Yahoo's actual field basis and the split-only factors needed to reconstruct historical executable prices; a field name or today's downloaded price is not proof. Do not combine future-adjusted prices with historical unadjusted share quantities or assume that dividend-adjusted Close is an executable historical price. Preserve the original fields, transformation details and source evidence.

Verify legal order units, ADR ratios and any historical changes for each affected instrument. Pending order intentions and filled-share entitlements are distinct states: audit their split handling, cash reservations, fees and eventual legal execution consistently. Do not round away actual ownership, manufacture cash-in-lieu proceeds or presume a fractional/odd-lot entitlement model. If an entitlement or special corporate action cannot be verified, pause the affected run and preserve its state and reason.

Unverified spin-offs, rights, special distributions, mergers and ADR/instrument conversions need evidenced economic treatment before the affected run continues. Do not treat an unexplained price discontinuity as a strategy loss, relabel it as an ordinary split, remove the frozen member or silently skip the event. The pause is scoped to the affected run; this rule does not change membership or authorize a new data source.

Cash dividend income remains excluded. Distinguish ordinary dividends from splits and special entitlements, avoid implicit dividend reinvestment or double counting, and retain the disclosed price-field/corporate-action biases. Historical revisions and information unavailable at the simulated time remain limitations even after the accounting convention is fixed.

## 12 Stock universes and evidence

Run each universe separately. Freeze the selection rule and actual membership before performance testing; do not replace members after seeing returns while retaining an out-of-sample label.

| universe_id | Selection rule | Size | Current status |
|---|---|---|---|
| existing_25 | Existing approved stock list | US12 plus JP13 | Members frozen below; full OHLCV coverage not audited |
| sector_28 | Four leaders/representatives in each of seven sectors | 28 per market | Members frozen below; full OHLCV coverage not audited |
| historical_30_user_fixed | Delivered review members with approved US daily NKE-to-PYPL exception; originally researched for historical Top30 | 30 per market and frequency | User-selected fixed baskets; JP source ranks verified, US full-market Top30 certification incomplete |

The seven sectors are semiconductor, semiconductor-memory-related, banking, restaurants, cybersecurity, retail and insurance.

### Approved selection scope

- Memory means semiconductor memory, including NAND, DRAM, SSD and related memory businesses. An HDD-head, magnetic-media or broad-materials connection alone does not establish eligibility. A diversified company with verified relevant semiconductor/SSD business is not automatically excluded.
- A sector leader can be mid/small-cap and need not be an absolute blue chip. Still verify relevant business and representativeness; do not redefine a sector merely to fill four slots.
- The original US historical research target was the full US-exchange-listed market, including foreign companies, ADRs and eligible foreign ordinary-share listings. The later instruction freezes the delivered provisional subset instead of requiring further re-selection. Inclusion of overseas companies remains; this does not certify complete historical market coverage.
- Rank companies rather than count multiple share classes as separate companies. Estimate whole-company equity capitalization, not only ADR float. Map historical class rights and ADR ratios before aggregation.
- A SPY-only candidate Top30 was not approved as a substitute. SPY filings are auxiliary evidence; the fixed delivered basket is explicitly a user-selected provisional research subset, not a certified full-market Top30.

The prior current-date market-cap ranking proposal is superseded. Today's survivors, shares or market caps cannot be presented as historically available. The latest fixed-membership instruction is an explicit selection override, not evidence that provisional ranks became exact. Preserve missing-data and estimation limitations; do not fabricate values or quietly replace selected members.

### Latest fixed-membership override

At 21:57 JST on 2026-10-03, the user instructed the project to keep the previously delivered list and stop selecting stocks again. At 22:07 JST, the user explicitly approved one exception: replace NKE with PYPL only in the US daily historical-review basket. The other 200 membership rows and every minute basket remain unchanged. The original baseline is the 201-row 12:16 UTC review snapshot, subsequently delivered to the user. The snapshot file is stock_universe_review_members.csv, SHA256 8697391da85799675eff3027c58f6982c73a8969babe2167fcaaae1582536cf5. Its old provisional status fields describe the evidence at review time; this configuration records the subsequent user selection and single replacement without rewriting that historical snapshot.

The operative English membership artifact is frozen_universe_members.csv (SHA256 c8908f73ea09ffa39a8aca1c486e87fc9c92635ed246ccc7a019842cf180f0f7), with frozen_universe_manifest.json (SHA256 72dc94bc16ae38fef13213ab59751d6dfb877cee20cca8ac00d39526dc89b7e5). Both preserve the delivered membership order except that PYPL occupies NKE's former US daily display slot. This slot is an audit order, not a claim that PayPal is the 30th-largest issuer. The frozen artifact uses historical_30_user_fixed as the operational universe ID; historical_top_30 and historical_top_30_INCOMPLETE_REVIEW_ONLY remain original review labels, not alternative baskets. It contains 127 unique market/ticker pairs across 201 membership rows. These files are reproducible projections of this selected configuration, not a separate authority.

The 201 rows are membership assignments, not 201 distinct issuers: existing25 contributes 25, sector28 contributes 56, and US/JP historical-review baskets contribute 30 each for daily and minute horizons, or 120. Each daily_and_5m row serves both frequencies. Preserve those memberships with the single approved US daily NKE-to-PYPL replacement; retain every other member and display slot. Do not add another newly researched US member, a newly computed July list, or a June JPX minute list. There is no periodic re-ranking. A future membership change requires an explicit new user decision and configuration version.

| Parameter | Current value | Status |
|---|---|---|
| universe_membership_policy | fixed_delivered_review_20261003_with_approved_exception | Approved fixed selection |
| universe_approved_exception | US daily historical_30_user_fixed: NKE replaced by PYPL | Approved 2026-10-03 at 22:07 JST |
| universe_membership_row_count | 201 | Verified against the delivered CSV plus exactly one replacement |
| universe_reselection_enabled | false | Approved |
| historical_rank_certification | Incomplete for the US full market | Evidence limitation retained |
| historical_rank_certification_required_for_fixed_basket | false | Latest user choice permits this exact provisional subset |
| minute_selection_date_policy | Preserve old review selection provenance while using maximum actual 5m history | Approved combination; look-ahead selection bias |

Data quality review may flag a member as unavailable, not yet listed, halted or otherwise untradable. It may not silently substitute another company or invent bars. Keep membership selection, original ranking/snapshot dates, source publication evidence, data start and tradable intervals separate. A ticker/issuer identity correction must be documented without changing the intended company; an unresolved material problem must be raised before dependent execution.

### Frozen existing and sector memberships

Membership is frozen as of 2026-10-03 for all baskets below, including the previously delivered US and JP historical-review baskets. Member selection is complete under the latest instruction; price coverage and execution readiness are not. Each market and each universe is a separate portfolio. Duplicates within a basket are prohibited; overlap between baskets is intentional.

These are retrospective research baskets selected with current knowledge, not lists claimed to have been selected in 2021. Preserve subjective-selection and survivorship bias when testing earlier history. Sector buckets are mutually exclusive research categories; restaurants do not also count toward retail, and memory members do not also occupy semiconductor slots. The sector lists are defensible representatives, not a verified market-cap Top4 in every industry.

#### Existing universe US12

| Symbol | Company | Primary evidence |
|---|---|---|
| NVDA | NVIDIA Corporation | [Source](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/) |
| AVGO | Broadcom Inc. | [Source](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-fourth-quarter-and-fiscal-year-2025) |
| AMD | Advanced Micro Devices, Inc. | [Source](https://ir.amd.com/news-events/press-releases/detail/1276/amd-reports-fourth-quarter-and-full-year-2025-financial-results) |
| MU | Micron Technology, Inc. | [Source](https://investors.micron.com/financials/quarterly-results/default.aspx) |
| TSM | Taiwan Semiconductor Manufacturing Company Limited | [Source](https://investor.tsmc.com/sites/ir/annual-report/2025/2025%20Annual%20Report_E.pdf) |
| ASML | ASML Holding N.V. | [Source](https://www.asml.com/en/investors/shares) |
| LRCX | Lam Research Corporation | [Source](https://investor.lamresearch.com/sec-filings?action=view&filer=Ticker%3ALRCX&item=1023799&pagetemplate=basic) |
| ANET | Arista Networks, Inc. | [Source](https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-Fourth-Quarter-and-Year-End-2025-Financial-Results/default.aspx) |
| VRT | Vertiv Holdings Co | [Source](https://www.sec.gov/Archives/edgar/data/1674101/000167410126000008/vrt-20251231.htm) |
| MSFT | Microsoft Corporation | [Source](https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm) |
| GOOGL | Alphabet Inc. | [Source](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm) |
| ORCL | Oracle Corporation | [Source](https://www.oracle.com/news/announcement/q3fy26-earnings-release-2026-03-10/) |

#### Existing universe JP13

| Symbol | Company | Primary evidence |
|---|---|---|
| 6857.T | Advantest | [Source](https://www.advantest.com/en/investors/individual-investors/faq/) |
| 8035.T | Tokyo Electron | [Source](https://www.tel.com/ir/faq/) |
| 6146.T | DISCO | [Source](https://www.disco.co.jp/eg/ir/stock/info.html) |
| 6920.T | Lasertec | [Source](https://www.lasertec.co.jp/ir/stock/outline.html) |
| 285A.T | Kioxia Holdings | [Source](https://www.jpx.co.jp/english/news/1031/20241217_01.html) |
| 4062.T | Ibiden | [Source](https://www.ibiden.com/ir/info17_01.pdf) |
| 4004.T | Resonac Holdings | [Source](https://www.resonac.com/sites/default/files/2023-03/pdf-news-20230302-114meeting-notice_en.pdf) |
| 4186.T | Tokyo Ohka Kogyo | [Source](https://www.tok.co.jp/application/files/2216/8086/4334/r_mid_1303.pdf) |
| 4063.T | Shin-Etsu Chemical | [Source](https://www.shinetsu.co.jp/en/ir/ir-faq/) |
| 5803.T | Fujikura | [Source](https://www.fujikura.co.jp/en/ir/faq/) |
| 5801.T | Furukawa Electric | [Source](https://www.furukawaelectric.com/ir/stock/information.html) |
| 9984.T | SoftBank Group | [Source](https://group.softbank/en/ir/faq) |
| 2737.T | Tomen Devices | [Source](https://www.tomendevices.co.jp/ir/faq.html) |

#### Sector universe US28

| Sector | Symbol | Company | Primary evidence |
|---|---|---|---|
| Semiconductor | NVDA | NVIDIA Corporation | [Source](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/) |
| Semiconductor | AVGO | Broadcom Inc. | [Source](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-fourth-quarter-and-fiscal-year-2025) |
| Semiconductor | AMD | Advanced Micro Devices, Inc. | [Source](https://ir.amd.com/news-events/press-releases/detail/1276/amd-reports-fourth-quarter-and-full-year-2025-financial-results) |
| Semiconductor | TSM | Taiwan Semiconductor Manufacturing Company Limited | [Source](https://investor.tsmc.com/sites/ir/annual-report/2025/2025%20Annual%20Report_E.pdf) |
| Semiconductor memory / SSD / RAM | MU | Micron Technology, Inc. | [Source](https://investors.micron.com/financials/quarterly-results/default.aspx) |
| Semiconductor memory / SSD / RAM | SNDK | Sandisk Corporation | [Source](https://www.sec.gov/Archives/edgar/data/2023554/000202355425000034/sndk-20250627.htm) |
| Semiconductor memory / SSD / RAM | SIMO | Silicon Motion Technology Corporation | [Source](https://www.sec.gov/Archives/edgar/data/1329394/000119312526197184/d17718d20f.htm) |
| Semiconductor memory / SSD / RAM | RMBS | Rambus Inc. | [Source](https://www.rambus.com/rambus-enables-power-efficient-ai-platforms-with-socamm2-server-module-chipset/) |
| Bank | JPM | JPMorgan Chase & Co. | [Source](https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/annualreport-2025.pdf) |
| Bank | BAC | Bank of America Corporation | [Source](https://www.sec.gov/Archives/edgar/data/70858/000007085826000157/bac-20251231.htm) |
| Bank | WFC | Wells Fargo & Company | [Source](https://www.sec.gov/Archives/edgar/data/72971/000007297126000133/wfc-20251231.htm) |
| Bank | C | Citigroup Inc. | [Source](https://www.sec.gov/Archives/edgar/data/831001/000110465926003604/c-20260114xex99d1.htm) |
| Restaurant | MCD | McDonald's Corporation | [Source](https://corporate.mcdonalds.com/content/dam/sites/corp/nfl/pdf/MCD%202025%20Annual%20Report.pdf) |
| Restaurant | SBUX | Starbucks Corporation | [Source](https://investor.starbucks.com/news/financial-releases/news-details/2025/Starbucks-Reports-Q4-and-Full-Fiscal-Year-2025-Results/) |
| Restaurant | CMG | Chipotle Mexican Grill, Inc. | [Source](https://ir.chipotle.com/2026-02-03-CHIPOTLE-ANNOUNCES-FOURTH-QUARTER-AND-FULL-YEAR-2025-RESULTS?lv=true) |
| Restaurant | YUM | Yum! Brands, Inc. | [Source](https://www.yum.com/wps/portal/yumbrands/Yumbrands/news/press-releases/yum%20brands%20announces%20leadership%20transition%20plans%20david%20gibbs%20to%20retire%20in%202026%20%20%20%20%20/%21ut/p/z0/fY5BCsIwFESv8i8gSQO23VdErVW6ENpsJDWx_Vh_QpIK3t70As5qhhmGxyTrmCT1wVFFtKTmlHuZ38u2Fgd-5ZfyVm15K7L6eN4XGd8V7MTk_0F6EL6pmpFJp-K0QXpa1n2XNwxekQ6giOxCDxNgNkobHyZ0EFMXcIUANycLOlFpGHEYAkQL3kT0BpBAcJHDKuZesv8B0cndwQ%21%21/) |
| Cybersecurity | PANW | Palo Alto Networks, Inc. | [Source](https://investors.paloaltonetworks.com/news-releases/news-release-details/palo-alto-networks-reports-fiscal-fourth-quarter-and-fiscal-9) |
| Cybersecurity | CRWD | CrowdStrike Holdings, Inc. | [Source](https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-reports-fourth-quarter-and-fiscal-year-2026) |
| Cybersecurity | FTNT | Fortinet, Inc. | [Source](https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-fourth-quarter-and-full-year-2025/) |
| Cybersecurity | ZS | Zscaler, Inc. | [Source](https://ir.zscaler.com/node/15186) |
| Retail | AMZN | Amazon.com, Inc. | [Source](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/default.aspx) |
| Retail | WMT | Walmart Inc. | [Source](https://stock.walmart.com/) |
| Retail | COST | Costco Wholesale Corporation | [Source](https://investor.costco.com/news/news-details/2025/Costco-Wholesale-Corporation-Reports-Fourth-Quarter-and-Fiscal-Year-2025-Operating-Results/) |
| Retail | HD | The Home Depot, Inc. | [Source](https://ir.homedepot.com/investor-resources/investor-documents) |
| Insurance | PGR | The Progressive Corporation | [Source](https://www.sec.gov/Archives/edgar/data/80661/000008066126000071/pgr202512ex991earningsrele.htm) |
| Insurance | CB | Chubb Limited | [Source](https://www.sec.gov/Archives/edgar/data/896159/000089615926000005/cb-20251231.htm) |
| Insurance | MET | MetLife, Inc. | [Source](https://www.metlife.com/about-us/newsroom/2026/february/metlife-announces-full-year-and-4q-2025-results/) |
| Insurance | AIG | American International Group, Inc. | [Source](https://www.aig.com/investor-relations) |

#### Sector universe JP28

| Sector | Symbol | Company | Primary evidence |
|---|---|---|---|
| Semiconductor | 8035.T | Tokyo Electron | [Source](https://www.tel.com/ir/faq/) |
| Semiconductor | 6857.T | Advantest | [Source](https://www.advantest.com/en/investors/individual-investors/faq/) |
| Semiconductor | 6146.T | DISCO | [Source](https://www.disco.co.jp/eg/ir/stock/info.html) |
| Semiconductor | 6723.T | Renesas Electronics | [Source](https://www.renesas.com/en/about/investor-relations/stock/stock-information) |
| Semiconductor memory / SSD / RAM | 285A.T | Kioxia Holdings | [Source](https://www.jpx.co.jp/english/news/1031/20241217_01.html) |
| Semiconductor memory / SSD / RAM | 6762.T | TDK | [Source](https://www.tdk.com/en/news_center/press/20201203_01.html) |
| Semiconductor memory / SSD / RAM | 2737.T | Tomen Devices | [Source](https://www2.jpx.co.jp/disc/27370/140120260424510045.pdf) |
| Semiconductor memory / SSD / RAM | 6676.T | Buffalo | [Source](https://www.buffalo.jp/ir/news/20250319.pdf) |
| Bank | 8306.T | Mitsubishi UFJ Financial Group | [Source](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) |
| Bank | 8316.T | Sumitomo Mitsui Financial Group | [Source](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) |
| Bank | 8411.T | Mizuho Financial Group | [Source](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) |
| Bank | 7182.T | Japan Post Bank | [Source](https://www.jp-bank.japanpost.jp/en/ir/faq/en_ir_qa_cat05.html) |
| Restaurant | 7550.T | Zensho Holdings | [Source](https://www2.jpx.co.jp/disc/75500/140120240808566581.pdf) |
| Restaurant | 2702.T | McDonald's Holdings Japan | [Source](https://www.mcdonalds.co.jp/cservice/list.stock/) |
| Restaurant | 3197.T | Skylark Holdings | [Source](https://corp.skylark.co.jp/ir/individual/) |
| Restaurant | 3563.T | FOOD & LIFE COMPANIES | [Source](https://food-and-life.co.jp/wp-content/uploads/2024/12/217c2caf45a7b824ccf93eec3dffff14.pdf) |
| Cybersecurity | 4704.T | Trend Micro | [Source](https://www.trendmicro.com/en_us/about/investor-relations/stocks-bonds.html) |
| Cybersecurity | 2326.T | Digital Arts | [Source](https://pages.daj.jp/ir/faq/) |
| Cybersecurity | 3692.T | FFRI Security | [Source](https://www.ffri.jp/assets/files/docs/1001/20140918_issue_price.pdf) |
| Cybersecurity | 4475.T | HENNGE | [Source](https://hennge.com/global/investor/) |
| Retail | 9983.T | Fast Retailing | [Source](https://www.fastretailing.com/eng/ir/faq/) |
| Retail | 3382.T | Seven & i Holdings | [Source](https://www2.jpx.co.jp/disc/33820/140120231218505062.pdf) |
| Retail | 8267.T | AEON | [Source](https://www.aeon.info/ir/faq/) |
| Retail | 7532.T | Pan Pacific International Holdings | [Source](https://ppih.co.jp/ir/faq/enq_count.php?ans=1&faqid=2274) |
| Insurance | 8766.T | Tokio Marine Holdings | [Source](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) |
| Insurance | 8725.T | MS&AD Insurance Group Holdings | [Source](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) |
| Insurance | 8630.T | Sompo Holdings | [Source](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) |
| Insurance | 8750.T | Daiichi Life Group | [Source](https://www.daiichilife-group.com/en/investor/news/assets/pdf/2025_index_032.pdf) |

#### Memory eligibility and identity caveats

- US memory members are MU (DRAM/NAND), SNDK (flash storage), SIMO (NAND/SSD controller ICs) and RMBS (memory-interface chipsets/IP). SIMO is a US-listed ADS, not a DRAM/NAND wafer manufacturer. RMBS is not being duplicated in semiconductor or cybersecurity slots.
- JP memory members are Kioxia285A (NAND/SSD), TDK6762 (actual NAND-controller/industrial-SSD business), Buffalo6676 (SSD/flash/memory products) and Tomen Devices2737 (technical DRAM/NAND/MCP/SSD distribution). TDK is not selected merely for HDD heads; Tomen is not represented as a wafer manufacturer.
- WDC/STX are not in the selected US memory basket. Resonac4004 is absent from the JP sector-memory group but remains in the original JP13.
- Kioxia began trading on 2024-12-18. The current independent SNDK began regular-way trading on 2025-02-24; do not splice the unrelated old SNDK ticker history into this issuer. Record NOT_YET_LISTED before actual listing and obtain legitimate post-listing warmup; never backfill prices or silently replace the company.
- SoftBank Group9984 and SoftBank Corp9434 are different issuers. Name changes such as Showa Denko/Resonac or Melco/Buffalo do not by themselves create a new listing.
- Identity evidence and an early IPO do not prove a continuous five-year daily or maximum-available five-minute series. Full-universe OHLCV coverage remains NOT_AUDITED despite the representative probes in Section2.

SIMO business qualification: [Evidence 1](https://ir.siliconmotion.com/static-files/14a3e8cc-d957-4700-a43d-eb88207842f9), [Evidence 2](https://ir.siliconmotion.com/news-releases/news-release-details/silicon-motion-showcases-next-generation-storage-architectures).
RMBS business qualification: [Evidence 1](https://investor.rambus.com/press-releases/press-release-details/2026/Rambus-Enables-Next-Generation-AI-PC-Memory-with-Complete-Client-Chipset-for-CUDIMM-and-CSODIMM-Modules/default.aspx), [Evidence 2](https://www.sec.gov/Archives/edgar/data/917273/000119312526057101/rmbs-20251231.htm), [Evidence 3](https://investor.rambus.com/financials/annual-reports-and-proxies/investor-home/investor-home/default.aspx).
6762.T business qualification: [Evidence 1](https://product.tdk.com/en/products/flash-storage/lineup/index.html).
6676.T business qualification: [Evidence 1](https://www.buffalo.jp/topics/special/detail/bcn2026.html).
2737.T business qualification: [Evidence 1](https://www.tomendevices.co.jp/recruit/partnership.html).

### Frozen Japanese historical-review members

The following exact member/rank sequences are now selected as the fixed JP baskets. Their ranks are verified source evidence; file-specific publication times and actual first tradable data bars remain unaudited. The latest selection overrides the earlier pending-adoption status and restores the July31 minute list as operative. These are Tokyo sections covered by the reports, not all Japanese exchanges. Record later-information use openly rather than inventing earlier availability; no monthly reconstitution is selected.

#### Daily-horizon source snapshot

Snapshot: 2021-09-30. [Official ranking](https://www.jpx.co.jp/english/markets/statistics-equities/misc/b5b4pj000004dwnm-att/202109-e.pdf). These exact members are selected. The original review anchor is 2021-10-04 JST, using a proposed conservative next-business-day publication schedule followed by another session; this is not file-level timestamp proof. Audit the actual data start and publication assumption without reselecting members.

| Rank | Symbol | Company |
|---:|---|---|
| 1 | 7203.T | Toyota Motor |
| 2 | 6861.T | Keyence |
| 3 | 6758.T | Sony Group |
| 4 | 6098.T | Recruit Holdings |
| 5 | 9984.T | SoftBank Group |
| 6 | 8306.T | Mitsubishi UFJ Financial Group |
| 7 | 9983.T | Fast Retailing |
| 8 | 9433.T | KDDI |
| 9 | 9432.T | NTT |
| 10 | 4063.T | Shin-Etsu Chemical |
| 11 | 8035.T | Tokyo Electron |
| 12 | 6594.T | Nidec |
| 13 | 9434.T | SoftBank |
| 14 | 6367.T | Daikin Industries |
| 15 | 7974.T | Nintendo |
| 16 | 4519.T | Chugai Pharmaceutical |
| 17 | 6981.T | Murata Manufacturing |
| 18 | 4661.T | Oriental Land |
| 19 | 7741.T | HOYA |
| 20 | 6501.T | Hitachi |
| 21 | 7267.T | Honda Motor |
| 22 | 4502.T | Takeda Pharmaceutical |
| 23 | 4568.T | Daiichi Sankyo |
| 24 | 6902.T | Denso |
| 25 | 4689.T | LY Corporation |
| 26 | 2413.T | M3 |
| 27 | 8316.T | Sumitomo Mitsui Financial Group |
| 28 | 8058.T | Mitsubishi Corporation |
| 29 | 8001.T | ITOCHU |
| 30 | 4901.T | Fujifilm Holdings |

#### Frozen minute-horizon review snapshot

Snapshot: 2026-07-31. [Official ranking](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf). The latest instruction restores this exact delivered 30-member list as the operative fixed minute basket. Its prior review anchor was 2026-08-04 JST; file-level publication time remains unverified. The maximum-history policy can include earlier July data. Applying this later snapshot membership to those earlier observations creates look-ahead selection bias, which must appear in every affected result. Do not re-rank or replace it with an earlier snapshot. v0.10's temporary superseded status remains in the version history only.

| Rank | Symbol | Company |
|---:|---|---|
| 1 | 7203.T | Toyota Motor |
| 2 | 8306.T | Mitsubishi UFJ Financial Group |
| 3 | 9984.T | SoftBank Group |
| 4 | 8316.T | Sumitomo Mitsui Financial Group |
| 5 | 8035.T | Tokyo Electron |
| 6 | 285A.T | Kioxia Holdings |
| 7 | 9983.T | Fast Retailing |
| 8 | 6501.T | Hitachi |
| 9 | 6857.T | Advantest |
| 10 | 6758.T | Sony Group |
| 11 | 8411.T | Mizuho Financial Group |
| 12 | 6861.T | Keyence |
| 13 | 6098.T | Recruit Holdings |
| 14 | 8058.T | Mitsubishi Corporation |
| 15 | 8001.T | ITOCHU |
| 16 | 8766.T | Tokio Marine Holdings |
| 17 | 6981.T | Murata Manufacturing |
| 18 | 8031.T | Mitsui & Co. |
| 19 | 7011.T | Mitsubishi Heavy Industries |
| 20 | 6503.T | Mitsubishi Electric |
| 21 | 9433.T | KDDI |
| 22 | 4519.T | Chugai Pharmaceutical |
| 23 | 4063.T | Shin-Etsu Chemical |
| 24 | 7182.T | Japan Post Bank |
| 25 | 9434.T | SoftBank |
| 26 | 6752.T | Panasonic Holdings |
| 27 | 7974.T | Nintendo |
| 28 | 2914.T | Japan Tobacco |
| 29 | 9432.T | NTT |
| 30 | 4502.T | Takeda Pharmaceutical |

### Corporate-action audit items discovered during membership research

Known examples requiring an explicit price/quantity/distribution audit include the Kioxia and current SNDK IPO histories, Sony6758’s 2025 Sony Financial Group distribution, and Buffalo6676’s 2024 spin-off followed by a same-code rename. These are not a complete action database. Do not manufacture a loss from an unmodeled distribution, silently apply a total-return adjustment despite excluding dividends, or retrospectively remove a problematic member. [Sony transaction information](https://www.sony.com/en/SonyInfo/IR/library/SFG_pso/), [Buffalo restructuring](https://www.buffalo.jp/ir/strategy/restructuring.html).

Historical member6594 remains in the September2021 snapshot even if later exchange-alert status creates additional audit needs. Current status is not grounds for deleting its earlier membership. US historical-review memberships are fixed below; their full-market Top30 accuracy is not certified.

### Frozen US historical-review members

These are the selected daily and minute lists from the delivered review, with one explicit US daily exception: PYPL replaces NKE. No other re-ranking or replacement is applied. Review order below preserves the provisional research ordering; it is not a certified full-US-market rank. The research combines public SEC share disclosures with Yahoo historical-price estimates and a partly reconstructed candidate set. Links identify review provenance, not a new full-market validation in this version. Keep issuer-share staleness, publication lag, omitted historical candidates/delistings, class conversion, ADR ratios and vendor adjustment limitations visible.

The daily review used an October4,2021 anchor. The minute review used an August4,2026 anchor. Those are original selection-research anchors, not the audited start of the current maximum-available price series. In particular, applying the August-based minute selection to earlier July data uses later information and is selection-look-ahead-biased. The latest user decision keeps these lists despite the unresolved certification; do not portray that choice as resolving the evidence gaps.

#### Daily fixed review basket

| Review order | Symbol | Company | Review source |
|---:|---|---|---|
| 1 | AAPL | APPLE INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/dei/EntityCommonStockSharesOutstanding.json) |
| 2 | MSFT | MICROSOFT CORP | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000789019/dei/EntityCommonStockSharesOutstanding.json) |
| 3 | GOOGL | ALPHABET INC | [Source](https://www.sec.gov/Archives/edgar/data/1652044/000165204421000047/goog-20210630.htm) |
| 4 | AMZN | AMAZON.COM INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001018724/dei/EntityCommonStockSharesOutstanding.json) |
| 5 | META | FACEBOOK INC | [Source](https://www.sec.gov/Archives/edgar/data/1326801/000132680121000049/fb-20210630.htm) |
| 6 | TSLA | TESLA INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001318605/dei/EntityCommonStockSharesOutstanding.json) |
| 7 | BRK-B | BERKSHIRE HATHAWAY | [Source](https://www.sec.gov/Archives/edgar/data/1067983/000156459021042312/brka-10q_20210630.htm) |
| 8 | TSM | TSMC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001046179/dei/EntityCommonStockSharesOutstanding.json) |
| 9 | NVDA | NVIDIA CORP | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001045810/dei/EntityCommonStockSharesOutstanding.json) |
| 10 | JPM | JPMORGAN CHASE | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/dei/EntityCommonStockSharesOutstanding.json) |
| 11 | V | VISA INC | [Source](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000042/v-20210630.htm) |
| 12 | JNJ | JOHNSON & JOHNSON | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000200406/dei/EntityCommonStockSharesOutstanding.json) |
| 13 | BABA | ALIBABA GRP | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001577552/dei/EntityCommonStockSharesOutstanding.json) |
| 14 | WMT | WALMART INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000104169/dei/EntityCommonStockSharesOutstanding.json) |
| 15 | UNH | UNITEDHEALTH GRP | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000731766/dei/EntityCommonStockSharesOutstanding.json) |
| 16 | BAC | BANK OF AMERICA | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000070858/dei/EntityCommonStockSharesOutstanding.json) |
| 17 | MA | MASTERCARD INC | [Source](https://www.sec.gov/Archives/edgar/data/1141391/000114139121000156/ma-20210630.htm) |
| 18 | HD | HOME DEPOT INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000354950/dei/EntityCommonStockSharesOutstanding.json) |
| 19 | PG | PROCTER & GAMBLE | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000080424/dei/EntityCommonStockSharesOutstanding.json) |
| 20 | DIS | WALT DISNEY CO | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001744489/dei/EntityCommonStockSharesOutstanding.json) |
| 21 | ASML | ASML HOLDING NV | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000937966/dei/EntityCommonStockSharesOutstanding.json) |
| 22 | ADBE | ADOBE INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000796343/dei/EntityCommonStockSharesOutstanding.json) |
| 23 | NFLX | NETFLIX INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001065280/dei/EntityCommonStockSharesOutstanding.json) |
| 24 | CRM | SALESFORCE.COM | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001108524/dei/EntityCommonStockSharesOutstanding.json) |
| 25 | CMCSA | COMCAST CORP | [Source](https://www.sec.gov/Archives/edgar/data/1166691/000116669121000029/cmcsa-20210630.htm) |
| 26 | XOM | EXXON MOBIL CORP | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000034088/dei/EntityCommonStockSharesOutstanding.json) |
| 27 | TM | TOYOTA MOTOR | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001094517/dei/EntityCommonStockSharesOutstanding.json) |
| 28 | ORCL | ORACLE CORP | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001341439/dei/EntityCommonStockSharesOutstanding.json) |
| 29 | PFE | PFIZER INC | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000078003/dei/EntityCommonStockSharesOutstanding.json) |
| 30 | PYPL | PayPal Holdings, Inc. | [Source](https://www.sec.gov/Archives/edgar/data/1633917/000163391721000149/pypl-20210630.htm) |

#### Minute fixed review basket

| Review order | Symbol | Company | Review source |
|---:|---|---|---|
| 1 | NVDA | NVIDIA Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001045810/dei/EntityCommonStockSharesOutstanding.json) |
| 2 | GOOGL | Alphabet Inc | [Source](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000071/goog-20260630.htm) |
| 3 | AAPL | Apple Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/dei/EntityCommonStockSharesOutstanding.json) |
| 4 | MSFT | Microsoft Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000789019/dei/EntityCommonStockSharesOutstanding.json) |
| 5 | AMZN | Amazon.com, Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001018724/dei/EntityCommonStockSharesOutstanding.json) |
| 6 | TSM | Taiwan Semiconductor Manufacturing Company Limited | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001046179/dei/EntityCommonStockSharesOutstanding.json) |
| 7 | AVGO | Broadcom Inc | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001730168/dei/EntityCommonStockSharesOutstanding.json) |
| 8 | SPCX | Space Exploration Technologies Corp. | [Source](https://www.sec.gov/Archives/edgar/data/1181412/000162828026042639/spaceexplorationtechnologi.htm) |
| 9 | META | Meta Platforms, Inc. | [Source](https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm) |
| 10 | TSLA | Tesla, Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001318605/dei/EntityCommonStockSharesOutstanding.json) |
| 11 | BRK-B | Berkshire Hathaway Inc | [Source](https://www.sec.gov/Archives/edgar/data/1067983/000119312526202243/brka-20260331.htm) |
| 12 | LLY | Eli Lilly and Company | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000059478/dei/EntityCommonStockSharesOutstanding.json) |
| 13 | JPM | JPMorgan Chase & Co | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/dei/EntityCommonStockSharesOutstanding.json) |
| 14 | MU | Micron Technology, Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000723125/dei/EntityCommonStockSharesOutstanding.json) |
| 15 | WMT | Walmart Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000104169/dei/EntityCommonStockSharesOutstanding.json) |
| 16 | AMD | Advanced Micro Devices, Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000002488/dei/EntityCommonStockSharesOutstanding.json) |
| 17 | V | Visa Inc. | [Source](https://www.sec.gov/Archives/edgar/data/1403161/000140316126000104/v-20260630.htm) |
| 18 | XOM | Exxon Mobil Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0002115436/dei/EntityCommonStockSharesOutstanding.json) |
| 19 | ASML | ASML Holding N.V. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000937966/dei/EntityCommonStockSharesOutstanding.json) |
| 20 | JNJ | Johnson & Johnson | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000200406/dei/EntityCommonStockSharesOutstanding.json) |
| 21 | MA | Mastercard Incorporated | [Source](https://www.sec.gov/Archives/edgar/data/1141391/000114139126000083/ma-20260630.htm) |
| 22 | INTC | Intel Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000050863/dei/EntityCommonStockSharesOutstanding.json) |
| 23 | CSCO | Cisco Systems, Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000858877/dei/EntityCommonStockSharesOutstanding.json) |
| 24 | BAC | Bank of America Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000070858/dei/EntityCommonStockSharesOutstanding.json) |
| 25 | ABBV | AbbVie Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001551152/dei/EntityCommonStockSharesOutstanding.json) |
| 26 | COST | Costco Wholesale Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000909832/dei/EntityCommonStockSharesOutstanding.json) |
| 27 | AMAT | Applied Materials, Inc. | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000006951/dei/EntityCommonStockSharesOutstanding.json) |
| 28 | ORCL | Oracle Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0001341439/dei/EntityCommonStockSharesOutstanding.json) |
| 29 | CVX | Chevron Corporation | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000093410/dei/EntityCommonStockSharesOutstanding.json) |
| 30 | GE | General Electric Company | [Source](https://data.sec.gov/api/xbrl/companyconcept/CIK0000040545/dei/EntityCommonStockSharesOutstanding.json) |

The full delivered CSV retains each row's original estimate, source snapshot date, additional source and caveat, including the superseded NKE row. The operative frozen artifact records PYPL in the former NKE display slot30 under the explicit 22:07 JST approval. That replacement is not a fresh rank calculation and does not certify full-market Top30. Every other membership remains unchanged. The two tables each contain one selected trading line per intended company, such as GOOGL and BRK-B; historical issuer identity and executable symbol mapping still require audit.

### Data and selection-provenance details still required

- Preserve each frequency's original review selection anchor separately from its audited data start; do not derive a new member list from that audit.
- Minute and daily start dates differ; preserve actual data dates and the fixed-list selection date for each.
- Define total versus float cap, eligible security types, company aggregation and executable trading-line selection.
- Match historical prices with historically available issuer shares; current shares times an old price are not strict historical cap.
- Preserve delisted, merged, renamed and newly listed names where eligible.
- Fixed membership is selected; no automatic monthly rebalance or further re-ranking is permitted for this frozen experiment.
- Keep industry overlap, ADRs, multiple classes and IPO-short histories explicit.
- Exact starts come from each market/frequency's data audit. Preserve earlier2026-08 review anchors as selection provenance while auditing the longer July-start price window; none of these examples establishes a final full-universe data date.

Yahoo remains the price source. Additional public sources are authorized for historical information Yahoo lacks; the free-data constraint remains.

### Japan historical snapshots

The [JPX historical directory](https://www.jpx.co.jp/english/markets/statistics-equities/misc/08.html) lists 2017–2026. The [September 2021 snapshot](https://www.jpx.co.jp/english/markets/statistics-equities/misc/b5b4pj000004dwnm-att/202109-e.pdf), [July 31 2026 snapshot](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi00000256ky-att/202607_r.pdf) and [August 31 2026 snapshot](https://www.jpx.co.jp/english/markets/statistics-equities/misc/vk0khi0000028ng0-att/202608_r.pdf) were opened and checked. The latest decision selects the already delivered September2021 daily and July2026 minute member lists; source verification alone did not establish that adoption.

JPX uses listed shares including treasury shares and presents market segments separately. It is not free-float cap or all-Japan-exchange coverage. The official schedule is approximately 13:00 on the next month's first business day. [Definitions and update schedule](https://www.jpx.co.jp/english/markets/statistics-equities/misc/08.html)

Store snapshot date, actual public-availability evidence and formation time separately. The general schedule does not prove each historical PDF's exact publication time. If file-level evidence is unavailable, disclose a conservative availability assumption rather than claiming strict point-in-time certainty.

Selected applications and limitations:

- The daily basket keeps the delivered September2021 members; audit the original publication assumption and actual data dates.
- The minute basket keeps the delivered July31,2026 members over maximum actually accessible five-minute history. Earlier-July observations use later membership information and must be labeled with look-ahead selection bias. No new June-based list replaces it.
- Tokyo segment coverage remains limited. A month-end snapshot is not an exact arbitrary-start-date ranking, even when its membership is selected as a fixed basket.

### US selected SEC estimation method

SEC public filing indexes extend to 1994Q3; XBRL was first required in 2009 and the APIs need no account or API key. Aggregated Company Facts includes standard-taxonomy, whole-entity facts, so class-specific or custom disclosures can require original filings. [EDGAR access](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data), [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

The historical estimation method uses issuer shares publicly disclosed before its original research anchor and a same-basis historical price. The original target was the full approved market, but the latest selection fixes the delivered provisional subset. Partial reconstructed coverage must not be labeled a completed full-market Top30; maximum-history minute results additionally disclose selection-information dates later than some price observations.

| Parameter | Current value | Status |
|---|---|---|
| us_historical_cap_source | SEC historical filings/XBRL plus consistent historical prices | Approved source method |
| us_historical_rank_mode | Historically available issuer shares × consistent contemporaneous prices | Approved estimate method |
| us_historical_market_scope | Originally full US-exchange-listed market, including overseas companies | Research target; historical coverage incomplete |
| us_current_basket_scope | Exact delivered daily/minute provisional review lists | Approved fixed subset; no further member selection |
| spy_only_scope_allowed | false | Cannot substitute SPY-only ranking |
| us_historical_candidate_coverage | Complete historical candidate set not established | Verification required |
| us_missing_cap_policy | Do not fabricate; retain missing values and exclusion effects | Integrity requirement |

Do not backfill a quarter-end fact published later, or multiply historical shares by an inconsistently adjusted future-basis price. Preserve publication time as well as the fact's observation date.

Known limitations include issuer-share disclosure lag, historical-member omissions, delisting/ticker gaps, multiple classes and ADR mapping. A current ticker directory or historical fund holding list is not the full market. Calculating some caps does not establish that an unresolved company lies below the Top30 boundary.

Coverage and ranking-boundary uncertainty remain evidence limitations. Under the latest explicit selection override, they no longer block freezing these exact delivered baskets. Step1 member selection is complete with the single approved US daily replacement and without claiming full-market certification. Do not continue re-ranking, silently narrow or expand the chosen lists, or make any additional replacement without a new user decision.

Sequential project development and baseline/testing are authorized. Prior software implementation exists, but synchronization to the current configuration and historical-run results are not verified by this document update. This configuration maintenance has not run an engine or changed production monitoring.

## 13 Causal walk-forward design

| Parameter | Current value | Units or role | Status |
|---|---|---|---|
| validation_scheme | Optimize earlier data, test later data | Time order | Approved |
| training_window_type | Fixed-length rolling | Model | Approved |
| minute_train_window | Previous 2 calendar weeks | Training window | Approved |
| minute_test_window_fold | Following 1 calendar week | Test window | Approved |
| minute_step | 1 calendar week | Rolling stride | Approved |
| daily_train_window | Previous 6 calendar months | Training window | Approved |
| daily_test_window_fold | Following 1 calendar month | Test window | Approved |
| daily_step | 1 calendar month | Rolling stride | Approved |
| minute_final_holdout | Most recent complete calendar week | One-time final test | Duration approved; dates await audit |
| daily_final_holdout | Most recent complete calendar month | One-time final test | Duration approved; dates await audit |
| final_holdout_reuse | false | Never re-enter training or selection | Approved |
| optimization_ranges | ADX 20/25/30; N 3/5/8; histogram drawdown 30/40/50% | Initial grid | Accepted recommendation |
| parameter_selection_policy | Maximize median after-tax training return over eligible local neighbors | Robustness | Approved |
| max_drawdown_limit_pct | 30 | Candidate-selection risk constraint | Approved |
| low_trade_count_reporting | Flag fewer than 5 complete position closures | Reporting only; no new exclusion | Approved |
| low_liquidity_reporting | Separately flag low market volume/execution limitations | Reporting | Principle approved; threshold pending |
| objective_function | After-tax training return, evaluated by eligible-neighborhood median | Candidate must satisfy MDD <= 30% | Approved |
| neighborhood_definition | Candidate itself plus one-step neighbors along one active parameter axis | Exclude diagonals and inapplicable axes | Approved |
| optimization_tie_break | Lower drawdown, then a fixed parameter order | Deterministic; preserve order in run manifest | Approved |
| sparse_trade_count_threshold | 5 | Completed closures; counts below 5 are flagged | Approved |
| minimum_trade_count_filter | None | Sparse count does not disqualify a candidate | Approved |
| calendar_week_start | Monday | Calendar boundary mapped to exchange sessions | Approved |
| calendar_month_start | First calendar day of month | Calendar boundary mapped to exchange sessions | Approved |
| parameter_freeze | Before each test segment | Rule | Principle approved |
| training_account_start | Fresh initial capital and no positions for each candidate in each training fold | Independent candidate account | Approved |
| ordinary_oos_account_state | Continuous across ordinary rolling out-of-sample folds | Carry the actual account; do not reset each fold | Approved |
| final_baseline_account_start | Fresh initial capital and no positions | Separate final-holdout account | Approved |
| final_selected_account_start | Fresh initial capital and no positions | Separate from baseline and prior development accounts | Approved |
| prior_history_use_at_fresh_start | Indicator warmup only | No inherited trading account or earlier P&L | Approved |

Minute folds train on the prior two calendar weeks, test the next week and advance one week. Daily folds train on the prior six calendar months, test the next month and advance one month. This replaces the earlier annual daily split.

Weeks begin on Monday and months at the start of the calendar month. Map those boundaries to actual exchange sessions; holidays do not create bars. Exact final-holdout dates and incomplete-window handling still require data/calendar audit before inspecting outcomes.

Earlier test periods may become legitimate historical training data in later ordinary folds. Future data must never revise earlier trades. The final holdout is an explicit exception and never re-enters training.

### Account state across research phases

Each training candidate in each fold begins with the market's approved initial capital, a flat position ledger and a fresh trading account. Candidate comparisons do not inherit prior candidate trades, profits, losses, tax accruals, reservations or pending orders. Past legitimate data may warm up indicators but may not contribute account returns to the scored training interval. Independent candidate accounts do not change fixed initial-capital sizing or the existing market separation.

Ordinary rolling out-of-sample folds form one continuous account per tested study/strategy stream. Carry actual cash, holdings, cost basis, current-year tax state, pending orders and cash reservations across fold boundaries; do not reset the account or discard residual risk to improve the curve. A parameter update for the next fold changes future decisions, not completed trades or the frozen decision snapshot of an already queued order. Existing daily/monthly liquidation rules still apply, including genuine failures to flatten.

For the final untouched holdout, initialize the baseline and selected strategy as two separate fresh accounts, each at the approved initial capital and with no positions. Neither inherits a training account, ordinary OOS positions, profits, losses, reservations, pending orders or tax ledger; they also do not share cash or trades with each other. Retain earlier data only to establish legitimate indicator warmup/state. Do not generate pre-holdout trades or carry earlier order intentions into these fresh accounts.

The selected account policy is a research definition, not a claim that all reported phases form one uninterrupted investable account. Ordinary OOS returns may be concatenated only with their continuous ledger. The final holdout is a separate fresh-account comparison and must not be silently appended as if it inherited the preceding OOS account. Report initialization, starting equity, interval and configuration for each phase. Parameter selection remains restricted to training, and this account definition does not permit inspecting the final holdout early.

### Warmup and final holdout

Past data before a training window may initialize SMA, EMA, MACD and ADX and carry recursive state. It does not enter that fold's training score or enlarge the approved two-week/six-month window. Legitimate earlier indicator state may enter a test segment; trading-account carry or reset follows the explicit phase policy above. Future returns and eventual peaks may not. No later research may alter the fixed constituent list. The approved retrospective membership and later-selection minute bias remain separate limitations; causal indicator processing does not remove them.

Reserve the latest complete week/month based on each market's actual latest complete data and calendar. Do not automatically treat an unfinished current week/month as complete. Freeze exact dates after audit.

The final holdout is excluded from training, optimization, internal validation and selection. Use it only after all training, grid and selection rules are fixed. Earlier data may warm up indicators, but holdout returns may not guide choices. If strategy changes follow inspection, record that this sample is no longer untouched and arrange a new validation plan.

The execution and scoring definitions in this version were explicitly accepted before dependent tests. Exact final-sample dates still come from the actual data/calendar audit; approval of durations and boundary conventions does not invent available bars. Pause and ask when a material unresolved problem requires a decision.

### First-round recommended grid

Current baseline remains ADX25, N5 and histogram peak drawdown40%. Candidate values do not automatically replace it.

| Parameter | Baseline | Candidates | Applicability |
|---|---:|---|---|
| adx_threshold | 25 | 20, 25, 30 | Arms with an ADX entry gate only |
| cross_window_bars | 5 | 3, 5, 8 | FULL double-cross arm only |
| hist_exit_drawdown_pct | 40% | 30%, 40%, 50% | All arms sharing the histogram exit; retained heights 70%, 60%, 50% |

FULL has 3 × 3 × 3 = 27 theoretical candidates per applicable market, universe, training fold and allocation mode. This is not a count of completed tests. Do not generate redundant pseudo-experiments for inapplicable axes.

| Entry arm | Active axes | Candidates per fold |
|---|---|---:|
| MA_ONLY | Histogram drawdown | 3 |
| MACD_HIST | Histogram drawdown | 3 |
| MA_ADX | ADX threshold and histogram drawdown | 9 |
| MACD_HIST_ADX | ADX threshold and histogram drawdown | 9 |
| FULL | ADX threshold, N and histogram drawdown | 27 |

Fixed this round: SMA5/20, MACD12/26/9, ADX14, three positive histogram increments, position_scale1 and minute D20. Price stop/take-profit thresholds remain modeled but nontriggering and unoptimized. Allocation modes are retained alternatives, not an additional scale search; the five-arm primary comparison uses fixed 1/15.

### Drawdown constraint and robustness

The 30% maximum drawdown is a candidate-selection constraint in training/optimization and approved internal validation. A consistent proposed measure is the largest account-equity decline from a prior peak, including unrealized positions and a consistent fee/tax basis. Freeze valuation frequency in the run manifest.

A candidate above 30% cannot be selected as satisfying this constraint. If none qualifies, report no eligible candidate; do not loosen the limit, hide failures or pick an ineligible winner merely to return a result.

This is not an account-level live stop or an automatic liquidation trigger at 30%. It cannot guarantee future/test drawdown. Report an out-of-sample breach honestly; never truncate the curve, discard subsequent losses or retune retrospectively to appear compliant.

For each candidate, form a neighborhood containing itself and immediate one-grid-step neighbors along a single active parameter axis. Do not include diagonal moves or axes that do not apply to that entry arm. Calculate after-tax training return for the candidate and each available neighbor. Only drawdown-eligible neighbors contribute to the neighborhood median, and the candidate itself must satisfy MDD <= 30% to be selected. Maximize this median; on equal scores choose lower drawdown, then the fixed parameter order recorded before outcomes are viewed. This ordering must be deterministic and must not be chosen retrospectively.

Flag fewer than five complete position closures as sparse. This is a warning, not a minimum-trades eligibility gate; zero or few completed closures must remain visible instead of being hidden. The implementation must state how aggregate stock-level closures are counted when a position was built through several fills. Select and score only on training and explicitly allowed internal validation, never on ordinary external tests or the final holdout.

Report sparse strategy trade counts separately from low market volume. Do not quietly turn reporting flags into new exclusion filters. All minute candidates in a round retain D20; another D belongs to another round.

### Five entry-control arms

The histogram condition below is the shared positive-increment and positive-final-value rule. Threshold25 and N5 are baseline labels; only applicable axes vary in optimization.

| signal_arm | Entry condition | ADX entry gate | Status |
|---|---|---|---|
| MA_ONLY | SMA5/SMA20 bullish cross only | None | Approved |
| MACD_HIST | MACD bullish cross plus histogram | None | Approved |
| MA_ADX | SMA bullish cross plus ADX>25 | Yes | Approved |
| MACD_HIST_ADX | MACD bullish cross plus histogram plus ADX>25 | Yes | Approved |
| FULL | Both crosses within N5 plus histogram plus ADX>25 | Yes | Approved |

MA_ONLY/MA_ADX do not add a MACD entry or histogram entry gate. MACD_HIST/MACD_HIST_ADX do not add an SMA cross. No-ADX arms must not inherit ADX>25 through shared code.

The primary approved comparison uses fixed 1/15 sizing across the five entry arms, while retaining the ADX scale mode and formula. A 5×2 fully crossed ten-arm allocation design is an optional proposed layout, not a newly selected optimization scope. The weighted branch must disclose its nonpositive-target behavior and changed exposure/trade set.

Use the same universe, dates, costs, delay, scheduled exits, data processing and priority rules. Share the selected histogram peak exit. These are entry-condition comparisons: MA_ONLY still has a MACD-based exit, and MACD arms still use SMA slope for cash priority. Do not describe them as whole strategies using only one indicator. A pure-indicator strategy study would require separately approved exits and ranking.

### Report contents

Report baseline and optimized results separately, including:

- Test intervals, out-of-sample segments, universe formation dates and members
- Gross, after-fee and after-tax returns with fill-model labels
- Maximum drawdown, trade count, win rate, per-trade return and holding time
- Capital utilization, concentration, no-fill, below-lot and cash-shortfall counts
- Each fold's parameters, results and concatenated ordinary out-of-sample results
- Entry/allocation labels, fixed round-level D and neighboring-candidate performance
- Sparse-trade/low-volume flags, queue states and cancellation reasons
- Missing data, exit reasons and unsuccessful scheduled liquidations
- For the approved pilot comparison: preserve fixed and ADX-scaled results side by side, with exact runtime snapshots; add permitted Nikkei225/S&P500 reference curves and their different price-index return basis

These are reporting requirements/recommendations, not existing results. The selected training objective and neighborhood rule are defined above; reporting an out-of-sample metric does not authorize using it for selection.

## 14 Bias register

| ID | Assumption or risk | Interpretation consequence |
|---|---|---|
| B01 | Yahoo coverage, gaps and revisions not audited | Sample availability and reproducibility can change |
| B02 | Maximum accessible minute history remains short and provider-dependent | Limited regimes; actual coverage is not established by a range label or two probes |
| B03 | Daily next-Open model without intraday delay | Separate execution precision; no proof of 20-minute performance |
| B04 | Market orders represented by five-minute observations | No verified depth/seconds-level executable quotes; no guaranteed halt fill |
| B05 | Zero spread and slippage | Potentially optimistic net results, especially for turnover/illiquidity |
| B06 | US fixed review baskets have incomplete historical-market coverage and disclosure lag | User selection does not certify full-market Top30; survivorship, omitted candidates and stale share counts remain |
| B07 | Existing25 and sector representatives can reflect present knowledge | Subjective/current-date selection and survivorship |
| B08 | Delisting, halt, IPO, merger and rename coverage incomplete | Poor performers or untradable names may be omitted |
| B09 | Reconstructing historical executable price/share units from vendor-adjusted data | Incorrect factor, effective time, quantity or indicator rescaling can distort costs, exposure and signals |
| B10 | No dividends but adjusted data may embed distributions | Hidden or double-counted returns |
| B11 | Conditional JP zero commission and simplified tax | Different from actual eligibility/fees/tax treatment |
| B12 | FX disabled, local currencies separate | No currency purchasing-power or conversion effects |
| B13 | Multiple parameters/universes and repeated inspection | Data mining and multiple-comparison risk |
| B14 | Future warmup/peaks forbidden; fixed later-selection membership is applied to earlier minute data | Keep signals causal but explicitly report the remaining universe-selection look-ahead |
| B15 | Scheduled minute final-continuous-bar Open and daily last-trading-day Open liquidation | Omits remaining session exposure; missing prices can leave residual positions despite the planned schedule |
| B16 | One stock can consume the account cap | Concentrated risk and few trades dominating results |
| B17 | Fee-inclusive signal-price reservation and shrink-only fills | Price changes, cap checks and lot rounding change actual exposure; verify event deduplication and cash accounting |
| B18 | Snapshot, publication, original selection anchor and actual data start differ | Preserve all dates; fixed minute list may predate its information availability and must not be presented as point-in-time selection |
| B19 | ADX sizing in no-ADX-entry arms | Implicit trade filtering and exposure changes confound attribution |
| B20 | Shared MACD exit and SMA ranking | Entry-arm names do not mean exclusive whole-strategy indicator use |
| B21 | Double-counted latency or future-based cancellation | Wrong D or lookahead |
| B22 | Eligible-neighborhood median selection; fewer than5 closures only flagged | Sparse strategies remain eligible and may be unstable; selecting neighborhoods from test outcomes would overfit |
| B23 | 30% drawdown is a selection constraint only | No future guarantee; do not censor test breaches |
| B24 | Representative range=60d responses extend into July and include null/terminal observations | Audit coverage without changing frozen members; do not infer full bars, causes of nulls or universal dates |
| B25 | Old August-selection/July31 snapshot members frozen over earlier July minute data | Explicit look-ahead selection bias; later full-market corrections and new July lists are not applied |
| B26 | Daily monthly liquidation at the last trading day Open with a full-day buy ban | Different month-end exposure from a Close exit; calendar-preplanned timing does not remove market-order proxy bias |
| B27 | Fresh training candidates and separate fresh final accounts, with continuous ordinary OOS | Phase results have different account histories; final results are not a seamless continuation of the OOS ledger |
| B28 | Unverified special corporate actions pause affected runs | Results may remain incomplete; do not hide the pause, invent entitlements or silently remove the member |
| B29 | Original25 assumption-based daily pilot uses only the selected pre-September2026 part of the available cache | Narrower membership and regime coverage; startup/IPO gaps and preselected-member bias remain |
| B30 | Cache contains September2026 and later observations outside the approved pilot interval | Exclude them from pilot evaluation and retain the separate formal holdout gate |
| B31 | Pilot PA01–PA04 assume split-only OHLC, complete cached split records, fixed units and series identity | Hypothetical outputs depend on unverified economic inputs; permission to simulate is not verification |
| B32 | ADX-scaled pilot changes target exposure and the cash/lot-constrained execution path | Different fills and trade counts can contribute to differences; this is not an equal-exposure attribution or untouched validation |
| B33 | Price-index reference curves omit dividends and strategy fees/taxes and may begin at a later common observation | Index and after-tax account curves have different return bases, constituents and potentially displayed spans; label base date and rights/source limitations |
| B34 | The 102-candidate entry-arm grid selects the highest observed eligible after-tax return on the already inspected pilot interval | Explicit in-sample selection and multiple-comparison bias; disclose every trial and do not relabel winners as formal walk-forward or untouched-holdout results |

Carry relevant flags into results. When a risk is resolved, document the evidence, method and version rather than erase its historical existence.

## 15 Implementation sequence and version control

### Approved sequence and current state

| Step | Work | Current state |
|---:|---|---|
| 1 | Freeze all universes with members, dates, sources and biases | Complete for selection: 201 membership rows fixed, with only the approved US daily NKE-to-PYPL change; full-US certification incomplete and selection/date biases disclosed; data readiness still unaudited |
| 2 | Reserve final minute week and daily month | Durations approved; exact per-market/frequency dates require audit |
| 3 | Establish Git version tracking | Repository implementation exists; pre-v0.14 checkpoint linked below |
| 4 | Design code and visual interface in the project | Prior software implementation exists; v0.14 synchronization and focused verification pending |
| 5 | Run baseline first, then tests | Formal prerequisites retained. Preserve the completed fixed pilot and publish its runtime configuration/result/PDF before the separately approved ADX-scaled pilot; comparison execution remains pending in this record |

The selected project name is TrendTrade101, matching [kyon-phy/TrendTrade101](https://github.com/kyon-phy/TrendTrade101). The user-supplied remote is git@github.com:kyon-phy/TrendTrade101.git. It is a public repository; its existence does not mean project files have been pushed. Earlier name suggestions were not selected.

The interface must show process status, intermediate results and final results, distinguishing actual output from not-started, failed and missing-data states. Do not present sample numbers as actual backtests. Existing software/dashboard work does not establish a completed market-data audit or historical result.

Do not mark later steps complete while prerequisites remain open. Do not publish raw bulk market data, private material, credentials or internal records to the public repository. Publish only authorized project files through the execution workflow.

Use the baseline to check the development/rolling-test pipeline first. Preserve the final holdout until data, training grid and selection rules are frozen, then report the pre-fixed baseline and selected strategy together without adjusting rules from early holdout inspection.

### Historical v0.14 recording checkpoint

The following checkpoint preserves the status when v0.14 was first recorded. The 2026-10-04 decision approved only the historical executable split/share basis, the pause for unverified special corporate actions, and the training/ordinary-OOS/final account-state definitions above. It did not automatically approve every other technical proposal or certify the engine's then-current behavior.

The inspected pre-change repository checkpoint is [f225b0772e20c6b30ee499ecae04770d61369b8e](https://github.com/kyon-phy/TrendTrade101/commit/f225b0772e20c6b30ee499ecae04770d61369b8e). Its [technical convention memo](https://github.com/kyon-phy/TrendTrade101/blob/f225b0772e20c6b30ee499ecae04770d61369b8e/docs/technical-conventions-v013.md) records the earlier proposals and guarded implementation, while the [decision log](https://github.com/kyon-phy/TrendTrade101/blob/f225b0772e20c6b30ee499ecae04770d61369b8e/docs/decisions.md) preserves their earlier pending status. The linked [software CI](https://github.com/kyon-phy/TrendTrade101/actions/runs/37182846961) is prior-version evidence and cannot verify this newly recorded configuration.

| Change group | Approved | Recorded in this version | Implementation synchronized to v0.14 | Focused verification |
|---|---|---|---|---|
| Historical executable units and split accounting | Yes | Yes | Pending | Pending |
| Unverified special-action pause | Yes | Yes | Pending | Pending |
| Training candidate fresh accounts | Yes | Yes | Pending | Pending |
| Continuous ordinary rolling OOS accounts | Yes | Yes | Pending | Pending |
| Separate fresh baseline/selected final accounts | Yes | Yes | Pending | Pending |

The designated implementation task must reconcile the engine, account/run orchestration and machine configuration against this version, update repository decision/provenance records, and run focused synthetic checks before claiming synchronization. Candidate code locations include trendtrade101/engine.py and config/baseline.json; verify the actual current locations and diff rather than infer success from this checklist. Historical runs still require actual data and corporate-action audits, exact sample dates and complete run provenance. Saving this configuration does not release those data checks or turn synthetic tests into historical-performance evidence.

### Historical fixed-pilot authorization and current comparison status

The fixed-pilot scope and assumptions were approved in v0.16. Its completed run and exact runtime snapshot must remain separately preserved; this configuration contains no performance figures and does not substitute for result evidence. Section2 now approves the subsequent ADX comparison and requested reference-index reporting. The preserved v0.17 summary now records completed hypothetical execution; the new v0.18 grid and benchmark-source/distribution checks have separate status. Mechanical/input validation stays separate from unverified economic assumptions.

The repository's [D015 implementation record](https://github.com/kyon-phy/TrendTrade101/blob/c1be2216a79bc7127b61c0243ef375181e61a321/docs/decisions.md) and [accounting memo](https://github.com/kyon-phy/TrendTrade101/blob/c1be2216a79bc7127b61c0243ef375181e61a321/docs/accounting-v014.md) describe prior v0.14 accounting implementation and synthetic checks. Those records concern software and do not certify the newly scoped local cache or pilot performance. Record the actual current code commit, working-tree status, package digests and applicable audit receipts before executing the pilot. The historical v0.14 table above is not the current pilot-readiness gate.

| Pilot stage | Current configuration-record status |
|---|---|
| Original fixed baseline scope | Preserved v0.16 FULL/fixed1/15 original25 simulation; do not retroactively edit its runtime snapshot |
| Additional allocation comparison | v0.17 FULL/ADX-scaled original25 approved; same assumptions and interval; execute after fixed-result/configuration/PDF publication |
| Reference-index reporting | Nikkei225 and S&P500 curves requested; source, permitted distribution and delivery pending |
| Economic assumptions PA01–PA04 | Recorded as assumptions; external truth unverified |
| Scored interval | 2024-11-01 inclusive to 2026-09-01 exclusive; October2024 warmup |
| Original25 membership | Selected from the unchanged frozen universe; late IPO/readiness respected |
| Formal holdout separation | September2026 and later price observations excluded from pilot evaluation |
| Mechanical validation | Still required; malformed data, contradictions and invalid account states block replay |
| Formal verified-data gates | Unchanged; hypothesis permission cannot satisfy them |
| Hypothesis-mode implementation and run outcome | Must be separately verified and recorded |
| Optimization / formal holdout | Outside this pilot authorization |

### Completion checklist

- [x] N5, nonpositive-boundary positive hump, and 40% peak drawdown selected
- [x] Five explicit entry arms and fixed-1/15 primary comparison selected; retain ADX scale
- [x] Minute D20 fixed for a complete round; signal queue has no future-based cancellation
- [x] Pyramiding, aggregate stock-level exits, cancellation of pending buys and sell-before-buy ordering selected
- [x] Signal-time slope/ADX snapshots and pending cash reservation selected
- [x] Minute Open proxy and separate daily next-session Open selected
- [x] Price stop/take-profit parameters retained with extremes/unbounded capability, currently nontriggering and excluded
- [x] Minute 2-week/1-week and daily 6-month/1-month rolling windows selected
- [x] Initial three-axis grid documented; FULL has 27 candidates without changing the baseline
- [x] Drawdown selection limit30%, not an automatic account stop
- [x] Final holdout durations selected; never return them to training
- [x] Semiconductor-memory/sector-leader scope and full-US target including foreign companies clarified
- [x] SEC method selected; SPY-only substitution rejected
- [x] Sequential Git/UI/baseline/testing work authorized
- [x] Freeze existing25 and both sector28 memberships with identity/qualification sources
- [x] Select maximum actually accessible five-minute history rather than fixed60 calendar days
- [x] Freeze 201 membership rows, applying only the approved US daily NKE-to-PYPL exception; no other swaps or new July list
- [x] Adopt delivered JP daily/minute lists and label US baskets as provisional fixed research subsets
- [x] Disclose look-ahead selection bias when later minute-list information is applied to earlier July data
- [ ] Audit market-specific data starts, original selection anchors and source availability without member reselection
- [ ] Verify JP market coverage and publication assumptions; preserve incomplete full-US certification as a limitation
- [ ] Audit actual OHLCV, timezones, calendars, gaps, short bars, corporate actions and lot units
- [x] Freeze inclusive N window and one-emission-per-cross-pair rule; evaluate nonpositive histogram exits before reset
- [x] Require decline and inclusive retained-height threshold for positive-hump exit
- [x] Approve fee-inclusive signal-price reservation, shrink-only quantities, market-value caps and ticker/event-ID tie-breaks
- [x] Plan minute final-continuous-bar Open liquidation and daily last-trading-day Open liquidation with a full-day buy ban
- [x] Approve per-trade current-year tax accrual/refunds without cross-year loss carry
- [x] Freeze Monday/month-start boundaries, after-tax eligible-neighborhood median scoring and sparse-trade flag below5 closures
- [x] Select historical executable prices/share units with effective-date split quantity, cost and indicator adjustments
- [x] Preserve total split cost and pause affected runs for unverified special corporate actions
- [x] Select fresh training candidates, continuous ordinary OOS, and separate fresh baseline/selected final accounts
- [ ] Synchronize and verify v0.14 corporate-action and account-state semantics in implementation
- [ ] Verify indicator startup/rising-count interpretation, exact event serialization, calendar and missing-fill handling
- [ ] Freeze exact holdout dates, partial-window treatment, valuation cadence and fixed parameter ordering before viewing outcomes
- [ ] If using full weighted crossing, freeze its layout and disclose normalization/nonpositive-target behavior
- [x] Authorize a separately labeled original25 cached-daily baseline pilot without changing the formal plan
- [x] Select the pilot interval [2024-11-01,2026-09-01) and October2024 warmup, with late-IPO/readiness constraints
- [x] Authorize explicit economic assumptions for a separately labeled hypothetical simulation without certifying those assumptions
- [ ] Validate mechanical/input integrity and end-date isolation; synchronize the dedicated hypothesis mode
- [ ] Record conditional simulation outputs and assumption/coverage flags, or the exact blocker; keep formal readiness unchanged
- [x] Approve the separate FULL ADX-scaled pilot with USD10,000/JPY1,600,000 bases, scale1 and signal-time ADX/25
- [x] Request Nikkei225/S&P500 reference curves for the pilot report
- [ ] Complete fixed-result/runtime-configuration/PDF publication before the ADX comparison
- [ ] Verify permitted benchmark source/use and comparison implementation, then record actual outputs and hashes
- [x] Authorize the separate 102-candidate fixed1/15 in-sample five-arm grid with bounded applicable axes
- [ ] Verify grid implementation and frozen enumeration, then report every trial and each market/arm's eligible historical best
- [ ] Complete prerequisites, then implement and validate the authorized sequence

### Update discipline

For every change, update value, definition, status and affected bias; retain superseded values and reasons in the version history. Associate each run with a configuration version and data snapshot. Keep one canonical document identity. A proposal does not become an approved rule merely because it appears here.

### Version history

| Version | Date | Changes |
|---|---|---|
| v0.1 | 2026-10-03 JST | Initial parameters, strategy, pending definitions and biases. Five-minute SMA5/20; separate60-day minute/five-year daily studies; D20 and63-minute signal cutoff; old13.5%-remaining peak exit with unresolved boundary; JP capital corrected toJPY16m; historical-start Top30 replaces current ranking; N/fills/ranges open |
| v0.2 | 2026-10-03 JST | 19:12 decisions: N5; hump after H<=0; change exit to40% drawdown/60% remaining; retain disabled price stops/targets; permit other public historical-cap research |
| v0.3 | 2026-10-03 JST | Add JPX/SEC feasibility evidence and publication-time/snapshot biases; JP adoption proposed, full-US coverage unverified; no selected parameters or members changed |
| v0.4 | 2026-10-03 JST | 19:26/19:29: D fixed outside the grid; queued signals; daily next-Open without intraday delay; repeated orders and pyramiding; five entry arms, fixed1/15 comparison and robust neighborhoods; SEC estimate source selected, members unbuilt |
| v0.5 | 2026-10-03 JST | 19:35/19:39: aggregate exits/cancel pending buys; sells before buys; signal-time sizing/priority and cash reservation; fixed1/15 primary controls retain ADX scale; minute Open proxy after signal close+D; no invented missing fills; MACD fixed; extreme-capable price thresholds retained, nontriggering and unoptimized |
| v0.6 | 2026-10-03 JST | 19:48: rolling minute2-week/1-week and daily6-month/1-month windows; ADX20/25/30,N3/5/8,drawdown30/40/50 grid; MDD30% candidate constraint; warmup excluded from scored window; final holdout/objective/minimum trades then open |
| v0.7 | 2026-10-03 JST | Record sequential universe/Git/UI/baseline/test authorization; final complete minute week/daily month, never reused; select TrendTrade101 public repository; members, exact dates and execution remain incomplete |
| v0.8 | 2026-10-03 JST | 20:11: semiconductor memory/SSD/DRAM-related scope, sector leaders need not be blue chips; full-US Top30 target rejects SPY-only substitution; SEC estimation retained but coverage/ranks incomplete |
| v0.9 | 2026-10-03 JST | Translate the complete canonical configuration and history into English under the same identity; record English-only project policy and explicit inclusion of overseas US-listed companies with company-level aggregation; preserve all selected parameters, evidence and pending states; freeze verified existing25 and both sector28 memberships, record JP snapshot ranks without claiming completed historical formation |
| v0.10 | 2026-10-03 JST | 21:45 decision: use maximum actually accessible five-minute history rather than fixed60 calendar days; record two representative July-start probes and their null/terminal limitations; retire the old early-August minute anchor pending audited earlier-start re-ranking; daily horizon, rolling windows and final-holdout durations unchanged |
| v0.11 | 2026-10-03 JST | 21:57 decision: freeze exactly the 201 delivered review membership rows and stop selecting again; add both US30 review tables without claiming full-market certification; restore delivered July31 JP minute members as operative; cancel v0.10's re-ranking requirement while retaining maximum actual five-minute history; explicitly disclose later-selection look-ahead bias on earlier July data; all strategy parameters and holdout durations unchanged |
| v0.12 | 2026-10-03 JST | 22:07 decision: replace NKE with PYPL only in the US daily fixed historical-review basket; keep the other200 membership rows, displayed order, all minute baskets, maximum actual five-minute history and every strategy parameter unchanged; preserve the original review and record exactly one exception in the frozen artifacts |
| v0.13 | 2026-10-03 JST | Accept the proposed execution and scoring definitions: inclusive N window with once-per-cross-pair emission; nonpositive exit before peak reset and declining inclusive60%-height branch; signal-price-plus-fee reservation, shrink-only fills, market-value caps and ticker/event-ID ties; minute final-continuous-bar Open and daily month-final-trading-day Open liquidation/full-day buy ban; per-trade current-year tax with bounded refunds and no carry; Monday/month-start boundaries, after-tax eligible-neighborhood median score, drawdown/fixed-order ties and fewer-than5-closure warning without exclusion. Exact final-sample dates await audit; all201 members including PYPL and maximum actual five-minute history preserved |
| v0.14 | 2026-10-04 JST | 15:35 approval: select historical executable prices/share units, adjust quantity/per-share cost/indicator scale on verified split effectiveness while preserving total cost, and pause affected runs for unverified special corporate actions. Each training candidate starts fresh and flat; ordinary rolling OOS stays continuous; final baseline and selected strategy use separate fresh flat accounts with prior history for indicator warmup only. Preserve all fixed members and other strategy rules. Record implementation synchronization and focused tests as pending |
| v0.15 | 2026-10-04 JST | 18:36 approval: add a separately labeled original25 exploratory daily baseline pilot using the existing roughly two-year cache only. Preserve the formal five-year daily/max-available-minute plan, all201 memberships, baseline rules and fixed1/15 allocation. Exact pilot window remains audit-dependent; require applicable price/action checks and formal-holdout isolation. No fresh price fetch, optimization, tuning or final-holdout consumption is authorized by the pilot; record incomplete audits as blockers, not performance |
| v0.16 | 2026-10-04 JST | 19:48 approval: permit a separately labeled assumption-based original25 daily FULL/fixed1/15 baseline for [2024-11-01,2026-09-01), with October warmup and late-IPO/readiness constraints. Assume cached OHLC is split-only adjusted, cached split records complete, and US1/JP100 units; disclose series-identity and existing technical conventions as implementation assumptions. These are not verified economic facts or blanket formal-convention approval. Preserve fees, tax, fills, account rules, frozen memberships and formal plan; no optimization, new prices or formal-holdout use |

| v0.17 | 2026-10-04 JST | 20:23 approval: select the separate FULL ADX-scaled original25 pilot, USD10,000 and JPY1,600,000 bases, scale1 and stored signal-time ADX/25 minus0.5. Preserve the completed fixed-run v0.16 snapshot and all other rules, assumptions and dates; publish its result, exact configuration and PDF before the new comparison. Request Nikkei225/S&P500 price-index report curves normalized to100 with explicit price-index versus after-tax-account basis and source/distribution verification; no index trades, provider migration, optimization or formal-holdout use |

| v0.18 | 2026-10-04 JST | 21:41/21:42: authorize a separate assumption-based in-sample original25 daily five-entry-arm experiment, fixed1/15, same cache and [2024-11-01,2026-09-01) interval. Apply only relevant axes from ADX20/25/30, N3/5/8 and peak drawdown30/40/50%, yielding51 candidates per market/102 total. Rank each market/arm by individual after-tax return subject to MDD<=30%, then lower drawdown and a predeclared active-parameter order; sparse<5 closures remains a flag. Preserve every trial and prior fixed/ADX snapshots, separate optional neighborhood robustness, and disclose look-back/overfitting; no formal holdout, rolling-selector replacement, new provider or broader search |

### Basis and limits

This record follows the successive decisions of 2026-10-03 and 2026-10-04, including overseas-company inclusion, English project language, maximum-minute-history selection, fixed membership with the single US daily NKE-to-PYPL exception, accepted execution/scoring definitions, the later historical executable split/share basis and research account-state policies, and the separate cached-original25 daily pilot with its explicitly approved hypothetical assumptions, fixed interval and later ADX allocation comparison, reference-index reporting request and separately authorized bounded in-sample entry-arm grid. Later explicit decisions override earlier conflicts. Indicator, fee and tax values are model inputs, not guarantees of brokerage eligibility, personal tax treatment or profitability. Source verification does not establish that data extraction, implementation or backtest execution has occurred.

