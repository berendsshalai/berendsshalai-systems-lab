from __future__ import annotations

import json

from attendance_reconciliation.cli import main
from attendance_reconciliation.io import read_attendance, read_shifts
from attendance_reconciliation.synthetic import generate


def test_cli_writes_report(tmp_path):
    data_dir = tmp_path / "data"
    generate(data_dir)
    output = tmp_path / "report.json"

    result = main(
        [
            "reconcile",
            "--shifts",
            str(data_dir / "shifts.csv"),
            "--attendance",
            str(data_dir / "attendance.csv"),
            "--output",
            str(output),
        ]
    )

    assert result == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["exception_count"] == 6


def test_json_readers_accept_list_payloads(tmp_path):
    shifts = [
        {
            "shift_id": "S001",
            "worker_id": "Worker 001",
            "site_id": "Site 001",
            "role": "Operator",
            "start": "2026-01-05T08:00:00",
            "end": "2026-01-05T16:00:00",
        }
    ]
    attendance = [
        {
            "event_id": "E001",
            "worker_id": "Worker 001",
            "site_id": "Site 001",
            "timestamp": "2026-01-05T08:00:00",
            "event_type": "clock_in",
        },
        {
            "event_id": "E002",
            "worker_id": "Worker 001",
            "site_id": "Site 001",
            "timestamp": "2026-01-05T16:00:00",
            "event_type": "clock_out",
        },
    ]
    shifts_path = tmp_path / "shifts.json"
    attendance_path = tmp_path / "attendance.json"
    shifts_path.write_text(json.dumps(shifts), encoding="utf-8")
    attendance_path.write_text(json.dumps(attendance), encoding="utf-8")

    assert read_shifts(shifts_path)[0].shift_id == "S001"
    assert read_attendance(attendance_path)[1].event_id == "E002"
