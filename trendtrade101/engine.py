"""Event-driven replay core.

The core accepts audited bars, explicit rule objects and a precomputed
liquidation schedule. Real-data orchestration is locked by readiness checks.
Unit tests pass synthetic data explicitly and do not validate profitability.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite
from zoneinfo import ZoneInfo
from .indicators import Indicators
from .portfolio import Ledger
from .signals import SignalState, SignalRules, target_notional
from .research import maximum_drawdown

@dataclass(frozen=True)
class Bar:
    ticker: str
    start: datetime
    end: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    entry_cutoff: datetime | None = None

    def __post_init__(self):
        if not self.start.tzinfo or not self.end.tzinfo or self.end <= self.start:
            raise ValueError("Bar timestamps must be aware and causal")
        if not all(isfinite(v) and v > 0 for v in (self.open,self.high,self.low,self.close)):
            raise ValueError("OHLC must be finite and positive")
        if not self.low <= min(self.open,self.close) <= max(self.open,self.close) <= self.high:
            raise ValueError("Inconsistent OHLC")
        if not isfinite(self.volume) or self.volume < 0:
            raise ValueError("Invalid volume")

@dataclass(frozen=True)
class PlannedExit:
    ticker: str
    signal_time: datetime
    due_time: datetime
    reason: str
    prohibit_buys_until: datetime

def replay(bars: list[Bar], *, ledger: Ledger, start: datetime, end: datetime,
           frequency: str, market_timezone: str, arm: str, allocation: str,
           signal_rules: SignalRules, seed_method: str, adx_threshold: float,
           cross_window: int, hist_drawdown: float, increments: int,
           delay_minutes: int, scaled_base: float | None, planned_exits: list[PlannedExit],
           dataset_kind: str) -> dict:
    if dataset_kind != "synthetic":
        raise ValueError("Real-data replay is locked until canonical synchronization and audit are complete")
    if frequency not in ("5m","daily") or end <= start:
        raise ValueError("Invalid replay interval/frequency")
    indicators, signals = {}, {}
    opened, closed, planned = defaultdict(list), defaultdict(list), defaultdict(list)
    prior_end = {}
    for b in sorted(bars,key=lambda b:(b.start,b.ticker)):
        if b.start < prior_end.get(b.ticker,b.start):
            raise ValueError("Duplicate or overlapping bars")
        prior_end[b.ticker] = b.end
        if b.end > end:
            continue
        opened[b.start].append(b)
        closed[b.end].append(b)
        if b.ticker not in indicators:
            indicators[b.ticker] = Indicators(seed_method=seed_method)
            signals[b.ticker] = SignalState(arm,rules=signal_rules,adx_threshold=adx_threshold,
                cross_window=cross_window,hist_drawdown=hist_drawdown,increments=increments)
    for e in planned_exits:
        if e.due_time < e.signal_time:
            raise ValueError("Noncausal planned liquidation")
        planned[e.signal_time].append(e)
    times = sorted(set(opened)|set(closed)|set(planned))
    blocked_until = {}
    curve = []
    for at in times:
        if at > end:
            break
        # Completed bars become observable before any open at the same instant.
        decisions = []
        for b in sorted(closed[at],key=lambda x:x.ticker):
            reading = indicators[b.ticker].update(b.high,b.low,b.close)
            signal = signals[b.ticker].update(reading)
            if start <= at <= end:
                ledger.mark(b.ticker,b.close)
                decisions.append((b,signal))
        if start <= at < end:
            # Scheduled exits have priority over any same-instant entries.
            for e in planned[at]:
                ledger.queue_exit(event_id=f"scheduled:{e.ticker}:{at.isoformat()}",
                    ticker=e.ticker,signal_time=at,due_time=e.due_time,reason=e.reason)
                blocked_until[e.ticker] = e.prohibit_buys_until
            for b,s in decisions:
                if s["exit"] and ledger.positions.get(b.ticker) and ledger.positions[b.ticker].quantity:
                    ledger.queue_exit(event_id=f"exit:{b.ticker}:{at.isoformat()}",
                        ticker=b.ticker,signal_time=at,
                        due_time=at+timedelta(minutes=delay_minutes) if frequency=="5m" else at+timedelta(microseconds=1),
                        reason="histogram_drawdown")
                    blocked_until[b.ticker] = max(blocked_until.get(b.ticker,at),at)
            for b,s in sorted(decisions,key=lambda p:(-(p[1]["slope_pct"] or 0),p[0].ticker)):
                if not s["entry"] or blocked_until.get(b.ticker,datetime.min.replace(tzinfo=at.tzinfo)) >= at:
                    continue
                if frequency=="5m" and (b.entry_cutoff is None or at > b.entry_cutoff):
                    continue
                target = target_notional(ledger.initial_capital,allocation,adx=s["adx"],
                    adx_threshold=adx_threshold,arm=arm,base=scaled_base)
                ledger.queue_buy(event_id=f"{arm}:{b.ticker}:{at.isoformat()}:{s['cross_identity']}",
                    ticker=b.ticker,signal_time=at,
                    due_time=at+timedelta(minutes=delay_minutes) if frequency=="5m" else at+timedelta(microseconds=1),
                    slope=s["slope_pct"] or 0,adx=s["adx"],target=target,signal_price=b.close)
            ledger.execute(at,{b.ticker:b.open for b in opened[at] if b.volume>0},
                           tax_year=at.astimezone(ZoneInfo(market_timezone)).year)
            curve.append({"time":at.isoformat(),"equity":ledger.equity,"cash":ledger.cash,
                          "exposure":ledger.exposure,"reserved":ledger.reserved,
                          "fees":ledger.fees,"taxes":ledger.taxes})
        elif at == end:
            curve.append({"time":at.isoformat(),"equity":ledger.equity,"cash":ledger.cash,
                          "exposure":ledger.exposure,"reserved":ledger.reserved,
                          "fees":ledger.fees,"taxes":ledger.taxes})
    ledger.finish(end)
    values = [ledger.initial_capital]+[p["equity"] for p in curve]
    final = values[-1]
    return {"status":"synthetic_test_only","dataset_kind":dataset_kind,
        "scope":{"start":start.isoformat(),"end":end.isoformat(),"arm":arm,"allocation":allocation,
                 "frequency":frequency,"delay_minutes":delay_minutes if frequency=="5m" else None},
        "metrics":{"after_tax_return":final/ledger.initial_capital-1,
                   "after_fee_return":(final+ledger.taxes)/ledger.initial_capital-1,
                   "gross_return":(final+ledger.taxes+ledger.fees)/ledger.initial_capital-1,
                   "max_drawdown":maximum_drawdown(values),"closed_trades":len(ledger.trades),
                   "fees":ledger.fees,"taxes":ledger.taxes,
                   "win_rate":sum(t["after_fee_pnl"]>0 for t in ledger.trades)/len(ledger.trades) if ledger.trades else None},
        "equity":curve,"orders":ledger.events,"trades":ledger.trades,
        "residual_positions":{t:p.quantity for t,p in ledger.positions.items() if p.quantity},
        "limitations":["Synthetic execution test; no historical strategy validation.",
                       "Gross/fee views reconcile costs on the same realized trade path; they are not separate reinvestment simulations."]}
