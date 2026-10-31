#!/usr/bin/env python3
"""Import MCP server metadata from the official MCP Registry into registry/mcp-servers.json.

Only servers already in the catalog (or added with --add) are imported; AgentHub curates, it does not mirror the
registry. Each run fetches the latest version of every listed server and rewrites only entries whose upstream record
changed, so repeated runs are idempotent. A new upstream version resets the entry to L0: verification applies to one
exact version. Nothing is installed or executed. Standard library only.

  python3 scripts/import_mcp_registry.py                         # refresh listed servers
  python3 scripts/import_mcp_registry.py --add com.gitlab/mcp --id gitlab
  python3 scripts/import_mcp_registry.py --check                 # exit 1 if a refresh would change the catalog
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli"))
from mcp_catalog import LOCAL_TRANSPORTS, PACKAGE_REGISTRIES, REMOTE_TRANSPORTS, validate_entry, validate_mcp_catalog

CATALOG = ROOT / "registry" / "mcp-servers.json"
API = "https://registry.modelcontextprotocol.io/v0.1"
OFFICIAL = "io.modelcontextprotocol.registry/official"
MAX_BYTES = 2 * 1024 * 1024


class NotFound(Exception):
    pass


def fetch_latest(name, api=API):
    url = f"{api}/servers/{urllib.parse.quote(name, safe='')}/versions/latest"
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "xdata-agenthub"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise NotFound(name) from error
        raise
    if len(body) > MAX_BYTES:
        raise ValueError(f"Registry response for {name} is too large")
    return json.loads(body)


def to_entry(record, entry_id, previous=None):
    """Map an official registry record to a catalog entry; keep verification fields only for the same version."""
    server = record["server"]
    meta = record.get("_meta", {}).get(OFFICIAL, {})
    artifacts, environment = [], {}
    for package in server.get("packages", []):
        transport = package.get("transport", {}).get("type")
        if package.get("registryType") not in PACKAGE_REGISTRIES or transport not in LOCAL_TRANSPORTS:
            continue
        artifact = {"kind": "package", "registry": package["registryType"], "identifier": package.get("identifier"),
                    "version": package.get("version") or server.get("version"), "transport": transport}
        if package.get("fileSha256"):
            artifact["sha256"] = package["fileSha256"].lower()
        artifacts.append(artifact)
        for var in package.get("environmentVariables", []):
            environment.setdefault(var.get("name"), {"name": var.get("name"), "required": bool(var.get("isRequired")),
                                                     "secret": bool(var.get("isSecret"))})
    for remote in server.get("remotes", []):
        if remote.get("type") in REMOTE_TRANSPORTS:
            artifacts.append({"kind": "remote", "transport": remote["type"], "url": remote.get("url")})
    entry = {"id": entry_id, "name": server.get("name"), "description": server.get("description"),
             "version": server.get("version"), "artifacts": artifacts,
             "registry": {"status": meta.get("status"), "published_at": meta.get("publishedAt"),
                          "updated_at": meta.get("updatedAt")},
             "level": "L0"}
    if server.get("title"):
        entry["title"] = server["title"]
    if (server.get("repository") or {}).get("url"):
        entry["repository"] = server["repository"]["url"]
    if server.get("websiteUrl"):
        entry["website"] = server["websiteUrl"]
    if environment:
        entry["environment"] = sorted(environment.values(), key=lambda v: v["name"])
    if previous and previous["version"] == entry["version"]:
        for field in ("level", "permissions", "evidence"):
            if field in previous:
                entry[field] = previous[field]
        # Digests recorded by AgentHub for the same version stay pinned.
        pinned = {(a["registry"], a["identifier"], a["version"]): a["sha256"]
                  for a in previous["artifacts"] if a["kind"] == "package" and "sha256" in a}
        for artifact in entry["artifacts"]:
            key = (artifact.get("registry"), artifact.get("identifier"), artifact.get("version"))
            if artifact["kind"] == "package" and key in pinned:
                artifact.setdefault("sha256", pinned[key])
    return validate_entry(entry, entry_id)


def refresh(catalog, fetch=None, add=None, log=print):
    """Return a new catalog with listed servers refreshed, or with only `add` = (name, id) imported."""
    fetch = fetch or fetch_latest
    servers = {s["id"]: s for s in validate_mcp_catalog(catalog)}
    wanted = [(s["name"], s["id"]) for s in servers.values() if s["registry"]["status"] != "unlisted"]
    if add:
        name, entry_id = add
        if entry_id in servers or name in [n for n, _ in wanted]:
            raise ValueError(f"Already listed: {name} ({entry_id})")
        wanted = [add]
    for name, entry_id in sorted(wanted, key=lambda w: w[1]):
        previous = servers.get(entry_id)
        try:
            record = fetch(name)
            if record.get("server", {}).get("name") != name:
                raise ValueError("registry returned a different server")
            entry = to_entry(record, entry_id, previous)
        except NotFound:
            if previous is None:
                raise ValueError(f"Not in the official registry: {name}")
            log(f"warning: {entry_id}: {name} not found upstream; entry kept unchanged")
            continue
        except (KeyError, TypeError, AttributeError, ValueError) as error:
            if previous is None:
                raise ValueError(f"Cannot import {name}: {error}")
            log(f"warning: {entry_id}: upstream record rejected ({error}); entry kept unchanged")
            continue
        if entry != previous:
            if previous and previous["version"] != entry["version"] and previous["level"] != "L0":
                log(f"{entry_id}: {previous['version']} -> {entry['version']}, level {previous['level']} reset to L0")
            else:
                log(f"{entry_id}: {'updated' if previous else 'added'} ({entry['version']})")
        servers[entry_id] = entry
    result = dict(catalog, servers=sorted(servers.values(), key=lambda s: s["id"]))
    validate_mcp_catalog(result)
    return result


def dump(catalog):
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", type=pathlib.Path, default=CATALOG)
    parser.add_argument("--add", metavar="NAME", help="Official registry server name to start listing")
    parser.add_argument("--id", help="Catalog ID for --add (lowercase slug)")
    parser.add_argument("--check", action="store_true", help="Do not write; exit 1 if the catalog would change")
    args = parser.parse_args(argv)
    if bool(args.add) != bool(args.id):
        parser.error("--add and --id are used together")
    text = args.catalog.read_text(encoding="utf-8")
    try:
        result = dump(refresh(json.loads(text), add=(args.add, args.id) if args.add else None,
                              log=lambda m: print(m, file=sys.stderr)))
    except (ValueError, urllib.error.URLError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if result == text:
        print("MCP catalog is up to date")
        return 0
    if args.check:
        print("MCP catalog is out of date; run scripts/import_mcp_registry.py")
        return 1
    args.catalog.write_text(result, encoding="utf-8")
    print(f"Updated {args.catalog}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
