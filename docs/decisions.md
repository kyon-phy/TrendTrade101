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
