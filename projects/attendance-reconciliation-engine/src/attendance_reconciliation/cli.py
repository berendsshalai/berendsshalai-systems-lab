from __future__ import annotations

import argparse

from .engine import ReconciliationConfig, reconcile
from .io import read_attendance, read_coverage, read_shifts, write_json
from .roster import RosterReviewConfig, review_roster


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="attendance-reconcile")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reconcile_parser = subparsers.add_parser("reconcile", help="Reconcile shifts and attendance CSV or JSON files.")
    reconcile_parser.add_argument("--shifts", required=True)
    reconcile_parser.add_argument("--attendance", required=True)
    reconcile_parser.add_argument("--output", required=True)
    reconcile_parser.add_argument("--late-grace-minutes", type=int, default=5)
    reconcile_parser.add_argument("--early-departure-grace-minutes", type=int, default=5)

    roster_parser = subparsers.add_parser("review-roster", help="Review planned shifts against neutral coverage rules.")
    roster_parser.add_argument("--shifts", required=True)
    roster_parser.add_argument("--coverage", required=True)
    roster_parser.add_argument("--output", required=True)
    roster_parser.add_argument("--max-shift-minutes", type=int, default=12 * 60)

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
    if args.command == "review-roster":
        config = RosterReviewConfig(max_shift_minutes=args.max_shift_minutes)
        report = review_roster(read_shifts(args.shifts), read_coverage(args.coverage), config)
        write_json(args.output, report)
        print(f"wrote roster review report to {args.output}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
