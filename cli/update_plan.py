"""Deterministic, read-only update planner for tracked XData AgentHub files."""
import hashlib
from pathlib import Path
from installed_manifest import load_manifest, _relative, _digest


def plan_update(target, item_id, planned):
    """Return (action, relative_path) pairs in stable order; never modify the target."""
    manifest = load_manifest(target)["files"]
    output = []
    for source, destination in planned:
        rel = _relative(target, destination)
        record = manifest.get(rel)
        if destination.is_symlink():
            action = "conflict"
        elif record is not None and record["item_id"] != item_id:
            action = "conflict"
        elif record is None:
            action = "conflict" if destination.exists() else "add"
        elif not destination.is_file():
            action = "conflict" if destination.exists() else "conflict"
        elif _digest(destination) != record["sha256"]:
            action = "conflict"
        elif _digest(source) == record["sha256"]:
            action = "skip"
        else:
            action = "update"
        output.append((action, rel))
    return sorted(output, key=lambda item: item[1])
