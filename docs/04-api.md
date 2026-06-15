# API

## Command-Line Interface

The stable user-facing API is the `aiproj` command.

```bash
aiproj --help
aiproj --version
aiproj init [--repo PATH] [--profile auto|generic|node|python|java|springboot|demo] [--skip-doc ID] [--gitignore check|merge|skip] [--dry-run]
aiproj agents refresh [--repo PATH] [--profile ...] [--skip-doc ID] [--dry-run]
aiproj doctor [--repo PATH]
aiproj docs check [--repo PATH] [--strict]
aiproj install-global [--home PATH] [--kit-root PATH] [--force] [--dry-run]
```

`--dryrun` is accepted as an alias for `--dry-run` on commands that mutate files.

## Codex Skill Interface

The Codex Skill name is:

```text
project-bootstrap
```

Typical usage:

```text
Use $project-bootstrap to initialize this repository for AI-assisted development.
```

The Skill calls `skills/project-bootstrap/scripts/bootstrap.py`, which locates the installed or bundled `bin/aiproj.py`.

## Managed File Blocks

The CLI owns only content between these marker pairs:

- `# >>> aiproj local workspace` / `# <<< aiproj local workspace`
- `# >>> aiproj managed instructions` / `# <<< aiproj managed instructions`
- `# >>> aiproj personal conventions` / `# <<< aiproj personal conventions`
- `# >>> aiproj generated ignores` / `# <<< aiproj generated ignores`

Do not change marker names without documenting a migration path.
