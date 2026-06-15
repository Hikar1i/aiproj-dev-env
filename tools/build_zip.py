#!/usr/bin/env python3
"""Build a portable zip archive for aiproj-dev-env."""

from __future__ import annotations

import argparse
import datetime as dt
import zipfile
from pathlib import Path


EXCLUDED_PARTS = {".git", ".ai-local", "dist", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def build_zip(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    base = root.name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or not should_include(path, root):
                continue
            archive.write(path, Path(base) / path.relative_to(root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build aiproj-dev-env zip archive.")
    parser.add_argument("--root", default=".", help="project root; defaults to current directory")
    parser.add_argument("--output", help="zip output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    stamp = dt.date.today().isoformat()
    output = Path(args.output).resolve() if args.output else root / "dist" / f"{root.name}-{stamp}.zip"
    build_zip(root, output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
