# Risk Register

| Risk | Severity | Likelihood | Control | Status |
|---|---:|---:|---|---|
| Private identifiers accidentally enter public docs | High | Medium | `.private` denylist, `tools/privacy_gate.py`, manual review | Active |
| Public project implies employer/client endorsement | High | Medium | Non-affiliation statement in every repository | Active |
| Scaffold is mistaken for production-ready software | Medium | Medium | Status badges, limitations and release gates | Active |
| Legal rules are hard-coded as universal truth | High | Low | All thresholds and rates live in configuration | Active |
| Git history contains private material | High | Low | New clean directory only; history scan before push | Active |
| Generated examples include realistic PII | High | Low | Synthetic IDs and neutral site names only | Active |
| Remote publication happens before review | High | Low | Publication report required before push/deploy | Active |
