# Architecture

## System Overview

`aiproj-dev-env` is intentionally simple: one standard-library Python CLI performs deterministic file operations, and surrounding templates/scripts make it pleasant to install and invoke.

```text
bin/aiproj.py
  owns initialization, doctor checks, docs checks, global install

install.ps1 / install.sh
  copy the kit into a user-level install directory and install the Codex Skill

skills/project-bootstrap/
  provides the Codex Skill wrapper and usage instructions

templates/
  stores reusable global and project documentation templates

tools/build_zip.py
  builds portable release archives

tests/
  verifies CLI behavior against temporary repositories
```

## Boundaries

- CLI logic belongs in `bin/aiproj.py`.
- Codex-specific workflow guidance belongs in `skills/project-bootstrap/SKILL.md`.
- User-facing installation flow belongs in `install.ps1` and `install.sh`.
- Durable knowledge about this repository belongs in `README.md` and `docs/`.
- Build artifacts belong in `dist/` and are ignored by Git.
- Local experiments and backups belong in `.ai-local/` and are ignored by Git.

## Data Flow

1. A user runs `aiproj init` directly, or asks Codex to use `$project-bootstrap`.
2. The Skill wrapper calls the installed or bundled CLI.
3. The CLI detects or accepts the repository profile.
4. The CLI creates `.ai-local/`, project docs, `AGENTS.override.md`, `.git/info/exclude`, and optional `.gitignore` blocks.
5. `doctor` and `docs check` validate the result.

## Design Decisions

- Use Python standard library only to keep installation portable.
- Use managed marker blocks for files that may already exist.
- Keep `.ai-local/` in `.git/info/exclude`, not project `.gitignore`, because it is personal local workflow state.
- Keep global `AGENTS.md` updates in a managed block to avoid overwriting user-authored global instructions.
