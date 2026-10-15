#!/usr/bin/env python3
"""XData AgentHub local-first alpha CLI. Python 3.10+, standard library only."""
import argparse
import json
import pathlib
import re
import shutil
import platform
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "registry" / "catalog.json"

def items():
    return json.loads(CATALOG.read_text(encoding="utf-8"))["items"]

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
    init = sub.add_parser("init", help="Install a curated local starter profile")
    init.add_argument("--target", default=".")
    init.add_argument("--profile", choices=["developer", "research", "devops"], default="developer")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
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
            agent_roots = {"generic": "skills", "claude": ".claude/skills", "codex": ".agents/skills", "opencode": ".opencode/skills"}
            for item_id in profiles[args.profile]:
                item = entry(item_id)
                src = source(item)
                rel = pathlib.Path(item["path"])
                if rel.is_absolute() or ".." in rel.parts:
                    raise ValueError("Unsafe destination")
                if item["type"] == "skill":
                    rel = pathlib.Path(agent_roots[args.agent]) / item["id"] / "SKILL.md"
                elif item["id"] == "project-agents" and args.agent != "generic":
                    rel = pathlib.Path("AGENTS.md" if args.agent == "codex" else ("CLAUDE.md" if args.agent == "claude" else "AGENTS.md"))
                dest = target / rel
                if dest.exists() or dest.is_symlink():
                    raise ValueError(f"Destination already exists: {dest}")
                parent = dest.parent
                while parent != target.parent:
                    if parent.is_symlink():
                        raise ValueError(f"Symlink destination refused: {parent}")
                    if parent == target:
                        break
                    parent = parent.parent
                planned.append((src, dest))
            for src, dest in planned:
                if args.dry_run:
                    print(f"Would install: {dest}")
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open("x", encoding="utf-8") as handle:
                    handle.write(src.read_text(encoding="utf-8"))
                print(f"Installed: {dest}")
        elif args.cmd == "add":
            item = entry(args.id)
            src = source(item)
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            # Avoid overwriting an existing AGENTS.md and avoid symlink traversal.
            rel = pathlib.Path(item["path"])
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError("Unsafe destination")
            dest = target / rel
            if dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p != target.parent):
                raise ValueError("Symlink destination refused")
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("x", encoding="utf-8") as handle:
                handle.write(src.read_text(encoding="utf-8"))
            print(f"Installed {item['id']} -> {dest}")
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
