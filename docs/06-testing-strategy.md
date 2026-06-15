# Testing Strategy

## Test Commands

Run the unit suite:

```bash
python -m unittest discover -s tests -v
```

Run CLI smoke checks:

```bash
python bin/aiproj.py --help
python bin/aiproj.py init --repo . --dry-run
python bin/aiproj.py doctor --repo .
```

Build and inspect a package:

```bash
python tools/build_zip.py
```

## Current Coverage

- `tests/test_aiproj.py` verifies:
  - top-level help works
  - dry-run does not write files
  - `init` is idempotent in a temporary Git repository
  - `--skip-doc testing-strategy` works for demo-style projects

## Manual Verification

- Install to a temporary HOME when changing installer behavior.
- Verify Windows installation with `install.ps1` before relying on PATH behavior.
- Verify the Skill structure after editing `skills/project-bootstrap/SKILL.md`.
- Run `aiproj docs check --repo .` before commits that change CLI behavior or docs.

## Known Test Gaps

- There is no automated GitHub publishing test.
- The shell installer is syntax-checked but not fully exercised on Linux/macOS in this Windows workspace.
- The Codex Skill validator may require optional Python packages that are not always present.
