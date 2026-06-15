# aiproj Dev Env

`aiproj` is a personal AI-assisted development bootstrap kit. It creates a stable local AI workspace, project documentation skeleton, local Codex instructions, and safe Git ignore rules.

This repository is the source of truth for the CLI, installers, Codex Skill, templates, tests, and project documentation.

Default A-mode layout:

```text
.ai-local/
  dev/
  references/
  bak/
  scratch-docs/
  config.json
README.md
docs/
  01-project-background.md
  02-architecture.md
  03-database.md
  04-api.md
  05-code-style.md
  06-testing-strategy.md
  07-deployment.md
  08-environments.md
  09-known-issues.md
AGENTS.override.md
```

`README.md` lives at the project root. Long-term project documentation lives under `docs/`. Local AI-only work lives under `.ai-local/` and is excluded through `.git/info/exclude`.

## Quick Start

Preview changes:

```bash
python bin/aiproj.py init --dry-run
```

Initialize a Git repository:

```bash
python bin/aiproj.py init
```

After installing globally, the same commands are available through:

```bash
aiproj init --dry-run
aiproj init
```

For a demo project that does not require testing documentation:

```bash
python bin/aiproj.py init --profile demo --skip-doc testing-strategy
```

Check status:

```bash
python bin/aiproj.py doctor
python bin/aiproj.py docs check
python bin/aiproj.py docs check --strict
```

Show help:

```bash
python bin/aiproj.py --help
python bin/aiproj.py init --help
```

## Install

Windows PowerShell:

```powershell
.\install.ps1
```

The Windows installer adds the `aiproj` command shim to the user PATH by default. Use `.\install.ps1 -NoPath` to skip PATH changes.

macOS, Linux, or WSL:

```bash
sh ./install.sh
```

After installation, restart your terminal or add the reported bin directory to `PATH`, then run:

```bash
aiproj --help
aiproj init --dry-run
```

## Design Notes

- The CLI is the source of deterministic file operations.
- The Codex Skill `project-bootstrap` is a convenient AI-agent entry point.
- Global `AGENTS.md` stores long-lived personal conventions.
- Project-local `AGENTS.override.md` stores local exceptions and is ignored by Git.
- `.git/info/exclude` stores personal local ignore rules; project `.gitignore` remains for team-wide ignore rules.
- Existing files are not overwritten unless the command explicitly manages a marked block or the user passes a force option.

## Repository Maintenance

Run tests:

```bash
python -m unittest discover -s tests -v
```

Build the portable zip package:

```bash
python tools/build_zip.py
```

The generated archive is written under `dist/`, which is intentionally ignored by Git.

Refresh the local installation from this checkout:

```powershell
.\install.ps1
```

Check the repository's own aiproj status:

```bash
aiproj doctor --repo .
aiproj docs check --repo .
```

## Gitignore Behavior

By default, `aiproj init` creates a managed `.gitignore` block only when `.gitignore` does not exist. If `.gitignore` already exists, it is left unchanged.

Use this to add or refresh the managed block:

```bash
aiproj init --gitignore merge
```

Use this to avoid `.gitignore` handling entirely:

```bash
aiproj init --gitignore skip
```
