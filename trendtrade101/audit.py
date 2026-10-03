"""Audit Yahoo payloads without filling gaps or treating terminal quotes as bars."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from math import isfinite
from .timing import Session

FIELDS = ("open", "high", "low", "close", "volume")

def audit_chart(payload: dict, sessions: list[Session], *, frequency: str) -> dict:
    chart = payload.get("chart", {})
    if chart.get("error") or not chart.get("result"):
        return {"status":"unavailable", "provider_error":chart.get("error"), "bars":[], "opens":[], "counts":{}}
    result = chart["result"][0]
    quote = result["indicators"]["quote"][0]
    stamps = result.get("timestamp", [])
    expected = {}
    session_dates = {}
    for s in sessions:
        session_dates[s.start.date()] = s
        for a, b in s.expected_bars():
            expected[int(a.timestamp())] = b
    counts = Counter()
    bars,opens = [],[]
    seen = set()
    terminal = {int(t.timestamp()) for s in sessions for _, t in s.segments()}
    for i, stamp in enumerate(stamps):
        if stamp in seen:
            counts["duplicate_timestamp"] += 1
            continue
        seen.add(stamp)
        values = {k: quote.get(k, [])[i] if i < len(quote.get(k, [])) else None for k in FIELDS}
        dt = datetime.fromtimestamp(stamp, timezone.utc)
        if frequency == "5m":
            if stamp not in expected:
                counts["terminal_observation" if stamp in terminal else "outside_audited_interval"] += 1
                continue
            end = expected[stamp]
        elif frequency == "daily":
            matches = [s for s in sessions if s.start == dt]
            if not matches:
                counts["outside_audited_session"] += 1
                continue
            end = matches[0].end
        else:
            raise ValueError("Unsupported frequency")
        opening=values["open"]
        if isinstance(opening,(int,float)) and isfinite(opening) and opening>0:
            opens.append({"start":dt.isoformat(),"open":opening})
        else:
            counts["invalid_or_missing_open"]+=1
        if any(v is None or not isinstance(v,(int,float)) or not isfinite(v) for v in values.values()):
            counts["null_or_nonfinite"] += 1
            continue
        o,h,l,c,v = (values[k] for k in FIELDS)
        if not (0 < l <= min(o,c) <= max(o,c) <= h) or v < 0:
            counts["invalid_ohlcv"] += 1
            continue
        if v == 0:
            counts["zero_volume"] += 1
        bars.append({"start":dt.isoformat(), "end":end.isoformat(), **values})
    if frequency == "5m" and stamps:
        first, last = min(stamps), max(stamps)
        valid = {int(datetime.fromisoformat(b["start"]).timestamp()) for b in bars}
        counts["missing_expected_intervals"] = sum(t not in valid for t in expected if first <= t <= last)
    counts["returned"] = len(stamps)
    counts["usable"] = len(bars)
    counts["usable_opens"] = len(opens)
    bars.sort(key=lambda b:b["start"]);opens.sort(key=lambda q:q["start"])
    return {"status":"audited_with_flags" if any(v for k,v in counts.items() if k not in {"usable","usable_opens","returned"}) else "audited",
            "counts":dict(counts), "first_usable":bars[0]["start"] if bars else None,
            "last_usable":bars[-1]["start"] if bars else None,
            "exchange_timezone":result.get("meta",{}).get("exchangeTimezoneName"),
            "currency":result.get("meta",{}).get("currency"),
            "events":result.get("events",{}), "bars":bars,"opens":opens,
            "limitations":["Adjustment/identity/lot review remains separate.",
                           "Null causes are not inferred from missing values.",
                           "Coverage does not establish maximum available history."]}
