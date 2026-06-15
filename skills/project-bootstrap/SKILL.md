---
name: project-bootstrap
description: Initialize or repair a local AI-assisted development workspace in a new or existing repository using the user's aiproj conventions. Use when the user asks to bootstrap, initialize, standardize, repair, or prepare a project for Codex-assisted development, including creating `.ai-local/`, root `README.md`, `docs/` documentation templates, `AGENTS.override.md`, `.git/info/exclude`, and safe `.gitignore` handling.
---

# Project Bootstrap

## Workflow

1. Locate the repository root with `git rev-parse --show-toplevel` when possible. If the user explicitly asks to initialize a non-Git directory, pass `--allow-non-git`.
2. Preview the operation first unless the user already asked to apply it directly:

   ```bash
   python scripts/bootstrap.py init --repo <repo> --dry-run
   ```

3. Apply the initialization:

   ```bash
   python scripts/bootstrap.py init --repo <repo>
   ```

4. If the user says the project is a demo, prototype, or intentionally has no tests, pass:

   ```bash
   --profile demo --skip-doc testing-strategy
   ```

5. Verify the result:

   ```bash
   python scripts/bootstrap.py doctor --repo <repo>
   python scripts/bootstrap.py docs check --repo <repo>
   ```

6. Summarize created, modified, skipped, and warning items. Do not manually reproduce the bootstrap steps unless the CLI fails and the user wants a fallback.

## Rules

- Default to A-mode: `.ai-local/` for local-only AI workspace, root `README.md`, and project docs under `docs/`.
- Do not place generated project documentation under `.ai-local/` when it should become durable project knowledge.
- Do not overwrite existing `README.md` or `docs/*.md` files.
- Treat `.ai-local/references/` as read-only unless the user explicitly asks to modify it.
- Use `--dry-run` or `--dryrun` to preview potentially broad changes.
- Use `--gitignore merge` only when the user wants the managed `.gitignore` block added to an existing `.gitignore`.

## Useful Commands

```bash
python scripts/bootstrap.py --help
python scripts/bootstrap.py init --help
python scripts/bootstrap.py init --repo <repo> --dry-run
python scripts/bootstrap.py init --repo <repo> --profile demo --skip-doc testing-strategy
python scripts/bootstrap.py agents refresh --repo <repo>
python scripts/bootstrap.py doctor --repo <repo>
python scripts/bootstrap.py docs check --repo <repo> --strict
```
