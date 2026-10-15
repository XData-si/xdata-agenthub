#!/usr/bin/env python3
"""XData AgentHub local-first alpha CLI. Python 3.10+, standard library only."""
import argparse
import json
import pathlib
import re
import shutil
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
            findings = 0
            patterns = [r"curl\\s+[^\\n|]+\\|\\s*(?:bash|sh)", r"wget\\s+[^\\n|]+\\|\\s*(?:bash|sh)", r"rm\\s+-rf\\s+/"]
            for file in target.rglob("*.md"):
                if file.is_symlink() or not file.is_file() or file.stat().st_size > 1_000_000:
                    continue
                body = file.read_text(encoding="utf-8", errors="replace")
                for pattern in patterns:
                    if re.search(pattern, body, re.IGNORECASE):
                        print(f"REVIEW: {file}: matched {pattern}")
                        findings += 1
            print(f"Heuristic audit: {findings} finding(s). Not a security certification.")
            if findings:
                return 2
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
