from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from .models import AttendanceEvent, Shift


@dataclass(frozen=True)
class ReconciliationConfig:
    late_grace_minutes: int = 5
    early_departure_grace_minutes: int = 5
    match_window_hours: int = 16


def _minutes(delta: timedelta) -> int:
    return int(delta.total_seconds() // 60)


def _positive_minutes(delta: timedelta) -> int:
    return max(0, _minutes(delta))


def _exception(
    code: str,
    worker_id: str,
    site_id: str,
    message: str,
    severity: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    return {
        "code": code,
        "worker_id": worker_id,
        "site_id": site_id,
        "message": message,
        "severity": severity,
        "source": source,
        "review_status": "needs_review",
    }


def _nearest_event(
    events: list[AttendanceEvent],
    target_shift: Shift,
    event_type: str,
    target: str,
    used_event_ids: set[str],
    cfg: ReconciliationConfig,
) -> AttendanceEvent | None:
    window_start = target_shift.start - timedelta(hours=cfg.match_window_hours)
    window_end = target_shift.end + timedelta(hours=cfg.match_window_hours)
    target_time = target_shift.start if target == "start" else target_shift.end
    candidates = [
        event
        for event in events
        if event.event_id not in used_event_ids
        and event.site_id == target_shift.site_id
        and event.event_type == event_type
        and window_start <= event.timestamp <= window_end
    ]
    if target == "end":
        candidates = [event for event in candidates if event.timestamp >= target_shift.start]
    return min(candidates, key=lambda event: abs(event.timestamp - target_time), default=None)


def reconcile(
    shifts: list[Shift],
    attendance_events: list[AttendanceEvent],
    config: ReconciliationConfig | None = None,
) -> dict[str, Any]:
    cfg = config or ReconciliationConfig()
    events_by_worker: dict[str, list[AttendanceEvent]] = defaultdict(list)
    for event in attendance_events:
        events_by_worker[event.worker_id].append(event)
    for events in events_by_worker.values():
        events.sort(key=lambda item: item.timestamp)

    used_event_ids: set[str] = set()
    exceptions: list[dict[str, Any]] = []
    reconciled: list[dict[str, Any]] = []

    for shift in sorted(shifts, key=lambda item: (item.start, item.worker_id)):
        worker_events = events_by_worker.get(shift.worker_id, [])
        first_in = _nearest_event(worker_events, shift, "clock_in", "start", used_event_ids, cfg)
        last_out = _nearest_event(worker_events, shift, "clock_out", "end", used_event_ids, cfg)

        if first_in is None and last_out is None:
            exceptions.append(
                _exception(
                    "ABSENT_WHILE_ROSTERED",
                    shift.worker_id,
                    shift.site_id,
                    "Worker has a planned shift but no matching clock events.",
                    "high",
                    {"shift_id": shift.shift_id},
                )
            )
            continue

        if first_in is None or last_out is None:
            exceptions.append(
                _exception(
                    "MISSING_CLOCK_EVENT",
                    shift.worker_id,
                    shift.site_id,
                    "Worker has an incomplete clock event pair.",
                    "high",
                    {
                        "shift_id": shift.shift_id,
                        "clock_in": first_in.event_id if first_in else None,
                        "clock_out": last_out.event_id if last_out else None,
                    },
                )
            )

        if first_in is not None:
            used_event_ids.add(first_in.event_id)
            late_minutes = _positive_minutes(first_in.timestamp - shift.start)
            if late_minutes > cfg.late_grace_minutes:
                exceptions.append(
                    _exception(
                        "LATE_ARRIVAL",
                        shift.worker_id,
                        shift.site_id,
                        f"Clock-in is {late_minutes} minutes after shift start.",
                        "medium",
                        {"shift_id": shift.shift_id, "event_id": first_in.event_id, "late_minutes": late_minutes},
                    )
                )
        else:
            late_minutes = None

        if last_out is not None:
            used_event_ids.add(last_out.event_id)
            early_minutes = _positive_minutes(shift.end - last_out.timestamp)
            if early_minutes > cfg.early_departure_grace_minutes:
                exceptions.append(
                    _exception(
                        "EARLY_DEPARTURE",
                        shift.worker_id,
                        shift.site_id,
                        f"Clock-out is {early_minutes} minutes before shift end.",
                        "medium",
                        {"shift_id": shift.shift_id, "event_id": last_out.event_id, "early_minutes": early_minutes},
                    )
                )
        else:
            early_minutes = None

        worked_minutes = None
        if first_in is not None and last_out is not None and last_out.timestamp >= first_in.timestamp:
            worked_minutes = _minutes(last_out.timestamp - first_in.timestamp)

        reconciled.append(
            {
                "shift_id": shift.shift_id,
                "worker_id": shift.worker_id,
                "site_id": shift.site_id,
                "planned_minutes": _minutes(shift.end - shift.start),
                "worked_minutes": worked_minutes,
                "late_minutes": late_minutes,
                "early_departure_minutes": early_minutes,
                "clock_in_event_id": first_in.event_id if first_in else None,
                "clock_out_event_id": last_out.event_id if last_out else None,
            }
        )

    shift_keys = {(shift.worker_id, shift.site_id, shift.start.date()) for shift in shifts}
    for event in attendance_events:
        if event.event_id in used_event_ids:
            continue
        event_key = (event.worker_id, event.site_id, event.timestamp.date())
        if event_key not in shift_keys:
            exceptions.append(
                _exception(
                    "PRESENT_WHILE_UNROSTERED",
                    event.worker_id,
                    event.site_id,
                    "Attendance event exists without a planned shift on the same date and site.",
                    "medium",
                    {"event_id": event.event_id, "event_type": event.event_type},
                )
            )
        else:
            exceptions.append(
                _exception(
                    "UNMATCHED_CLOCK_EVENT",
                    event.worker_id,
                    event.site_id,
                    "Attendance event was not used in any shift match and requires review.",
                    "low",
                    {"event_id": event.event_id, "event_type": event.event_type},
                )
            )

    daily_summary: dict[str, dict[str, Any]] = {}
    for shift in shifts:
        key = f"{shift.site_id}:{shift.start.date().isoformat()}"
        daily_summary.setdefault(
            key,
            {"site_id": shift.site_id, "date": shift.start.date().isoformat(), "planned_shifts": 0, "planned_minutes": 0},
        )
        daily_summary[key]["planned_shifts"] += 1
        daily_summary[key]["planned_minutes"] += _minutes(shift.end - shift.start)

    audit_trail = [
        {
            "rule_id": "attendance.reconcile.v1",
            "message": "Compared planned shifts with attendance events using configurable grace windows.",
            "record_count": len(shifts) + len(attendance_events),
        }
    ]
    return {
        "summary": {
            "shift_count": len(shifts),
            "attendance_event_count": len(attendance_events),
            "exception_count": len(exceptions),
            "validation_message_count": len(exceptions),
        },
        "exceptions": exceptions,
        "reconciled_shifts": reconciled,
        "daily_summary": list(daily_summary.values()),
        "audit_trail": audit_trail,
        "validation_messages": [
            {
                "code": item["code"],
                "severity": item["severity"],
                "message": item["message"],
                "source": item["source"],
            }
            for item in exceptions
        ],
    }
