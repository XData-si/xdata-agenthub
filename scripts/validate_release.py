#!/usr/bin/env python3
"""Offline release gate for bundled, original XData resources."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "registry/catalog.json"
ALLOWED_TYPES = {"skill", "instruction", "workflow", "agent"}
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FIELDS = {"id", "name", "description", "type", "path", "source", "license", "targets"}

def validate():
    failures = []
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = data["items"]
    if data.get("schema_version") != 1:
        failures.append("Unsupported catalog schema")
    if not (ROOT / "LICENSE").is_file():
        failures.append("Missing root LICENSE")
    seen = set()
    for item in entries:
        label = str(item.get("id", "<missing>"))
        if not FIELDS.issubset(item):
            failures.append(f"{label}: missing metadata fields")
            continue
        if not ID.fullmatch(label) or label in seen:
            failures.append(f"{label}: unsafe or duplicate ID")
        seen.add(label)
        if item["type"] not in ALLOWED_TYPES:
            failures.append(f"{label}: unknown type")
        if not all(isinstance(item[k], str) and item[k].strip() for k in ("name", "description", "path", "source", "license")):
            failures.append(f"{label}: empty metadata")
        if item["source"] != "XData original" or item["license"] != "MIT":
            failures.append(f"{label}: external or unverified provenance; do not bundle")
        if not isinstance(item["targets"], list) or not item["targets"]:
            failures.append(f"{label}: missing target metadata")
        relative = pathlib.PurePosixPath(item["path"])
        if relative.is_absolute() or ".." in relative.parts or "\\" in item["path"]:
            failures.append(f"{label}: unsafe source path")
            continue
        file = ROOT.joinpath(*relative.parts)
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(ROOT):
            failures.append(f"{label}: source missing, symlinked or escaping root")
            continue
        if item["type"] == "skill":
            if relative != pathlib.PurePosixPath(f"skills/{label}/SKILL.md"):
                failures.append(f"{label}: unexpected skill layout")
            content = file.read_text(encoding="utf-8")
            if not content.startswith("---\n") or "\n---\n" not in content[4:]:
                failures.append(f"{label}: invalid YAML frontmatter boundaries")
            else:
                header = content.split("---", 2)[1]
                if not re.search(r"(?m)^name:\s*" + re.escape(label) + r"\s*$", header):
                    failures.append(f"{label}: frontmatter name mismatch")
                if not re.search(r"(?m)^description:\s*\S", header):
                    failures.append(f"{label}: frontmatter description missing")
            for child in file.parent.rglob("*"):
                if child.is_symlink() or (not child.is_file() and not child.is_dir()):
                    failures.append(f"{label}: unsupported or symlinked package entry: {child}")
    candidates = ROOT / "registry/external-candidates.json"
    if candidates.is_file():
        raw = candidates.read_text(encoding="utf-8")
        # External discovery data must never be implicitly treated as approved imports.
        if not raw.strip():
            failures.append("External candidate registry empty")
    return failures, len(entries)

if __name__ == "__main__":
    problems, count = validate()
    for problem in problems:
        print("FAIL:", problem)
    print(f"Release metadata validation: {count} local resources, {len(problems)} finding(s)")
    sys.exit(1 if problems else 0)
