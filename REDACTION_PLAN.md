# Redaction Plan

## Local Private Area

`.private/` stores untracked denylist and review notes. It is excluded by `.gitignore`.

Required local files:

- `.private/redaction_terms.txt`
- `.private/source_inventory.json`
- `.private/publication_review.md`

## Alias Rules

| Private category | Public alias pattern |
|---|---|
| Organisation | Example Operations Group |
| Business unit | Division Alpha |
| Store or branch | Site 001 |
| Location | Region North |
| Employee | Worker 001 |
| Manager | Reviewer 001 |
| External platform | External Platform A |
| Accounting platform | Example Ledger |

## Gate Rules

- Never print a denylisted term in normal logs.
- Reports may show only a hash, category and file path.
- Build fails when a denylisted value appears in tracked content.
- Manual publication review is required before remote push, release or deployment.
