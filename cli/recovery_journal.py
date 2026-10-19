"""Strict, read-only validation for proposed XAH crash-recovery journals.

This module does not write transactions or perform recovery.
"""
import re
from pathlib import PurePosixPath

HEX = re.compile(r"^[0-9a-f]{64}$")
TXID = re.compile(r"^[0-9a-f]{32}$")
STATES = {"prepared", "applying", "committed", "cleaned", "recovery_required"}
ACTIONS = {"add", "update"}


def _digest(value, *, optional=False):
    if value is None and optional:
        return
    if not isinstance(value, str) or HEX.fullmatch(value) is None:
        raise ValueError("Invalid journal digest")


def _path(value):
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("Unsafe journal path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("Unsafe journal path")
    if ":" in value.split("/")[0]:
        raise ValueError("Unsafe journal path")
    return value


def validate_journal(data):
    """Validate untrusted JSON-decoded journal metadata; return data unchanged.

    This is schema validation only: filesystem symlinks and backup bytes must
    be checked separately before any future recovery operation.
    """
    if not isinstance(data, dict) or set(data) != {
        "schema_version", "transaction_id", "item_id", "state", "operations"
    }:
        raise ValueError("Invalid journal fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported journal schema")
    if not isinstance(data["transaction_id"], str) or not TXID.fullmatch(data["transaction_id"]):
        raise ValueError("Invalid transaction ID")
    if not isinstance(data["item_id"], str) or not data["item_id"] or len(data["item_id"]) > 256:
        raise ValueError("Invalid item ID")
    if data["state"] not in STATES:
        raise ValueError("Invalid journal state")
    ops = data["operations"]
    if not isinstance(ops, list) or not ops or len(ops) > 10000:
        raise ValueError("Invalid journal operations")
    seen = set()
    for op in ops:
        if not isinstance(op, dict) or set(op) != {
            "action", "path", "original_sha256", "intended_sha256",
            "backup_sha256", "completed"
        }:
            raise ValueError("Invalid journal operation")
        if op["action"] not in ACTIONS:
            raise ValueError("Invalid journal action")
        path = _path(op["path"])
        if path in seen:
            raise ValueError("Duplicate journal path")
        seen.add(path)
        _digest(op["intended_sha256"])
        _digest(op["original_sha256"], optional=op["action"] == "add")
        _digest(op["backup_sha256"], optional=op["action"] == "add")
        if op["action"] == "update" and op["original_sha256"] != op["backup_sha256"]:
            raise ValueError("Backup digest does not match original")
        if op["action"] == "add" and (op["original_sha256"] is not None or op["backup_sha256"] is not None):
            raise ValueError("Add must not have original or backup")
        if type(op["completed"]) is not bool:
            raise ValueError("Invalid completion flag")
    if data["state"] == "prepared" and any(op["completed"] for op in ops):
        raise ValueError("Prepared transaction cannot have completed operations")
    if data["state"] in ("committed", "cleaned") and not all(op["completed"] for op in ops):
        raise ValueError("Committed transaction has incomplete operations")
    return data

def transition_journal(tx, state, *, completed=None):
    """Atomically persist a validated journal state/progress update.

    Caller holds the cooperative writer lock. Does not perform recovery.
    """
    import json
    import os
    import tempfile
    from pathlib import Path
    from journal_prepare import _sync_directory

    tx = Path(tx)
    path = tx / "journal.json"
    if tx.is_symlink() or path.is_symlink():
        raise ValueError("Symlink journal path refused")
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_journal(data)
    old_state = data["state"]
    allowed = {
        "prepared": {"applying", "recovery_required"},
        "applying": {"applying", "committed", "recovery_required"},
        "committed": {"cleaned"},
        "recovery_required": set(),
        "cleaned": set(),
    }
    if state not in allowed[old_state]:
        raise ValueError("Invalid journal state transition")
    if completed is not None:
        if type(completed) is not int or not 0 <= completed < len(data["operations"]):
            raise ValueError("Invalid completed operation index")
        if state != "applying":
            raise ValueError("Completion requires applying state")
        data["operations"][completed]["completed"] = True
    data["state"] = state
    validate_journal(data)
    fd, name = tempfile.mkstemp(prefix=".xah-journal-", dir=str(tx))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write((json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        _sync_directory(tx)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return data
