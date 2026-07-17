# Quickstart

Generate synthetic data:

```bash
python -m pip install -e .
python -m attendance_reconciliation.synthetic data/demo
```

Run reconciliation:

```bash
python -m attendance_reconciliation.cli reconcile --shifts data/demo/shifts.csv --attendance data/demo/attendance.csv --output out/report.json
```
