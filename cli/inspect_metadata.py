"""Local inspect metadata with explicit verified vs declared trust boundaries."""
import hashlib
from pathlib import Path
from installed_manifest import load_manifest, file_states


def inspect_metadata(item, source_path, target=None):
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    result = {
        "id": item["id"],
        "type": item["type"],
        "name": item["name"],
        "source": {"value": item["source"], "verification": "catalog-declared"},
        "license": {"value": item["license"], "verification": "catalog-declared"},
        "version": {"value": item.get("version"), "verification": "catalog-declared" if "version" in item else "not-provided"},
        "local_sha256": {"value": digest, "verification": "computed-from-local-file"},
        "catalog_digest": {"value": item.get("digest"), "verification": "catalog-declared" if "digest" in item else "not-provided"},
        "digest_matches": None,
        "compatibility": {"value": item.get("compatibility", {}), "verification": "catalog-declared-not-runtime-tested"},
        "targets": {"value": item["targets"], "verification": "catalog-declared-not-runtime-tested"},
        "upstream": {"value": item.get("upstream"), "verification": "catalog-declared" if "upstream" in item else "not-provided"},
        "installed_files": [],
    }
    declared = item.get("digest")
    if declared is not None:
        result["digest_matches"] = declared["algorithm"] == "sha256" and declared["value"] == digest
    if target is not None:
        target = Path(target).expanduser().resolve()
        if not target.is_dir():
            raise ValueError("Target must be an existing directory")
        records = load_manifest(target)["files"]
        states = file_states(target)
        result["installed_files"] = [
            {"path": rel, "state": states[rel], "recorded_sha256": record["sha256"]}
            for rel, record in sorted(records.items())
            if record["item_id"] == item["id"]
        ]
    return result
