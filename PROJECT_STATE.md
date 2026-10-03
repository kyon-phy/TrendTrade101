# Project state

This is a concise evidence index, not the strategy authority or a claim that the current HEAD is verified. The checkpoint below records an observed commit and its software-only result. Inspect actual HEAD and fresh evidence on every recovery.

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-03T15:57:45.844039+00:00",
  "verified_checkpoint": {
    "commit": "8d8dc82c29aa3d8fef18d3e8090335b6dc8f178a",
    "tests_passed": 82,
    "test_scope": "synthetic_software",
    "ci_url": "https://github.com/kyon-phy/TrendTrade101/actions/runs/37132449542",
    "artifact_name": "research-dashboard",
    "artifact_sha256": "2bca2b8a46c8e23d499aeaf29a565dc35e0f28952cb2a4b293e871d45dcd86da"
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
      "id": "network_allowlist",
      "status": "blocked",
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
    "Resolve pending technical conventions through the canonical configuration owner; preserve proposed status until then.",
    "Keep Yahoo access paused until normal environment allowlist authorization is resolved; never bypass the denial.",
    "After authorized connectivity and actual data audits, freeze data/configuration/code and holdout dates; run baseline before optimization.",
    "At each material milestone, reconcile this index with actual Git, CI, artifacts and run evidence."
  ]
}
```

## Read next

- [Repository-local continuity skill](.agents/skills/maintain-project-context/SKILL.md) and [decision log](docs/decisions.md).
- [Approved-rule public projection](config/inputs/TrendTrade101_Backtest_Configuration.md) and [original/public provenance](config/inputs/public_input_provenance.json).
- [Pending technical bundle and JP alternative](docs/technical-conventions-v013.md), [network blocker](docs/network-access.md), and [data/run contract](docs/data-and-runs.md).
- [Checkpoint CI and downloadable dashboard](https://github.com/kyon-phy/TrendTrade101/actions/runs/37132449542). HTML is a timestamped snapshot; no public live URL is verified. Local port availability must be checked after environment restarts.

No historical baseline, optimization or final-holdout result is claimed. The original input bytes were not verified here; the public derivatives were. No stock reselection is authorized.
