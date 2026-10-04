# Project state

This is a concise evidence index, not the strategy authority or a claim that the current HEAD is verified. The checkpoint below records an observed commit and its software-only result. Inspect actual HEAD and fresh evidence on every recovery.

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-04T10:04:46.659527+00:00",
  "verified_checkpoint": {
    "commit": "817134bd55e8b230bc95c189503107cf29a73868",
    "tests_passed": 118,
    "test_scope": "synthetic_software",
    "ci_url": "https://github.com/kyon-phy/TrendTrade101/actions/runs/37193649266",
    "artifact_name": "research-dashboard",
    "artifact_sha256": "607133c25382e8d643f583d732d3b989182945d00759cd6f0b67b6108210ab20"
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
      "status": "blocked",
      "evidence": "docs/daily-pilot-contract.md",
      "reason": "Current supported private transfer failed twice; no ZIP bytes present. Bounded retry exhausted."
    }
  ],
  "pending_decisions": [
    "D014",
    "D003"
  ],
  "next_actions": [
    "Resolve private input delivery with the coordinating owner. First supported Library transfer and one bounded retry failed; no further transfer fallback is authorized by this receipt.",
    "After readable bytes arrive, verify the expected ZIP hash and safely extract; prioritize actual-cache mechanical and indicator diagnostics. Preserve all pending economic audit entries.",
    "Complete price-basis, legal-lot, issuer/action evidence and remaining technical verification; sequester the formal daily final month before any returns. Run only the isolated FULL baseline after applicable gates pass.",
    "The coordinating owner reports the pinned Ponytail plain-text review of 817134bd55e8b230bc95c189503107cf29a73868 complete, with two optional reuse cleanups and no identified correctness issue. This executor has no direct review artifact; defer optional refactoring."
  ],
  "pilot": {
    "scope": "existing_25_daily_FULL_fixed_baseline",
    "status": "blocked_private_transfer",
    "dataset_sha256": null,
    "exact_interval": "not_frozen",
    "formal_holdout_consumed": false,
    "evidence": "docs/daily-pilot-contract.md",
    "input_package_sha256_expected": "68e795b24de5f6d0f3f32caa960c026f32b3d8a8389d68f9c77a615904f1d638",
    "input_bytes_verified": false,
    "diagnostics_run": false
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
