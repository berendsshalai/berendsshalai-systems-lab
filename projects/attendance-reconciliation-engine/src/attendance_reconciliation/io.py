from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import AttendanceEvent, Shift


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def read_shifts_csv(path: str | Path) -> list[Shift]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return [
            Shift(
                shift_id=row["shift_id"],
                worker_id=row["worker_id"],
                site_id=row["site_id"],
                role=row["role"],
                start=parse_dt(row["start"]),
                end=parse_dt(row["end"]),
            )
            for row in csv.DictReader(handle)
        ]


def _shift_from_row(row: dict[str, Any]) -> Shift:
    return Shift(
        shift_id=str(row["shift_id"]),
        worker_id=str(row["worker_id"]),
        site_id=str(row["site_id"]),
        role=str(row["role"]),
        start=parse_dt(str(row["start"])),
        end=parse_dt(str(row["end"])),
    )


def _attendance_from_row(row: dict[str, Any]) -> AttendanceEvent:
    return AttendanceEvent(
        event_id=str(row["event_id"]),
        worker_id=str(row["worker_id"]),
        site_id=str(row["site_id"]),
        timestamp=parse_dt(str(row["timestamp"])),
        event_type=str(row["event_type"]),  # type: ignore[arg-type]
    )


def read_attendance_csv(path: str | Path) -> list[AttendanceEvent]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return [
            AttendanceEvent(
                event_id=row["event_id"],
                worker_id=row["worker_id"],
                site_id=row["site_id"],
                timestamp=parse_dt(row["timestamp"]),
                event_type=row["event_type"],  # type: ignore[arg-type]
            )
            for row in csv.DictReader(handle)
        ]


def read_shifts_json(path: str | Path) -> list[Shift]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload["shifts"] if isinstance(payload, dict) and "shifts" in payload else payload
    return [_shift_from_row(row) for row in rows]


def read_attendance_json(path: str | Path) -> list[AttendanceEvent]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload["attendance"] if isinstance(payload, dict) and "attendance" in payload else payload
    return [_attendance_from_row(row) for row in rows]


def read_shifts(path: str | Path) -> list[Shift]:
    source = Path(path)
    if source.suffix.lower() == ".json":
        return read_shifts_json(source)
    return read_shifts_csv(source)


def read_attendance(path: str | Path) -> list[AttendanceEvent]:
    source = Path(path)
    if source.suffix.lower() == ".json":
        return read_attendance_json(source)
    return read_attendance_csv(source)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
