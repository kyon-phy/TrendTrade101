"""Load immutable, private local datasets and validate audit receipts.

This module performs no network requests. An audit receipt is evidence of
completed review, not a switch that invents provider coverage.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date,datetime
from hashlib import sha256 as hash_bytes
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from math import isfinite
from .engine import Bar,OpenQuote
from .inputs import EXPECTED,project_members,symbols_for
from .storage import sha256
from .timing import Session

REQUIRED_AUDITS=("calendar","timestamps","coverage","maximum_history","identity_and_ipo",
                 "price_adjustments","corporate_actions","historical_lots","missing_data")
PILOT_SCOPE="exploratory_existing25_daily"
PILOT_KIND="yahoo_daily_pilot"
PILOT_AUDITS=tuple("cache_scope" if k=="maximum_history" else k for k in REQUIRED_AUDITS)

def dataset_members(root: Path, manifest: dict, *, pilot=False) -> set[str]:
    rows=project_members(root)
    if pilot:
        if manifest.get("research_scope")!=PILOT_SCOPE or manifest.get("frequency")!="daily":
            raise ValueError("Pilot scope must be existing-25 daily only")
        return set(symbols_for(rows,manifest["market"],"existing_25","daily"))
    return {r["ticker"] for r in rows if r["market"]==manifest["market"]
            and r["frequency"] in (manifest["frequency"],"daily_and_5m")}

def fingerprint(value) -> str:
    return hash_bytes(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def unresolved_action_symbols(manifest: dict) -> set[str]:
    """Keep unresolved economics explicit; never silently discard a member."""
    actions=manifest.get("unresolved_corporate_actions",[])
    if not isinstance(actions,list):
        raise ValueError("Unresolved corporate actions require an explicit event list")
    for action in actions:
        if not isinstance(action,dict) or action.get("ticker") not in manifest["members"] or not action.get("type"):
            raise ValueError("Unresolved corporate action must identify a frozen ticker and event type")
    return {action["ticker"] for action in actions}

@dataclass
class Dataset:
    manifest: dict
    digest: str
    bars: list[Bar]
    sessions: list[Session]
    source_path: Path
    open_quotes: list[OpenQuote] | None = None

    @property
    def kind(self): return self.manifest["kind"]
    @property
    def frequency(self): return self.manifest["frequency"]
    @property
    def market(self): return self.manifest["market"]

def load_dataset(root: Path, path: Path, *, allow_synthetic=False, allow_pilot=False) -> Dataset:
    manifest=json.loads(path.read_text())
    kind=manifest.get("kind")
    pilot=kind in (PILOT_KIND,"synthetic_pilot_fixture")
    if pilot and not allow_pilot:
        raise ValueError("Pilot datasets require the isolated pilot route; formal research is prohibited")
    if kind in ("synthetic_fixture","synthetic_pilot_fixture"):
        if not allow_synthetic:
            raise ValueError("Synthetic data requires the explicit synthetic fixture route")
    elif kind not in ("yahoo_audited",PILOT_KIND):
        raise ValueError("Unrecognized audited dataset kind")
    if manifest["configuration_source_sha256"] != EXPECTED["TrendTrade101_Backtest_Configuration.md"]:
        raise ValueError("Dataset audit targets a different canonical configuration")
    if manifest["frequency"] not in ("daily","5m") or manifest["market"] not in ("US","JP"):
        raise ValueError("Invalid market/frequency")
    selected=dataset_members(root,manifest,pilot=pilot)
    symbols=set(manifest["members"])
    if symbols != selected:
        raise ValueError("Dataset must account for every frozen market/frequency member")
    unresolved_action_symbols(manifest)
    if manifest["price_basis"]!="historical_unadjusted_split_events":
        raise ValueError("Unsupported price/quantity basis; do not silently use dividend-adjusted prices")
    if not manifest.get("calendar_complete_through"):
        raise ValueError("Full calendar coverage must be recorded")
    if kind in ("yahoo_audited",PILOT_KIND):
        if not manifest.get("calendar_complete_from") or not manifest.get("study_start"):
            raise ValueError("Real packages require explicit calendar coverage and study-start boundaries")
        if not datetime.fromisoformat(manifest["study_start"]).tzinfo:
            raise ValueError("Study-start boundary must include a timezone")
        receipt=manifest.get("audit",{})
        if any(receipt.get(k,{}).get("status")!="verified" or not receipt[k].get("evidence")
               for k in (PILOT_AUDITS if pilot else REQUIRED_AUDITS)):
            raise ValueError("Incomplete data audit receipt")
        if manifest.get("provider")!="Yahoo" or not manifest.get("source_snapshots"):
            raise ValueError("Missing Yahoo snapshot provenance")
        available={t for t,m in manifest["members"].items() if m["availability"]=="available"}
        captured={s.get("ticker") for s in manifest["source_snapshots"] if s.get("ticker")}
        if available!=captured:
            raise ValueError("Snapshot inventory differs from available frozen members")
        if any(not m.get("first_trade_date") for m in manifest["members"].values()):
            raise ValueError("Audited issuer first-trade dates are required")
    sources=[]
    for source in manifest.get("source_snapshots",[]):
        target=(path.parent/source["file"]).resolve()
        if not target.is_relative_to(path.parent.resolve()) or sha256(target)!=source["sha256"]:
            raise ValueError("Source snapshot path/hash mismatch")
        sources.append(source["sha256"])
    payload_path=(path.parent/manifest["bars_file"]).resolve()
    if not payload_path.is_relative_to(path.parent.resolve()) or sha256(payload_path)!=manifest["bars_sha256"]:
        raise ValueError("Dataset bars hash mismatch")
    bars=[]
    for row in json.loads(payload_path.read_text()):
        record=dict(row)
        for field in ("start","end","entry_cutoff"):
            record[field]=datetime.fromisoformat(record[field]) if record.get(field) else None
        bars.append(Bar(**record))
    if any(b.ticker not in symbols for b in bars):
        raise ValueError("Data contains a security outside frozen membership")
    if kind in ("yahoo_audited",PILOT_KIND) and not manifest.get("opens_file"):
        raise ValueError("Real packages require independent executable Open observations")
    if manifest.get("opens_file"):
        quote_path=(path.parent/manifest["opens_file"]).resolve()
        if not quote_path.is_relative_to(path.parent.resolve()) or sha256(quote_path)!=manifest["opens_sha256"]:
            raise ValueError("Executable Open path/hash mismatch")
        quotes=[OpenQuote(q["ticker"],datetime.fromisoformat(q["start"]),q["open"]) for q in json.loads(quote_path.read_text())]
    else:
        quotes=[OpenQuote(b.ticker,b.start,b.open) for b in bars]
    sessions=[Session(s["market"],datetime.fromisoformat(s["start"]),datetime.fromisoformat(s["end"]),
                      tuple((datetime.fromisoformat(a),datetime.fromisoformat(b)) for a,b in s.get("breaks",[])))
              for s in manifest["sessions"]]
    if not sessions or not bars:
        raise ValueError("Dataset contains no audited sessions/bars")
    lookup={(s.start,s.end):s for s in sessions}
    if len(lookup)!=len(sessions):
        raise ValueError("Duplicate calendar session")
    expected={a:b for s in sessions for a,b in s.expected_bars()}
    starts=set(expected) if manifest["frequency"]=="5m" else {s.start for s in sessions}
    quote_keys=set()
    quote_prices={}
    for quote in quotes:
        key=(quote.ticker,quote.start)
        if quote.ticker not in symbols or quote.start not in starts or key in quote_keys:
            raise ValueError("Executable Open is duplicated or outside frozen symbols/calendar")
        first_trade=manifest["members"][quote.ticker].get("first_trade_date")
        if first_trade and quote.start.astimezone(ZoneInfo(manifest["timezone"])).date()<date.fromisoformat(first_trade):
            raise ValueError("Executable Open predates audited issuer listing")
        quote_keys.add(key)
        quote_prices[key]=quote.open
    for bar in bars:
        if quote_prices.get((bar.ticker,bar.start))!=bar.open:
            raise ValueError("Completed bar Open differs from independently recorded execution quote")
        first_trade=manifest["members"][bar.ticker].get("first_trade_date")
        if first_trade and bar.start.astimezone(ZoneInfo(manifest["timezone"])).date()<date.fromisoformat(first_trade):
            raise ValueError("Bar predates the audited issuer listing; ticker reuse is not continuity")
        if manifest["frequency"]=="5m":
            if expected.get(bar.start)!=bar.end:
                raise ValueError("Intraday bar is outside the audited continuous-session grid")
        elif (bar.start,bar.end) not in lookup:
            raise ValueError("Daily bar does not match its session")
    for ticker,meta in manifest["members"].items():
        if meta.get("lot_history") or meta.get("lot_schedule"):
            raise ValueError("Time-varying legal lots require a dated execution model")
        if not isinstance(meta["lot"],int) or meta["lot"]<=0:
            raise ValueError("Invalid legal lot")
        if meta["availability"] not in ("available","not_yet_listed","unavailable","halted"):
            raise ValueError("Unknown availability status")
        if not any(b.ticker==ticker for b in bars) and not meta.get("reason"):
            raise ValueError("Missing member must retain an explicit reason")
    action_keys=set()
    for action in manifest.get("splits",[]):
        if action["ticker"] not in symbols or not isfinite(action["ratio"]) or action["ratio"]<=0:
            raise ValueError("Invalid split record")
        at=datetime.fromisoformat(action["at"])
        if not at.tzinfo or (action["ticker"],at) in action_keys:
            raise ValueError("Naive or duplicate split event")
        if any(b.ticker==action["ticker"] and b.start<at<b.end for b in bars):
            raise ValueError("Split inside an observed bar mixes price units; audit its effective time and OHLC basis")
        action_keys.add((action["ticker"],at))
    digest=fingerprint({"manifest":manifest,"bars_sha256":manifest["bars_sha256"],"sources":sources})
    return Dataset(manifest,digest,bars,sessions,path,quotes)
