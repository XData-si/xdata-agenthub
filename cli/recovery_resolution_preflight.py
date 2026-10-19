"""Read-only proof that a transaction has already been fully rolled back.

No journal mutation, lock removal, or file writes. The manifest is checked
separately by the operator before any future resolution implementation.
"""
from recovery_inspect import inspect_transactions


def resolution_preflight(target, transaction_id):
    matches = [tx for tx in inspect_transactions(target)
               if tx["transaction_id"] == transaction_id]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous transaction ID")
    tx = matches[0]
    if tx["state"] not in ("prepared", "applying", "recovery_required"):
        raise ValueError("Transaction is not pending resolution")
    for op in tx["operations"]:
        expected = "original" if op["action"] == "update" else "missing"
        if op["file_state"] != expected:
            raise ValueError("Destination not restored to original state: " + op["path"])
        if op["action"] == "update" and op["backup_state"] != "verified":
            raise ValueError("Original backup integrity failed: " + op["path"])
        if op["action"] == "add" and op["backup_state"] != "not_applicable":
            raise ValueError("Unexpected add backup: " + op["path"])
    return {"transaction_id": transaction_id, "state": tx["state"],
            "files_restored": True, "journal_unchanged": True,
            "manifest_verified": False,
            "warning": "Not authorization to unlock or resolve; verify installed manifest and writer ownership separately."}
