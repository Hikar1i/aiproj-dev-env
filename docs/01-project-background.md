# Project Background and Business Goals

## Current Facts

- `aiproj-dev-env` packages a personal AI-assisted development workflow into a reusable CLI, Codex Skill, templates, installers, and documentation.
- The project was created to remove repeated setup work when starting or inheriting repositories.
- The default project convention is A-mode: local-only AI workspace files live under `.ai-local/`, while durable project knowledge lives in the root `README.md` and `docs/`.
- The primary user is a developer working across Windows, Ubuntu, macOS, WSL, Codex, and other AI coding agents.

## Business Goals

- Initialize new or existing repositories quickly and consistently.
- Preserve personal AI-agent working files without polluting team Git history.
- Make documentation maintenance explicit when code changes affect project knowledge.
- Provide a portable package that can be installed on another machine with minimal manual steps.

## Success Criteria

- `aiproj init --dry-run` previews all changes without writing files.
- `aiproj init` is idempotent and safe to rerun.
- Windows installation makes `aiproj` available through the user PATH.
- The Codex Skill delegates deterministic work to the CLI instead of duplicating logic.
- Project documentation states known facts only and avoids invented details.

## Evidence

- Source CLI: `bin/aiproj.py`
- Skill entry point: `skills/project-bootstrap/SKILL.md`
- Installer scripts: `install.ps1`, `install.sh`
- Tests: `tests/test_aiproj.py`
- Original discussion material: `docs/research/chatgpt回复.md`
