#!/usr/bin/env python3
"""Wrapper that dispatches to the installed or bundled aiproj CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def candidates() -> list[Path]:
    here = Path(__file__).resolve()
    paths: list[Path] = []
    env_home = os.environ.get("AIPROJ_HOME")
    if env_home:
        paths.append(Path(env_home).expanduser() / "bin" / "aiproj.py")
    paths.append(Path.home() / ".aiproj" / "bin" / "aiproj.py")
    paths.append(here.parents[3] / "bin" / "aiproj.py")
    return paths


def main(argv: list[str]) -> int:
    for cli in candidates():
        if cli.exists():
            completed = subprocess.run([sys.executable, str(cli), *argv])
            return completed.returncode
    print("Unable to find aiproj.py. Install the kit with install.sh or install.ps1.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
