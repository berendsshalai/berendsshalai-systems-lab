from __future__ import annotations

import csv
from pathlib import Path

SHIFT_ROWS = [
    {"shift_id": "S001", "worker_id": "Worker 001", "site_id": "Site 001", "role": "Operator", "start": "2026-01-05T08:00:00", "end": "2026-01-05T16:00:00"},
    {"shift_id": "S002", "worker_id": "Worker 002", "site_id": "Site 001", "role": "Operator", "start": "2026-01-05T08:00:00", "end": "2026-01-05T16:00:00"},
    {"shift_id": "S003", "worker_id": "Worker 003", "site_id": "Site 001", "role": "Lead", "start": "2026-01-05T09:00:00", "end": "2026-01-05T17:00:00"},
    {"shift_id": "S004", "worker_id": "Worker 004", "site_id": "Site 002", "role": "Operator", "start": "2026-01-05T10:00:00", "end": "2026-01-05T18:00:00"},
]

COVERAGE_ROWS = [
    {"requirement_id": "C001", "site_id": "Site 001", "role": "Operator", "start": "2026-01-05T08:00:00", "end": "2026-01-05T16:00:00", "minimum_workers": "2"},
    {"requirement_id": "C002", "site_id": "Site 001", "role": "Lead", "start": "2026-01-05T08:00:00", "end": "2026-01-05T17:00:00", "minimum_workers": "1"},
    {"requirement_id": "C003", "site_id": "Site 002", "role": "Operator", "start": "2026-01-05T10:00:00", "end": "2026-01-05T18:00:00", "minimum_workers": "1"},
]

ATTENDANCE_ROWS = [
    {"event_id": "E001", "worker_id": "Worker 001", "site_id": "Site 001", "timestamp": "2026-01-05T08:02:00", "event_type": "clock_in"},
    {"event_id": "E002", "worker_id": "Worker 001", "site_id": "Site 001", "timestamp": "2026-01-05T16:01:00", "event_type": "clock_out"},
    {"event_id": "E003", "worker_id": "Worker 002", "site_id": "Site 001", "timestamp": "2026-01-05T08:22:00", "event_type": "clock_in"},
    {"event_id": "E004", "worker_id": "Worker 002", "site_id": "Site 001", "timestamp": "2026-01-05T15:30:00", "event_type": "clock_out"},
    {"event_id": "E005", "worker_id": "Worker 003", "site_id": "Site 001", "timestamp": "2026-01-05T09:01:00", "event_type": "clock_in"},
    {"event_id": "E006", "worker_id": "Worker 005", "site_id": "Site 001", "timestamp": "2026-01-05T11:00:00", "event_type": "clock_in"},
    {"event_id": "E007", "worker_id": "Worker 005", "site_id": "Site 001", "timestamp": "2026-01-05T14:00:00", "event_type": "clock_out"},
]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate(target: str | Path) -> None:
    root = Path(target)
    _write_csv(root / "shifts.csv", SHIFT_ROWS)
    _write_csv(root / "attendance.csv", ATTENDANCE_ROWS)
    _write_csv(root / "coverage.csv", COVERAGE_ROWS)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic attendance reconciliation data.")
    parser.add_argument("target", nargs="?", default="data/demo")
    args = parser.parse_args()
    generate(args.target)
    print(f"synthetic data written to {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
