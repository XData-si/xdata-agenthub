#!/usr/bin/env python3
"""Recompute package digests in registry/catalog.json (schema v2). Use --check in CI to fail on stale digests."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
import xah  # noqa: E402
from package_digest import package_digest  # noqa: E402

CATALOG = ROOT / "registry" / "catalog.json"


def main(check=False):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    stale = []
    for item in data["items"]:
        digest = {"algorithm": "sha256", "value": package_digest(xah.skill_files(item))}
        if item.get("digest") != digest:
            stale.append(item["id"])
            item["digest"] = digest
    if check:
        for item_id in stale:
            print(f"STALE: {item_id}")
        print(f"Digest check: {len(data['items'])} entries, {len(stale)} stale")
        return 1 if stale else 0
    data["schema_version"] = 2
    data.setdefault("catalog_id", "xdata-agenthub")
    ordered = {k: data[k] for k in ("schema_version", "catalog_id", "catalog_version", "generated_at") if k in data}
    ordered["items"] = data["items"]
    CATALOG.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {len(stale)} of {len(data['items'])} digests")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv[1:]))
