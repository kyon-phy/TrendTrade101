# Project state

This is a concise evidence index, not the strategy authority or a claim that the current HEAD is verified. The checkpoint below records an observed commit and its software-only result. Inspect actual HEAD and fresh evidence on every recovery.

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-04T06:23:59+00:00",
  "verified_checkpoint": {
    "commit": "ee6ca122c38030b424615d4b85c7251192343215",
    "tests_passed": 93,
    "test_scope": "synthetic_software",
    "ci_url": "https://github.com/kyon-phy/TrendTrade101/actions/runs/37139453759",
    "artifact_name": "research-dashboard",
    "artifact_sha256": "f5ec949844b9346665306c4861e26f9f614bb6a09028a27dc8d4d01b9ff955b5"
  },
  "configuration": {
    "version": "v0.13",
    "public_path": "config/inputs/TrendTrade101_Backtest_Configuration.md",
    "public_sha256": "ea3038c311c00be7db448ee63ac7454c59f5ad91e88a38068c47ddad945a30b7",
    "source_sha256": "707cf2472d97d535061395a439fbe81764e9fec53b303edb88419d90c5553bce",
    "provenance_path": "config/inputs/public_input_provenance.json",
    "provenance_sha256": "18a38bbaa2817e1b295dd0c1cd0086ad66070c4a32d864a23eb73b0a4ecdcf38",
    "implementation_path": "config/baseline.json",
    "implementation_sha256": "074c2970507d7cc1221459023f2312fbb09ea2d65013db42bdf4ab09ce528654"
  },
  "research": {
    "dataset_sha256": null,
    "baseline": "not_run",
    "optimization": "not_run",
    "holdout": "not_run",
    "holdout_dates": "not_frozen"
  },
  "results": [],
  "blockers": [
    {
      "id": "yahoo_http_429",
      "status": "blocked",
      "observation_scope": "parent_observed_preflight",
      "latest_observed_at": "2026-10-04T06:15:27Z",
      "executor_retry_authorized": false,
      "preflight_coordination": "Parent owns dedicated preflight; no duplicate requests from this executor.",
      "evidence": "docs/network-access.md"
    },
    {
      "id": "data_audit",
      "status": "not_complete",
      "evidence": "docs/data-and-runs.md"
    },
    {
      "id": "technical_sync",
      "status": "pending",
      "evidence": "docs/technical-conventions-v013.md"
    }
  ],
  "pending_decisions": [
    "D002",
    "D003"
  ],
  "next_actions": [
    "Consolidate material split/share-unit and training/OOS/final-account choices through the canonical owner. Continue ordinary offline implementation verification without repeated routine approvals; pending strategy definitions remain pending.",
    "Keep this executor's Yahoo requests paused: parent preflight still returned HTTP 429 on October 4 despite effective hostname authorization. Dedicated preflight stays coordinated with the parent; the exact limiting layer remains unknown. See D011 and the network evidence receipt.",
    "After authorized connectivity and actual data audits, freeze data/configuration/code and holdout dates; run baseline before optimization.",
    "At each material milestone, reconcile this index with actual Git, CI, artifacts and run evidence."
  ]
}
```

## Read next

- [Repository-local continuity skill](.agents/skills/maintain-project-context/SKILL.md) and [decision log](docs/decisions.md).
- [Approved-rule public projection](config/inputs/TrendTrade101_Backtest_Configuration.md) and [original/public provenance](config/inputs/public_input_provenance.json).
- [Pending technical bundle and JP alternative](docs/technical-conventions-v013.md), [network blocker](docs/network-access.md), and [data/run contract](docs/data-and-runs.md).
- [Checkpoint CI and downloadable dashboard](https://github.com/kyon-phy/TrendTrade101/actions/runs/37139453759). HTML is a timestamped snapshot; no public live URL is verified. Local port availability must be checked after environment restarts.

No historical baseline, optimization or final-holdout result is claimed. The original input bytes were not verified here; the public derivatives were. No stock reselection is authorized.
