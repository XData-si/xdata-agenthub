"""Read-only proof that a transaction has already been fully rolled back.

No journal mutation, lock removal, or file writes. Manifest entries and destination digests are verified; writer ownership remains external.
"""
from recovery_inspect import inspect_transactions
from installed_manifest import load_manifest


def resolution_preflight(target, transaction_id):
    matches = [tx for tx in inspect_transactions(target)
               if tx["transaction_id"] == transaction_id]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous transaction ID")
    tx = matches[0]
    if tx["state"] not in ("prepared", "applying", "recovery_required"):
        raise ValueError("Transaction is not pending resolution")
    manifest = load_manifest(target)
    for op in tx["operations"]:
        expected = "original" if op["action"] == "update" else "missing"
        if op["file_state"] != expected:
            raise ValueError("Destination not restored to original state: " + op["path"])
        record = manifest["files"].get(op["path"])
        if op["action"] == "update":
            if record is None or record["item_id"] != tx["item_id"]:
                raise ValueError("Manifest ownership missing or mismatched: " + op["path"])
            from pathlib import Path
            from recovery_inspect import _hash
            if record["sha256"] != _hash(Path(target) / op["path"]):
                raise ValueError("Manifest checksum differs from restored file: " + op["path"])
        elif record is not None:
            raise ValueError("Manifest still tracks added file: " + op["path"])
        if op["action"] == "update" and op["backup_state"] != "verified":
            raise ValueError("Original backup integrity failed: " + op["path"])
        if op["action"] == "add" and op["backup_state"] != "not_applicable":
            raise ValueError("Unexpected add backup: " + op["path"])
    return {"transaction_id": transaction_id, "state": tx["state"],
            "files_restored": True, "journal_unchanged": True,
            "manifest_verified": True,
            "warning": "Not authorization to unlock or resolve; verify writer ownership separately."}
