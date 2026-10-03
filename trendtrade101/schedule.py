"""Preplanned liquidation events derived only from the supplied calendar."""
from datetime import timedelta
from .engine import PlannedExit
from .timing import Session

def liquidation_schedule(sessions: list[Session], tickers: list[str], *,
                         frequency: str, delay_minutes: int) -> list[PlannedExit]:
    ordered=sorted(sessions,key=lambda s:s.start)
    if frequency=="5m":
        chosen=ordered
    elif frequency=="daily":
        months={}
        for s in ordered:
            months[(s.start.year,s.start.month)]=s
        chosen=list(months.values())
    else:
        raise ValueError("Unsupported frequency")
    events=[]
    for s in chosen:
        if frequency=="5m":
            due=list(s.expected_bars())[-1][0]
            signal=due-timedelta(minutes=delay_minutes)
            reason="scheduled_daily_flatten"
        else:
            due=signal=s.start
            reason="scheduled_monthly_flatten"
        for ticker in tickers:
            events.append(PlannedExit(ticker,signal,due,reason,s.end))
    return events
