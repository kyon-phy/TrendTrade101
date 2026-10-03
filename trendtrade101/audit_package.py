"""Build a private dataset from already captured Yahoo files and reviewed evidence.

There is no network fallback. The capture manifest must identify an audited
calendar and explicit adjustment/identity/action reviews before normalization.
"""
from __future__ import annotations
from datetime import date,datetime,timedelta
from math import prod
from pathlib import Path
from zoneinfo import ZoneInfo
from .audit import audit_chart
from .dataset import REQUIRED_AUDITS
from .inputs import EXPECTED,project_members
from .storage import read_json,sha256,write_json,utcnow
from .timing import Session

def audit_local_charts(root:Path,capture_path:Path,output:Path):
    capture=read_json(capture_path)
    if capture.get("provider")!="Yahoo": raise ValueError("Only the approved Yahoo source is supported")
    review=capture.get("review",{})
    if any(review.get(k,{}).get("status")!="verified" or not review[k].get("evidence") for k in REQUIRED_AUDITS):
        raise ValueError("Supply completed, evidence-backed audits; booleans alone are insufficient")
    if capture.get("unresolved_corporate_actions"):
        raise ValueError("Corporate distributions must be resolved before producing a runnable package")
    market,frequency=capture["market"],capture["frequency"]
    tz=ZoneInfo(capture["timezone"])
    as_of=datetime.fromisoformat(capture["as_of"])
    if not as_of.tzinfo:raise ValueError("Capture as_of must include a timezone")
    members={r["ticker"] for r in project_members(root) if r["market"]==market
             and r["frequency"] in (frequency,"daily_and_5m")}
    if set(capture["members"])!=members: raise ValueError("Capture inventory differs from frozen membership")
    calendar_file=(capture_path.parent/capture["calendar_file"]).resolve()
    if not calendar_file.is_relative_to(capture_path.parent.resolve()) or sha256(calendar_file)!=capture["calendar_sha256"]:
        raise ValueError("Calendar hash/path mismatch")
    calendar=read_json(calendar_file)
    sessions=[Session(market,datetime.fromisoformat(s["start"]),datetime.fromisoformat(s["end"]),
               tuple((datetime.fromisoformat(a),datetime.fromisoformat(b)) for a,b in s.get("breaks",[])))
              for s in calendar["sessions"]]
    if not sessions:raise ValueError("Empty calendar")
    vendor_basis=capture["vendor_ohlc_basis"]
    if vendor_basis not in ("historical_unadjusted","split_adjusted_only"):
        raise ValueError("Dividend-adjusted or unknown OHLC basis is not supported")
    # Verified split events must include all splits reflected in the vendor basis.
    splits=capture.get("splits",[])
    raw_sources=[];bars=[];audits={}
    output.mkdir(parents=True,exist_ok=True,mode=0o700)
    for ticker in sorted(members):
        meta=capture["members"][ticker]
        if not meta.get("first_trade_date"):
            raise ValueError(f"{ticker}: audited issuer first-trade date is required")
        if meta["availability"]!="available":
            if not meta.get("reason"):raise ValueError("Unavailable members require an audit reason")
            audits[ticker]={"status":meta["availability"],"reason":meta["reason"]}
            continue
        source=(capture_path.parent/meta["file"]).resolve()
        if not source.is_relative_to(capture_path.parent.resolve()) or sha256(source)!=meta["sha256"]:
            raise ValueError("Raw capture hash/path mismatch")
        audit=audit_chart(read_json(source),sessions,frequency=frequency)
        retrieved=datetime.fromisoformat(meta["retrieved_at"])
        if not retrieved.tzinfo:raise ValueError("Retrieval timestamp must include a timezone")
        observable_through=min(as_of,retrieved)
        if not audit["bars"]:raise ValueError(f"{ticker}: no usable observed bars")
        if audit.get("exchange_timezone")!=capture["timezone"]:
            raise ValueError(f"{ticker}: provider timezone differs from audited calendar")
        if audit.get("currency")!=("USD" if market=="US" else "JPY"):
            raise ValueError(f"{ticker}: wrong price currency")
        for b in audit.pop("bars"):
            start,end=datetime.fromisoformat(b["start"]),datetime.fromisoformat(b["end"])
            if end>observable_through:
                audit["counts"]["incomplete_at_retrieval"]=audit["counts"].get("incomplete_at_retrieval",0)+1
                continue
            if start.astimezone(tz).date()<date.fromisoformat(meta.get("first_trade_date","1900-01-01")):
                raise ValueError(f"{ticker}: vendor bars predate audited issuer identity")
            ratio=prod(a["ratio"] for a in splits if a["ticker"]==ticker and
                       datetime.fromisoformat(a["at"])>start) if vendor_basis=="split_adjusted_only" else 1
            session=next(s for s in sessions if s.start<=start<s.end)
            bars.append(dict(ticker=ticker,start=start.isoformat(),end=end.isoformat(),
                **{field:b[field]*ratio for field in ("open","high","low","close")},
                volume=b["volume"],entry_cutoff=(session.end-timedelta(minutes=63)).isoformat()))
        audits[ticker]=audit
        raw=source.read_bytes()
        target=output/"sources"/source.name
        target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        if target.exists() and target.read_bytes()!=raw:raise ValueError("Source filename collision")
        target.write_bytes(raw);target.chmod(0o600)
        raw_sources.append({"file":str(target.relative_to(output)),"sha256":meta["sha256"],
                            "ticker":ticker,
                            "retrieved_at":meta["retrieved_at"],"request":meta["request"]})
    calendar_target=output/"sources"/"calendar.json"
    calendar_target.parent.mkdir(parents=True,exist_ok=True)
    calendar_target.write_bytes(calendar_file.read_bytes())
    raw_sources.append({"file":"sources/calendar.json","sha256":capture["calendar_sha256"],"kind":"calendar"})
    bars.sort(key=lambda b:(b["start"],b["ticker"]))
    write_json(output/"bars.json",bars)
    complete=[]
    endpoints={(b["ticker"],datetime.fromisoformat(b["end"])) for b in bars}
    for s in sessions:
        target=s.end if frequency=="daily" else list(s.expected_bars())[-1][1]
        available=[t for t,m in capture["members"].items() if m["availability"]=="available"
                   and date.fromisoformat(m.get("first_trade_date","1900-01-01"))<=s.start.astimezone(tz).date()]
        if target<=as_of and available and all((t,target) in endpoints for t in available):
            complete.append(s.start.astimezone(tz).date())
    grouped={}
    for s in sessions:
        d=s.start.astimezone(tz).date()
        key=d-timedelta(days=d.weekday()) if frequency=="5m" else d.replace(day=1)
        grouped[key]=max(grouped.get(key,d),d)
    known_through=date.fromisoformat(calendar["complete_through"])
    period_ends=[]
    from .research import month_shift
    for key,last in grouped.items():
        stop=key+timedelta(days=7) if frequency=="5m" else month_shift(key,1)
        if known_through>=stop-timedelta(days=1) and last in complete:
            period_ends.append(last.isoformat())
    manifest={"schema_version":1,"kind":"yahoo_audited","provider":"Yahoo","market":market,
        "frequency":frequency,"timezone":capture["timezone"],"as_of_date":as_of.astimezone(tz).date().isoformat(),
        "configuration_source_sha256":EXPECTED["TrendTrade101_Backtest_Configuration.md"],
        "price_basis":"historical_unadjusted_split_events","vendor_ohlc_basis":vendor_basis,
        "members":{t:{k:v for k,v in m.items() if k in ("lot","availability","reason","first_trade_date")}
                   for t,m in capture["members"].items()},
        "sessions":[{"market":s.market,"start":s.start.isoformat(),"end":s.end.isoformat(),
                     "breaks":[[a.isoformat(),b.isoformat()] for a,b in s.breaks]} for s in sessions],
        "calendar_complete_through":calendar["complete_through"],
        "complete_session_dates":[d.isoformat() for d in complete],"complete_period_ends":sorted(period_ends),
        "bars_file":"bars.json","bars_sha256":sha256(output/"bars.json"),
        "source_snapshots":raw_sources,"splits":splits,"audit":review,
        "unresolved_corporate_actions":[],"per_symbol_audit":audits,"audited_at":utcnow()}
    write_json(output/"dataset.json",manifest)
    return {"dataset":str(output/"dataset.json"),"members":len(members),"usable_bars":len(bars),
            "complete_periods":len(period_ends),"status":"audited_local_package"}
