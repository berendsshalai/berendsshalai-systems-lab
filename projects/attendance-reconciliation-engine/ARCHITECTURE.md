# Architecture

```mermaid
flowchart LR
  A["Shift import"] --> C["Reconciliation engine"]
  B["Attendance import"] --> C
  D["Rules config"] --> C
  C --> E["Exception queue"]
  C --> F["Daily summary"]
  C --> G["Audit trail"]
```

The deterministic core lives in `src/attendance_reconciliation/engine.py`. Adapters parse CSV and JSON into dataclasses. Reports are plain dictionaries so they can be exported to JSON, CSV or browser views.
