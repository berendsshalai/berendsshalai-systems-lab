from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".private", "node_modules", "__pycache__", ".pytest_cache", "out"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts)
    ]


def local_target_exists(source: Path, link: str) -> bool:
    target = link.split("#", 1)[0].strip()
    if not target:
        return True
    parsed = urlparse(target)
    if parsed.scheme or target.startswith("mailto:"):
        return True
    target_path = Path(unquote(target))
    if not target_path.is_absolute():
        target_path = source.parent / target_path
    return target_path.exists()


def main() -> int:
    findings: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            link = match.group(1)
            if not local_target_exists(path, link):
                findings.append(f"{path.relative_to(ROOT)} -> {link}")
    if findings:
        print("link verification failed")
        for finding in findings:
            print(finding)
        return 1
    print("link verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
