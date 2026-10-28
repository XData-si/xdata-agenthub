"""Verify local catalog sources or installed items against catalog package digests (offline)."""
from pathlib import Path, PurePosixPath

from installed_manifest import load_manifest
from package_digest import digest_from_entries, package_digest


def verify_sources(catalog_items, files_for):
    """Check every catalog item's local source package against its declared digest.

    files_for(item) returns [(absolute path, relative path)] for the item's package.
    Returns a list of (item id, state, detail) with state in verified / mismatch / no-digest.
    """
    results = []
    for item in catalog_items:
        declared = item.get("digest")
        if not declared:
            results.append((item["id"], "no-digest", "catalog declares no digest"))
            continue
        actual = package_digest(files_for(item))
        if declared.get("algorithm") == "sha256" and declared.get("value") == actual:
            results.append((item["id"], "verified", actual))
        else:
            results.append((item["id"], "mismatch", f"catalog {declared.get('value')} != local {actual}"))
    return results


def verify_installed(target, catalog_items):
    """Check items recorded in the target's install manifest.

    States per item: verified (matches the current catalog), outdated (unchanged since install but the catalog
    changed), modified (files changed, missing or added after install), unknown (not in the catalog or no digest).
    Files present in an installed skill directory but absent from the manifest count as modifications, because an
    added file (for example a script) changes what an agent may load.
    """
    target = Path(target).expanduser().resolve()
    if not target.is_dir():
        raise ValueError("Target must be an existing directory")
    manifest = load_manifest(target)["files"]
    by_item = {}
    for rel, record in manifest.items():
        by_item.setdefault(record["item_id"], []).append((rel, record["sha256"]))
    catalog = {item["id"]: item for item in catalog_items}
    results = []
    for item_id, records in sorted(by_item.items()):
        rels = [PurePosixPath(rel) for rel, _ in records]
        root = rels[0].parent if len(rels) == 1 else PurePosixPath(*_common_parts([r.parent.parts for r in rels]))
        item = catalog.get(item_id)
        if item is not None and item["type"] == "skill":
            skill_md = [r for r in rels if r.name == "SKILL.md"]
            if skill_md:
                root = skill_md[0].parent
        missing = [str(r) for r in rels if not (target / r).is_file()]
        extra = []
        if item is not None and item["type"] == "skill" and (target / root).is_dir():
            tracked = {r.as_posix() for r in rels}
            for path in sorted((target / root).rglob("*")):
                if path.is_file() or path.is_symlink():
                    rel = path.relative_to(target).as_posix()
                    if rel not in tracked:
                        extra.append(rel)
        if missing or extra:
            detail = "; ".join(filter(None, [
                ("missing: " + ", ".join(missing)) if missing else "",
                ("unexpected: " + ", ".join(extra)) if extra else ""]))
            results.append((item_id, "modified", detail))
            continue
        files = [(target / r, r.relative_to(root)) for r in rels]
        current = package_digest(files)
        recorded = digest_from_entries((PurePosixPath(rel).relative_to(root).as_posix(), sha) for rel, sha in records)
        declared = (item or {}).get("digest", {}).get("value")
        if item is None or not declared:
            results.append((item_id, "unknown", "not in catalog or no catalog digest"))
        elif current == declared:
            results.append((item_id, "verified", current))
        elif current == recorded:
            results.append((item_id, "outdated", "unchanged since install; catalog version differs (see xah update)"))
        else:
            results.append((item_id, "modified", "installed files changed after install"))
    return results


def _common_parts(part_lists):
    common = []
    for parts in zip(*part_lists):
        if len(set(parts)) != 1:
            break
        common.append(parts[0])
    return common
