# TrendTrade101 working instructions

## Start or resume

1. Read [PROJECT_STATE.md](PROJECT_STATE.md) and the repository-local [maintain-project-context skill](.agents/skills/maintain-project-context/SKILL.md). This is a short index, not a replacement for source evidence.
2. Inspect the actual branch, HEAD, working tree and relevant files. Run `python3 scripts/project_context.py lint` and `python3 scripts/project_context.py recover`. Read only the linked decisions and technical sections needed for this task.
3. Before claiming remote/CI/artifact success, obtain fresh read-only observations for the exact commit. Missing access or evidence remains unverified. Do not fetch prices, rerun research or alter settings merely to recover context.
4. Approved strategy rules remain owned by the canonical configuration. The [public projection](config/inputs/TrendTrade101_Backtest_Configuration.md) and [provenance](config/inputs/public_input_provenance.json) identify its version and distinct hashes. A newer state note, code change or proposal cannot approve a rule. Resolve conflicts with the designated configuration owner; do not guess or apply automatic latest-wins precedence.

## During work and handoff

- Follow current user authorization. Do not repeat approvals already established, and do not infer new approval from an old handoff. Continue independent authorized work while a material question remains open.
- Apply the continuity skill after material decisions, implementation/test milestones, blockers/errors, scope changes and handoff. Do not guess context-window fullness or wait for an unavailable token-window detector.
- Update the concise state index and append decision/evidence records. Preserve superseded decisions with explicit links. Keep proposals, approvals, implementation and verification distinct; synthetic tests never establish historical performance.
- Record exact code/configuration/data hashes and result scope when results exist. A checked-in file cannot contain its own eventual commit hash: record the last externally observed verified checkpoint and inspect current HEAD separately.
- Run relevant checks, inspect the diff, commit/push only within authorization, then verify the remote commit and CI. Record a newly observed verification in a following checkpoint update when needed; do not invent success before CI finishes.
- Use English throughout repository content. Never commit credentials, personal information, private messages, private source/thread identifiers, internal reasoning, vendor caches or raw third-party reports. Public records use public paths/URLs and safe digests only.

This skill is local to this repository. It does not install a personal skill, create an automation, grant network access or authorize trading.
