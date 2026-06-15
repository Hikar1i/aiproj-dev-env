# Aiproj Dev Env Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable AI development environment kit with an `aiproj` CLI, Codex Skill, templates, installers, and a zip archive.

**Architecture:** Use one standalone Python CLI with standard-library-only code for cross-platform behavior. Package templates and the Codex Skill beside the CLI, and provide shell installers that copy files into user-level locations.

**Tech Stack:** Python 3 standard library, PowerShell, POSIX shell, Markdown templates, Codex Skill format.

---

### Task 1: Scaffold Package

**Files:**
- Create: `aiproj-dev-env/README.md`
- Create: `aiproj-dev-env/bin/aiproj.py`
- Create: `aiproj-dev-env/templates/global/AGENTS.md`
- Create: `aiproj-dev-env/templates/project/AGENTS.override.md`
- Create: `aiproj-dev-env/templates/project/README.md`
- Create: `aiproj-dev-env/templates/project/docs/*.md`
- Create: `aiproj-dev-env/install.ps1`
- Create: `aiproj-dev-env/install.sh`

- [x] **Step 1: Create the directory structure and template files**

Create the standalone kit in `aiproj-dev-env/`. The default project layout is `.ai-local/` plus root `README.md` and `docs/`.

- [x] **Step 2: Write the CLI**

Implement `init`, `doctor`, `agents refresh`, `docs check`, and `install-global` subcommands. Support `--help`, `--dry-run`, and `--dryrun`.

- [x] **Step 3: Write installers**

Installers copy the CLI and templates to a user-level directory and install the Codex Skill under the Codex skill directory.

- [x] **Step 4: Add Codex Skill**

Create `skills/project-bootstrap/` with `SKILL.md`, `agents/openai.yaml`, and a wrapper script that calls the packaged CLI.

- [x] **Step 5: Test without mutating the current repo**

Run:

```powershell
python aiproj-dev-env/bin/aiproj.py --help
python aiproj-dev-env/bin/aiproj.py init --repo . --dry-run
python aiproj-dev-env/bin/aiproj.py doctor --repo .
```

Expected: commands return exit code `0`, dry run reports planned changes only, and `doctor` reports the current repo is not yet initialized.

- [x] **Step 6: Test against a disposable Git repo**

Run the CLI in a temporary Git repo, verify `.ai-local/`, root `README.md`, `docs/`, `AGENTS.override.md`, and `.git/info/exclude` are created, then re-run init to verify idempotency.

- [x] **Step 7: Build zip archive**

Create `dist/aiproj-dev-env-2026-06-15.zip` from the package directory and verify it contains the CLI, installers, templates, and Skill.

### Self-Review

- Scope covers the requested A-mode layout, root `README.md`, `--help`, `--dry-run`, Codex Skill, templates, and zip output.
- No placeholder implementation remains in this plan.
- All planned commands are standard Python, PowerShell, or POSIX shell.
