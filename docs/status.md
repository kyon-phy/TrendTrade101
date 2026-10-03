# Historical implementation checkpoint

Snapshot for commit `8d8dc82c29aa3d8fef18d3e8090335b6dc8f178a`. Start current recovery at [PROJECT_STATE.md](../PROJECT_STATE.md); this historical narrative is not an automatically current status or a competing authority.

## Complete

- Read canonical v0.13 in full and reconcile its accepted execution/scoring definitions.
- Safely integrate the separately authorized public input commit, verify pinned public hashes and provenance, and validate all 201 memberships, 127 unique securities and PYPL exception. This is public-derived verification, not original-byte verification.
- Implement causal indicators, delayed orders, reservations, whole lots, aggregate exits, tax accrual/refunds and split-aware state.
- Implement private offline audit packages, immutable data/configuration/code-bound plans, baseline-first execution, training-only bounded selection, continuous ordinary OOS accounts and a once-only final-holdout registry.
- Exercise that pipeline with deterministic synthetic fixtures, including poisoned future data, calendar boundaries, IPO identity guards, splits, cash accounting, no-fill diagnostics and holdout reuse prevention.
- Provide a read-only live console and self-contained HTML snapshot with actual prerequisite status and generated historical result rendering. Synthetic fixtures are excluded from research charts.
- Keep credentials, private source metadata, vendor caches and synthetic run output outside tracked project content.

## Blocked

The sole representative Yahoo request failed with `<urlopen error Tunnel connection failed: 403 Forbidden>`. Read-only policy inspection found a restricted HTTP allowlist without `query1.finance.yahoo.com`. Further affected requests stopped. The exact endpoint and normal setup requirement are in [network access](network-access.md). No network/security settings were modified, and no alternate data route was used.

Original Library files failed supported materialization, including bounded retries. The authorized public-derived route now supplies implementation inputs, while explicitly preserving the original-byte verification distinction.

Actual calendars, timestamp conventions, maximum accessible history, all-symbol gaps, IPO identities, corporate distributions, split basis and historical lots still need evidence-backed audit. Indicator initialization and related implementation conventions require canonical synchronization before real execution. The JP ADX-scaled base remains unresolved; the approved primary five-arm experiment uses fixed 1/15 sizing.

The SSH configuration rejects the supplied SSH remote. The existing HTTPS remote addresses the same authorized repository; system settings were not changed.

## Not performed

No real Yahoo dataset has been captured in this executor. No exact real holdout dates are frozen, and no real baseline, optimization, ordinary OOS or final-holdout result exists. Software tests demonstrate implementation behavior, not profitability or historical data quality. The real execution flag remains closed.

## Access and recovery

The [README](../README.md) documents the environment-local console and downloadable `research-dashboard` CI artifact. The exported HTML is a timestamped snapshot with no raw vendor data. Browser visual QA was blocked by the environment's Chromium sandbox configuration; HTTP behavior, JavaScript syntax and snapshot packaging were checked without disabling the sandbox.

After normal authorization of the requested Yahoo hostname, perform one read-only preflight, capture and audit the frozen members, synchronize remaining material implementation conventions, then freeze actual holdout dates and execute baseline before optimization. Do not remove audit guards simply to produce a result.
