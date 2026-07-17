from __future__ import annotations

from datetime import datetime

from attendance_reconciliation.engine import reconcile
from attendance_reconciliation.io import read_attendance_csv, read_shifts_csv
from attendance_reconciliation.models import AttendanceEvent, Shift
from attendance_reconciliation.synthetic import ATTENDANCE_ROWS, SHIFT_ROWS
from attendance_reconciliation.synthetic import _write_csv


def test_reconciliation_detects_expected_exceptions(tmp_path):
    shifts_path = tmp_path / "shifts.csv"
    attendance_path = tmp_path / "attendance.csv"
    _write_csv(shifts_path, SHIFT_ROWS)
    _write_csv(attendance_path, ATTENDANCE_ROWS)

    report = reconcile(read_shifts_csv(shifts_path), read_attendance_csv(attendance_path))
    codes = {item["code"] for item in report["exceptions"]}

    assert report["summary"]["shift_count"] == 4
    assert "LATE_ARRIVAL" in codes
    assert "EARLY_DEPARTURE" in codes
    assert "MISSING_CLOCK_EVENT" in codes
    assert "ABSENT_WHILE_ROSTERED" in codes
    assert "PRESENT_WHILE_UNROSTERED" in codes
    assert "validation_messages" in report


def test_clean_shift_reconciles_without_exception_for_worker_001(tmp_path):
    shifts_path = tmp_path / "shifts.csv"
    attendance_path = tmp_path / "attendance.csv"
    _write_csv(shifts_path, [SHIFT_ROWS[0]])
    _write_csv(attendance_path, [ATTENDANCE_ROWS[0], ATTENDANCE_ROWS[1]])

    report = reconcile(read_shifts_csv(shifts_path), read_attendance_csv(attendance_path))

    assert report["summary"]["exception_count"] == 0
    assert report["reconciled_shifts"][0]["worked_minutes"] == 479
    assert report["reconciled_shifts"][0]["early_departure_minutes"] == 0


def test_adjacent_shifts_do_not_reuse_clock_events():
    shifts = [
        Shift(
            "S001",
            "Worker 010",
            "Site 001",
            "Operator",
            datetime.fromisoformat("2026-01-05T08:00:00"),
            datetime.fromisoformat("2026-01-05T12:00:00"),
        ),
        Shift(
            "S002",
            "Worker 010",
            "Site 001",
            "Operator",
            datetime.fromisoformat("2026-01-05T13:00:00"),
            datetime.fromisoformat("2026-01-05T17:00:00"),
        ),
    ]
    events = [
        AttendanceEvent("E001", "Worker 010", "Site 001", datetime.fromisoformat("2026-01-05T08:00:00"), "clock_in"),
        AttendanceEvent("E002", "Worker 010", "Site 001", datetime.fromisoformat("2026-01-05T12:01:00"), "clock_out"),
        AttendanceEvent("E003", "Worker 010", "Site 001", datetime.fromisoformat("2026-01-05T13:02:00"), "clock_in"),
        AttendanceEvent("E004", "Worker 010", "Site 001", datetime.fromisoformat("2026-01-05T17:00:00"), "clock_out"),
    ]

    report = reconcile(shifts, events)

    assert report["summary"]["exception_count"] == 0
    assert [item["clock_in_event_id"] for item in report["reconciled_shifts"]] == ["E001", "E003"]
    assert [item["clock_out_event_id"] for item in report["reconciled_shifts"]] == ["E002", "E004"]


def test_unmatched_same_day_clock_event_is_reviewed():
    shifts = [
        Shift(
            "S001",
            "Worker 011",
            "Site 001",
            "Operator",
            datetime.fromisoformat("2026-01-05T08:00:00"),
            datetime.fromisoformat("2026-01-05T16:00:00"),
        ),
    ]
    events = [
        AttendanceEvent("E001", "Worker 011", "Site 001", datetime.fromisoformat("2026-01-05T08:00:00"), "clock_in"),
        AttendanceEvent("E002", "Worker 011", "Site 001", datetime.fromisoformat("2026-01-05T12:00:00"), "clock_in"),
        AttendanceEvent("E003", "Worker 011", "Site 001", datetime.fromisoformat("2026-01-05T16:00:00"), "clock_out"),
    ]

    report = reconcile(shifts, events)

    assert any(
        item["code"] == "UNMATCHED_CLOCK_EVENT" and item["source"]["event_id"] == "E002"
        for item in report["exceptions"]
    )
