# Decision and evidence log

This incremental log begins with checked repository evidence and the current narrowly authorized workflow. It does not reconstruct earlier conversations. Approved rules remain in the canonical configuration; see [provenance](../config/inputs/public_input_provenance.json). Append corrections or superseding entries; retain prior records. Current recovery starts at [PROJECT_STATE.md](../PROJECT_STATE.md).

## D001

```json
{
  "id": "D001",
  "recorded_at": "2026-10-03T15:57:45.844039+00:00",
  "domain": "strategy",
  "status": "approved",
  "summary": "Index only the explicitly approved rules in canonical v0.13. Its proposed and verification-required rows retain their original status. Earlier history remains in that configuration changelog.",
  "evidence": [
    "config/inputs/TrendTrade101_Backtest_Configuration.md",
    "config/inputs/public_input_provenance.json"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D002

```json
{
  "id": "D002",
  "recorded_at": "2026-10-03T15:57:45.844039+00:00",
  "domain": "strategy",
  "status": "proposed",
  "summary": "Technical convention bundle remains pending canonical synchronization. Synthetic implementation/testing does not approve its startup, gap, valuation, account-state, window or share-unit choices.",
  "evidence": [
    "docs/technical-conventions-v013.md",
    "config/baseline.json"
  ],
  "pending_fields": [
    "indicator_initialization",
    "signal_gap_policy",
    "valuation_cadence",
    "fold_account_state",
    "final_account_state",
    "partial_window_policy",
    "split_lot_basis"
  ],
  "supersedes": null
}
```

## D003

```json
{
  "id": "D003",
  "recorded_at": "2026-10-03T15:57:45.844039+00:00",
  "domain": "strategy",
  "status": "proposed",
  "summary": "JP ADX base remains an optional-branch proposal; it does not block the selected fixed-allocation primary comparison. Legal historical units and actions require evidence rather than an invented default.",
  "evidence": [
    "docs/technical-conventions-v013.md",
    "config/baseline.json"
  ],
  "pending_fields": [
    "jp_scaled_base"
  ],
  "supersedes": null
}
```

## D004

```json
{
  "id": "D004",
  "recorded_at": "2026-10-03T15:57:45.844039+00:00",
  "domain": "data",
  "status": "blocked",
  "summary": "Recorded Yahoo CONNECT denial and unfinished data audit persist. No price retries, security-setting changes or alternative data route are authorized by context recovery.",
  "evidence": [
    "docs/network-access.md",
    "config/project_status.json"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D005

```json
{
  "id": "D005",
  "recorded_at": "2026-10-03T15:45:31+00:00",
  "domain": "workflow",
  "status": "approved",
  "summary": "Explicit project-owner authorization: implement repository-local continuity skill and concise evidence records, update at material milestones, verify on recovery, and commit/push. This changes no strategy, membership, canonical configuration or personal skill registry.",
  "evidence": [
    "AGENTS.md",
    ".agents/skills/maintain-project-context/SKILL.md"
  ],
  "authorization_basis": "Current explicit project-owner task authorization; no private transcript retained.",
  "pending_fields": [],
  "supersedes": null
}
```

## D006

```json
{
  "id": "D006",
  "recorded_at": "2026-10-03T15:57:45.844039+00:00",
  "domain": "software",
  "status": "verified",
  "summary": "Commit 8d8dc82c29aa3d8fef18d3e8090335b6dc8f178a passed 82 software tests and the linked CI; a dashboard snapshot artifact exists. This is not historical research verification.",
  "verification_scope": "synthetic_software",
  "evidence": [
    "https://github.com/kyon-phy/TrendTrade101/actions/runs/37132449542",
    "docs/technical-conventions-v013.md"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D007

```json
{
  "id": "D007",
  "recorded_at": "2026-10-03T16:06:46.028397+00:00",
  "domain": "workflow",
  "status": "implemented",
  "summary": "Repository-local continuity skill, concise state index, append-only decision records, read-only recovery and CI record checks implemented in ee743bb43c53c33784572a114a30bafe221e8e04. No personal registry installation or strategy change.",
  "evidence": [
    ".agents/skills/maintain-project-context/SKILL.md",
    "scripts/project_context.py",
    "tests/test_project_context.py"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D008

```json
{
  "id": "D008",
  "recorded_at": "2026-10-03T16:06:46.028397+00:00",
  "domain": "software",
  "status": "verified",
  "summary": "Commit ee743bb43c53c33784572a114a30bafe221e8e04 passed 93 local software tests; exact-head CI succeeded and its dashboard artifact was observed. A fresh read-only recovery matched remote HEAD and supplied CI/artifact observations. Historical research remains unexecuted.",
  "verification_scope": "synthetic_software",
  "evidence": [
    "https://github.com/kyon-phy/TrendTrade101/actions/runs/37135521443",
    "tests/test_project_context.py"
  ],
  "pending_fields": [],
  "supersedes": "D006"
}
```

## D009

```json
{
  "id": "D009",
  "recorded_at": "2026-10-03T17:07:38+00:00",
  "domain": "data",
  "status": "blocked",
  "summary": "Parent-observed preflights in a fresh environment after the user republished settings reached HTTP 429 at 15:59:42Z and again at 17:02:10Z on 2026-10-03. The second request was the one explicitly authorized delayed retry. Both returned Edge: Too Many Requests, server envoy, with no Retry-After. The exact limiting layer is unknown. No data, JP request or historical run resulted, and no further retry is authorized. This supersedes D004 as the current network blocker; the earlier executor CONNECT 403 remains historical evidence.",
  "observation_scope": "parent_observed_preflight",
  "evidence": [
    "docs/network-access.md"
  ],
  "pending_fields": [],
  "supersedes": "D004"
}
```

## D010

```json
{
  "id": "D010",
  "recorded_at": "2026-10-04T06:23:59+00:00",
  "domain": "workflow",
  "status": "approved",
  "summary": "Project-owner authorization permits autonomous ordinary reversible troubleshooting, tests and scoped publication. Consolidate genuinely material decisions; do not request repeated routine approvals. This does not approve pending strategy definitions, paid data, security changes, production-monitor changes, trades or duplicate provider requests. Dedicated Yahoo preflight stays with the parent.",
  "authorization_basis": "Current explicit project-owner task authorization; no private transcript retained.",
  "evidence": ["AGENTS.md", "docs/technical-conventions-v013.md"],
  "pending_fields": [],
  "supersedes": null
}
```

## D011

```json
{
  "id": "D011",
  "recorded_at": "2026-10-04T06:23:59+00:00",
  "domain": "data",
  "status": "blocked",
  "summary": "Parent-observed preflight at 2026-10-04T06:15:27Z, 13 hours 13 minutes 17 seconds after the previous retry, returned HTTP 429 with Edge: Too Many Requests and no Retry-After. Hostname authorization is effective; failure precedes price-data parsing. Exact limiting layer remains unknown. No data or historical result was obtained, and this executor made no duplicate request. Retain prior observations and keep dedicated preflight coordinated with the parent.",
  "observation_scope": "parent_observed_preflight",
  "evidence": ["docs/network-access.md", "config/project_status.json"],
  "pending_fields": [],
  "supersedes": "D009"
}
```

## D012

```json
{
  "id": "D012",
  "recorded_at": "2026-10-04T06:23:59+00:00",
  "domain": "software",
  "status": "implemented",
  "summary": "Preserve completed-Close valuations before simultaneous Opens; reconcile provider observations by their own timestamps; keep preflight success distinct from completed data auditing; expose bounded HTTP/connection diagnostics without retries. Synthetic regressions reproduce the omitted drawdown and stale-status failures. Canonical v0.13, fixed memberships, pending split/account decisions and the real-run lock remain unchanged.",
  "evidence": ["trendtrade101/engine.py", "trendtrade101/readiness.py", "trendtrade101/provider.py", "tests/test_execution_audit.py", "tests/test_status_observations.py", "tests/test_provider.py", "docs/technical-conventions-v013.md"],
  "pending_fields": [],
  "supersedes": null
}
```

## D013

```json
{
  "id": "D013",
  "recorded_at": "2026-10-04T06:55:27+00:00",
  "domain": "strategy",
  "status": "approved",
  "summary": "Canonical v0.14 records the explicit approval of historical executable split/share units and a pause for unverified special actions in affected runs; fresh training candidate accounts, continuous ordinary OOS accounts and separate fresh final baseline/selected accounts. Only split_lot_basis, fold_account_state and final_account_state changed approval status. No membership, execution/scoring or other technical proposal changed.",
  "approved_fields": [
    "split_lot_basis",
    "fold_account_state",
    "final_account_state"
  ],
  "evidence": [
    "config/inputs/TrendTrade101_Backtest_Configuration.md",
    "config/inputs/public_input_provenance.json",
    "docs/accounting-v014.md"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D014

```json
{
  "id": "D014",
  "recorded_at": "2026-10-04T06:55:27+00:00",
  "domain": "strategy",
  "status": "proposed",
  "summary": "The remaining technical bundle retains pending indicator initialization, valid-bar gap/startup handling, valuation/reporting cadence and partial-window treatment. D013 resolves only the split/account subset of D002. Synthetic implementation and verification do not approve the remaining conventions.",
  "evidence": [
    "docs/technical-conventions-v013.md",
    "config/baseline.json"
  ],
  "pending_fields": [
    "indicator_initialization",
    "signal_gap_policy",
    "valuation_cadence",
    "partial_window_policy"
  ],
  "supersedes": "D002"
}
```

## D015

```json
{
  "id": "D015",
  "recorded_at": "2026-10-04T06:55:27+00:00",
  "domain": "software",
  "status": "implemented",
  "summary": "Machine configuration and input pins are reconciled to the verified v0.14 public projection. Frozen plans validate/store account and split policies; affected special-action runs stop before replay without deleting members, while unaffected baskets retain the unresolved-event record. Split audit logs preserve aggregate cost and expose per-share cost. Added synthetic regressions for split equivalence, state validation, per-run action scope, independent training, carried OOS positions/orders/tax and separate warmed final accounts. Real execution remains locked.",
  "evidence": [
    "docs/accounting-v014.md",
    "config/baseline.json",
    "tests/test_approved_accounting.py",
    "trendtrade101/orchestration.py",
    "trendtrade101/dataset.py",
    "trendtrade101/portfolio.py"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D016

```json
{
  "id": "D016",
  "recorded_at": "2026-10-04T07:02:11.496914+00:00",
  "domain": "software",
  "status": "verified",
  "summary": "Implementation commit c1be2216a79bc7127b61c0243ef375181e61a321 synchronized the three approved v0.14 accounting fields and passed 109 software tests, including nine focused accounting regressions. Its exact-head CI succeeded and an unexpired research-dashboard artifact was observed. Public input hashes and all 201 memberships verified; original source bytes were not independently materialized here. Real research remains unexecuted and locked.",
  "verification_scope": "synthetic_software",
  "evidence": [
    "https://github.com/kyon-phy/TrendTrade101/actions/runs/37184472204",
    "docs/accounting-v014.md",
    "tests/test_approved_accounting.py"
  ],
  "pending_fields": [],
  "supersedes": "D008"
}
```

## D017

```json
{
  "id": "D017",
  "recorded_at": "2026-10-04T09:53:31.993143+00:00",
  "domain": "strategy",
  "status": "approved",
  "summary": "Canonical v0.15 authorizes only a separately labeled existing-25 cached-daily FULL baseline with fixed 1/15 allocation. Formal five-year and maximum-minute research, frozen memberships and untouched holdout remain unchanged. No fresh prices, optimization or holdout performance under this scope. Exact eligible dates and applicable audit/technical verification remain prerequisites.",
  "evidence": [
    "config/inputs/TrendTrade101_Backtest_Configuration.md",
    "config/inputs/public_input_provenance.json"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D018

```json
{
  "id": "D018",
  "recorded_at": "2026-10-04T09:53:31.993143+00:00",
  "domain": "software",
  "status": "implemented",
  "summary": "Added isolated daily-pilot import, plan, FULL baseline and dashboard labels. Pilot data cannot enter formal research, cannot write the formal holdout registry, and uses separate private run directories. Both execution flags remain false. Private inputs and the requested pinned Ponytail review remain unavailable in this executor.",
  "evidence": [
    "docs/daily-pilot-contract.md",
    "config/daily_pilot.json",
    "trendtrade101/pilot.py",
    "tests/test_daily_pilot.py"
  ],
  "pending_fields": [],
  "supersedes": null
}
```

## D019

```json
{
  "id": "D019",
  "recorded_at": "2026-10-04T10:04:46.659527+00:00",
  "domain": "software",
  "status": "verified",
  "summary": "Pilot implementation commit 817134bd55e8b230bc95c189503107cf29a73868 passed 118 synthetic software tests. Fresh read-only observations confirm exact-head CI success and an unexpired research-dashboard artifact. The coordinating owner separately reports its pinned Ponytail plain-text review complete, with no identified correctness issue and two optional reuse cleanups; the review artifact was not independently accessed here. No historical performance is verified.",
  "verification_scope": "synthetic_software",
  "evidence": [
    "https://github.com/kyon-phy/TrendTrade101/actions/runs/37193649266",
    "tests/test_daily_pilot.py",
    "docs/daily-pilot-contract.md"
  ],
  "pending_fields": [],
  "supersedes": "D016"
}
```

## D020

```json
{
  "id": "D020",
  "recorded_at": "2026-10-04T10:04:46.659527+00:00",
  "domain": "data",
  "status": "blocked",
  "summary": "The supplied private pilot ZIP was prepared through the current supported Library route, but the initial download and one bounded retry both returned download failed. Neither destination contains readable bytes. Expected size/hash are known, but package hash, extraction, actual-cache diagnostics and performance replay remain unverified/unexecuted. No generic downloader, public upload, Yahoo request or alternate route was attempted.",
  "evidence": [
    "docs/daily-pilot-contract.md"
  ],
  "pending_fields": [],
  "supersedes": null
}
```
