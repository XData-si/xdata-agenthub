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
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--kind", choices=["skill", "instruction", "workflow", "agent"])
    search.add_argument("--tag")
    search.add_argument("--agent")
    search.add_argument("--license")
    search.add_argument("--provenance")
    search.add_argument("--json", action="store_true", help="Emit JSON array")
    inspect = sub.add_parser("inspect", help="Print a catalog item")
    inspect.add_argument("id")
    inspect.add_argument("--target", help="Inspect installed-file states in this project")
    inspect.add_argument("--json", action="store_true", help="Emit structured metadata")
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
    mode = update.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    refresh = sub.add_parser("catalog-refresh", help="Explicit pinned HTTPS catalog update")
    refresh.add_argument("--url", required=True)
    refresh.add_argument("--revision", required=True)
    refresh.add_argument("--sha256", required=True)
    refresh.add_argument("--approve", action="store_true")
    refresh.add_argument("--offline", action="store_true")
    status = sub.add_parser("status", help="Report installed-file modification states")
    status.add_argument("--target", default=".")
    recovery = sub.add_parser("recovery", help="Read-only inspection of update journals")
    recovery.add_argument("--target", default=".")
    recovery.add_argument("--json", action="store_true")
    recovery.add_argument("--rollback", metavar="TRANSACTION_ID",
                          help="Explicitly restore verified original files; refuses existing locks")
    recovery.add_argument("--lock-status", action="store_true",
                          help="Read-only writer lock diagnostic; never removes a lock")
    recovery.add_argument("--rollback-plan", metavar="TRANSACTION_ID",
                          help="Read-only rollback eligibility and file action plan")
    sub.add_parser("doctor", help="Check Python version, catalog and template paths")
    audit = sub.add_parser("audit", help="Heuristic inspection of markdown in a target")
    audit.add_argument("--target", default=".")
    args = parser.parse_args()
    try:
        if args.cmd in ("list", "search"):
            from catalog_search import filter_items
            found = (sorted(items(), key=lambda item: item["id"]) if args.cmd == "list" else
                     filter_items(items(), query=args.query, kind=args.kind, tag=args.tag,
                                  agent=args.agent, license=args.license, provenance=args.provenance))
            if args.cmd == "search" and args.json:
                print(json.dumps(found, indent=2, ensure_ascii=False))
            else:
                for item in found:
                    print(f'{item["id"]:20} {item["type"]:12} {item["description"]}')
        elif args.cmd == "trust":
            from catalog_trust import classify_provenance
            selected = [entry(args.id)] if args.id else items()
            results = [{"id": item["id"], **classify_provenance(item)} for item in selected]
            if args.json:
                print(json.dumps(results, indent=2, sort_keys=True))
            else:
                for result in results:
                    print(f'{result["id"]:20} {result["trust"]:16} {result["reason"]}')
        elif args.cmd == "inspect":
            from inspect_metadata import inspect_metadata
            item = entry(args.id)
            metadata = inspect_metadata(item, source(item), args.target)
            if args.json:
                print(json.dumps(metadata, sort_keys=True, indent=2, ensure_ascii=False))
            else:
                print(f'# {item["name"]} ({item["id"]})')
                print(f'Source (declared): {item["source"]}')
                print(f'License (declared): {item["license"]}')
                print(f'Version (declared): {item.get("version", "not provided")}')
                print(f'Local SHA-256 (computed): {metadata["local_sha256"]["value"]}')
                print(f'Catalog digest comparison: {metadata["digest_matches"] if metadata["digest_matches"] is not None else "not available"}')
                print('Compatibility: catalog declarations only; native runtime not verified')
                for installed in metadata["installed_files"]:
                    print(f'Installed: {installed["state"]} {installed["path"]}')
                print()
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
            if args.apply:
                from update_apply import apply_update
                result = apply_update(target, args.id, planned)
            else:
                result = plan_update(target, args.id, planned)
            for action, rel in result:
                print(f"{action:10} {rel}")
            if any(action == "conflict" for action, _ in result):
                return 2
        elif args.cmd == "catalog-refresh":
            from catalog_refresh import refresh_catalog
            digest = refresh_catalog(CATALOG, source_url=args.url, revision=args.revision,
                                     sha256=args.sha256, approve=args.approve, offline=args.offline)
            print(f"Catalog refreshed; verified SHA-256: {digest}")
        elif args.cmd == "status":
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            for rel, state in file_states(target).items():
                print(f"{state:10} {rel}")
        elif args.cmd == "recovery":
            from recovery_inspect import inspect_transactions
            if args.rollback:
                from recovery_execute import rollback_transaction
                result = rollback_transaction(pathlib.Path(args.target).expanduser(), args.rollback)
            elif args.resolution_check:
                from recovery_resolution_preflight import resolution_preflight
                result = resolution_preflight(pathlib.Path(args.target).expanduser(), args.resolution_check)
            elif args.lock_status:
                from recovery_lock_inspect import inspect_writer_lock
                result = inspect_writer_lock(pathlib.Path(args.target).expanduser())
            elif args.rollback_plan:
                from recovery_preflight import rollback_preflight
                result = rollback_preflight(pathlib.Path(args.target).expanduser(), args.rollback_plan)
            else:
                result = inspect_transactions(pathlib.Path(args.target).expanduser())
            if args.json:
                print(json.dumps(result, sort_keys=True, indent=2))
            elif args.rollback:
                print("Rollback completed: " + result["transaction_id"])
            elif args.resolution_check:
                print("Restored files verified; manifest and writer ownership NOT verified: " + result["transaction_id"])
            elif args.lock_status:
                print("Writer lock: " + result["status"] + " (removal not authorized)")
            elif args.rollback_plan:
                print("Read-only rollback plan: " + result["transaction_id"])
                for op in result["operations"]:
                    print("  " + op["action"] + " " + op["path"])
                print(result["warning"])
            else:
                for tx in result:
                    print(f'{tx["transaction_id"]} {tx["state"]} {tx["item_id"]}')
                    for op in tx["operations"]:
                        print(f'  {op["file_state"]:15} backup={op["backup_state"]:15} {op["path"]}')
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
                from update_lock import update_lock
                with update_lock(target):
                    from recovery_guard import require_no_pending_transactions
                    require_no_pending_transactions(target)
                    planned = []
                    ownership = []
                    for item_id in profiles[args.profile]:
                        item_plan = install_plan(entry(item_id), target, args.agent)
                        planned.extend(item_plan)
                        ownership.extend((item_id, dest) for _, dest in item_plan)
                    record_installs(target, ownership, planned, copy_plan)
        elif args.cmd == "add":
            target = pathlib.Path(args.target).expanduser().resolve()
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            from installed_manifest import record_installs
            from update_lock import update_lock
            with update_lock(target):
                from recovery_guard import require_no_pending_transactions
                require_no_pending_transactions(target)
                planned = install_plan(entry(args.id), target, args.agent)
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
