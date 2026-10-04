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
import re
from zoneinfo import ZoneInfo
from .indicators import Indicators
from .portfolio import Ledger
from .signals import SignalState, SignalRules, target_notional
from .reporting import account_point,summarize

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

@dataclass(frozen=True)
class OpenQuote:
    ticker: str
    start: datetime
    open: float

    def __post_init__(self):
        if not self.start.tzinfo or not isfinite(self.open) or self.open<=0:
            raise ValueError("An Open needs an aware timestamp and positive finite price")

def replay(bars: list[Bar], *, ledger: Ledger, start: datetime, end: datetime,
           frequency: str, market_timezone: str, arm: str, allocation: str,
           signal_rules: SignalRules, seed_method: str, adx_threshold: float,
           cross_window: int, hist_drawdown: float, increments: int,
           delay_minutes: int, scaled_base: float | None, planned_exits: list[PlannedExit],
           dataset_kind: str, audit_digest: str | None = None,
           allow_entries: bool = True, splits: list[dict] | None = None,
           open_quotes: list[OpenQuote] | None = None, market: str | None = None) -> dict:
    if dataset_kind not in ("synthetic","yahoo_audited","yahoo_daily_pilot"):
        raise ValueError("Unrecognized or unaudited dataset kind")
    if dataset_kind!="synthetic" and not re.fullmatch(r"[0-9a-f]{64}",audit_digest or ""):
        raise ValueError("Real replay requires a verified dataset audit digest")
    if dataset_kind=="yahoo_daily_pilot" and frequency!="daily":
        raise ValueError("Exploratory cache pilot is daily only")
    if frequency not in ("5m","daily") or end <= start:
        raise ValueError("Invalid replay interval/frequency")
    indicators, signals = {}, {}
    initial_equity,initial_fees,initial_taxes = ledger.equity,ledger.fees,ledger.taxes
    initial_events,initial_trades = len(ledger.events),len(ledger.trades)
    opened, closed, planned = defaultdict(list), defaultdict(list), defaultdict(list)
    actions = defaultdict(list)
    for action in splits or []:
        actions[datetime.fromisoformat(action["at"])].append(action)
    prior_end = {}
    for b in sorted(bars,key=lambda b:(b.start,b.ticker)):
        if b.start < prior_end.get(b.ticker,b.start):
            raise ValueError("Duplicate or overlapping bars")
        prior_end[b.ticker] = b.end
        if open_quotes is None and b.start<end:
            opened[b.start].append(OpenQuote(b.ticker,b.start,b.open))
        if b.end > end:
            continue
        closed[b.end].append(b)
        if b.ticker not in indicators:
            indicators[b.ticker] = Indicators(seed_method=seed_method)
            signals[b.ticker] = SignalState(arm,rules=signal_rules,adx_threshold=adx_threshold,
                cross_window=cross_window,hist_drawdown=hist_drawdown,increments=increments)
    if open_quotes is not None:
        quote_ids=set()
        for quote in open_quotes:
            key=(quote.ticker,quote.start)
            if key in quote_ids:raise ValueError("Duplicate executable Open")
            quote_ids.add(key)
            if quote.start<end:opened[quote.start].append(quote)
    for e in planned_exits:
        if e.due_time < e.signal_time:
            raise ValueError("Noncausal planned liquidation")
        planned[e.signal_time].append(e)
    times = sorted(set(opened)|set(closed)|set(planned)|set(actions))
    blocked_until = {}
    curve = [account_point(ledger,start)]
    inadequate_hump_bars=undefined_histogram_bars=0
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
                inadequate_hump_bars+=bool(signal["inadequate_hump_history"])
                undefined_histogram_bars+=reading.histogram is None
        if decisions:
            # A next bar can open at this same instant at a different price.
            # Preserve the completed-Close valuation before any Open overwrites it.
            curve.append(account_point(ledger,at))
        for action in actions[at]:
            ticker,ratio=action["ticker"],action["ratio"]
            if ticker in indicators:
                indicators[ticker].apply_split(ratio)
                signals[ticker].apply_split(ratio)
            if start <= at < end:
                ledger.apply_split(ticker,ratio,at)
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
                if not allow_entries or not s["entry"] or blocked_until.get(b.ticker,datetime.min.replace(tzinfo=at.tzinfo)) >= at:
                    continue
                if frequency=="5m" and (b.entry_cutoff is None or at > b.entry_cutoff):
                    continue
                target = target_notional(ledger.initial_capital,allocation,adx=s["adx"],
                    adx_threshold=adx_threshold,arm=arm,base=scaled_base)
                # Cross identities are stable indices in the immutable ticker history.
                # Signal time is logged separately, so a fold parameter change cannot
                # resubmit the same cross pair at another evaluation timestamp.
                ledger.queue_buy(event_id=f"entry:{market or market_timezone}:{frequency}:{arm}:{b.ticker}:{s['cross_identity']}",
                    ticker=b.ticker,signal_time=at,
                    due_time=at+timedelta(minutes=delay_minutes) if frequency=="5m" else at+timedelta(microseconds=1),
                    slope=s["slope_pct"] or 0,adx=s["adx"],target=target,signal_price=b.close)
            ledger.execute(at,{b.ticker:b.open for b in opened[at]},
                           tax_year=at.astimezone(ZoneInfo(market_timezone)).year)
            curve.append(account_point(ledger,at))
        elif at == end and not decisions:
            curve.append(account_point(ledger,at))
    if curve[-1]["time"]!=end.isoformat():
        curve.append(account_point(ledger,end))
    ledger.finish(end)
    trades=ledger.trades[initial_trades:]
    fees,taxes=ledger.fees-initial_fees,ledger.taxes-initial_taxes
    events=ledger.events[initial_events:]
    metrics=summarize(curve,initial_equity,fees,taxes,trades,events)
    metrics["zero_volume_observations"]=sum(b.volume==0 for b in bars if start<=b.end<end)
    metrics["positive_hump_without_known_boundary_bars"]=inadequate_hump_bars
    metrics["undefined_histogram_bars"]=undefined_histogram_bars
    return {"status":"synthetic_test_only" if dataset_kind=="synthetic" else "completed","dataset_kind":dataset_kind,
        "scope":{"start":start.isoformat(),"end":end.isoformat(),"arm":arm,"allocation":allocation,
                 "market":market or market_timezone,
                 "fill_model":"Observed five-minute Open after fixed delay" if frequency=="5m" else "Daily next-session-Open simplified fills",
                 "frequency":frequency,"delay_minutes":delay_minutes if frequency=="5m" else None},
        "metrics":metrics,"equity":curve,"orders":events,"trades":trades,
        "residual_positions":{t:p.quantity for t,p in ledger.positions.items() if p.quantity},
        "limitations":(["Synthetic execution test; no historical strategy validation."] if dataset_kind=="synthetic" else [])+[
                       "Fill eligibility does not use eventual bar volume; Open quotes are execution proxies.",
                       "Gross/fee views reconcile costs on the same realized trade path; they are not separate reinvestment simulations."]}
