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
