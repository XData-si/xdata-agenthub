#!/usr/bin/env python3
"""XData AgentHub local-first alpha CLI. Python 3.10+, standard library only."""
import argparse
import json
import os
import pathlib
import re
import shutil
import platform
import sys
from catalog_schema import validate_catalog
from installed_manifest import file_states, record_install, load_manifest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "registry" / "catalog.json"
MCP_CATALOG = ROOT / "registry" / "mcp-servers.json"
# Additional local catalogs (e.g. private organisation skills) from --catalog or XAH_CATALOGS
# (os.pathsep-separated). Item paths in an additional catalog are relative to that catalog file's directory.
EXTRA_CATALOGS_ENV = "XAH_CATALOGS"
_extra_catalogs = []
_item_roots = {}

def catalog_files():
    files = [(CATALOG, ROOT)]
    configured = list(_extra_catalogs) + [p for p in os.environ.get(EXTRA_CATALOGS_ENV, "").split(os.pathsep) if p]
    for value in configured:
        path = pathlib.Path(value).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"Additional catalog not found: {path}")
        if path in [existing for existing, _ in files]:
            continue
        files.append((path, path.parent))
    return files

def items():
    merged = []
    roots = {}
    for path, root in catalog_files():
        for item in validate_catalog(json.loads(path.read_text(encoding="utf-8"))):
            if item["id"] in roots:
                raise ValueError(f"Duplicate item ID across catalogs: {item['id']} ({path})")
            roots[item["id"]] = root
            merged.append(item)
    _item_roots.clear()
    _item_roots.update(roots)
    return merged

def item_root(item):
    if item["id"] not in _item_roots:
        items()
    return _item_roots.get(item["id"], ROOT)

def entry(item_id):
    for item in items():
        if item["id"] == item_id:
            return item
    raise ValueError(f"Unknown item: {item_id}")

def source(item):
    root = item_root(item)
    path = (root / item["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Unsafe or missing catalog path")
    return path

def skill_files(item):
    """Inspect complete local skill package without following symlinks."""
    main_file = source(item)
    if item["type"] != "skill":
        return [(main_file, pathlib.Path(main_file.name))]
    root = main_file.parent
    if pathlib.Path(item_root(item) / item["path"]).is_symlink() or root.is_symlink():
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


def install_plan(item, target, agent, scope="project"):
    from adapter_contract import destination_for
    if item["type"] == "skill":
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"]):
            raise ValueError("Unsafe skill identifier")
        base = pathlib.Path(destination_for(agent, item["id"], "skill", scope))
        package = skill_files(item)
        if not any(rel == pathlib.Path("SKILL.md") for _, rel in package):
            raise ValueError("Missing SKILL.md in skill package")
        planned = [(src, target / base / rel) for src, rel in package]
    else:
        if scope != "project":
            raise ValueError(f"{scope} scope supports skill items only")
        rel = pathlib.Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts or "\\" in item["path"]:
            raise ValueError("Unsafe destination")
        if item["id"] == "project-agents" and agent != "generic":
            rel = pathlib.Path(destination_for(agent, item["id"], "instruction"))
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


def resolve_target(args):
    """--scope user installs relative to the home directory; an explicit --target overrides it."""
    if getattr(args, "scope", "project") == "user" and args.target == ".":
        return pathlib.Path.home().resolve()
    return pathlib.Path(args.target).expanduser().resolve()


def main():
    parser = argparse.ArgumentParser(prog="xah", description="XData AgentHub — portable agent resources")
    parser.add_argument("--catalog", action="append", default=[], metavar="PATH",
                        help=f"Additional local catalog JSON (repeatable; also {EXTRA_CATALOGS_ENV})")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List catalog items")
    trust = sub.add_parser("trust", help="Inspect declared catalog provenance (not certification)")
    trust.add_argument("id", nargs="?")
    trust.add_argument("--json", action="store_true")
    search = sub.add_parser("search", help="Search local catalog")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--kind", choices=["skill", "instruction", "workflow", "agent"])
    search.add_argument("--tag")
    search.add_argument("--agent")
    search.add_argument("--license")
    search.add_argument("--provenance")
    search.add_argument("--json", action="store_true", help="Emit JSON array")
    browse = sub.add_parser("browse", help="Browse local catalog with facets and pagination")
    browse.add_argument("--query", default="", help="Case-insensitive search")
    browse.add_argument("--kind", choices=["skill", "instruction", "workflow", "agent"])
    browse.add_argument("--tag")
    browse.add_argument("--agent")
    browse.add_argument("--license")
    browse.add_argument("--offset", type=int, default=0)
    browse.add_argument("--limit", type=int, default=20)
    browse.add_argument("--json", action="store_true")
    inspect = sub.add_parser("inspect", help="Print a catalog item")
    inspect.add_argument("id")
    inspect.add_argument("--target", help="Inspect installed-file states in this project")
    inspect.add_argument("--json", action="store_true", help="Emit structured metadata")
    add = sub.add_parser("add", help="Copy a vetted template into a project")
    add.add_argument("id")
    add.add_argument("--target", default=".")
    add.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
    add.add_argument("--scope", choices=["project", "user"], default="project",
                     help="user: install a skill into the agent's user-level directory under the home directory")
    init = sub.add_parser("init", help="Install a curated local starter profile")
    init.add_argument("--target", default=".")
    init.add_argument("--profile", choices=["developer", "research", "devops"], default="developer")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
    update = sub.add_parser("update", help="Preview updates to a tracked item (read-only)")
    update.add_argument("id")
    update.add_argument("--target", default=".")
    update.add_argument("--agent", choices=["generic", "claude", "codex", "opencode"], default="generic")
    update.add_argument("--scope", choices=["project", "user"], default="project")
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
    recovery.add_argument("--resolution-check", metavar="TRANSACTION_ID",
                          help="Read-only restored file and manifest verification")
    recovery.add_argument("--lock-status", action="store_true",
                          help="Read-only writer lock diagnostic; never removes a lock")
    recovery.add_argument("--rollback-plan", metavar="TRANSACTION_ID",
                          help="Read-only rollback eligibility and file action plan")
    gates = sub.add_parser("release-check", help="Evaluate explicit release evidence JSON (no publishing)")
    gates.add_argument("--evidence", required=True, help="Path to evidence JSON")
    gates.add_argument("--json", action="store_true")
    sub.add_parser("doctor", help="Check Python version, catalog, template paths and package digests")
    verify = sub.add_parser("verify", help="Verify catalog sources or installed items against package digests")
    verify.add_argument("--target", help="Verify items installed in this directory (default: verify catalog sources)")
    verify.add_argument("--scope", choices=["project", "user"], default="project",
                        help="user: verify the home directory installation")
    verify.add_argument("--json", action="store_true")
    audit = sub.add_parser("audit", help="Heuristic inspection of markdown in a target")
    audit.add_argument("--target", default=".")
    mcp = sub.add_parser("mcp", help="Browse listed MCP servers (metadata only; never installs or runs them)")
    mcp_sub = mcp.add_subparsers(dest="mcp_cmd", required=True)
    mcp_sub.add_parser("list", help="List MCP servers with their verification level")
    mcp_search = mcp_sub.add_parser("search", help="Search MCP servers")
    mcp_search.add_argument("query", nargs="?", default="")
    mcp_search.add_argument("--level", choices=["L0", "L1", "L2", "L3", "L4"])
    mcp_search.add_argument("--transport", choices=["stdio", "streamable-http", "sse"])
    mcp_search.add_argument("--json", action="store_true")
    mcp_inspect = mcp_sub.add_parser("inspect", help="Print one MCP server entry")
    mcp_inspect.add_argument("id")
    mcp_inspect.add_argument("--json", action="store_true")
    args = parser.parse_args()
    _extra_catalogs[:] = args.catalog
    try:
        if args.cmd == "mcp":
            import mcp_catalog
            servers = mcp_catalog.load(MCP_CATALOG)
            if args.mcp_cmd == "inspect":
                found = [s for s in servers if s["id"] == args.id]
                if not found:
                    raise ValueError(f"Unknown MCP server: {args.id}")
                server = found[0]
                if args.json:
                    print(json.dumps(server, indent=2, ensure_ascii=False))
                else:
                    print(f'# {server.get("title", server["id"])} ({server["id"]})')
                    print(f'Registry name: {server["name"]}')
                    print(f'Version: {server["version"]} (registry status: {server["registry"]["status"]})')
                    print(f'Level: {server["level"]} {mcp_catalog.LEVEL_LABELS[server["level"]]}')
                    if server["level"] == "L0":
                        print("  Listed only: metadata from the official MCP Registry; not reviewed, scanned or tested.")
                    print(f'Description (declared): {server["description"]}')
                    if "repository" in server:
                        print(f'Repository: {server["repository"]}')
                    for artifact in server["artifacts"]:
                        if artifact["kind"] == "package":
                            print(f'Package: {artifact["registry"]} {artifact["identifier"]}@{artifact["version"]} ({artifact["transport"]})')
                        else:
                            print(f'Remote: {artifact["url"]} ({artifact["transport"]})')
                    secrets = [v["name"] for v in server.get("environment", []) if v["secret"]]
                    if secrets:
                        print("Secrets it asks for: " + ", ".join(secrets))
                    if "evidence" in server:
                        print(f'Evidence: {server["evidence"]}')
            else:
                found = (servers if args.mcp_cmd == "list" else
                         mcp_catalog.filter_servers(servers, query=args.query, level=args.level, transport=args.transport))
                if args.mcp_cmd == "search" and args.json:
                    print(json.dumps(found, indent=2, ensure_ascii=False))
                else:
                    for server in sorted(found, key=lambda s: s["id"]):
                        print(f'{server["id"]:14} {server["level"]:3} {",".join(mcp_catalog.transports(server)):24} {server["name"]}')
                    if args.mcp_cmd == "list":
                        print("L0 = listed only (metadata, not verified). Levels: docs/VERIFIED_MCP.md")
        elif args.cmd in ("list", "search"):
            from catalog_search import filter_items
            found = (sorted(items(), key=lambda item: item["id"]) if args.cmd == "list" else
                     filter_items(items(), query=args.query, kind=args.kind, tag=args.tag,
                                  agent=args.agent, license=args.license, provenance=args.provenance))
            if args.cmd == "search" and args.json:
                print(json.dumps(found, indent=2, ensure_ascii=False))
            else:
                for item in found:
                    print(f'{item["id"]:20} {item["type"]:12} {item["description"]}')
        elif args.cmd == "browse":
            from catalog_browse import facets, page
            from catalog_search import filter_items
            catalog = filter_items(items(), query=args.query, kind=args.kind,
                                   tag=args.tag, agent=args.agent, license=args.license)
            result = page(catalog, offset=args.offset, limit=args.limit)
            result["facets"] = facets(catalog)
            if args.json:
                print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
            else:
                print(f'Catalog: {result["total"]} entries (offset {args.offset}, limit {args.limit})')
                for item in result["items"]:
                    print(f'{item["id"]:20} {item["type"]:12} {item["description"]}')
                print("Facets:")
                for name, values in result["facets"].items():
                    print(f'  {name}: ' + ", ".join(f"{k}={v}" for k, v in values.items()))
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
            metadata = inspect_metadata(item, source(item), args.target, package_files=skill_files(item))
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
            target = resolve_target(args)
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            item = entry(args.id)
            from adapter_contract import destination_for
            if item["type"] == "skill":
                base = pathlib.Path(destination_for(args.agent, item["id"], "skill", args.scope))
                planned = [(src, target / base / rel) for src, rel in skill_files(item)]
            else:
                if args.scope != "project":
                    raise ValueError(f"{args.scope} scope supports skill items only")
                rel = pathlib.Path(item["path"])
                if rel.is_absolute() or ".." in rel.parts or "\\\\" in item["path"]:
                    raise ValueError("Unsafe destination")
                if item["id"] == "project-agents" and args.agent != "generic":
                    rel = pathlib.Path(destination_for(args.agent, item["id"], "instruction"))
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
                print("Restored files and manifest verified; writer ownership NOT verified: " + result["transaction_id"])
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
        elif args.cmd == "release-check":
            from release_gates import evaluate
            evidence_path = pathlib.Path(args.evidence).expanduser()
            if evidence_path.is_symlink() or not evidence_path.is_file() or evidence_path.stat().st_size > 100_000:
                raise ValueError("Missing, symlinked or oversized evidence file")
            result = evaluate(json.loads(evidence_path.read_text(encoding="utf-8")))
            if args.json:
                print(json.dumps(result, sort_keys=True, indent=2))
            else:
                for name, gate in result["gates"].items():
                    print(f'{name:24} {gate["status"]}')
                print("READY" if result["ready"] else "NOT READY")
            if not result["ready"]:
                return 2
        elif args.cmd == "verify":
            from verify import verify_installed, verify_sources
            if args.target is None and args.scope == "user":
                args.target = "."
            if args.target is None:
                results = verify_sources(items(), skill_files)
            else:
                results = verify_installed(resolve_target(args), items())
            if args.json:
                print(json.dumps([{"id": i, "state": s, "detail": d} for i, s, d in results], indent=2))
            else:
                for item_id, state, detail in results:
                    print(f"{state:10} {item_id:28} {detail}")
                counts = {}
                for _, state, _ in results:
                    counts[state] = counts.get(state, 0) + 1
                print("Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) if counts else "Summary: nothing to verify")
            if any(state != "verified" for _, state, _ in results):
                return 2
        elif args.cmd == "doctor":
            print(f"Python: {platform.python_version()}")
            for path, _ in catalog_files():
                print(f"Catalog: {path}")
            if sys.version_info < (3, 10):
                raise ValueError("Python 3.10+ required")
            catalog = items()
            seen = set()
            for item in catalog:
                if item["id"] in seen:
                    raise ValueError("Duplicate catalog ID: " + item["id"])
                seen.add(item["id"])
                source(item)
                files = skill_files(item)
                declared = item.get("digest")
                if declared:
                    from package_digest import package_digest
                    if package_digest(files) != declared["value"]:
                        raise ValueError(f"Package digest mismatch: {item['id']} (run xah verify)")
            print(f"OK: {len(catalog)} catalog entries, all local paths valid, declared digests match")
            if MCP_CATALOG.is_file():
                import mcp_catalog
                import mcp_evidence
                servers = mcp_catalog.load(MCP_CATALOG)
                verified = mcp_evidence.check_catalog_evidence(servers, ROOT)
                print(f"OK: {len(servers)} MCP server entries valid, {verified} with evidence above L0")
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
            target = resolve_target(args)
            if not target.is_dir():
                raise ValueError("Target must be an existing directory")
            from installed_manifest import record_installs
            from update_lock import update_lock
            with update_lock(target):
                from recovery_guard import require_no_pending_transactions
                require_no_pending_transactions(target)
                planned = install_plan(entry(args.id), target, args.agent, args.scope)
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
