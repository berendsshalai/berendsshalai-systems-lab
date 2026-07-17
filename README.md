# Sha-Lai Berends Systems Lab

Practical open-source systems for payroll, workforce operations, reconciliation, recruitment and administrative automation.

This control repository defines the clean-room standards, shared tooling, project registry and publication gates for a family of reusable public systems by Sha-Lai Berends.

## Public Identity

Sha-Lai Berends is a South African business-automation and data-operations builder creating privacy-conscious, auditable and practical workflow systems.

## What This Repository Contains

- Clean-room publication policy and privacy gate.
- GitHub-ready repository standards.
- Synthetic-data strategy.
- SEO, course, MCP and social content plans.
- A first flagship scaffold: Attendance Reconciliation Engine.

## Local Verification

From a fresh clone:

```bash
python tools/release_check.py
```

To work on the first flagship project directly:

```bash
cd projects/attendance-reconciliation-engine
python -m pip install -e .
python -m pytest tests
```

## Publication Status

Local scaffold only. Nothing in this repository should be published until privacy gates, tests, link checks and manual publication review pass.

## Non-Affiliation

These projects are independent public implementations based on common operational problems. They are not endorsed by, affiliated with, or representative of any employer, client, franchise, platform or private organisation.
