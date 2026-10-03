# TrendTrade101 Frozen Membership Manifest

Publication: sanitized public projection. Membership and order are unchanged. See public_input_provenance.json for source and published SHA256 checksums. The public CSV omits one nonessential source-URL tracking parameter.

Fixed by user choice: 2026-10-03 12:57:28 UTC. There are 201 membership records. Relative to the delivered 12:16 UTC review, the only change is the explicitly approved US daily NKE-to-PYPL substitution at 13:07:06 UTC. All other members and their order remain unchanged.

## Operative files

- frozen_universe_members.csv: current frozen membership and interpretation
- frozen_universe_manifest.json: exact ordered groups, audit hashes, and data-window caveats
- frozen_review_source_201.csv: original reviewed-source snapshot, referenced for historical provenance only and not bundled in these public inputs

## Group counts

| Market | Universe | Frequency | Members |
|---|---|---|---:|
| US | existing_25 | daily_and_5m | 12 |
| US | sector_28 | daily_and_5m | 28 |
| JP | existing_25 | daily_and_5m | 13 |
| JP | sector_28 | daily_and_5m | 28 |
| JP | historical_30_user_fixed | daily | 30 |
| JP | historical_30_user_fixed | 5m | 30 |
| US | historical_30_user_fixed | daily | 30 |
| US | historical_30_user_fixed | 5m | 30 |

## Important limitations

The US historical baskets are now user-fixed provisional selections, not a claim of certified full-market Top30 membership. The PayPal correction is applied only as that explicit one-for-one exception; it does not authorize any other reranking. The June JPX reconstruction and July US rebasing remain audit-only.

Maximum actual Yahoo5m history remains selected. Representative starts are July10 for NVDA and July6 for6857.T; those two probes do not establish full-universe coverage. Because the retained minute lists originally referenced later selection dates, earlier data are subject to selection/look-ahead bias. That limitation must remain in the configuration and reports.

Data coverage, nulls, session boundaries, closing-auction/terminal points, IPO history, and corporate actions still need implementation audit. Such findings must not silently change membership. No strategy engine, baseline, optimization, or Git action was executed by this freeze.

Source review SHA256: 8697391da85799675eff3027c58f6982c73a8969babe2167fcaaae1582536cf5

## Approved exception

US daily historical basket only: NKE is replaced by PYPL. The source review remains unchanged as an audit snapshot. The new member occupies the previous display slot; no new market-cap display rank is assigned. PayPal evidence: [SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1633917/000163391721000149/pypl-20210630.htm) and [filing index](https://www.sec.gov/Archives/edgar/data/1633917/000163391721000149/0001633917-21-000149-index.html), filed 2021-07-29.
