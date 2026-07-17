# Case Study: Attendance Reconciliation Engine

## Observed Problem

Operations teams often compare planned shifts and actual clock events manually, making exception review slow and hard to audit.

## Generic Public Interpretation

The public version treats the problem as a neutral reconciliation workflow: import planned work, import attendance events, classify differences and produce review queues.

## Clean-Room Design

This project is an independent clean-room implementation based on a common operational problem. It contains no private organisational source code, data, branding or proprietary documentation.

## Implementation

A deterministic Python core compares shifts and attendance events using configurable grace windows.

## Testing

Synthetic fixtures assert expected exception categories.

## Demonstration

A browser-only demo shows the exception queue using generated data.

## Limitations

The project is not payroll software and does not claim statutory compliance.

## Transferable Lesson

Separating input data, rules, exceptions and audit events turns spreadsheet checking into a reusable review system.
