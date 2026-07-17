from __future__ import annotations

from datetime import datetime

from attendance_reconciliation.models import CoverageRequirement, Shift
from attendance_reconciliation.roster import RosterReviewConfig, review_roster


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_roster_review_detects_coverage_gap():
    shifts = [
        Shift("S001", "Worker 001", "Site 001", "Operator", _dt("2026-01-05T08:00:00"), _dt("2026-01-05T12:00:00"))
    ]
    coverage = [
        CoverageRequirement("C001", "Site 001", "Operator", _dt("2026-01-05T08:00:00"), _dt("2026-01-05T16:00:00"), 1)
    ]

    report = review_roster(shifts, coverage)

    assert report["summary"]["coverage_gap_count"] == 1
    assert report["findings"][0]["code"] == "COVERAGE_GAP"
    assert report["findings"][0]["source"]["window_start"] == "2026-01-05T12:00:00"


def test_roster_review_detects_worker_overlap():
    shifts = [
        Shift("S001", "Worker 001", "Site 001", "Operator", _dt("2026-01-05T08:00:00"), _dt("2026-01-05T12:00:00")),
        Shift("S002", "Worker 001", "Site 002", "Operator", _dt("2026-01-05T11:30:00"), _dt("2026-01-05T15:00:00")),
    ]

    report = review_roster(shifts)
    codes = {item["code"] for item in report["findings"]}

    assert "ROSTER_OVERLAP" in codes
    assert report["summary"]["overlap_count"] == 1


def test_roster_review_flags_long_shift_with_configurable_threshold():
    shifts = [
        Shift("S001", "Worker 001", "Site 001", "Lead", _dt("2026-01-05T06:00:00"), _dt("2026-01-05T18:30:00"))
    ]

    report = review_roster(shifts, config=RosterReviewConfig(max_shift_minutes=12 * 60))

    assert any(item["code"] == "LONG_SHIFT_REVIEW" for item in report["findings"])
