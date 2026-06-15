# Database, Tables, and Migrations

## Current Facts

- This project has no application database.
- There are no database tables, migrations, seed files, or schema ownership rules.
- The CLI writes only filesystem artifacts in the target repository and user-level install locations.

## Persistent Files Written by the Tool

- Target repository:
  - `.ai-local/config.json`
  - `README.md`
  - `docs/*.md`
  - `AGENTS.override.md`
  - `.git/info/exclude`
  - optional `.gitignore` managed block
- User install:
  - `%USERPROFILE%/.aiproj/` on Windows by default
  - `$HOME/.aiproj/` on POSIX systems by default
  - `$CODEX_HOME/AGENTS.md` or `%USERPROFILE%/.codex/AGENTS.md`
  - `$CODEX_HOME/skills/project-bootstrap/`

## Migration Notes

- There is no database migration workflow.
- Future config format changes should be handled in `bin/aiproj.py` by reading old `.ai-local/config.json` files safely and writing the current schema.
- Do not silently delete unknown keys from existing config files unless a migration plan is documented first.
