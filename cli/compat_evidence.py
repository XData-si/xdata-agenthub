"""Validate reproducible agent compatibility evidence without external dependencies."""
import json
from pathlib import Path

CLIENTS = {"claude", "codex", "opencode", "generic"}
RESULTS = {"pass", "fail", "blocked"}
METHODS = {"discovery", "native_invocation", "direct_read"}
REQUIRED = {"client", "client_version", "os", "os_version", "method",
            "result", "prompt", "steps", "evidence", "redacted", "timestamp_utc"}


def validate_evidence(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported evidence schema")
    clients = data.get("clients")
    if not isinstance(clients, list) or {x.get("client") for x in clients if isinstance(x, dict)} != CLIENTS:
        raise ValueError("Expected one baseline entry per client")
    if len(clients) != len(CLIENTS) or any(x.get("status") not in {"not_tested", "tested"} for x in clients):
        raise ValueError("Invalid client baseline")
    entries = data.get("evidence")
    if not isinstance(entries, list):
        raise ValueError("Evidence must be a list")
    for row in entries:
        if not isinstance(row, dict) or not REQUIRED.issubset(row):
            raise ValueError("Incomplete evidence entry")
        if row["client"] not in CLIENTS or row["method"] not in METHODS or row["result"] not in RESULTS:
            raise ValueError("Unknown client, method or result")
        for field in ("client_version", "os", "os_version", "prompt", "evidence", "timestamp_utc"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError("Missing evidence field: " + field)
        if not isinstance(row["steps"], list) or not row["steps"] or not all(isinstance(s, str) and s.strip() for s in row["steps"]):
            raise ValueError("Reproduction steps required")
        if row["redacted"] is not True:
            raise ValueError("Evidence must be reviewed and redacted")
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate redacted agent compatibility evidence")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        validate_evidence(json.loads(args.path.read_text(encoding="utf-8")))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Invalid evidence: {exc}\n")
    print("Evidence schema OK")


if __name__ == "__main__":
    main()
