# Deployment

## Local Installation

Windows:

```powershell
.\install.ps1
```

POSIX shell:

```bash
sh ./install.sh
```

The installer copies this kit to the user-level install directory, installs or refreshes the Codex Skill, and updates global Codex instructions.

## Package Build

Create a portable zip archive:

```bash
python tools/build_zip.py
```

The archive is written under `dist/`. Git ignores `dist/` because packages are generated artifacts.

## Release Checklist

1. Run `python -m unittest discover -s tests -v`.
2. Run `python bin/aiproj.py init --repo . --dry-run`.
3. Run `python tools/build_zip.py`.
4. Install from the checkout on Windows with `.\install.ps1`.
5. Verify `aiproj --version` in a refreshed terminal.
6. Commit source and documentation changes.
7. Publish to GitHub when a remote repository is available.

## Rollback

- Remove or rename `%USERPROFILE%/.aiproj` to disable the installed CLI.
- Remove `%USERPROFILE%/.aiproj/bin-shim` from the user PATH if command discovery should be disabled.
- Remove `%USERPROFILE%/.codex/skills/project-bootstrap` to uninstall the Skill.
- Remove the `aiproj personal conventions` block from `%USERPROFILE%/.codex/AGENTS.md` to remove global instructions.
