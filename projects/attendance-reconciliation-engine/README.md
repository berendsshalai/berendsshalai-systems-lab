# Attendance Reconciliation Engine

Reconciles planned shifts with actual attendance records and produces auditable exception reports.

## Problem Solved

Manual attendance checks often require operators to compare rostered shifts, clock events and exception notes across spreadsheets. This project provides a clean-room local engine for validating those records with synthetic examples and configurable rules.

## Capabilities

- CSV and JSON input paths.
- Deterministic synthetic demonstration.
- Planned-versus-actual reconciliation.
- Roster review against neutral coverage requirements.
- Overlapping planned shift, long shift, duplicate identifier and coverage gap detection.
- Missing clock event, absent while rostered, present while unrostered, lateness and early departure detection.
- CLI, Python API, browser demo and local stdio MCP server scaffold.
- Audit trail with rule identifiers and validation messages.

## Quick Start

```bash
python -m pip install -e .
python -m attendance_reconciliation.synthetic data/demo
python -m attendance_reconciliation.cli reconcile --shifts data/demo/shifts.csv --attendance data/demo/attendance.csv --output out/report.json
python -m attendance_reconciliation.cli review-roster --shifts data/demo/shifts.csv --coverage data/demo/coverage.csv --output out/roster-review.json
```

## Public Pages

- Project page: `https://berendsshalai.github.io/attendance-reconciliation-engine/`
- Social reference: `https://berendsshalai.github.io/attendance-reconciliation-engine/socials/`

## Non-Technical Explanation

This repository is written for both technical and non-technical reviewers. Start with:

- `docs/NON_TECHNICAL_GUIDE.md`
- `docs/RECRUITER_BRIEF.md`
- `docs/ROSTER_SYSTEM_GUIDE.md`
- `docs/SOCIAL_MEDIA_REFERENCE.md`

## Privacy

This project uses synthetic data and neutral identifiers. It is an independent clean-room implementation and contains no private organisational source code, data, branding or proprietary documentation.

## Limitations

This is not a payroll-calculation product and does not claim legal compliance. Rates, thresholds, break rules and pay-period definitions must be configured by the user.
