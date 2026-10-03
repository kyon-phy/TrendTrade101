# Record format and recovery observations

`PROJECT_STATE.md` has one JSON block and short Markdown links. Required keys are enforced by `scripts/project_context.py`. Keep it below 12 KB. Never duplicate strategy tables there.

`docs/decisions.md` has one JSON block per entry. Minimal example:

```json
{
  "id": "D-next",
  "recorded_at": "<actual aware timestamp>",
  "domain": "strategy",
  "status": "proposed",
  "summary": "<short factual scope; no transcript>",
  "evidence": ["docs/technical-conventions-v013.md"],
  "pending_fields": ["indicator_initialization"],
  "supersedes": null
}
```

Domains: `strategy`, `workflow`, `software`, `data`. Statuses: `proposed`, `approved`, `implemented`, `verified`, `blocked`. Proposed strategy fields still listed as pending in machine configuration cannot be labeled approved/verified by this log. Approval requires a checked authoritative source; implementation and synthetic verification are separate claims. For a workflow-only approval, record its narrow authorization without private conversation content.

Append corrections/supersession records with evidence; do not overwrite prior entries. Existing pre-log strategy history remains in the canonical configuration changelog. If the log grows, use a linked archival file while preserving IDs, evidence and supersession relations; extend the validator before changing the log layout.

The validator compares retained JSON entries against available local Git history; CI checks out two commits for this purpose. Missing/shallow history cannot prove earlier preservation and is never fetched automatically by recovery. The check does not authenticate an approval or reconstruct an absent log.

Recovery observations are local, temporary JSON produced from fresh read-only tool results, not committed private tool dumps. Required shape:

```json
{
  "observed_at": "<actual UTC timestamp>",
  "remote_head_sha": "<actual 40-hex main SHA>",
  "ci": {
    "head_sha": "<actual 40-hex run SHA>",
    "conclusion": "success",
    "html_url": "https://github.com/kyon-phy/TrendTrade101/actions/runs/<actual-run-id>"
  },
  "artifacts": [{
    "name": "research-dashboard",
    "head_sha": "<actual workflow-run SHA>",
    "digest": "sha256:<actual 64-hex archive digest>",
    "expired": false
  }]
}
```

Use `python3 scripts/project_context.py recover --remote --observations <local-json>`. `--remote` only runs `git ls-remote origin refs/heads/main`; it does not fetch/rebase/write. Without it, a supplied remote value remains an observation, not an independently rechecked branch. CI/artifact JSON is checked for shape, commit agreement and freshness (one hour), but its origin is not authenticated by the script. Retrieve it using the existing authorized GitHub connection before relying on it. Do not invent missing fields or substitute a synthetic fixture.

Exit codes: lint returns 0 for structurally consistent records, 1 for problems. Recovery returns 0 only when the tree is clean and remote/CI/artifact observations match current HEAD; otherwise 2. Recovery never certifies historical research. A checkpoint older than HEAD remains explicitly identified; its test count is never copied onto HEAD.
