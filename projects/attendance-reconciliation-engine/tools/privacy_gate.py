from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".private", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "dist", "build", "coverage", "out"}
TEXT_EXTENSIONS = {".md", ".py", ".txt", ".json", ".yml", ".yaml", ".toml", ".html", ".css", ".js", ".csv", ".cff"}
PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "windows_path": re.compile(r"\b[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)+[^\\/:*?\"<>|\r\n]*"),
    "possible_account": re.compile(r"\b(?:account|tax|merchant|order)[-_ ]?(?:id|number|no)?[:# ]+[A-Za-z0-9-]{6,}\b", re.IGNORECASE),
    "api_token": re.compile(r"\b(?:ghp|github_pat|sk|xoxb|xoxp|AKIA)[A-Za-z0-9_\-]{12,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
}


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def git_files() -> set[Path]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=ROOT, check=False, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return {ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()}
    except FileNotFoundError:
        pass
    return set()


def iter_files() -> set[Path]:
    return {
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts)
        and (path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"LICENSE", "NOTICE"})
    }


def main() -> int:
    findings: list[str] = []
    for path in sorted(iter_files() | git_files()):
        if not path.exists() or any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for category, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                if "example.com" in value:
                    continue
                findings.append(f"{path.relative_to(ROOT)} {category} {digest(value)}")
    if findings:
        print(f"privacy gate failed: {len(findings)} finding(s)")
        for finding in findings:
            print(finding)
        return 1
    print("privacy gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
