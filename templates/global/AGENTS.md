# Personal AI Development Conventions

## Local AI Workspace

When a repository contains `.ai-local/`, treat it as a local-only AI workspace:

- `.ai-local/dev/`: disposable experiments, diagnostic scripts, temporary test code, and generated intermediate artifacts.
- `.ai-local/references/`: user-provided reference material. Treat it as read-only unless explicitly instructed otherwise.
- `.ai-local/bak/`: local backups. Never treat backups as the source of truth unless explicitly instructed.
- `.ai-local/scratch-docs/`: AI-generated drafts, plans, investigations, and temporary notes that should not be committed.

These files may be Git-ignored. Use explicit paths or commands such as `rg --hidden --no-ignore` when searching them.

## Project Documentation

Project documentation belongs in the repository root `README.md` and in `docs/`.
When code changes affect documented behavior, architecture, database schema, API contracts, code style, tests, deployment, startup commands, or known issues, update the matching document in the same task.

Keep documentation concise, non-duplicative, and evidence-based. Do not invent project facts.

## Local Overrides

Project-specific personal rules may live in `AGENTS.override.md`. Local overrides must not weaken safety rules unless the user explicitly asks for that project.

