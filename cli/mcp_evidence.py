"""Evidence documents for Verified MCP levels L1 and L2 (reports/mcp/<id>/<version>.json).

An entry in registry/mcp-servers.json above L0 points to one evidence document. The document is bound to the entry:
same server name and version, and the same sha256 for every package. The level the entry claims must follow from the
recorded results, and the tools/list snapshot is re-checked here, so a report cannot claim a clean scan that the
snapshot contradicts. Standard library only; nothing is fetched or executed.
"""
import json

from mcp_catalog import HEX, LEVELS, TIMESTAMP, _fields, _https, _text, validate_entry
import mcp_tool_scan

RESULTS = {"pass", "fail"}
L2_SCANS = ("tools", "dependencies", "sbom", "secrets", "licence")
IDENTITY_CHECKS = ("namespace", "repository", "artifacts")


def _result(obj, where, required=(), optional=()):
    _fields(obj, {"result", *required}, {"tool", "details", *optional}, where)
    if obj["result"] not in RESULTS:
        raise ValueError(f"{where}.result must be pass or fail")
    if "tool" in obj:
        _text(obj["tool"], f"{where}.tool", 100)
    if "details" in obj:
        _text(obj["details"], f"{where}.details", 2000)


def validate_evidence(evidence, entry):
    """Validate an evidence document against its catalog entry; return the highest level it supports."""
    validate_entry(entry)
    _fields(evidence, {"schema_version", "server", "artifacts", "generated_at", "identity"},
            {"run", "scans", "tools"}, "evidence")
    if type(evidence["schema_version"]) is not int or evidence["schema_version"] != 1:
        raise ValueError("Unsupported MCP evidence schema version")
    server = evidence["server"]
    _fields(server, {"id", "name", "version"}, set(), "evidence.server")
    if (server["id"], server["name"], server["version"]) != (entry["id"], entry["name"], entry["version"]):
        raise ValueError(f"evidence.server does not match catalog entry {entry['id']} {entry['version']}")
    if not isinstance(evidence["generated_at"], str) or not TIMESTAMP.fullmatch(evidence["generated_at"]):
        raise ValueError("evidence.generated_at must be a UTC timestamp")
    if "run" in evidence:
        _https(evidence["run"], "evidence.run")

    packages = [a for a in entry["artifacts"] if a["kind"] == "package"]
    recorded = evidence["artifacts"]
    if not isinstance(recorded, list):
        raise ValueError("evidence.artifacts must be an array")
    for idx, artifact in enumerate(recorded):
        _fields(artifact, {"registry", "identifier", "version", "sha256"}, set(), f"evidence.artifacts[{idx}]")
        if not isinstance(artifact["sha256"], str) or not HEX.fullmatch(artifact["sha256"]):
            raise ValueError(f"evidence.artifacts[{idx}].sha256 must be 64 lowercase hex characters")
    key = lambda a: (a["registry"], a["identifier"], a["version"], a.get("sha256"))
    if sorted(map(key, recorded)) != sorted(map(key, packages)):
        raise ValueError(f"evidence.artifacts do not match the pinned packages of {entry['id']}")

    identity = evidence["identity"]
    _result(identity, "evidence.identity", required=IDENTITY_CHECKS)
    for check in IDENTITY_CHECKS:
        _result(identity[check], f"evidence.identity.{check}")
    identity_ok = identity["result"] == "pass" and all(identity[c]["result"] == "pass" for c in IDENTITY_CHECKS)
    if identity["result"] == "pass" and not identity_ok:
        raise ValueError("evidence.identity passes although one of its checks failed")
    level = "L1" if identity_ok else "L0"

    if "scans" in evidence or "tools" in evidence:
        scans = evidence.get("scans")
        _fields(scans, set(L2_SCANS), set(), "evidence.scans")
        for scan in L2_SCANS:
            _result(scans[scan], f"evidence.scans.{scan}",
                    optional=("count", "digest", "errors", "warnings") if scan == "tools" else ())
        tools = evidence.get("tools")
        findings = mcp_tool_scan.scan_tools(tools)
        errors = sum(1 for f in findings if f[1] == "error")
        recorded_tools = scans["tools"]
        expected = {"count": len(tools), "digest": mcp_tool_scan.tools_digest(tools), "errors": errors,
                    "warnings": len(findings) - errors}
        for field, value in expected.items():
            if recorded_tools.get(field) != value:
                raise ValueError(f"evidence.scans.tools.{field} does not match the tools snapshot ({value})")
        if recorded_tools["result"] == "pass" and (errors or not tools):
            raise ValueError("evidence.scans.tools passes although the snapshot is empty or has errors")
        # L2 needs a package to scan: remote-only servers stop at L1.
        if level == "L1" and packages and all(scans[s]["result"] == "pass" for s in L2_SCANS):
            level = "L2"
    return level


def check_catalog_evidence(servers, root):
    """For every entry above L0: the evidence file exists, is bound to the entry and supports the claimed level."""
    checked = 0
    for entry in servers:
        if entry["level"] == "L0":
            continue
        path = root / entry["evidence"]
        if not path.is_file():
            raise ValueError(f"{entry['id']}: evidence file {entry['evidence']} not found")
        supported = validate_evidence(json.loads(path.read_text(encoding="utf-8")), entry)
        if LEVELS.index(entry["level"]) > LEVELS.index(supported):
            raise ValueError(f"{entry['id']}: level {entry['level']} claimed, evidence supports {supported}")
        checked += 1
    return checked
