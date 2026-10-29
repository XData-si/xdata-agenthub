"""Verified MCP catalog (registry/mcp-servers.json): dependency-free validation and offline search.

Entries describe MCP servers; AgentHub never installs or runs them. The level states what was checked for the pinned
version (docs/VERIFIED_MCP.md). L0 means listed only: metadata imported from the official MCP Registry, nothing more.
"""
import json
import re

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
# Official registry server names: reverse-DNS namespace, a slash, then a name.
SERVER_NAME = re.compile(r"[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
TIMESTAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\Z")
# Control, zero-width and bidirectional characters can hide text from reviewers.
HIDDEN = re.compile("[\x00-\x1f\x7f\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")

LEVELS = ("L0", "L1", "L2", "L3", "L4")
LEVEL_LABELS = {"L0": "Listed", "L1": "Identity verified", "L2": "Security scanned",
                "L3": "Runtime tested", "L4": "Continuously verified"}
PACKAGE_REGISTRIES = {"npm", "pypi", "oci", "nuget", "mcpb"}
LOCAL_TRANSPORTS = {"stdio", "streamable-http", "sse"}
REMOTE_TRANSPORTS = {"streamable-http", "sse"}
REGISTRY_STATUSES = {"active", "deprecated", "deleted"}
PERMISSIONS = {
    "filesystem": {"none", "read", "write"},
    "network": {"none", "allowlisted", "any"},
    "data": {"read-only", "modify", "delete"},
    "external_actions": {"none", "sends-messages", "spends-money", "changes-infrastructure"},
    "credentials": {"none", "user-token", "service-account"},
}

ENTRY_REQUIRED = {"id", "name", "description", "version", "artifacts", "registry", "level"}
ENTRY_OPTIONAL = {"title", "repository", "website", "environment", "permissions", "evidence"}


def _fields(obj, required, optional, where):
    if not isinstance(obj, dict):
        raise ValueError(f"{where} must be an object")
    missing = required - obj.keys()
    extra = obj.keys() - required - optional
    if missing or extra:
        raise ValueError(f"{where}: missing {sorted(missing)}, unknown {sorted(extra)}")


def _text(value, where, limit=500):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or HIDDEN.search(value):
        raise ValueError(f"{where} must be visible text of at most {limit} characters")


def _https(value, where):
    _text(value, where, 2048)
    if not value.startswith("https://") or any(c.isspace() for c in value):
        raise ValueError(f"{where} must be an https URL")


def _artifact(artifact, where):
    if not isinstance(artifact, dict) or artifact.get("kind") not in ("package", "remote"):
        raise ValueError(f"{where}.kind must be package or remote")
    if artifact["kind"] == "package":
        _fields(artifact, {"kind", "registry", "identifier", "version", "transport"}, {"sha256"}, where)
        if artifact["registry"] not in PACKAGE_REGISTRIES:
            raise ValueError(f"{where}.registry is not supported")
        _text(artifact["identifier"], f"{where}.identifier", 300)
        _text(artifact["version"], f"{where}.version", 100)
        if artifact["transport"] not in LOCAL_TRANSPORTS:
            raise ValueError(f"{where}.transport is not supported")
        if "sha256" in artifact and not (isinstance(artifact["sha256"], str) and HEX.fullmatch(artifact["sha256"])):
            raise ValueError(f"{where}.sha256 must be 64 lowercase hex characters")
    else:
        _fields(artifact, {"kind", "transport", "url"}, set(), where)
        if artifact["transport"] not in REMOTE_TRANSPORTS:
            raise ValueError(f"{where}.transport is not supported")
        _https(artifact["url"], f"{where}.url")


def validate_entry(entry, where="server"):
    _fields(entry, ENTRY_REQUIRED, ENTRY_OPTIONAL, where)
    if not isinstance(entry["id"], str) or not SLUG.fullmatch(entry["id"]):
        raise ValueError(f"{where}.id must be a lowercase slug")
    if not isinstance(entry["name"], str) or not SERVER_NAME.fullmatch(entry["name"]):
        raise ValueError(f"{where}.name must be an official registry server name")
    _text(entry["description"], f"{where}.description")
    _text(entry["version"], f"{where}.version", 100)
    if "title" in entry:
        _text(entry["title"], f"{where}.title", 100)
    for field in ("repository", "website"):
        if field in entry:
            _https(entry[field], f"{where}.{field}")
    artifacts = entry["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"{where}.artifacts must be a non-empty array")
    for idx, artifact in enumerate(artifacts):
        _artifact(artifact, f"{where}.artifacts[{idx}]")
    if "environment" in entry:
        if not isinstance(entry["environment"], list):
            raise ValueError(f"{where}.environment must be an array")
        names = set()
        for idx, var in enumerate(entry["environment"]):
            _fields(var, {"name", "required", "secret"}, set(), f"{where}.environment[{idx}]")
            if not isinstance(var["name"], str) or not ENV_NAME.fullmatch(var["name"]) or var["name"] in names:
                raise ValueError(f"{where}.environment[{idx}].name is invalid or duplicate")
            names.add(var["name"])
            if type(var["required"]) is not bool or type(var["secret"]) is not bool:
                raise ValueError(f"{where}.environment[{idx}] flags must be booleans")
    registry = entry["registry"]
    _fields(registry, {"status", "published_at", "updated_at"}, set(), f"{where}.registry")
    if registry["status"] not in REGISTRY_STATUSES:
        raise ValueError(f"{where}.registry.status is invalid")
    for field in ("published_at", "updated_at"):
        if not isinstance(registry[field], str) or not TIMESTAMP.fullmatch(registry[field]):
            raise ValueError(f"{where}.registry.{field} must be a UTC timestamp")
    if entry["level"] not in LEVELS:
        raise ValueError(f"{where}.level must be one of {', '.join(LEVELS)}")
    if "permissions" in entry:
        _fields(entry["permissions"], set(), set(PERMISSIONS), f"{where}.permissions")
        for key, value in entry["permissions"].items():
            if value not in PERMISSIONS[key]:
                raise ValueError(f"{where}.permissions.{key} is invalid")
    if "evidence" in entry:
        evidence = entry["evidence"]
        _text(evidence, f"{where}.evidence", 300)
        if evidence.startswith("/") or "\\" in evidence or any(p in ("", ".", "..") for p in evidence.split("/")):
            raise ValueError(f"{where}.evidence must be a relative repository path")
    # A level above L0 is a claim; claims need evidence and a pinned package digest or a remote endpoint.
    if entry["level"] != "L0":
        if "evidence" not in entry:
            raise ValueError(f"{where}: level {entry['level']} requires evidence")
        if any(a["kind"] == "package" and "sha256" not in a for a in artifacts):
            raise ValueError(f"{where}: level {entry['level']} requires sha256 for every package")
    if entry["level"] in ("L3", "L4") and "permissions" not in entry:
        raise ValueError(f"{where}: level {entry['level']} requires a permission profile")
    return entry


def validate_mcp_catalog(data):
    """Validate the MCP catalog and return its servers; never mutate input."""
    _fields(data, {"schema_version", "source", "servers"}, set(), "mcp catalog")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported MCP catalog schema version")
    _https(data["source"], "source")
    if not isinstance(data["servers"], list):
        raise ValueError("servers must be an array")
    ids, names = set(), set()
    for idx, entry in enumerate(data["servers"]):
        validate_entry(entry, f"servers[{idx}]")
        if entry["id"] in ids or entry["name"] in names:
            raise ValueError(f"Duplicate MCP server: {entry['id']} ({entry['name']})")
        ids.add(entry["id"])
        names.add(entry["name"])
    return data["servers"]


def load(path):
    return validate_mcp_catalog(json.loads(path.read_text(encoding="utf-8")))


def transports(entry):
    return sorted({a["transport"] for a in entry["artifacts"]})


def filter_servers(servers, *, query="", level=None, transport=None):
    if not isinstance(query, str) or any(ord(c) < 32 for c in query):
        raise ValueError("Query must be text without control characters")
    def matches(entry):
        if query.casefold() not in json.dumps(entry, ensure_ascii=False, sort_keys=True).casefold():
            return False
        if level is not None and entry["level"] != level:
            return False
        if transport is not None and transport not in transports(entry):
            return False
        return True
    return sorted((e for e in servers if matches(e)), key=lambda e: e["id"])
