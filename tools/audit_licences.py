from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = [ROOT, ROOT / "projects" / "attendance-reconciliation-engine"]


def check_project(path: Path) -> list[str]:
    findings: list[str] = []
    for filename in ["LICENSE", "NOTICE", "CITATION.cff"]:
        if not (path / filename).exists():
            findings.append(f"{path.relative_to(ROOT)} missing {filename}")
    license_text = (path / "LICENSE").read_text(encoding="utf-8") if (path / "LICENSE").exists() else ""
    if "MIT License" not in license_text or "Sha-Lai Berends" not in license_text:
        findings.append(f"{path.relative_to(ROOT)} LICENSE does not contain expected MIT attribution")
    return findings


def main() -> int:
    findings: list[str] = []
    for project in PROJECTS:
        findings.extend(check_project(project))
    if findings:
        print("licence audit failed")
        for finding in findings:
            print(finding)
        return 1
    print("licence audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
