# TrendTrade101

Auditable US and Japan trend-strategy research with a read-only progress console.

For continued work, start with [PROJECT_STATE.md](PROJECT_STATE.md), [AGENTS.md](AGENTS.md) and the [repository-local continuity skill](.agents/skills/maintain-project-context/SKILL.md). The state file is a short evidence index; recover actual Git/CI/data status before relying on it.

**Current state:** the authorized public input derivatives are verified: 201 memberships, 127 unique securities and the approved PYPL substitution. Canonical configuration v0.15 retains approved accounting and adds an isolated existing-25 cached-daily FULL baseline pilot. Its private data and applicable evidence have not yet been supplied to this executor. The implementation has synthetic regression coverage; remaining technical conventions and actual data audits still gate real execution. The latest parent-observed Yahoo preflight returned HTTP 429 despite effective hostname authorization; its limiting layer is unknown. No historical baseline, optimization or final-holdout returns have been calculated.

## Open the console

Python 3.11 or newer is sufficient; the project has no runtime dependencies.

```bash
cd /workspace/TrendTrade101
python3 -m trendtrade101 dashboard --host 127.0.0.1 --port 8765
```

The live console listens at `http://127.0.0.1:8765` inside the saved cloud environment. A user-facing cloud port preview must be provided by that environment; this local address is not a public URL. No public live deployment is configured.

For a server-free view, open the latest successful [Tests workflow run](https://github.com/kyon-phy/TrendTrade101/actions/workflows/tests.yml), download its `research-dashboard` artifact, unzip it and open `TrendTrade101_Dashboard.html`. This self-contained HTML is a timestamped snapshot; it works without installation or a server. CI exports only status and permitted summaries, and does not fetch prices or run historical research.

The console refreshes actual prerequisite status every five seconds. It never displays synthetic test values as strategy results. Its HTTP server exposes only its own UI files and a status endpoint; private files and raw vendor data are not served.

## Verify the implementation

```bash
python3 scripts/check.py
python3 -m trendtrade101 status
python3 -m trendtrade101 verify-inputs
python3 -m trendtrade101 export-dashboard --output .private/export/TrendTrade101_Dashboard.html
```

Input verification succeeds for the published derivatives. Real research commands require an immutable, audited local dataset and a frozen plan; see the [ordered command sequence](docs/data-and-runs.md). Calling `baseline` without a dataset reports the current blockers and returns exit code 2. Synthetic tests do not unlock actual-data execution.

## Research scope

Each market, stock basket and frequency is an independent experiment. US accounts start with USD 100,000; JP accounts start with JPY 16,000,000. The primary comparison retains five entry arms with fixed initial-capital 1/15 sizing. SMA 5/20, MACD 12/26/9, ADX 14/25, three positive histogram increments, N5 and a 40% positive-hump drawdown are the baseline.

Minute orders use the first eligible observed Open after signal-bar completion plus a fixed 20 minutes. Daily signals use the next session Open. Completed bars and past-only state are required. Pyramiding, aggregate stock exits, reservation and sell-before-buy processing are represented in the replay core.

The last complete minute week and daily month remain sealed. Minute training/test windows are two weeks/one week; daily windows are six months/one month. The bounded grids contain 3, 3, 9, 9 and 27 candidates for the five respective arms. Maximum training drawdown is a selection constraint, not an account stop.

## Inputs and privacy

`config/inputs/` contains the authorized sanitized public projection, its provenance and separately pinned hashes. Its `public_derived` verification explicitly reports `original_bytes_verified: false`. The distinct `original_source` route uses the original hashes and supported private materialization under `.private/inputs/`. A failed public validation never silently falls back. Both routes check 201 membership rows, 127 unique market/ticker pairs, ordered groups and the single US daily NKE-to-PYPL substitution. No missing pool is reconstructed, and the canonical Library configuration remains authoritative.

Private source identities, credentials, conversations, third-party report bodies and vendor price caches must never be committed. `.private/`, `data/` and `runs/` are ignored. Data capture writes private content-addressed snapshots with retrieval metadata. A representative connectivity request failed with HTTP 403; no vendor price snapshot was obtained.

Frozen historical US baskets are user-fixed estimated subsets, not certified whole-market Top30. Applying later minute membership information to earlier July observations introduces selection look-ahead bias. Current-membership survivorship, excluded dividends, zero spread/slippage, conditional JP fees and simplified taxes remain explicit limitations.

See [architecture](docs/architecture.md), [execution definitions](docs/execution-definitions.md), [data and runs](docs/data-and-runs.md), [network access](docs/network-access.md) and [current blockers](docs/status.md).

The [v0.14 accounting synchronization](docs/accounting-v014.md) records the approved split/account policies and regression evidence. The [technical convention audit](docs/technical-conventions-v013.md) retains the remaining proposals, optional JP ADX sizing and data evidence still required before historical execution.

The [daily pilot input contract](docs/daily-pilot-contract.md) defines private handoff and audit fields. The dedicated pilot commands cannot optimize parameters or consume the formal holdout. Both formal and pilot execution remain locked pending their applicable evidence.
