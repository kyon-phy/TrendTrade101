# Project state

This is a concise evidence index, not the strategy authority or a claim that the current HEAD is verified. The checkpoint below records an observed commit and its software-only result. Inspect actual HEAD and fresh evidence on every recovery.

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-04T07:02:11.496914+00:00",
  "verified_checkpoint": {
    "commit": "c1be2216a79bc7127b61c0243ef375181e61a321",
    "tests_passed": 109,
    "test_scope": "synthetic_software",
    "ci_url": "https://github.com/kyon-phy/TrendTrade101/actions/runs/37184472204",
    "artifact_name": "research-dashboard",
    "artifact_sha256": "3075bb530ff62989b0790e673fe465cec59bb4b7369df5f8808281a11bd47d39"
  },
  "configuration": {
    "version": "v0.14",
    "public_path": "config/inputs/TrendTrade101_Backtest_Configuration.md",
    "public_sha256": "48fa986f650168253d8eeff612178376f50eeeec0868efce0e83408f7f85f034",
    "source_sha256": "79c788ca74c3e21b3d56fbfe954f67d57817aa492e29b2b4fd06db08c2a3690d",
    "provenance_path": "config/inputs/public_input_provenance.json",
    "provenance_sha256": "3edc8ef764b276665cb488145e16fc2567da79a3eb5fe635569241959910d311",
    "implementation_path": "config/baseline.json",
    "implementation_sha256": "3a56dba5b787a11cd5e0017dd1377d7c36d92f49d8fc595cc3ebba952d949ab0"
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
    "D014",
    "D003"
  ],
  "next_actions": [
    "The three v0.14 split/account fields are approved and synchronized. Verify/freeze the remaining startup, gap, valuation and partial-window conventions with the canonical owner; do not reopen settled choices or enable real execution from synthetic tests.",
    "Keep this executor's Yahoo requests paused: parent preflight still returned HTTP 429 on October 4 despite effective hostname authorization. Dedicated preflight stays coordinated with the parent; the exact limiting layer remains unknown. See D011 and the network evidence receipt.",
    "After authorized connectivity and actual data audits, freeze data/configuration/code and holdout dates; run baseline before optimization.",
    "At each material milestone, reconcile this index with actual Git, CI, artifacts and run evidence."
  ]
}
```

## Read next

- [Repository-local continuity skill](.agents/skills/maintain-project-context/SKILL.md) and [decision log](docs/decisions.md).
- [Approved-rule public projection](config/inputs/TrendTrade101_Backtest_Configuration.md) and [original/public provenance](config/inputs/public_input_provenance.json).
- [Approved v0.14 accounting synchronization](docs/accounting-v014.md).
- [Remaining technical conventions and JP alternative](docs/technical-conventions-v013.md), [network blocker](docs/network-access.md), and [data/run contract](docs/data-and-runs.md).
- [Checkpoint CI and downloadable dashboard](https://github.com/kyon-phy/TrendTrade101/actions/runs/37184472204). HTML is a timestamped snapshot; no public live URL is verified. Local port availability must be checked after environment restarts.

No historical baseline, optimization or final-holdout result is claimed. The original input bytes were not verified here; the public derivatives were. No stock reselection is authorized.
