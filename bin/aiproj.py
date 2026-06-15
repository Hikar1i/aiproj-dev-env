#!/usr/bin/env python3
"""Personal AI project bootstrap CLI.

This tool is intentionally dependency-free so it can run on Windows, macOS,
Linux, WSL, and inside most coding-agent environments.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


VERSION = "0.1.0"
LOCAL_ROOT = ".ai-local"
CONFIG_REL = f"{LOCAL_ROOT}/config.json"
MANAGED_EXCLUDE = "aiproj local workspace"
MANAGED_AGENTS = "aiproj managed instructions"
MANAGED_GLOBAL_AGENTS = "aiproj personal conventions"
MANAGED_GITIGNORE = "aiproj generated ignores"


DOCS = [
    {
        "id": "project-background",
        "path": "docs/01-project-background.md",
        "title": "Project Background and Business Goals",
        "purpose": "Record verified project context, users, business goals, and success criteria.",
    },
    {
        "id": "architecture",
        "path": "docs/02-architecture.md",
        "title": "Architecture",
        "purpose": "Record the current system architecture, module boundaries, dependencies, and important design decisions.",
    },
    {
        "id": "database",
        "path": "docs/03-database.md",
        "title": "Database, Tables, and Migrations",
        "purpose": "Record database engines, schema ownership, migration commands, table notes, and data caveats.",
    },
    {
        "id": "api",
        "path": "docs/04-api.md",
        "title": "API",
        "purpose": "Record public and internal API contracts, request/response conventions, auth, and compatibility notes.",
    },
    {
        "id": "code-style",
        "path": "docs/05-code-style.md",
        "title": "Code Style",
        "purpose": "Record project-specific coding rules that cannot be reliably inferred from the codebase.",
    },
    {
        "id": "testing-strategy",
        "path": "docs/06-testing-strategy.md",
        "title": "Testing Strategy",
        "purpose": "Record test levels, commands, coverage expectations, fixtures, and known testing limitations.",
    },
    {
        "id": "deployment",
        "path": "docs/07-deployment.md",
        "title": "Deployment",
        "purpose": "Record deployment targets, release flow, required services, rollback notes, and operational checks.",
    },
    {
        "id": "environments",
        "path": "docs/08-environments.md",
        "title": "Multi-Environment Startup",
        "purpose": "Record how to start the project in local, test, staging, and production-like environments.",
    },
    {
        "id": "known-issues",
        "path": "docs/09-known-issues.md",
        "title": "Known Issues and Fix History",
        "purpose": "Record traps, incident notes, recurring failures, and verified solutions.",
    },
]

DOC_ALIASES = {
    "background": "project-background",
    "business": "project-background",
    "project": "project-background",
    "arch": "architecture",
    "db": "database",
    "schema": "database",
    "apis": "api",
    "style": "code-style",
    "code": "code-style",
    "test": "testing-strategy",
    "testing": "testing-strategy",
    "tests": "testing-strategy",
    "deploy": "deployment",
    "env": "environments",
    "environment": "environments",
    "issues": "known-issues",
    "pitfalls": "known-issues",
}


LOCAL_DIRS = [
    f"{LOCAL_ROOT}/dev/scripts",
    f"{LOCAL_ROOT}/dev/experiments",
    f"{LOCAL_ROOT}/dev/fixtures",
    f"{LOCAL_ROOT}/dev/output",
    f"{LOCAL_ROOT}/dev/tmp",
    f"{LOCAL_ROOT}/references/documents",
    f"{LOCAL_ROOT}/references/images",
    f"{LOCAL_ROOT}/references/examples",
    f"{LOCAL_ROOT}/references/vendor",
    f"{LOCAL_ROOT}/bak/code",
    f"{LOCAL_ROOT}/bak/config",
    f"{LOCAL_ROOT}/bak/database",
    f"{LOCAL_ROOT}/bak/bootstrap",
    f"{LOCAL_ROOT}/scratch-docs/requirements",
    f"{LOCAL_ROOT}/scratch-docs/design",
    f"{LOCAL_ROOT}/scratch-docs/plans",
    f"{LOCAL_ROOT}/scratch-docs/tests",
    f"{LOCAL_ROOT}/scratch-docs/research",
    f"{LOCAL_ROOT}/scratch-docs/decisions",
    f"{LOCAL_ROOT}/scratch-docs/archive",
    f"{LOCAL_ROOT}/logs",
]


GITIGNORE_RULES = {
    "generic": [
        ".DS_Store",
        "Thumbs.db",
        "*.swp",
        "*.swo",
        ".env",
        ".env.*",
        "!.env.example",
    ],
    "node": [
        "node_modules/",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
        "pnpm-debug.log*",
        "dist/",
        "build/",
        "coverage/",
        ".next/",
        ".nuxt/",
        ".turbo/",
    ],
    "python": [
        "__pycache__/",
        "*.py[cod]",
        ".Python",
        ".venv/",
        "venv/",
        "env/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        ".coverage",
        "htmlcov/",
        "dist/",
        "build/",
        "*.egg-info/",
    ],
    "java": [
        "target/",
        "build/",
        "*.class",
        "*.jar",
        "*.war",
        "*.ear",
        ".gradle/",
        ".mvn/timing.properties",
    ],
}


@dataclass
class Reporter:
    dry_run: bool = False
    created: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def _prefix(self, action: str) -> str:
        return f"DRY-RUN {action}" if self.dry_run else action

    def create(self, path: Path) -> None:
        self.created.append(str(path))
        print(f"[{self._prefix('CREATE')}] {path}")

    def modify(self, path: Path) -> None:
        self.modified.append(str(path))
        print(f"[{self._prefix('MODIFY')}] {path}")

    def skip(self, path: str | Path, reason: str) -> None:
        self.skipped.append(f"{path} ({reason})")
        print(f"[SKIP] {path} - {reason}")

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"[WARN] {message}")

    def summary(self) -> None:
        print()
        print("Summary:")
        print(f"  created: {len(self.created)}")
        print(f"  modified: {len(self.modified)}")
        print(f"  skipped:  {len(self.skipped)}")
        print(f"  warnings: {len(self.warnings)}")


def now_utc() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat()


def run(cmd: list[str], cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def is_git_repo(path: Path) -> bool:
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=path)
    return result.returncode == 0


def git_root(path: Path) -> Path | None:
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=path)
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def resolve_repo(value: str | None, allow_non_git: bool = False) -> tuple[Path, bool]:
    base = Path(value or ".").expanduser().resolve()
    root = git_root(base)
    if root:
        return root, True
    if allow_non_git:
        return base, False
    raise SystemExit(
        f"{base} is not inside a Git repository. Run 'git init' first, "
        "or pass --allow-non-git for a file-only bootstrap."
    )


def rel(repo: Path, path: str | Path) -> Path:
    return repo / Path(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, reporter: Reporter, overwrite: bool = True) -> None:
    if path.exists() and not overwrite:
        reporter.skip(path, "already exists")
        return
    old = read_text(path) if path.exists() else None
    if old == content:
        reporter.skip(path, "already up to date")
        return
    if old is None:
        reporter.create(path)
    else:
        reporter.modify(path)
    if not reporter.dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


def ensure_dir(path: Path, reporter: Reporter) -> None:
    if path.is_dir():
        reporter.skip(path, "directory exists")
        return
    reporter.create(path)
    if not reporter.dry_run:
        path.mkdir(parents=True, exist_ok=True)


def normalize_skip_docs(values: Iterable[str]) -> set[str]:
    result: set[str] = set()
    valid = {doc["id"] for doc in DOCS}
    for raw in values:
        key = raw.strip().lower().replace("_", "-")
        key = DOC_ALIASES.get(key, key)
        if key not in valid:
            raise SystemExit(f"Unknown document id for --skip-doc: {raw}")
        result.add(key)
    return result


def detect_profile(repo: Path) -> str:
    if (repo / "package.json").exists():
        return "node"
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists() or (repo / "setup.py").exists():
        return "python"
    pom = repo / "pom.xml"
    if pom.exists():
        content = read_text(pom)[:20000]
        return "springboot" if "spring-boot" in content.lower() else "java"
    if (repo / "build.gradle").exists() or (repo / "build.gradle.kts").exists() or (repo / "settings.gradle").exists():
        return "java"
    return "generic"


def profile_rules(profile: str) -> list[str]:
    effective = "java" if profile == "springboot" else profile
    rules = list(GITIGNORE_RULES["generic"])
    rules.extend(GITIGNORE_RULES.get(effective, []))
    seen: set[str] = set()
    deduped: list[str] = []
    for rule in rules:
        if rule not in seen:
            deduped.append(rule)
            seen.add(rule)
    return deduped


def managed_block(name: str, body: str) -> str:
    body = body.strip("\n")
    return f"# >>> {name}\n{body}\n# <<< {name}\n"


def replace_managed_block(existing: str, name: str, body: str) -> str:
    start = f"# >>> {name}"
    end = f"# <<< {name}"
    block = managed_block(name, body)
    if start in existing and end in existing:
        before, rest = existing.split(start, 1)
        _, after = rest.split(end, 1)
        return before.rstrip() + "\n\n" + block + after.lstrip("\n")
    separator = "\n\n" if existing.strip() else ""
    return existing.rstrip() + separator + block


def update_managed_file(path: Path, name: str, body: str, reporter: Reporter, header: str = "") -> None:
    existing = read_text(path) if path.exists() else header
    content = replace_managed_block(existing, name, body)
    write_text(path, content, reporter, overwrite=True)


def tracked_paths(repo: Path, paths: list[str]) -> list[str]:
    result = run(["git", "ls-files", "--", *paths], cwd=repo)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def load_config(repo: Path) -> dict:
    path = rel(repo, CONFIG_REL)
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}


def write_config(repo: Path, profile: str, skipped_docs: set[str], reporter: Reporter) -> None:
    config = {
        "tool": "aiproj",
        "version": VERSION,
        "layout": "a-mode",
        "local_root": LOCAL_ROOT,
        "profile": profile,
        "skipped_docs": sorted(skipped_docs),
        "updated_at": now_utc(),
    }
    write_text(rel(repo, CONFIG_REL), json.dumps(config, indent=2) + "\n", reporter, overwrite=True)


def project_name(repo: Path) -> str:
    return repo.name or "Project"


def root_readme_template(name: str) -> str:
    return f"""# {name}

## Overview

Record the verified project purpose here. Keep this README concise and link to deeper documents under `docs/`.

## Documentation

- `docs/01-project-background.md`: project context and business goals
- `docs/02-architecture.md`: architecture and module boundaries
- `docs/03-database.md`: database, tables, and migrations
- `docs/04-api.md`: API contracts
- `docs/05-code-style.md`: project-specific code style
- `docs/06-testing-strategy.md`: testing strategy
- `docs/07-deployment.md`: deployment notes
- `docs/08-environments.md`: multi-environment startup
- `docs/09-known-issues.md`: known issues and fixes

## Local AI Workspace

Personal AI-agent scratch work lives under `.ai-local/` and is excluded through `.git/info/exclude`.
Do not commit `.ai-local/` or `AGENTS.override.md` unless the team explicitly adopts them.
"""


def doc_template(title: str, purpose: str) -> str:
    return f"""# {title}

Purpose: {purpose}

Status: Draft

## Current Facts

- Unknown. Replace this line only with verified information from code, runtime output, project owners, or supplied references.

## Maintenance Notes

- Update this document when code changes alter the facts it records.
- Keep content concise and avoid duplicating details owned by another document.
- Do not invent missing details. Mark unknown information as `Unknown` and explain what evidence is needed.
"""


def global_agents_template() -> str:
    return """## Personal AI Development Conventions

### Local AI Workspace

When a repository contains `.ai-local/`, treat it as a local-only AI workspace:

- `.ai-local/dev/`: disposable experiments, diagnostic scripts, temporary test code, and generated intermediate artifacts.
- `.ai-local/references/`: user-provided reference material. Treat it as read-only unless explicitly instructed otherwise.
- `.ai-local/bak/`: local backups. Never treat backups as the source of truth unless explicitly instructed.
- `.ai-local/scratch-docs/`: AI-generated drafts, plans, investigations, and temporary notes that should not be committed.

These files may be Git-ignored. Use explicit paths or commands such as `rg --hidden --no-ignore` when searching them.

### Project Documentation

Project documentation belongs in the repository root `README.md` and in `docs/`.
When code changes affect documented behavior, architecture, database schema, API contracts, code style, tests, deployment, startup commands, or known issues, update the matching document in the same task.

Keep documentation concise, non-duplicative, and evidence-based. Do not invent project facts.

### Local Overrides

Project-specific personal rules may live in `AGENTS.override.md`. Local overrides must not weaken safety rules unless the user explicitly asks for that project.
"""


def agents_override_body(profile: str, skipped_docs: set[str]) -> str:
    skipped = ", ".join(sorted(skipped_docs)) if skipped_docs else "none"
    doc_lines = "\n".join(f"- `{doc['path']}`: {doc['purpose']}" for doc in DOCS)
    return f"""## Aiproj Local Workspace

This repository uses A-mode:

- `.ai-local/dev/`: disposable experiments, diagnostic scripts, temporary test code, and generated intermediate artifacts.
- `.ai-local/references/`: user-provided reference material. Treat as read-only unless explicitly instructed otherwise.
- `.ai-local/bak/`: local backups. Do not treat backups as current source unless explicitly instructed.
- `.ai-local/scratch-docs/`: AI-generated drafts, plans, investigations, and temporary notes that should not be committed.

The root `README.md` is the project entry point. Long-term project documentation lives in `docs/`.

Detected or selected profile: `{profile}`.
Project-local skipped documentation duties: `{skipped}`.

## Documentation Map

{doc_lines}

## Documentation Maintenance Rules

- If code changes affect a document listed above, update that document in the same task unless its document id is listed as skipped for this project.
- Keep each document focused on its own responsibility. Prefer links over duplicated content.
- Keep documentation concise and evidence-based. Do not invent missing details.
- Use `Unknown` for facts that are not yet verified.

## Searching Local Workspace Files

`.ai-local/` is intentionally excluded through `.git/info/exclude`, so file pickers may not discover it. Use explicit paths or `rg --hidden --no-ignore` when searching local-only files.
"""


def update_git_exclude(repo: Path, reporter: Reporter) -> None:
    git_dir = repo / ".git"
    if not git_dir.exists():
        reporter.warn("No .git directory found; skipping .git/info/exclude.")
        return
    exclude_path = git_dir / "info" / "exclude"
    body = f"/{LOCAL_ROOT}/\n/AGENTS.override.md"
    update_managed_file(exclude_path, MANAGED_EXCLUDE, body, reporter)


def update_gitignore(repo: Path, profile: str, mode: str, reporter: Reporter) -> None:
    path = repo / ".gitignore"
    rules = profile_rules(profile)
    body = "\n".join(rules)
    if mode == "skip":
        reporter.skip(path, "--gitignore skip")
        return
    if mode == "check" and path.exists():
        reporter.skip(path, "existing .gitignore left unchanged; use --gitignore merge to update managed block")
        return
    update_managed_file(path, MANAGED_GITIGNORE, body, reporter)


def init_command(args: argparse.Namespace) -> int:
    reporter = Reporter(dry_run=args.dry_run or args.dryrun)
    repo, has_git = resolve_repo(args.repo, allow_non_git=args.allow_non_git)
    skipped_docs = normalize_skip_docs(args.skip_doc or [])
    profile = detect_profile(repo) if args.profile == "auto" else args.profile

    if has_git:
        tracked = tracked_paths(repo, [LOCAL_ROOT, "AGENTS.override.md"])
        if tracked:
            reporter.warn("These local-only paths are already tracked by Git: " + ", ".join(tracked))
            reporter.warn("Ignoring tracked files will not untrack them. Review before committing.")

    for item in LOCAL_DIRS:
        ensure_dir(rel(repo, item), reporter)

    write_config(repo, profile, skipped_docs, reporter)
    write_text(repo / "README.md", root_readme_template(project_name(repo)), reporter, overwrite=False)

    for doc in DOCS:
        if doc["id"] in skipped_docs:
            reporter.skip(repo / doc["path"], f"document id skipped: {doc['id']}")
            continue
        write_text(
            repo / doc["path"],
            doc_template(doc["title"], doc["purpose"]),
            reporter,
            overwrite=False,
        )

    update_managed_file(
        repo / "AGENTS.override.md",
        MANAGED_AGENTS,
        agents_override_body(profile, skipped_docs),
        reporter,
        header="# Local Project Instructions\n\n",
    )

    if has_git:
        update_git_exclude(repo, reporter)
    else:
        reporter.warn("Repository is not a Git repo; local exclude rules were not written.")

    update_gitignore(repo, profile, args.gitignore, reporter)
    reporter.summary()
    return 0


def agents_refresh_command(args: argparse.Namespace) -> int:
    reporter = Reporter(dry_run=args.dry_run or args.dryrun)
    repo, _ = resolve_repo(args.repo, allow_non_git=args.allow_non_git)
    config = load_config(repo)
    skipped_docs = set(config.get("skipped_docs", []))
    if args.skip_doc:
        skipped_docs = normalize_skip_docs(args.skip_doc)
    profile = args.profile if args.profile != "auto" else config.get("profile") or detect_profile(repo)
    update_managed_file(
        repo / "AGENTS.override.md",
        MANAGED_AGENTS,
        agents_override_body(profile, skipped_docs),
        reporter,
        header="# Local Project Instructions\n\n",
    )
    reporter.summary()
    return 0


def doctor_command(args: argparse.Namespace) -> int:
    repo, has_git = resolve_repo(args.repo, allow_non_git=True)
    config = load_config(repo)
    profile = config.get("profile") or (detect_profile(repo) if repo.exists() else "unknown")
    print(f"aiproj version: {VERSION}")
    print(f"repo: {repo}")
    print(f"git repository: {'yes' if has_git else 'no'}")
    print(f"profile: {profile}")
    checks = [
        (repo / LOCAL_ROOT, "local workspace"),
        (repo / "README.md", "root README"),
        (repo / "docs", "docs directory"),
        (repo / "AGENTS.override.md", "local agent override"),
    ]
    ok = True
    for path, label in checks:
        exists = path.exists()
        ok = ok and exists
        print(f"{label}: {'ok' if exists else 'missing'} ({path})")
    if has_git:
        exclude = repo / ".git" / "info" / "exclude"
        has_block = exclude.exists() and f"# >>> {MANAGED_EXCLUDE}" in read_text(exclude)
        ok = ok and has_block
        print(f"git info exclude: {'ok' if has_block else 'missing managed block'} ({exclude})")
    expected_docs = [doc for doc in DOCS if doc["id"] not in set(config.get("skipped_docs", []))]
    missing_docs = [doc["path"] for doc in expected_docs if not (repo / doc["path"]).exists()]
    if missing_docs:
        ok = False
        print("missing docs:")
        for item in missing_docs:
            print(f"  - {item}")
    else:
        print("docs templates: ok")
    return 0 if ok else 1


def is_code_file(path: str) -> bool:
    suffixes = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".kt",
        ".go",
        ".rs",
        ".cs",
        ".php",
        ".rb",
        ".c",
        ".cc",
        ".cpp",
        ".h",
        ".hpp",
        ".sql",
        ".yml",
        ".yaml",
        ".toml",
        ".json",
        ".xml",
        ".gradle",
    }
    return Path(path).suffix.lower() in suffixes


def docs_check_command(args: argparse.Namespace) -> int:
    repo, has_git = resolve_repo(args.repo, allow_non_git=args.allow_non_git)
    config = load_config(repo)
    skipped = set(config.get("skipped_docs", []))
    missing = [doc["path"] for doc in DOCS if doc["id"] not in skipped and not (repo / doc["path"]).exists()]
    if missing:
        print("Missing required docs:")
        for item in missing:
            print(f"  - {item}")
    else:
        print("Required docs are present.")

    needs_doc_update = False
    if has_git:
        status = run(["git", "status", "--porcelain"], cwd=repo)
        changed = [line[3:] for line in status.stdout.splitlines() if len(line) > 3]
        code_changed = [item for item in changed if is_code_file(item) and not item.startswith("docs/")]
        docs_changed = [item for item in changed if item == "README.md" or item.startswith("docs/")]
        if code_changed and not docs_changed:
            needs_doc_update = True
            print("Code/config files changed but no README.md/docs change is staged or pending:")
            for item in code_changed[:20]:
                print(f"  - {item}")
            if len(code_changed) > 20:
                print(f"  - ... {len(code_changed) - 20} more")
        elif code_changed:
            print("Code/config changes and documentation changes are both present.")
        else:
            print("No code/config changes detected in git status.")
    else:
        print("Not a Git repository; skipped change-based docs check.")

    failed = bool(missing) or (args.strict and needs_doc_update)
    if needs_doc_update and not args.strict:
        print("Hint: pass --strict to make this condition fail the command.")
    return 1 if failed else 0


def kit_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_tree(src: Path, dst: Path, force: bool, reporter: Reporter) -> None:
    if not src.exists():
        reporter.warn(f"Source not found: {src}")
        return
    if dst.exists() and force:
        reporter.modify(dst)
        if not reporter.dry_run:
            shutil.rmtree(dst)
            shutil.copytree(src, dst)
        return
    if dst.exists():
        reporter.skip(dst, "already exists; pass --force to replace")
        return
    reporter.create(dst)
    if not reporter.dry_run:
        shutil.copytree(src, dst)


def install_global_command(args: argparse.Namespace) -> int:
    reporter = Reporter(dry_run=args.dry_run or args.dryrun)
    home = Path(args.home).expanduser().resolve() if args.home else Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
    global_agents = codex_home / "AGENTS.md"
    skill_dst = codex_home / "skills" / "project-bootstrap"
    kit = Path(args.kit_root).expanduser().resolve() if args.kit_root else kit_root()

    update_managed_file(
        global_agents,
        MANAGED_GLOBAL_AGENTS,
        global_agents_template(),
        reporter,
        header="# Codex Global Instructions\n\n",
    )
    copy_tree(kit / "skills" / "project-bootstrap", skill_dst, args.force, reporter)
    reporter.summary()
    print(f"Codex home: {codex_home}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aiproj",
        description="Initialize a personal AI-assisted development workspace.",
    )
    parser.add_argument("--version", action="version", version=f"aiproj {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize the current repository")
    init.add_argument("--repo", default=".", help="repository path; defaults to current directory")
    init.add_argument("--profile", default="auto", choices=["auto", "generic", "node", "python", "java", "springboot", "demo"])
    init.add_argument("--skip-doc", action="append", default=[], help="skip a project doc id for this repository")
    init.add_argument("--gitignore", choices=["check", "merge", "skip"], default="check", help="how to handle .gitignore")
    init.add_argument("--dry-run", action="store_true", help="preview changes without writing files")
    init.add_argument("--dryrun", action="store_true", help="alias for --dry-run")
    init.add_argument("--allow-non-git", action="store_true", help="allow bootstrapping a directory before git init")
    init.set_defaults(func=init_command)

    agents = sub.add_parser("agents", help="manage local agent instruction files")
    agents_sub = agents.add_subparsers(dest="agents_command", required=True)
    refresh = agents_sub.add_parser("refresh", help="refresh AGENTS.override.md managed block")
    refresh.add_argument("--repo", default=".")
    refresh.add_argument("--profile", default="auto", choices=["auto", "generic", "node", "python", "java", "springboot", "demo"])
    refresh.add_argument("--skip-doc", action="append", default=[])
    refresh.add_argument("--dry-run", action="store_true")
    refresh.add_argument("--dryrun", action="store_true")
    refresh.add_argument("--allow-non-git", action="store_true")
    refresh.set_defaults(func=agents_refresh_command)

    doctor = sub.add_parser("doctor", help="check aiproj initialization status")
    doctor.add_argument("--repo", default=".")
    doctor.set_defaults(func=doctor_command)

    docs = sub.add_parser("docs", help="documentation utilities")
    docs_sub = docs.add_subparsers(dest="docs_command", required=True)
    docs_check = docs_sub.add_parser("check", help="check required docs and optional code/docs drift")
    docs_check.add_argument("--repo", default=".")
    docs_check.add_argument("--strict", action="store_true", help="fail if code changed without docs changes")
    docs_check.add_argument("--allow-non-git", action="store_true")
    docs_check.set_defaults(func=docs_check_command)

    install = sub.add_parser("install-global", help="install global AGENTS.md and the Codex Skill")
    install.add_argument("--home", help="home directory override for testing")
    install.add_argument("--kit-root", help="kit root override for testing")
    install.add_argument("--force", action="store_true", help="replace existing global files")
    install.add_argument("--dry-run", action="store_true")
    install.add_argument("--dryrun", action="store_true")
    install.set_defaults(func=install_global_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
