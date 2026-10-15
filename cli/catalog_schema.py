"""Versioned, dependency-free catalog validation for XData AgentHub."""
import re
from pathlib import PurePosixPath

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
REQUIRED = {"id", "type", "name", "description", "path", "license", "source", "targets"}
OPTIONAL = {"version", "digest", "upstream", "tags", "compatibility"}
KINDS = {"skill", "instruction", "workflow", "agent"}
STATUSES = {"untested", "direct-read", "native-observed"}


def _fields(obj, required, optional, where):
    if not isinstance(obj, dict):
        raise ValueError(f"{where} must be an object")
    missing = required - obj.keys()
    extra = obj.keys() - required - optional
    if missing or extra:
        raise ValueError(f"{where}: missing {sorted(missing)}, unknown {sorted(extra)}")


def _string(value, where):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError(f"{where} must be a non-empty string")


def validate_catalog(data):
    """Validate v1/v2 catalog structure and return its items; never mutate input."""
    _fields(data, {"schema_version", "items"},
            {"catalog_id", "catalog_version", "generated_at"} if isinstance(data, dict) and type(data.get("schema_version")) is int and data.get("schema_version") == 2 else set(),
            "catalog")
    version = data["schema_version"]
    if type(version) is not int or version not in (1, 2):
        raise ValueError("Unsupported catalog schema version")
    if not isinstance(data["items"], list):
        raise ValueError("items must be an array")
    if version == 2:
        for field in ("catalog_id", "catalog_version", "generated_at"):
            if field in data:
                _string(data[field], field)
        if "catalog_id" in data and not SLUG.fullmatch(data["catalog_id"]):
            raise ValueError("Invalid catalog_id")
    seen = set()
    for idx, item in enumerate(data["items"]):
        where = f"items[{idx}]"
        _fields(item, REQUIRED, OPTIONAL if version == 2 else set(), where)
        for field in ("id", "type", "name", "description", "path", "license", "source"):
            _string(item[field], f"{where}.{field}")
        if not SLUG.fullmatch(item["id"]) or item["id"] in seen:
            raise ValueError(f"Invalid or duplicate item ID: {item['id']}")
        seen.add(item["id"])
        if item["type"] not in KINDS:
            raise ValueError(f"Invalid item type: {item['type']}")
        path = item["path"]
        parts = PurePosixPath(path).parts
        if path.startswith("/") or "\\" in path or any(p in ("", ".", "..") for p in path.split("/")) or not parts:
            raise ValueError(f"Unsafe catalog path: {path}")
        targets = item["targets"]
        if not isinstance(targets, list) or not targets or any(not isinstance(t, str) or not SLUG.fullmatch(t) for t in targets) or len(set(targets)) != len(targets):
            raise ValueError(f"Invalid targets for {item['id']}")
        if version == 1:
            continue
        if "version" in item:
            _string(item["version"], "version")
        if "tags" in item:
            tags = item["tags"]
            if not isinstance(tags, list) or any(not isinstance(t, str) or not SLUG.fullmatch(t) for t in tags) or len(set(tags)) != len(tags):
                raise ValueError("Invalid tags")
        if "digest" in item:
            digest = item["digest"]
            _fields(digest, {"algorithm", "value"}, set(), "digest")
            if digest["algorithm"] != "sha256" or not isinstance(digest["value"], str) or not HEX.fullmatch(digest["value"]):
                raise ValueError("Invalid digest")
        if "upstream" in item:
            upstream = item["upstream"]
            _fields(upstream, set(), {"url", "revision", "license_url"}, "upstream")
            for field, value in upstream.items():
                _string(value, f"upstream.{field}")
        if "compatibility" in item:
            compatibility = item["compatibility"]
            if not isinstance(compatibility, dict):
                raise ValueError("Invalid compatibility")
            for client, record in compatibility.items():
                if not isinstance(client, str) or not SLUG.fullmatch(client):
                    raise ValueError("Invalid client key")
                _fields(record, {"status"}, {"tested_version", "platform", "evidence"}, "compatibility record")
                if record["status"] not in STATUSES:
                    raise ValueError("Invalid compatibility status")
                for field in ("tested_version", "platform", "evidence"):
                    if field in record:
                        _string(record[field], field)
    return data["items"]
