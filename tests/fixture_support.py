"""Deterministic synthetic prices. Never used as historical research results."""
import json,math
from datetime import date,datetime,time,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from trendtrade101.inputs import EXPECTED,project_members
from trendtrade101.storage import write_json,sha256
from trendtrade101.dataset import load_dataset

ROOT=Path(__file__).resolve().parents[1]

def build_fixture(directory:Path,frequency="5m",holdout_multiplier=1):
    timezone="America/New_York";tz=ZoneInfo(timezone)
    tickers=sorted({r["ticker"] for r in project_members(ROOT) if r["market"]=="US"
                    and r["frequency"] in (frequency,"daily_and_5m")})
    begin,finish=(date(2026,1,5),date(2026,2,2)) if frequency=="5m" else (date(2025,1,1),date(2025,10,1))
    holdout_start=date(2026,1,26) if frequency=="5m" else date(2025,9,1)
    sessions=[];bars=[];dates=[];index=0;day=begin
    while day<finish:
        if day.weekday()<5:
            start=datetime.combine(day,time(9,30),tzinfo=tz)
            end=start+timedelta(minutes=120) if frequency=="5m" else datetime.combine(day,time(16),tzinfo=tz)
            sessions.append({"market":"US","start":start.isoformat(),"end":end.isoformat(),"breaks":[]})
            dates.append(day.isoformat())
            count=24 if frequency=="5m" else 1
            for i in range(count):
                at=start+timedelta(minutes=5*i) if frequency=="5m" else start
                stop=at+timedelta(minutes=5) if frequency=="5m" else end
                for ticker in tickers:
                    offset=tickers.index(ticker)%4
                    price=(100+15*math.sin((index+offset)/4)+.015*index)
                    if day>=holdout_start:price*=holdout_multiplier
                    bars.append({"ticker":ticker,"start":at.isoformat(),"end":stop.isoformat(),
                        "open":price,"high":price+1,"low":price-1,"close":price,"volume":1000,
                        "entry_cutoff":(end-timedelta(minutes=63)).isoformat()})
                index+=1
        day+=timedelta(days=1)
    periods={}
    for value in dates:
        d=date.fromisoformat(value)
        key=d-timedelta(days=d.weekday()) if frequency=="5m" else d.replace(day=1)
        periods[key]=value
    write_json(directory/"bars.json",bars)
    manifest={"schema_version":1,"kind":"synthetic_fixture","market":"US","frequency":frequency,
        "timezone":timezone,"as_of_date":finish.isoformat(),
        "configuration_source_sha256":EXPECTED["TrendTrade101_Backtest_Configuration.md"],
        "price_basis":"historical_unadjusted_split_events",
        "members":{t:{"lot":1,"availability":"available"} for t in tickers},
        "sessions":sessions,"calendar_complete_through":finish.isoformat(),
        "complete_session_dates":dates,"complete_period_ends":list(periods.values()),
        "bars_file":"bars.json","bars_sha256":sha256(directory/"bars.json"),"source_snapshots":[],"splits":[]}
    write_json(directory/"dataset.json",manifest)
    return load_dataset(ROOT,directory/"dataset.json",allow_synthetic=True)
