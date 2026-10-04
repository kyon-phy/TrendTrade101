# Existing-25 daily cache pilot

This is a separate exploratory fixed-baseline workflow, not the formal five-year,
127-security research plan. Its effective interval and technical conventions must
be recorded by the canonical configuration owner before real execution. The
v0.15 configuration records the FULL-only scope. Exact dates and remaining
technical/data verification are still pending; this document certifies no cache.

## Private input handoff

Provide a newly generated private ZIP with one `US/` and one `JP/` directory. Each
contains `capture.json`, `calendar.json`, the original captured Yahoo JSON files,
and local evidence files referenced by the review. No prices belong in public
Git, issue comments, review text or screenshots. Include the ZIP byte count and
SHA256 separately. Preserve the original files and per-file capture timestamps;
packaging today is not a new market-data retrieval.

The transfer may include incomplete reviews with explicit `pending` status and
reasons. Do not relabel them `verified` just to satisfy an importer. Intake and
mechanical OHLCV inspection are possible before economic audit completion;
normalization and performance replay remain blocked by missing required evidence.
Raw-price indicator arithmetic can be checked as software diagnostics only and
cannot establish executable-price signals or after-cost performance.

For a Library handoff, supply the new exact Library identity, current version,
filename and digest. The consuming executor uses the current supported Library
materialization helper with an executor-local private destination and verifies
readable bytes. A returned path in another workspace is not a transfer. If the
first transfer and one bounded supported retry fail, stop and report the blocker.
Do not substitute public Git or guessed download URLs. An explicitly supplied
uploaded-file attachment is another supported private input route; its attachment
identity must actually be provided, not inferred from a Library identity.

Alternatively, a completed normalized package can be handed off with
`dataset.json`, `bars.json`, `opens.json` and every hashed `source_snapshots` file.
It must use the dedicated pilot kind below, match the synchronized canonical hash,
and pass the same loader and execution gates. A ZIP transport digest does not
certify the data audit. The consumer still validates the contents locally.

## Capture manifest

Each market uses the existing `audit-local` capture shape documented in
[data-and-runs.md](data-and-runs.md), with these explicit pilot fields:

```json
{
  "research_scope": "exploratory_existing25_daily",
  "configuration_source_sha256": "<current canonical source SHA256>",
  "provider": "Yahoo",
  "market": "US",
  "frequency": "daily",
  "timezone": "America/New_York",
  "as_of": "<aware original evidence boundary>",
  "study_start": "<aware audited pilot start>",
  "calendar_file": "calendar.json",
  "calendar_sha256": "<SHA256>",
  "vendor_ohlc_basis": "<verified historical_unadjusted or split_adjusted_only>",
  "members": {},
  "splits": [],
  "unresolved_corporate_actions": [],
  "review": {},
  "evidence_files": []
}
```

- `members` must contain exactly the frozen `existing_25` members for that market:
  12 US and 13 Japan. No replacements or omission of an affected security.
- Each member records constant legal `lot`, `availability`, audited
  `first_trade_date`, source `file`, `sha256`, original aware `retrieved_at`, and
  `request` metadata. Missing/unavailable members need an explicit `reason`.
  An observed first cache bar is not automatically an issuer's listing date.
- Calendar sessions need aware `start`, `end`, `breaks`, `complete_from` and
  `complete_through`. Include evidence for holidays, US short sessions, Japan's
  session-hours change, and both original observation and scoring boundaries.
- `review` requires evidence-backed entries with `status: "verified"` for
  `calendar`, `timestamps`, `coverage`, `cache_scope`, `identity_and_ipo`,
  `price_adjustments`, `corporate_actions`, `historical_lots`, and `missing_data`.
  `cache_scope` verifies only the delivered cache's limits; it does not claim
  maximum accessible history or five-year coverage. Formal imports still require
  `maximum_history` instead and full frozen market/frequency membership.
- `evidence_files` entries contain relative `file` and `sha256`; referenced local
  evidence must be included. Review prose alone does not establish completion.
- Splits use `ticker`, aware effective `at`, and positive new-shares/old-shares
  `ratio`. Check every split reflected in vendor normalization through retrieval,
  including after the scoring cutoff if it affects earlier price units.
- Explicitly distinguish cash dividends (excluded by the approved model) from
  special distributions, spin-offs, mergers or unknown adjustment factors.
  Unknown actions remain unresolved. An affected market pilot pauses; it must
  not silently drop a constituent or declare an unknown action verified.
- Keep raw nulls and gaps. Do not forward-fill, synthesize pre-IPO observations,
  or substitute adjusted Close for executable OHLC. A pending final daily bar
  cannot generate a completed-Close signal.

## Isolation and outputs

The dedicated normalized kind is `yahoo_daily_pilot`. Formal research commands
reject it. Pilot plans and results live under `.private/pilots/`, use only the
FULL baseline with fresh separate market accounts, and offer no optimization or final
holdout command. Run dates, protected boundary, source/configuration/code/data
digests and actual coverage are frozen before any outcomes are calculated.

Only legitimate earlier observations warm indicators. Observations on or after
the protected boundary are excluded from replay, including Opens and actions.
Unfilled orders and residual positions remain disclosed, without invented end
fills. The pilot does not write a formal plan, selection or holdout registry.
Any future formal holdout must remain disjoint from the explored pilot interval.

```bash
python3 -m trendtrade101 audit-pilot-local --capture .private/pilot-input/US/capture.json --output .private/pilot-data/US
python3 -m trendtrade101 pilot-plan --dataset .private/pilot-data/US/dataset.json --run-dir .private/pilots/US-original25
python3 -m trendtrade101 pilot-baseline --dataset .private/pilot-data/US/dataset.json --run-dir .private/pilots/US-original25
```

Repeat independently for Japan. There is no override to run through a missing
audit, unresolved material action, unknown price basis or unverified pilot scope.

The dashboard labels these outputs **Exploratory daily pilot** and keeps formal
research stages unchanged. The current two-year cache description is a handoff
claim until the private bytes, calendar and evidence have been audited here.
