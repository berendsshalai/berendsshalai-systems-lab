from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new clean-room project placeholder.")
    parser.add_argument("slug")
    parser.add_argument("title")
    args = parser.parse_args()
    target = ROOT / "projects" / args.slug
    target.mkdir(parents=True, exist_ok=False)
    (target / "README.md").write_text(f"# {args.title}\n\nClean-room project placeholder.\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
