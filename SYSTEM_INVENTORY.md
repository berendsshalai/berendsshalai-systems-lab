# System Inventory

No private operational directories were imported into this workspace. The only source material used for this first execution is a user-provided public orchestration brief and generic functional requirements.

| Local identifier | Generic problem | Input types | Transformations | Outputs | Risk class | Public project | Priority | Status |
|---|---|---|---|---|---|---|---|---|
| `sha256:generic-attendance` | Planned-versus-actual attendance reconciliation | CSV, XLSX, JSON, synthetic fixtures | Normalise identifiers, compare rostered shifts with clock events, classify exceptions | Exception report, daily summary, audit trail | Clean-room rebuild required | Attendance Reconciliation Engine | P0 | Scaffolded |
| `sha256:generic-roster` | Workforce schedule generation | Availability, demand, roles, rules | Optimise coverage, fairness and cost | Roster, explainability report, exports | Clean-room rebuild required | Workforce Roster Optimisation Engine | P1 | Planned |
| `sha256:generic-hours-audit` | Payroll evidence comparison | Attendance, approvals, payroll-ready hours | Detect mismatches, duplicate entries and missing approvals | Evidence pack, sign-off report | Clean-room rebuild required | Payroll Evidence and Hours Audit | P1 | Planned |
| `sha256:generic-revenue` | External platform revenue reconciliation | Platform transactions, ledger records, evidence refs | Match, classify, queue exceptions | Reconciliation workbook, management summary | Clean-room rebuild required | Revenue Reconciliation Toolkit | P2 | Planned |
| `sha256:generic-document-capture` | Local document-to-data extraction | PNG, JPEG, PDF | Preprocess, OCR, template extraction, confidence scoring | Structured records, review queue | Clean-room rebuild required | Document-to-Data Workbench | P2 | Planned |
| `sha256:generic-sales-ops` | Hourly sales operations processing | Daily sales files, synthetic transactions | Normalise site/date/channel, aggregate hourly metrics | Dashboard JSON, CSV, XLSX | Clean-room rebuild required | Hourly Sales Operations Processor | P2 | Planned |
| `sha256:generic-recruitment` | Recruitment intake and candidate routing | Candidate forms, site preferences | Validate, deduplicate, score configurable travel/location factors | Reviewer queue, summaries | Clean-room rebuild required | Recruitment Intake and Candidate Routing | P1 | Planned |
| `sha256:generic-evidence-monitor` | Checklist evidence monitoring | Checklist exports, authorised evidence refs | Classify overdue or missing evidence | RAG summary, escalation queue | Clean-room rebuild required | Operations Evidence Monitor | P3 | Planned |
| `sha256:generic-workflow-comm` | Workflow communication routing | Workflow configs, templates, events | Validate, preview, queue, retry | Outbox, mock messages, audit records | Clean-room rebuild required | Configurable Workflow Communication Framework | P3 | Planned |
| `sha256:generic-executive-dashboard` | Sanitised executive operations reporting | Aggregated metrics | Define indicators, render role views | Static dashboard, metric definitions | Clean-room rebuild required | Operations Metrics Dashboard | P3 | Planned |

Files classified as uncertain, confidential, proprietary or unsuitable must remain outside tracked content and be represented only by private hashes in `.private/`.
