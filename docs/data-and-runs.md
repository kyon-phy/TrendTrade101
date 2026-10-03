# Local data audit and research runs

## Input routes

`verify-inputs` chooses `config/inputs/` as the explicit `public_derived` route when that directory is present. It verifies the four published hashes and the pinned provenance document, source-to-public hash mapping, file sizes, manifest CSV checksum, 201 ordered memberships, 127 unique market/ticker pairs and the PYPL exception. Its report sets `original_bytes_verified: false`.

Without that public directory, `.private/inputs/` uses the distinct `original_source` route and the original hashes. A failed public check never silently falls back. The canonical Library record remains authoritative. No original source bytes or price caches are reconstructed from displayed text.

## Private capture package

The network blocker must be resolved through authorized environment setup. The code does not fetch Yahoo from CI or another environment.

`audit-local` reads existing captured JSON files. Its capture manifest contains:

- Provider, market, frequency, exchange timezone and aware retrieval/as-of timestamp.
- A calendar file and SHA256, covering all sessions through its declared `complete_through` date, including lunch, auctions and short sessions.
- Every frozen market/frequency member with lot, dataset availability, reason for missing history, issuer's first trade date, source file, SHA256, retrieval timestamp and request parameters.
- Verified split events with symbol, effective timestamp and ratio; an explicitly reviewed vendor OHLC basis.
- Evidence-backed review entries for calendar, timestamps, coverage, maximum accessible history, issuer/IPO identity, price adjustments, corporate actions, historical lots and missing data.
- An empty unresolved-corporate-action list. Unknown distributions or fractional split entitlements block execution.

Availability is a dataset-wide audit statement, not permission to remove earlier history because a security is currently halted. An issuer's earlier ticker reuse is never spliced into its history.

```bash
python3 -m trendtrade101 audit-local \
  --capture .private/captures/capture.json \
  --output .private/datasets/us-5m
```

The resulting package retains raw snapshots privately, normalized bars, immutable hashes, per-symbol diagnostics, actual complete sessions and eligible period ends. Incomplete retrieval-time bars are excluded. Missing observations remain missing. Terminal quotes and auction/lunch intervals are excluded according to the audited calendar, not a universal hardcoded assumption.

Historical executable prices use historical share units. If vendor OHLC is verified split-only normalized, audited split factors restore historical executable prices. At each effective split, indicator price state is rescaled and held/pending share quantities are adjusted consistently, preserving notional. Dividend-adjusted fields are rejected. Non-cash distributions and fractional entitlements require a separately resolved model; they are not silently converted to losses, dividends or cash.

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

Whole calendar windows are required. Weeks start Monday and months start on day one. Partial leading/trailing periods are excluded. Legitimate earlier observations only warm up indicators and event state. Signal age counts observed valid bars; missing bars are not fabricated.

SMA-seeded EMA and Wilder ADX are explicit implementation conventions. Equity is marked at observed Opens/Closes and scheduled events. Bar-end volume cannot determine an earlier Open fill. Open quotes remain execution proxies, with zero modeled spread/slippage and no guarantee of actual market liquidity.

Final choices use only the immediately preceding training window. Before final returns are computed, consumption is recorded atomically. Real holdout reuse is prevented across run directories by a registry keyed to market, frequency, basket and interval. Failed final runs remain consumed. Changes to code, configuration or data invalidate existing frozen plans.

## Interface and audit trail

Each run writes a plan, progress, baseline outputs, per-fold training scores, frozen selections, test outputs and any final results. The dashboard reads generated results and excludes all `synthetic_fixture` datasets from historical charts.

```bash
python3 -m trendtrade101 dashboard --port 8765
python3 -m trendtrade101 export-dashboard --output .private/export/TrendTrade101_Dashboard.html
```

The HTML export is self-contained, includes a capture timestamp and works without the Python server. It is a snapshot, not a continuously connected cloud dashboard. The CI workflow publishes this file as its `research-dashboard` artifact after tests pass. Raw vendor data is never included.

Gross, after-fee and after-tax views reconcile costs on the same actual trade path. They are not independent reinvestment simulations. Trade counts mean complete aggregate position closures. Current residual positions, missing fills and sparse samples remain visible.
