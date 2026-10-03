# TrendTrade101

Auditable US and Japan trend-strategy research with a read-only progress console.

**Current state:** a tested research foundation, not a completed historical backtest. Canonical configuration v0.12 has been read. Exact input bytes are unavailable in this executor, accepted execution definitions await canonical synchronization, and real-data execution remains locked. No baseline, optimization or final-holdout returns have been calculated.

## Open the console

Python 3.11 or newer is sufficient; the project has no runtime dependencies.

```bash
cd /workspace/TrendTrade101
python3 -m trendtrade101 dashboard --host 127.0.0.1 --port 8765
```

Open the saved cloud environment's port 8765 preview at `http://127.0.0.1:8765`. If its preview requires listening on all interfaces, explicitly launch with `--host 0.0.0.0` and keep the preview private. No deployment or public dashboard is configured.

The console refreshes actual prerequisite status every five seconds. It never displays synthetic test values as strategy results. Its HTTP server exposes only its own UI files and a status endpoint; private files and raw vendor data are not served.

## Verify the implementation

```bash
python3 -m unittest discover -s tests -v
python3 -m trendtrade101 status
python3 -m trendtrade101 verify-inputs
python3 -m trendtrade101 baseline
```

The last two commands deliberately return exit code 2 while prerequisites are blocked. The baseline command is a readiness check in this revision; real-data orchestration is not enabled.

## Research scope

Each market, stock basket and frequency is an independent experiment. US accounts start with USD 100,000; JP accounts start with JPY 16,000,000. The primary comparison retains five entry arms with fixed initial-capital 1/15 sizing. SMA 5/20, MACD 12/26/9, ADX 14/25, three positive histogram increments, N5 and a 40% positive-hump drawdown are the baseline.

Minute orders use the first eligible observed Open after signal-bar completion plus a fixed 20 minutes. Daily signals use the next session Open. Completed bars and past-only state are required. Pyramiding, aggregate stock exits, reservation and sell-before-buy processing are represented in the replay core.

The last complete minute week and daily month remain sealed. Minute training/test windows are two weeks/one week; daily windows are six months/one month. The bounded grids contain 3, 3, 9, 9 and 27 candidates for the five respective arms. Maximum training drawdown is a selection constraint, not an account stop.

## Inputs and privacy

The exact four delegated input files belong in `.private/inputs/` after supported materialization. The validator checks supplied SHA256 values, 201 membership rows, 127 unique market/ticker pairs, ordered manifest groups and the single US daily NKE-to-PYPL substitution. It does not reconstruct a missing pool.

Private source identities, credentials, conversations, third-party report bodies and vendor price caches must never be committed. `.private/`, `data/` and `runs/` are ignored. Data capture writes private content-addressed snapshots with retrieval metadata. No capture has yet been performed in this checkout.

Frozen historical US baskets are user-fixed estimated subsets, not certified whole-market Top30. Applying later minute membership information to earlier July observations introduces selection look-ahead bias. Current-membership survivorship, excluded dividends, zero spread/slippage, conditional JP fees and simplified taxes remain explicit limitations.

See [architecture](docs/architecture.md), [execution definitions](docs/execution-definitions.md) and [current blockers](docs/status.md).
