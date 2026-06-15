# Multi-Environment Startup

## Windows 11

Development and installation are currently verified on Windows 11 with PowerShell and Python.

```powershell
python --version
python -m unittest discover -s tests -v
.\install.ps1
aiproj --help
```

If the current terminal cannot find `aiproj` immediately after installation, open a new terminal or refresh `$env:Path` from the user environment.

## Ubuntu, macOS, and WSL

The CLI uses Python standard library only. Expected commands:

```bash
python3 --version
python3 -m unittest discover -s tests -v
sh ./install.sh
aiproj --help
```

The POSIX installer writes to `$HOME/.aiproj` and `$HOME/.local/bin` by default.

## Codex

The installed Skill lives under:

```text
%USERPROFILE%/.codex/skills/project-bootstrap
```

or the platform equivalent of `$CODEX_HOME/skills/project-bootstrap`.

The Skill should be invoked explicitly as `$project-bootstrap` for initialization tasks.

## GitHub

This workspace does not currently have `gh` installed. Automatic GitHub repository creation is not available through the current local shell. Use a remote URL or install/authenticate GitHub CLI to publish directly from Git.
