"""Causal calendar folds and constrained candidate selection."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import product
from statistics import median
from .signals import ARMS, ADX_ARMS

@dataclass(frozen=True)
class Interval:
    start: date
    end: date

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("Intervals are half-open and nonempty")

    def overlaps(self, other):
        return self.start < other.end and other.start < self.end

def month_shift(d: date, count: int) -> date:
    index = d.year*12+d.month-1+count
    return date(index//12,index%12+1,1)

def holdout_from_complete_sessions(complete_dates: list[date], *, frequency: str,
                                   as_of: date, audited_period_ends: set[date]) -> Interval:
    """An audited calendar supplies each completed period's last session."""
    candidates = sorted(d for d in complete_dates if d <= as_of and d in audited_period_ends)
    if not candidates:
        raise ValueError("No audited complete period")
    last = candidates[-1]
    if frequency == "5m":
        start = last-timedelta(days=last.weekday())
        return Interval(start,start+timedelta(days=7))
    if frequency == "daily":
        start = last.replace(day=1)
        return Interval(start,month_shift(start,1))
    raise ValueError("Unsupported frequency")

def folds(available_start: date, holdout: Interval, *, frequency: str):
    if frequency == "5m":
        start = available_start+timedelta(days=(-available_start.weekday())%7)
        test = start+timedelta(weeks=2)
        while test+timedelta(weeks=1) <= holdout.start:
            yield Interval(test-timedelta(weeks=2),test),Interval(test,test+timedelta(weeks=1))
            test += timedelta(weeks=1)
    elif frequency == "daily":
        start = available_start.replace(day=1)
        if start < available_start:
            start = month_shift(start,1)
        test = month_shift(start,6)
        while month_shift(test,1) <= holdout.start:
            yield Interval(month_shift(test,-6),test),Interval(test,month_shift(test,1))
            test = month_shift(test,1)
    else:
        raise ValueError("Unsupported frequency")

def guard_training(interval: Interval, holdout: Interval):
    if interval.overlaps(holdout) or interval.end > holdout.start:
        raise ValueError("Final holdout cannot enter training or selection")

def candidates(arm: str):
    if arm not in ARMS:
        raise ValueError("Unknown entry arm")
    axes = ([20,25,30] if arm in ADX_ARMS else [25],
            [3,5,8] if arm == "FULL" else [5], [0.3,0.4,0.5])
    return [{"adx_threshold":a,"cross_window":n,"hist_drawdown":h} for a,n,h in product(*axes)]

def select_candidate(results: list[dict], *, objective: str, neighborhood: str,
                     minimum_trades: int, sparse_is_filter: bool, max_drawdown: float):
    """All rows must be training-only; tie and scoring choices are explicit."""
    if objective != "after_tax_return" or neighborhood != "axis_adjacent_median":
        raise ValueError("Unsupported, unapproved scoring convention")
    eligible = [r for r in results if r["scope"] == "training" and
                r["max_drawdown"] <= max_drawdown and
                (not sparse_is_filter or r["trades"] >= minimum_trades)]
    if any(r["scope"] != "training" for r in results):
        raise ValueError("Selection accepts training scores only")
    if not eligible:
        return None
    axes = {"adx_threshold":[20,25,30],"cross_window":[3,5,8],"hist_drawdown":[0.3,0.4,0.5]}
    def distance(a,b):
        return sum(abs(values.index(a[k])-values.index(b[k])) for k,values in axes.items())
    scored = []
    for r in eligible:
        neighbors = [n for n in eligible if distance(r["parameters"],n["parameters"]) <= 1]
        score = median(n["after_tax_return"] for n in neighbors)
        scored.append({**r,"neighborhood_score":score,"neighbor_count":len(neighbors),
                       "sparse":r["trades"] < minimum_trades})
    return min(scored,key=lambda r:(-r["neighborhood_score"],r["max_drawdown"],
                                    tuple(r["parameters"][k] for k in axes)))

def maximum_drawdown(equity: list[float]) -> float:
    peak, worst = 0.0, 0.0
    for value in equity:
        if value <= 0:
            return 1.0
        peak = max(peak,value)
        worst = max(worst,(peak-value)/peak)
    return worst
