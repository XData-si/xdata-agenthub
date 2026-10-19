"""Fail-closed, read-only preflight for a future explicit rollback command.

This module never restores files, changes journals, or removes locks.
"""
from recovery_inspect import inspect_transactions


def rollback_preflight(target, transaction_id):
    """Return a per-file rollback plan only when all evidence is safe.

    The result is informational. Future execution must revalidate under lock.
    """
    transactions = inspect_transactions(target)
    matches = [tx for tx in transactions if tx["transaction_id"] == transaction_id]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous transaction ID")
    tx = matches[0]
    if tx["state"] not in ("applying", "recovery_required"):
        raise ValueError("Rollback refused for transaction state: " + tx["state"])
    plan = []
    for op in tx["operations"]:
        state = op["file_state"]
        backup = op["backup_state"]
        if op["action"] == "update":
            if backup != "verified":
                raise ValueError("Rollback refused: backup is not verified: " + op["path"])
            if state == "original":
                action = "unchanged"
            elif state == "intended":
                action = "restore_original"
            else:
                raise ValueError("Rollback refused: unknown destination contents: " + op["path"])
        else:
            if backup != "not_applicable":
                raise ValueError("Rollback refused: unexpected add backup: " + op["path"])
            if state == "missing":
                action = "unchanged"
            elif state == "intended":
                action = "remove_added"
            else:
                raise ValueError("Rollback refused: unknown added file contents: " + op["path"])
        plan.append({"path": op["path"], "action": action})
    return {"transaction_id": transaction_id, "state": tx["state"],
            "eligible": True, "operations": plan,
            "warning": "Read-only assessment; execution requires fresh locked validation."}
