from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .models import CoverageRequirement, Shift


@dataclass(frozen=True)
class RosterReviewConfig:
    max_shift_minutes: int = 12 * 60


def _minutes(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)


def _overlaps(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return left_start < right_end and right_start < left_end


def _finding(
    code: str,
    message: str,
    severity: str,
    source: dict[str, Any],
    site_id: str | None = None,
    worker_id: str | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "site_id": site_id,
        "worker_id": worker_id,
        "role": role,
        "message": message,
        "severity": severity,
        "source": source,
        "review_status": "needs_review",
    }


def _coverage_segments(requirement: CoverageRequirement, shifts: list[Shift]) -> list[tuple[datetime, datetime]]:
    boundaries = {requirement.start, requirement.end}
    for shift in shifts:
        if _overlaps(requirement.start, requirement.end, shift.start, shift.end):
            boundaries.add(max(requirement.start, shift.start))
            boundaries.add(min(requirement.end, shift.end))
    ordered = sorted(boundaries)
    return [
        (ordered[index], ordered[index + 1])
        for index in range(len(ordered) - 1)
        if ordered[index] < ordered[index + 1]
    ]


def _active_count(shifts: list[Shift], start: datetime, end: datetime) -> int:
    return sum(1 for shift in shifts if shift.start <= start and shift.end >= end)


def review_roster(
    shifts: list[Shift],
    coverage_requirements: list[CoverageRequirement] | None = None,
    config: RosterReviewConfig | None = None,
) -> dict[str, Any]:
    cfg = config or RosterReviewConfig()
    requirements = coverage_requirements or []
    findings: list[dict[str, Any]] = []

    for shift in shifts:
        missing_fields = [
            name
            for name, value in {
                "shift_id": shift.shift_id,
                "worker_id": shift.worker_id,
                "site_id": shift.site_id,
                "role": shift.role,
            }.items()
            if not str(value).strip()
        ]
        if missing_fields:
            findings.append(
                _finding(
                    "MISSING_SHIFT_FIELD",
                    "A planned shift is missing a required neutral identifier.",
                    "high",
                    {"shift_id": shift.shift_id, "missing_fields": missing_fields},
                    shift.site_id or None,
                    shift.worker_id or None,
                    shift.role or None,
                )
            )
        if shift.start >= shift.end:
            findings.append(
                _finding(
                    "INVALID_SHIFT_WINDOW",
                    "A planned shift starts at or after its end time.",
                    "high",
                    {"shift_id": shift.shift_id, "start": shift.start.isoformat(), "end": shift.end.isoformat()},
                    shift.site_id,
                    shift.worker_id,
                    shift.role,
                )
            )
            continue
        shift_minutes = _minutes(shift.start, shift.end)
        if shift_minutes > cfg.max_shift_minutes:
            findings.append(
                _finding(
                    "LONG_SHIFT_REVIEW",
                    f"Planned shift is {shift_minutes} minutes and exceeds the configured review threshold.",
                    "medium",
                    {"shift_id": shift.shift_id, "shift_minutes": shift_minutes, "threshold": cfg.max_shift_minutes},
                    shift.site_id,
                    shift.worker_id,
                    shift.role,
                )
            )

    shifts_by_worker: dict[str, list[Shift]] = defaultdict(list)
    for shift in shifts:
        shifts_by_worker[shift.worker_id].append(shift)
    for worker_id, worker_shifts in shifts_by_worker.items():
        ordered = sorted(worker_shifts, key=lambda item: item.start)
        for index, current in enumerate(ordered):
            for other in ordered[index + 1 :]:
                if other.start >= current.end:
                    break
                if _overlaps(current.start, current.end, other.start, other.end):
                    findings.append(
                        _finding(
                            "ROSTER_OVERLAP",
                            "The same worker has overlapping planned shifts that need human review.",
                            "high",
                            {"shift_ids": [current.shift_id, other.shift_id]},
                            current.site_id,
                            worker_id,
                            current.role,
                        )
                    )

    duplicate_shift_ids = [shift_id for shift_id, count in Counter(shift.shift_id for shift in shifts).items() if count > 1]
    for shift_id in duplicate_shift_ids:
        findings.append(
            _finding(
                "DUPLICATE_SHIFT_ID",
                "The same planned shift identifier appears more than once.",
                "medium",
                {"shift_id": shift_id},
            )
        )

    for requirement in requirements:
        if requirement.start >= requirement.end or requirement.minimum_workers < 1:
            findings.append(
                _finding(
                    "INVALID_COVERAGE_REQUIREMENT",
                    "A coverage requirement has an invalid time window or worker count.",
                    "high",
                    {
                        "requirement_id": requirement.requirement_id,
                        "minimum_workers": requirement.minimum_workers,
                        "start": requirement.start.isoformat(),
                        "end": requirement.end.isoformat(),
                    },
                    requirement.site_id,
                    role=requirement.role,
                )
            )
            continue

        matching_shifts = [
            shift
            for shift in shifts
            if shift.site_id == requirement.site_id
            and shift.role == requirement.role
            and _overlaps(requirement.start, requirement.end, shift.start, shift.end)
        ]
        for segment_start, segment_end in _coverage_segments(requirement, matching_shifts):
            actual_workers = _active_count(matching_shifts, segment_start, segment_end)
            if actual_workers < requirement.minimum_workers:
                findings.append(
                    _finding(
                        "COVERAGE_GAP",
                        "Planned coverage is below the configured requirement for this work window.",
                        "high" if actual_workers == 0 else "medium",
                        {
                            "requirement_id": requirement.requirement_id,
                            "required_workers": requirement.minimum_workers,
                            "actual_workers": actual_workers,
                            "window_start": segment_start.isoformat(),
                            "window_end": segment_end.isoformat(),
                        },
                        requirement.site_id,
                        role=requirement.role,
                    )
                )

    finding_counts = Counter(item["code"] for item in findings)
    return {
        "summary": {
            "shift_count": len(shifts),
            "coverage_requirement_count": len(requirements),
            "finding_count": len(findings),
            "coverage_gap_count": finding_counts.get("COVERAGE_GAP", 0),
            "overlap_count": finding_counts.get("ROSTER_OVERLAP", 0),
        },
        "findings": findings,
        "audit_trail": [
            {
                "rule_id": "roster.review.v1",
                "message": "Reviewed planned shifts for neutral identifiers, overlap risk, long windows, and coverage gaps.",
                "record_count": len(shifts) + len(requirements),
            }
        ],
    }
