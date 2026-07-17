from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

EventType = Literal["clock_in", "clock_out"]


@dataclass(frozen=True)
class Shift:
    shift_id: str
    worker_id: str
    site_id: str
    role: str
    start: datetime
    end: datetime


@dataclass(frozen=True)
class AttendanceEvent:
    event_id: str
    worker_id: str
    site_id: str
    timestamp: datetime
    event_type: EventType
