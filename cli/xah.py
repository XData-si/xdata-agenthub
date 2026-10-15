#!/usr/bin/env python3
"""XData AgentHub local-first alpha CLI. Python 3.10+, standard library only."""
import argparse
import json
import pathlib
import re
import shutil
import platform
import sys
from catalog_schema import validate_catalog
from installed_manifest import file_states, record_install, load_manifest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "registry" / "catalog.json"

def items():
    return validate_catalog(json.loads(CATALOG.read_text(encoding="utf-8")))

def entry(item_id):
    for item in items():
        if item["id"] == item_id:
            return item
    raise ValueError(f"Unknown item: {item_id}")

def source(item):
    path = (ROOT / item["path"]).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError("Unsafe or missing catalog path")
    return path

def skill_files(item):
    """Inspect complete local skill package without following symlinks."""
    main_file = source(item)
    if item["type"] != "skill":
        return [(main_file, pathlib.Path(main_file.name))]
    root = main_file.parent
    if pathlib.Path(ROOT / item["path"]).is_symlink() or root.is_symlink():
        raise ValueError("Symlinked skill entry refused")
    found = []
    for candidate in sorted(root.rglob("*")):
        if candidate.is_symlink():
            raise ValueError(f"Symlink in skill package refused: {candidate}")
        if candidate.is_dir():
            continue
        if not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Unsafe skill package entry: {candidate}")
        found.append((candidate, candidate.relative_to(root)))
    return found


def install_plan(item, target, agent):
    roots = {"generic": "skills", "claude": ".claude/skills",
             "codex": ".agents/skills", "opencode": ".opencode/skills"}
    if item["type"] == "skill":
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"]):
            raise ValueError("Unsafe skill identifier")
        base = pathlib.Path(roots[agent]) / item["id"]
        package = skill_files(item)
        if not any(rel == pathlib.Path("SKILL.md") for _, rel in package):
            raise ValueError("Missing SKILL.md in skill package")
        planned = [(src, target / base / rel) for src, rel in package]
    else:
        rel = pathlib.Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts or "\\" in item["path"]:
            raise ValueError("Unsafe destination")
        if item["id"] == "project-agents" and agent != "generic":
            rel = pathlib.Path("CLAUDE.md" if agent == "claude" else "AGENTS.md")
        planned = [(source(item), target / rel)]
    for _, dest in planned:
        if not dest.is_relative_to(target):
            raise ValueError("Destination escapes target")
        if dest.exists() or dest.is_symlink():
            raise ValueError(f"Destination already exists: {dest}")
        for parent in dest.parents:
            if parent == target.parent:
                break
            if parent.is_symlink():
                raise ValueError(f"Symlink destination refused: {parent}")
    return planned


def copy_plan(planned, dry_run=False):
    if dry_run:
        for _, dest in planned:
            print(f"Would install: {dest}")
        return
    written = []
    try:
        for src, dest in planned:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as handle:
                handle.write(src.read_bytes())
            written.append(dest)
            print(f"Installed: {dest}")
    except OSError:
        for dest in reversed(written):
            dest.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(prog="xah", description="XData AgentHub — portable agent resources")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List catalog items")
    search = sub.add_parser("search", help="Search local catalog")
    search.add_argument("query")
    inspect = sub.add_parser("inspect", help="Print a catalog item")
    inspect.add_argument("id")
    add = sub.add_parser("add", help="Copy a vetted template into a project")
    add.add_argument("id")
    add.add_argument("--target", default=".")
    add.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
    init = sub.add_parser("init", help="Install a curated local starter profile")
    init.add_argument("--target", default=".")
    init.add_argument("--profile", choices=["developer", "research", "devops"], default="developer")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
    update = sub.add_parser("update", help="Preview updates to a tracked item (read-only)")
    update.add_argument("id")
    update.add_argument("--target", default=".")
    update.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
    update.add_argument("--dry-run", action="store_true", required=True)
    status = sub.add_parser("status", help="Report installed-file modification states")
    status.add_argument("--target", default=".")
    sub.add_parser("doctor", help="Check Python version, catalog and template paths")
    audit = sub.add_parser("audit", help="Heuristic inspection of markdown in a target")
    audit.add_argument("--target", default=".")
    args = parser.parse_args()
    try:
        if args.cmd in ("list", "search"):
            for item in items():
                if args.cmd == "list" or args.query.lower() in json.dumps(item).lower():
                    print(f'{item["id"]:20} {item["type"]:12} {item["description"]}')
        elif args.cmd == "inspect":
            item = entry(args.id)
            print(f'# {item["name"]} ({item["id"]})\nSource: {item["source"]}\nLicense: {item["license"]}\n')
            print(source(item).read_text(encoding="utf-8"))
        elif args.cmd == "update":
            from update_plan import plan_update
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            item = entry(args.id)
            roots = {"generic": "skills", "claude": ".claude/skills", "codex": ".agents/skills", "opencode": ".opencode/skills"}
            if item["type"] == "skill":
                base = pathlib.Path(roots[args.agent]) / item["id"]
                planned = [(src, target / base / rel) for src, rel in skill_files(item)]
            else:
                rel = pathlib.Path(item["path"])
                if rel.is_absolute() or ".." in rel.parts or "\\\\" in item["path"]:
                    raise ValueError("Unsafe destination")
                if item["id"] == "project-agents" and args.agent != "generic":
                    rel = pathlib.Path("CLAUDE.md" if args.agent == "claude" else "AGENTS.md")
                planned = [(source(item), target / rel)]
            result = plan_update(target, args.id, planned)
            for action, rel in result:
                print(f"{action:10} {rel}")
            if any(action == "conflict" for action, _ in result):
                return 2
        elif args.cmd == "status":
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            for rel, state in file_states(target).items():
                print(f"{state:10} {rel}")
        elif args.cmd == "doctor":
            print(f"Python: {platform.python_version()}")
            print(f"Catalog: {CATALOG}")
            if sys.version_info < (3, 10):
                raise ValueError("Python 3.10+ required")
            catalog = items()
            seen = set()
            for item in catalog:
                if item["id"] in seen:
                    raise ValueError("Duplicate catalog ID: " + item["id"])
                seen.add(item["id"])
                source(item)
                if item["type"] == "skill":
                    skill_files(item)
            print(f"OK: {len(catalog)} catalog entries, all local paths valid")
        elif args.cmd == "init":
            profiles = {
                "developer": ["project-agents", "code-review", "documentation"],
                "research": ["project-agents", "research-agent", "documentation"],
                "devops": ["project-agents", "devops-review", "code-review"],
            }
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            planned = []
            ownership = []
            for item_id in profiles[args.profile]:
                item_plan = install_plan(entry(item_id), target, args.agent)
                planned.extend(item_plan)
                ownership.extend((item_id, dest) for _, dest in item_plan)
            if args.dry_run:
                copy_plan(planned, True)
            else:
                from installed_manifest import record_installs
                record_installs(target, ownership, planned, copy_plan)
        elif args.cmd == "add":
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            planned = install_plan(entry(args.id), target, args.agent)
            from installed_manifest import record_installs
            record_installs(target, [(args.id, dest) for _, dest in planned], planned, copy_plan)
        elif args.cmd == "audit":
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            actionable = 0
            examples = 0
            patterns = [r"curl\s+[^\n|]+\|\s*(?:bash|sh)\b",
                        r"wget\s+[^\n|]+\|\s*(?:bash|sh)\b",
                        r"rm\s+-rf\s+/"]
            # An explicit marker applies only to the next fenced code block.
            # Unmarked code blocks remain actionable; documentation is not
            # automatically trusted merely because it is fenced.
            for file in target.rglob("*.md"):
                if file.is_symlink() or not file.is_file() or file.stat().st_size > 1_000_000:
                    continue
                lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
                marked_next = False
                in_fence = False
                fence_marker = ""
                example_fence = False
                for line_no, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not in_fence and stripped == "<!-- xah-audit: fixture -->":
                        marked_next = True
                        continue
                    fence = re.match(r"^\s*(`{3,}|~{3,})", line)
                    if fence:
                        delimiter = fence.group(1)
                        if not in_fence:
                            in_fence = True
                            fence_marker = delimiter
                            example_fence = marked_next
                            marked_next = False
                        elif delimiter[0] == fence_marker[0] and len(delimiter) >= len(fence_marker):
                            in_fence = False
                            example_fence = False
                        continue
                    if not in_fence and stripped:
                        marked_next = False
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            if in_fence and example_fence:
                                print(f"INFO: {file}:{line_no}: documented test fixture ({pattern})")
                                examples += 1
                            else:
                                print(f"REVIEW: {file}:{line_no}: matched {pattern}")
                                actionable += 1
            print(f"Heuristic audit: {actionable} review finding(s), {examples} fixture example(s). Not a security certification.")
            if actionable:
                return 2
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
