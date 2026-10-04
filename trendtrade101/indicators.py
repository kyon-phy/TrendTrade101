"""Streaming causal indicators. Initialization is explicit, never inferred.

SMA-seeded EMA and Wilder smoothing are available technical conventions.
They remain pending choices for real-data runs under configuration v0.14.
Missing/nonfinite bars are rejected; the caller must audit gaps.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import isfinite

class Smoother:
    def __init__(self, period: int, alpha: float):
        if period < 1 or not 0 < alpha <= 1:
            raise ValueError("Invalid smoother")
        self.period, self.alpha = period, alpha
        self.seed = []
        self.value = None

    def update(self, value: float) -> float | None:
        if not isfinite(value):
            raise ValueError("Nonfinite indicator input")
        if self.value is None:
            self.seed.append(value)
            if len(self.seed) == self.period:
                self.value = sum(self.seed) / self.period
                self.seed.clear()
        else:
            self.value += self.alpha * (value - self.value)
        return self.value

class SMA:
    def __init__(self, period: int):
        if period < 1:
            raise ValueError("Invalid SMA period")
        self.values = deque(maxlen=period)
        self.period = period

    def update(self, value: float) -> float | None:
        self.values.append(value)
        return sum(self.values) / self.period if len(self.values) == self.period else None

@dataclass(frozen=True)
class Reading:
    sma_fast: float | None
    sma_slow: float | None
    macd: float | None
    signal: float | None
    histogram: float | None
    adx: float | None
    slope_pct: float | None

class Indicators:
    def __init__(self, *, seed_method: str, sma_fast=5, sma_slow=20,
                 macd_fast=12, macd_slow=26, macd_signal=9, adx_period=14):
        if seed_method != "sma_seed":
            raise ValueError("Only the explicit sma_seed convention is implemented")
        self.fast, self.slow = SMA(sma_fast), SMA(sma_slow)
        self.ef = Smoother(macd_fast, 2/(macd_fast+1))
        self.es = Smoother(macd_slow, 2/(macd_slow+1))
        self.sig = Smoother(macd_signal, 2/(macd_signal+1))
        self.tr, self.plus, self.minus, self.dx = [Smoother(adx_period, 1/adx_period) for _ in range(4)]
        self.previous = None
        self.previous_fast = None

    def apply_split(self, ratio: float):
        """Rescale past price state at the split's effective time."""
        if not isfinite(ratio) or ratio <= 0:
            raise ValueError("Invalid split ratio")
        for sma in (self.fast,self.slow):
            sma.values = deque((v/ratio for v in sma.values),maxlen=sma.period)
        for smoother in (self.ef,self.es,self.sig,self.tr,self.plus,self.minus):
            smoother.seed = [v/ratio for v in smoother.seed]
            if smoother.value is not None:
                smoother.value /= ratio
        if self.previous is not None:
            self.previous = tuple(v/ratio for v in self.previous)
        if self.previous_fast is not None:
            self.previous_fast /= ratio

    def update(self, high: float, low: float, close: float) -> Reading:
        if not all(isfinite(x) and x > 0 for x in (high, low, close)) or not low <= close <= high:
            raise ValueError("Invalid OHLC input")
        sf, ss = self.fast.update(close), self.slow.update(close)
        ef, es = self.ef.update(close), self.es.update(close)
        macd = ef-es if ef is not None and es is not None else None
        signal = self.sig.update(macd) if macd is not None else None
        hist = macd-signal if signal is not None else None
        adx = None
        if self.previous:
            ph, pl, pc = self.previous
            up, down = high-ph, pl-low
            tr = self.tr.update(max(high-low, abs(high-pc), abs(low-pc)))
            plus = self.plus.update(up if up > down and up > 0 else 0)
            minus = self.minus.update(down if down > up and down > 0 else 0)
            if tr is not None:
                pd = 100*plus/tr if tr else 0
                md = 100*minus/tr if tr else 0
                adx = self.dx.update(100*abs(pd-md)/(pd+md) if pd+md else 0)
        slope = 100*(sf/self.previous_fast-1) if sf is not None and self.previous_fast else None
        self.previous_fast, self.previous = sf, (high, low, close)
        return Reading(sf, ss, macd, signal, hist, adx, slope)

def positive_histogram(values, increments: int = 3) -> bool:
    if len(values) < increments + 1:
        return False
    tail = list(values)[-(increments+1):]
    return all(x is not None and isfinite(x) for x in tail) and tail[-1] > 0 and all(
        b > a for a, b in zip(tail, tail[1:]))

def bullish_cross(previous_fast, previous_slow, fast, slow) -> bool:
    return all(v is not None for v in (previous_fast, previous_slow, fast, slow)) and (
        previous_fast <= previous_slow and fast > slow)
