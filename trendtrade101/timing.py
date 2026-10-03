"""Exchange-session primitives use explicitly supplied, audited schedules."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True)
class Session:
    market: str
    start: datetime
    end: datetime
    breaks: tuple[tuple[datetime, datetime], ...] = ()

    def __post_init__(self):
        if not self.start.tzinfo or not self.end.tzinfo or self.end <= self.start:
            raise ValueError("An aware, positive session interval is required")
        previous = self.start
        for a, b in self.breaks:
            if not previous <= a < b <= self.end:
                raise ValueError("Invalid session breaks")
            previous = b

    def segments(self):
        cursor = self.start
        for a, b in self.breaks:
            yield cursor, a
            cursor = b
        yield cursor, self.end

    def expected_bars(self, minutes=5):
        if minutes <= 0:
            raise ValueError("Bar length must be positive")
        for start, end in self.segments():
            while start < end:
                stop = min(start + timedelta(minutes=minutes), end)
                yield start, stop
                start = stop

def minute_due(signal_end: datetime, delay_minutes: int) -> datetime:
    if not signal_end.tzinfo or delay_minutes < 0:
        raise ValueError("Aware time and nonnegative delay required")
    return signal_end + timedelta(minutes=delay_minutes)

def eligible_open(signal_end, observed_starts, *, delay_minutes):
    due = minute_due(signal_end, delay_minutes)
    return next((t for t in sorted(observed_starts) if t >= due), None)

def daily_due(signal_end: datetime, sessions: list[Session]) -> datetime | None:
    return next((s.start for s in sorted(sessions, key=lambda s:s.start) if s.start > signal_end), None)

def entry_allowed(signal_end: datetime, session: Session, delay_minutes=20):
    return signal_end <= session.end - timedelta(minutes=3*(delay_minutes+1))
