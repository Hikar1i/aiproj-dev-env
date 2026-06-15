# Local Project Instructions

# >>> aiproj managed instructions
## Aiproj Local Workspace

This repository uses A-mode:

- `.ai-local/dev/`: disposable experiments, diagnostic scripts, temporary test code, and generated intermediate artifacts.
- `.ai-local/references/`: user-provided reference material. Treat as read-only unless explicitly instructed otherwise.
- `.ai-local/bak/`: local backups. Do not treat backups as current source unless explicitly instructed.
- `.ai-local/scratch-docs/`: AI-generated drafts, plans, investigations, and temporary notes that should not be committed.

The root `README.md` is the project entry point. Long-term project documentation lives in `docs/`.

If code changes affect documented behavior, update the matching document in the same task. Keep documentation concise and evidence-based. Do not invent missing details.

`.ai-local/` is intentionally excluded through `.git/info/exclude`, so file pickers may not discover it. Use explicit paths or `rg --hidden --no-ignore` when searching local-only files.
# <<< aiproj managed instructions

