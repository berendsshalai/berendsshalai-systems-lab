from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    checks = [
        (ROOT, [sys.executable, "tools/privacy_gate.py"]),
        (ROOT, [sys.executable, "tools/audit_licences.py"]),
        (ROOT, [sys.executable, "tools/verify_links.py"]),
        (ROOT / "projects" / "attendance-reconciliation-engine", [sys.executable, "tools/privacy_gate.py"]),
        (ROOT / "projects" / "attendance-reconciliation-engine", [sys.executable, "-m", "compileall", "src"]),
        (ROOT / "projects" / "attendance-reconciliation-engine", [sys.executable, "-m", "pytest", "tests"]),
    ]

    for cwd, check in checks:
        print("+", " ".join(check))
        result = subprocess.run(check, cwd=cwd)
        if result.returncode:
            return result.returncode
    print("release checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
