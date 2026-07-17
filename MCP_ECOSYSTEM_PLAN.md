# MCP Ecosystem Plan

## Standard Tools

Each project MCP server should expose:

- `describe_project`
- `generate_synthetic_dataset`
- `run_demo_reconciliation` or equivalent project core action
- `explain_exception`
- `export_report`

## Safety

- Local stdio transport by default.
- No live email, payroll, HR or finance actions by default.
- Inputs must be validated with schemas.
- Logs must avoid private row-level content.
- MCP documentation must include example prompts and limitations.
