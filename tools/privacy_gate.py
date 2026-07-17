from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / ".private"

DEFAULT_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"),
    "windows_path": re.compile(r"\b[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)+[^\\/:*?\"<>|\r\n]*"),
    "possible_account": re.compile(r"\b(?:account|tax|merchant|order)[-_ ]?(?:id|number|no)?[:# ]+[A-Za-z0-9-]{6,}\b", re.IGNORECASE),
    "api_token": re.compile(r"\b(?:ghp|github_pat|sk|xoxb|xoxp|AKIA)[A-Za-z0-9_\-]{12,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
}
DATE_LIKE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_EMAILS = {"security@example.com"}
SKIP_DIRS = {".git", ".private", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", "coverage", "out"}
TEXT_EXTENSIONS = {
    ".md", ".py", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".csv", ".svg", ".cff"
}


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"LICENSE", "NOTICE"}:
            files.append(path)
    return files


def load_denylist() -> list[str]:
    denylist = PRIVATE / "redaction_terms.txt"
    if not denylist.exists():
        return []
    terms = []
    for line in denylist.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        terms.append(value)
    return terms


def tracked_files() -> set[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return set(iter_files())
    if result.returncode != 0:
        return set(iter_files())
    return {ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()}


def scan_file(path: Path, deny_terms: list[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings
    rel = str(path.relative_to(ROOT))
    for term in deny_terms:
        if term and term in text:
            findings.append({"file": rel, "category": "denylist", "hash": digest(term)})
    for category, pattern in DEFAULT_PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group(0)
            if category == "email" and value in ALLOWED_EMAILS:
                continue
            if category == "phone" and DATE_LIKE.fullmatch(value):
                continue
            if "example.com" in value or "wix-site-host.com" in value:
                continue
            findings.append({"file": rel, "category": category, "hash": digest(value)})
    return findings


def scan_git_history() -> list[dict[str, str]]:
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H%x09%s"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    findings: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        for category, pattern in DEFAULT_PATTERNS.items():
            for match in pattern.finditer(line):
                findings.append({"file": "git-history", "category": f"commit-{category}", "hash": digest(match.group(0))})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Privacy publication gate.")
    parser.add_argument("--json", action="store_true", help="Print JSON findings.")
    args = parser.parse_args()

    deny_terms = load_denylist()
    candidates = set(iter_files())
    if (ROOT / ".git").exists():
        candidates |= tracked_files()
    findings: list[dict[str, str]] = []
    for path in sorted(candidates):
        if path.exists() and path.is_file():
            findings.extend(scan_file(path, deny_terms))
    findings.extend(scan_git_history())

    report = {"root": str(ROOT), "finding_count": len(findings), "findings": findings}
    if args.json:
        print(json.dumps(report, indent=2))
    elif findings:
        print(f"privacy gate failed: {len(findings)} finding(s)")
        for finding in findings:
            print(f"{finding['file']} {finding['category']} {finding['hash']}")
    else:
        print("privacy gate passed: no denylisted or high-risk text patterns found")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
