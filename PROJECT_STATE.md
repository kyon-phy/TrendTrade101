# Project state

This is a concise evidence index, not the strategy authority or a claim that the current HEAD is verified. The checkpoint below records an observed commit and its software-only result. Inspect actual HEAD and fresh evidence on every recovery.

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-04T09:53:31.993143+00:00",
  "verified_checkpoint": {
    "commit": "c1be2216a79bc7127b61c0243ef375181e61a321",
    "tests_passed": 109,
    "test_scope": "synthetic_software",
    "ci_url": "https://github.com/kyon-phy/TrendTrade101/actions/runs/37184472204",
    "artifact_name": "research-dashboard",
    "artifact_sha256": "3075bb530ff62989b0790e673fe465cec59bb4b7369df5f8808281a11bd47d39"
  },
  "configuration": {
    "version": "v0.15",
    "public_path": "config/inputs/TrendTrade101_Backtest_Configuration.md",
    "public_sha256": "2a297ba5f2203ba278a2e6b905a5637aaf30ae50852b0101db15b344a61cd1e8",
    "source_sha256": "0d0c647363ae61fd3287ad4f6ac922a12510e2945358b6d3ff17158f460be1c0",
    "provenance_path": "config/inputs/public_input_provenance.json",
    "provenance_sha256": "281966ddc1daeca120326a8a66948fd8ea7b3b9ec7f241d6e26c8f823c3b6be2",
    "implementation_path": "config/baseline.json",
    "implementation_sha256": "11fd51dca3960df40a91412cfe56dc574be2b401cffcec6b01355defb1c39e70"
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
    },
    {
      "id": "pilot_private_input_and_evidence",
      "status": "pending",
      "evidence": "docs/daily-pilot-contract.md"
    }
  ],
  "pending_decisions": [
    "D014",
    "D003"
  ],
  "next_actions": [
    "Receive the private existing-25 cache using docs/daily-pilot-contract.md; preserve pending audit entries. No Yahoo requests or public price uploads.",
    "Complete price-basis, historical legal-lot, issuer/action evidence and remaining technical verification. Freeze eligible pilot dates and sequester the formal daily final month before any returns.",
    "Run the isolated FULL-only daily baseline after applicable gates pass. Do not optimize or consume the formal holdout.",
    "Obtain the requested pinned Ponytail text review through the coordinating owner; no Ponytail tool or skill is available in this executor."
  ],
  "pilot": {
    "scope": "existing_25_daily_FULL_fixed_baseline",
    "status": "not_run",
    "dataset_sha256": null,
    "exact_interval": "not_frozen",
    "formal_holdout_consumed": false,
    "evidence": "docs/daily-pilot-contract.md"
  }
}
```

## Read next

- [Repository-local continuity skill](.agents/skills/maintain-project-context/SKILL.md) and [decision log](docs/decisions.md).
- [Approved-rule public projection](config/inputs/TrendTrade101_Backtest_Configuration.md) and [original/public provenance](config/inputs/public_input_provenance.json).
- [Approved v0.14 accounting synchronization](docs/accounting-v014.md).
- [Remaining technical conventions and JP alternative](docs/technical-conventions-v013.md), [network blocker](docs/network-access.md), and [data/run contract](docs/data-and-runs.md).
- [Checkpoint CI and downloadable dashboard](https://github.com/kyon-phy/TrendTrade101/actions/runs/37184472204). HTML is a timestamped snapshot; no public live URL is verified. Local port availability must be checked after environment restarts.

No historical baseline, optimization or final-holdout result is claimed. The original input bytes were not verified here; the public derivatives were. No stock reselection is authorized.
