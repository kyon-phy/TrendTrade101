# Local data audit and research runs

## Input routes

`verify-inputs` chooses `config/inputs/` as the explicit `public_derived` route when that directory is present. It verifies the four published hashes and the pinned provenance document, source-to-public hash mapping, file sizes, manifest CSV checksum, 201 ordered memberships, 127 unique market/ticker pairs and the PYPL exception. Its report sets `original_bytes_verified: false`.

Without that public directory, `.private/inputs/` uses the distinct `original_source` route and the original hashes. A failed public check never silently falls back. The canonical Library record remains authoritative. No original source bytes or price caches are reconstructed from displayed text.

## Private capture package

The latest parent-observed request still returned HTTP 429 despite effective hostname authorization; see [network evidence](network-access.md). The code does not fetch Yahoo from CI or another environment.

`audit-local` reads existing captured JSON files. Its capture manifest contains:

- Provider, market, frequency, exchange timezone, aware retrieval/as-of timestamp and an explicitly audited `study_start` distinct from warmup history. The daily boundary must implement the approved five-year target; the minute boundary cannot discard earlier audited accessible history.
- A calendar file and SHA256, covering all sessions from `complete_from` through `complete_through`, including lunch, auctions and short sessions.
- Every frozen market/frequency member with lot, dataset availability, reason for missing history, issuer's first trade date, source file, SHA256, retrieval timestamp and request parameters.
- Verified split events with symbol, effective timestamp and ratio; an explicitly reviewed vendor OHLC basis.
- Evidence-backed review entries for calendar, timestamps, coverage, maximum accessible history, issuer/IPO identity, price adjustments, corporate actions, historical lots and missing data.
- An explicit unresolved-corporate-action list, with frozen ticker and event type for each known unresolved economic treatment. Every affected run is blocked before replay; unrelated baskets may be prepared without deleting the member or event. Unidentified events fail package validation. Fractional split entitlements still block affected execution.

Availability is a dataset-wide audit statement, not permission to remove earlier history because a security is currently halted. An issuer's earlier ticker reuse is never spliced into its history.

```bash
python3 -m trendtrade101 audit-local \
  --capture .private/captures/capture.json \
  --output .private/datasets/us-5m
```

The resulting package retains raw snapshots privately, normalized bars, independently stored executable Opens, immutable hashes, per-symbol diagnostics, actual complete sessions and eligible period ends. A valid Open does not depend on the eventual High, Low, Close or volume. Incomplete retrieval-time bars are excluded from signals, while an Open already observed by that file's retrieval timestamp can remain usable. Missing observations remain missing. Terminal quotes and auction/lunch intervals are excluded according to the audited calendar, not a universal hardcoded assumption.

Historical executable prices use historical share units. If vendor OHLC is verified split-only normalized, audited split factors restore historical executable prices. At each effective split, indicator price state is rescaled and held/pending share quantities are adjusted consistently, preserving notional. Pending quantities round down to their legal unit; fractional or odd-lot held entitlements block the current model. Dividend-adjusted fields are rejected. Non-cash distributions require a separately resolved model; they are not silently converted to losses, dividends or cash. The current loader requires evidence for a constant legal unit over the sample and rejects time-varying lot metadata instead of discarding it.

## Ordered research commands

```bash
python3 -m trendtrade101 plan --dataset .private/datasets/us-5m/dataset.json --run-dir .private/runs/us-5m-existing --universe existing_25
python3 -m trendtrade101 baseline --dataset .private/datasets/us-5m/dataset.json --run-dir .private/runs/us-5m-existing
python3 -m trendtrade101 optimize --dataset .private/datasets/us-5m/dataset.json --run-dir .private/runs/us-5m-existing
python3 -m trendtrade101 freeze-final --dataset .private/datasets/us-5m/dataset.json --run-dir .private/runs/us-5m-existing
python3 -m trendtrade101 holdout --dataset .private/datasets/us-5m/dataset.json --run-dir .private/runs/us-5m-existing
```

These commands exist and are tested using deterministic synthetic fixtures. They are not evidence that any of the shown real datasets exists. Real execution also requires completed configuration/implementation verification; `execution_ready` remains false until those prerequisites are actually satisfied.

Plans bind the configuration, implementation and dataset digests before outcomes. Candidate choices are written before their subsequent test segment. Baseline completion is required before optimization. Training accounts start flat; ordinary OOS folds retain cash, tax ledger and residual positions, while entry targets still use fixed initial capital. If no candidate is eligible, no new positions are opened during that fold; prior pending/residual risk remains managed and reported.

The currently proposed window convention requires whole calendar windows. Weeks start Monday and months start on day one. Audited calendar coverage recognizes a holiday/weekend at the period start; an initial partial trading session cannot qualify as a full leading window. Partial leading/trailing periods are excluded. Legitimate earlier observations only warm up indicators and event state. Signal age counts observed valid bars; missing bars are not fabricated. Canonical v0.14 approves separate fresh initial-capital flat final accounts, with no inherited positions, orders, reservations or tax state. Final returns are not a continuation of the ordinary OOS ledger.

SMA-seeded EMA and Wilder ADX are explicit implementation conventions. Equity is marked at observed Opens/Closes and scheduled events. Bar-end volume cannot determine an earlier Open fill. Open quotes remain execution proxies, with zero modeled spread/slippage and no guarantee of actual market liquidity.

Final choices use only the immediately preceding training window. Before final returns are computed, consumption is recorded atomically. Real holdout reuse is prevented across run directories by a registry keyed to market, frequency, basket and interval. Failed final runs remain consumed. Changes to code, configuration or data invalidate existing frozen plans.

## Interface and audit trail

Each run writes a plan, progress, baseline outputs, per-fold training scores, frozen selections, test outputs and any final results. The dashboard reads generated results and excludes all `synthetic_fixture` datasets from historical charts.

```bash
python3 -m trendtrade101 dashboard --port 8765
python3 -m trendtrade101 export-dashboard --output .private/export/TrendTrade101_Dashboard.html
```

The HTML export is self-contained, includes a capture timestamp and works without the Python server. It is a snapshot, not a continuously connected cloud dashboard. The CI workflow publishes this file as its `research-dashboard` artifact after tests pass. Raw vendor data is never included.

Gross, after-fee and after-tax views reconcile costs on the same actual trade path. They are not independent reinvestment simulations. Trade counts mean complete aggregate position closures. Current residual positions, missing fills and sparse samples remain visible. A positive histogram hump whose preceding nonpositive boundary is unavailable is flagged without inventing its earlier peak. See [the implementation audit and decision memo](technical-conventions-v013.md) for the exact remaining proposals and evidence requirements.

The [v0.14 accounting record](accounting-v014.md) describes executable units, per-run special-action gates and fresh/continuous account policies. The original/public provenance file retains the handoff-time synchronization status; current implementation evidence belongs in this record and the append-only decision log.
