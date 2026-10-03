"""Signal primitives with explicit experimental definitions, no production defaults."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, replace
from .indicators import Reading, bullish_cross, positive_histogram

ARMS = ("MA_ONLY", "MACD_HIST", "MA_ADX", "MACD_HIST_ADX", "FULL")
ADX_ARMS = ("MA_ADX", "MACD_HIST_ADX", "FULL")

@dataclass(frozen=True)
class SignalRules:
    window_includes_current: bool
    deduplicate_cross_pair: bool
    evaluate_exit_before_zero_reset: bool
    require_histogram_decline: bool
    exit_includes_equality: bool

class SignalState:
    def __init__(self, arm: str, *, rules: SignalRules, adx_threshold: float,
                 cross_window: int, hist_drawdown: float, increments: int):
        if arm not in ARMS or cross_window < 1 or not 0 < hist_drawdown < 1:
            raise ValueError("Invalid signal parameters")
        self.arm, self.rules = arm, rules
        self.adx_threshold, self.window = adx_threshold, cross_window
        self.drawdown, self.increments = hist_drawdown, increments
        self.hist = deque(maxlen=increments+1)
        self.previous = None
        self.index = -1
        self.sma_cross = self.macd_cross = None
        self.seen = set()
        self.peak = None
        self.hump_boundary_seen = False

    def apply_split(self, ratio: float):
        if ratio <= 0:
            raise ValueError("Invalid split ratio")
        self.hist = deque((h/ratio if h is not None else None for h in self.hist),maxlen=self.increments+1)
        if self.peak is not None:
            self.peak /= ratio
        if self.previous is not None:
            fields = ("sma_fast","sma_slow","macd","signal","histogram")
            self.previous = replace(self.previous,**{
                name:getattr(self.previous,name)/ratio if getattr(self.previous,name) is not None else None
                for name in fields})

    def update(self, reading: Reading) -> dict:
        self.index += 1
        previous = self.previous
        sma_cross = bool(previous and bullish_cross(previous.sma_fast, previous.sma_slow,
                                                    reading.sma_fast, reading.sma_slow))
        macd_cross = bool(previous and bullish_cross(previous.macd, previous.signal,
                                                     reading.macd, reading.signal))
        if sma_cross:
            self.sma_cross = self.index
        if macd_cross:
            self.macd_cross = self.index
        h = reading.histogram
        self.hist.append(h)
        hist_entry = positive_histogram(self.hist, self.increments)
        exit_signal = False
        if h is not None:
            prior_peak = self.peak
            declining = previous is not None and previous.histogram is not None and h < previous.histogram
            if h <= 0 and self.rules.evaluate_exit_before_zero_reset:
                exit_signal = True
            if h > 0:
                self.peak = max(prior_peak or h, h)
            reference = self.peak if h > 0 else (
                prior_peak if self.rules.evaluate_exit_before_zero_reset else None)
            if reference is not None and not exit_signal:
                threshold = (1-self.drawdown)*reference
                hit = h <= threshold if self.rules.exit_includes_equality else h < threshold
                exit_signal = hit and (declining or not self.rules.require_histogram_decline)
            if h <= 0:
                self.peak = None
                self.hump_boundary_seen = True
        adx_ok = reading.adx is not None and reading.adx > self.adx_threshold
        identity = None
        if self.arm in ("MA_ONLY", "MA_ADX"):
            entry = sma_cross
            identity = ("sma", self.sma_cross)
        elif self.arm in ("MACD_HIST", "MACD_HIST_ADX"):
            entry = macd_cross and hist_entry
            identity = ("macd", self.macd_cross)
        else:
            age_limit = self.window-1 if self.rules.window_includes_current else self.window
            entry = all(c is not None and 0 <= self.index-c <= age_limit
                        for c in (self.sma_cross,self.macd_cross)) and hist_entry
            identity = (self.sma_cross,self.macd_cross)
        if self.arm in ADX_ARMS:
            entry = entry and adx_ok
        if self.rules.deduplicate_cross_pair and identity in self.seen:
            entry = False
        if entry:
            self.seen.add(identity)
        self.previous = reading
        return {"entry":bool(entry), "exit":bool(exit_signal), "cross_identity":identity,
                "inadequate_hump_history":h is not None and h>0 and not self.hump_boundary_seen,
                "histogram_peak":self.peak, "slope_pct":reading.slope_pct, "adx":reading.adx}

def target_notional(initial_capital: float, allocation: str, *, adx: float | None,
                    adx_threshold: float, arm: str, base: float | None, scale: float=1) -> float:
    if allocation == "fixed":
        return initial_capital/15
    if allocation != "adx_scaled" or base is None:
        raise ValueError("ADX scaling needs an explicit approved base")
    if adx is None:
        return 0
    denominator = adx_threshold if arm in ADX_ARMS else 25
    return max(0, base*scale*(adx/denominator-0.5))
