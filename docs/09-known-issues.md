# Known Issues and Fix History

## Known Issues

- New terminals may be required before Windows sees the updated user PATH.
- Current shell sessions can run the command shim directly from `%USERPROFILE%/.aiproj/bin-shim/aiproj.cmd`.
- The GitHub CLI is not installed in the current Windows environment, so automatic GitHub repository creation is not available from local `gh`.
- The optional Skill validator may fail if its Python environment lacks `yaml`; use structural checks when that dependency is missing.
- Git-ignored `.ai-local/` files may not appear in some AI-agent file pickers. Use explicit paths or `rg --hidden --no-ignore`.

## Fix History

- Added `--dry-run` and `--dryrun` support to mutating CLI commands.
- Changed Windows installation to add `bin-shim` to the user PATH by default.
- Changed global `AGENTS.md` installation to use a managed block instead of overwriting the whole file.
- Installed the `project-bootstrap` Skill into the local Codex skills directory.
- Moved this tool into its own Git-maintained project directory.

## Operational Notes

- `aiproj doctor --repo .` should pass for this repository after initialization.
- `aiproj docs check --repo .` should pass unless docs were intentionally skipped or moved.
- Release zips in `dist/` are generated artifacts and should be rebuilt from source when needed.
