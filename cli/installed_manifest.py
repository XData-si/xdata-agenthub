"""Local installed-file manifest: record, inspect, and classify changes safely."""
import hashlib
import json
import os
from pathlib import Path

MANIFEST_NAME = ".xah-installed.json"


def _digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _relative(target, destination):
    target = target.resolve()
    # Reject symlinked destinations and any symlinked parent.
    raw_path = Path(destination).absolute()
    raw = raw_path.parent.resolve() / raw_path.name
    if not raw.is_relative_to(target):
        raise ValueError("Manifest destination outside target")
    rel = raw.relative_to(target)
    if not rel.parts or any(part in (".", "..") for part in rel.parts):
        raise ValueError("Invalid manifest path")
    cursor = target
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("Symlinked manifest path refused")
    return rel.as_posix()


def load_manifest(target):
    path = target / MANIFEST_NAME
    if path.is_symlink():
        raise ValueError("Symlinked manifest refused")
    if not path.exists():
        return {"schema_version": 1, "files": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("files"), dict):
        raise ValueError("Invalid installed-file manifest")
    for rel, record in data["files"].items():
        if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel or any(p in ("", ".", "..") for p in rel.split("/")):
            raise ValueError("Unsafe manifest entry")
        if not isinstance(record, dict) or set(record) != {"sha256", "item_id"}:
            raise ValueError("Invalid manifest entry")
        if not isinstance(record["sha256"], str) or len(record["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in record["sha256"]):
            raise ValueError("Invalid manifest checksum")
        if not isinstance(record["item_id"], str) or not record["item_id"]:
            raise ValueError("Invalid manifest item")
    return data


def file_states(target):
    """Return mapping of installed paths to untouched, modified, or missing."""
    manifest = load_manifest(target)
    states = {}
    for rel, record in sorted(manifest["files"].items()):
        path = target / rel
        try:
            _relative(target, path)
        except ValueError:
            states[rel] = "modified"
            continue
        if not path.is_file():
            states[rel] = "missing"
        else:
            states[rel] = "untouched" if _digest(path) == record["sha256"] else "modified"
    return states


def save_manifest(target, data):
    path = target / MANIFEST_NAME
    if path.is_symlink():
        raise ValueError("Symlinked manifest refused")
    temp = target / (MANIFEST_NAME + ".tmp")
    if temp.exists() or temp.is_symlink():
        raise ValueError("Temporary manifest path already exists")
    encoded = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")
    try:
        with temp.open("xb") as f:
            f.write(encoded)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def record_install(target, item_id, planned):
    """Record installed files; refuse overwriting an existing tracked path."""
    data = load_manifest(target)
    for _, destination in planned:
        rel = _relative(target, destination)
        if rel in data["files"]:
            raise ValueError(f"Already tracked: {rel}")
        if not destination.is_file():
            raise ValueError(f"Missing installed file: {rel}")
        data["files"][rel] = {"sha256": _digest(destination), "item_id": item_id}
    save_manifest(target, data)
