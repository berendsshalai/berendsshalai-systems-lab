# Roster System Guide

This guide explains the roster side of the project in plain language.

## What The Roster Review Adds

Attendance reconciliation answers: did the clock events match the planned shift?

Roster review answers: did the planned shift pattern itself make sense before clock events were considered?

The public engine now checks:

- Coverage gaps: a work window requires more people than the roster provides.
- Overlapping planned shifts: the same worker is planned in two places at the same time.
- Long shifts: a planned shift exceeds the configured review threshold.
- Duplicate identifiers: the same planned shift identifier appears more than once.
- Missing neutral identifiers: a planned row is incomplete.

## Clean-Room Boundary

This repository intentionally uses generic terms such as `Site 001`, `Worker 001`, `Operator`, and `Lead`.

It does not publish private workbooks, private application files, branch names, customer names, employer names, screenshots with operational records, API tokens, financial values, payroll exports, or live identifiers.

## Example Workflow

1. Create fictional `shifts.csv`, `attendance.csv`, and `coverage.csv` files.
2. Run attendance reconciliation to compare planned shifts with clock events.
3. Run roster review to compare planned shifts with coverage requirements.
4. Read the generated exception list and decide what a human should review.

```bash
python -m attendance_reconciliation.synthetic data/demo
python -m attendance_reconciliation.cli reconcile --shifts data/demo/shifts.csv --attendance data/demo/attendance.csv --output out/report.json
python -m attendance_reconciliation.cli review-roster --shifts data/demo/shifts.csv --coverage data/demo/coverage.csv --output out/roster-review.json
```

## Why This Matters To A Hiring Manager

The project shows that operational work can be translated into a reusable system without exposing the original business context. It demonstrates process mapping, data modelling, privacy judgment, automation, testing, and documentation for both technical and non-technical audiences.
