---
name: maintain-project-context
description: Maintain and recover TrendTrade101 project continuity when starting or resuming work, after material decisions, implementation or verification milestones, errors, scope changes, and handoffs. Use concise repository records and current evidence without turning proposals or synthetic tests into approved strategy or historical results. Repository-local workflow only; not a personal skill installer.
---

# Maintain project context

## Recover progressively

1. Read the root [instructions](../../../AGENTS.md), [state index](../../../PROJECT_STATE.md), and only the referenced entries in [decisions](../../../docs/decisions.md). Read linked implementation/source sections as needed; do not load the entire history by default.
2. Run these read-only commands from the repository root:

   ```bash
   git status --short --branch
   git rev-parse HEAD
   python3 scripts/project_context.py lint
   python3 scripts/project_context.py recover
   ```

3. Compare the actual checkout and configuration hashes to the recorded checkpoint. A changed HEAD, dirty tree, missing source, expired artifact or conflicting handoff is a reason to reconcile evidence. It is not evidence that the newest prose is authoritative. Preserve existing work.
4. For remote claims, obtain fresh authorized read-only GitHub run and artifact metadata for the exact HEAD, plus the actual remote branch. The optional `recover --remote --observations <local-json>` route checks those observations without fetching source/data or modifying the checkout. See [record format](references/record-format.md). Without them it reports remote/CI/artifact evidence as unverified; the default never contacts a network service.
5. Separate what the record says, what exists in code, and what was verified. If evidence conflicts or a material decision is genuinely unresolved, identify the exact conflict and ask the responsible user/configuration owner while continuing independent authorized work. Do not rebuild missing membership or price history from conversation memory.

## Authority and evidence

- Current explicit user authorization controls task scope. Approved strategy rules remain in the canonical configuration, whose [public projection](../../../config/inputs/TrendTrade101_Backtest_Configuration.md) is identified by [provenance](../../../config/inputs/public_input_provenance.json). Preserve the original/public-byte distinction.
- [PROJECT_STATE.md](../../../PROJECT_STATE.md) is a concise index and observed checkpoint, not the sole authority, an approval ledger substitute, or a claim about current HEAD.
- [The technical memo](../../../docs/technical-conventions-v013.md) contains proposals and implementation findings. Implementation or passing tests do not approve those proposals. Synchronize accepted changes through the designated canonical writer before dependent real execution.
- Test, CI and artifact observations support only their declared code/version/scope. Synthetic software success cannot establish audited market coverage, baseline returns, optimization success or untouched-holdout performance. This continuity checker does not certify those outcomes.

## Update at material boundaries

Update after an actual decision, material code/test result, blocker/error, changed scope, or handoff. Do not continuously rewrite records for routine tool calls. No token-window detector or automatic background save is assumed.

1. Keep the state index within 12 KB: current verified checkpoint, authority/provenance hashes, research status, blockers, pending decision IDs, next actions and public evidence links. Link detail instead of copying it.
2. Append a small decision/evidence entry with a stable ID, time, domain, status, evidence and scope. Use `proposed`, `approved`, `implemented`, `verified`, or `blocked` accurately. An implementation may still correspond to an unapproved proposal. A later decision uses `supersedes` and leaves the previous entry intact. Do not reconstruct old history beyond checked sources.
3. For actual results record exact code commit, dataset digest, original/public configuration hashes, implementation digest, phase and a safe public summary path. Keep raw datasets private. Before asserting a historical result, use the project's actual data/plan/run verification, not this metadata checker.
4. Record current failures/blockers even if earlier work succeeded. Preserve the specific network denial until normal setup is authorized and verified; this workflow never retries Yahoo or changes security settings.
5. Run the validator and relevant tests. Inspect public-record privacy. Commit within existing authorization. After push, verify exact remote SHA, CI conclusion/head SHA, artifact existence/digest/expiry. Never predeclare those observations in the commit being checked.

A record commit can point to the preceding externally verified code commit; this avoids impossible self-referential hashes. Recovery always reports actual HEAD independently. Add a following checkpoint entry when new evidence is available rather than rewriting old evidence or entering an endless commit-hash update loop.

## Limits

The skill is instruction-driven and repository-local. It cannot guarantee perfect recall, detect context compaction in advance, install itself in a personal registry, authenticate arbitrary JSON receipts, or replace human interpretation of approval/source evidence. The deterministic checks validate declared structure, links, hashes and known contradictions; fresh remote observations still require the authorized read-only tools.
