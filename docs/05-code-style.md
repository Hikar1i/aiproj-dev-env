# Code Style

## Python

- Use the Python standard library unless a dependency removes substantial complexity.
- Keep `bin/aiproj.py` deterministic and dependency-free.
- Prefer Python APIs compatible with Python 3.9+ unless a newer version requirement is documented.
- Prefer small helper functions over adding framework-style abstractions.
- Use explicit `Path` handling for filesystem operations.
- Write UTF-8 text with LF newlines.
- Keep CLI output concise and script-friendly.

## PowerShell

- Use native PowerShell cmdlets for Windows filesystem operations.
- Avoid destructive recursive deletes unless the target path is clearly resolved and bounded.
- Keep `install.ps1` usable from a standard Windows PowerShell session.

## Shell

- Keep `install.sh` POSIX-sh compatible.
- Prefer conservative file copying and clear install paths.

## Documentation

- Keep user-facing docs practical and evidence-based.
- Do not duplicate long explanations across multiple files.
- Put durable project knowledge in `README.md` and `docs/`.
- Put temporary experiments and notes in `.ai-local/`.
