from __future__ import annotations

import argparse

from .engine import ReconciliationConfig, reconcile
from .io import read_attendance, read_shifts, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="attendance-reconcile")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reconcile_parser = subparsers.add_parser("reconcile", help="Reconcile shifts and attendance CSV or JSON files.")
    reconcile_parser.add_argument("--shifts", required=True)
    reconcile_parser.add_argument("--attendance", required=True)
    reconcile_parser.add_argument("--output", required=True)
    reconcile_parser.add_argument("--late-grace-minutes", type=int, default=5)
    reconcile_parser.add_argument("--early-departure-grace-minutes", type=int, default=5)

    args = parser.parse_args(argv)
    if args.command == "reconcile":
        config = ReconciliationConfig(
            late_grace_minutes=args.late_grace_minutes,
            early_departure_grace_minutes=args.early_departure_grace_minutes,
        )
        report = reconcile(read_shifts(args.shifts), read_attendance(args.attendance), config)
        write_json(args.output, report)
        print(f"wrote reconciliation report to {args.output}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
