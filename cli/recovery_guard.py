"""Fail closed before any XAH writer if unresolved recovery journals exist.

The guard is read-only and requires callers to hold the cooperative writer lock.
"""
from recovery_inspect import inspect_transactions

UNRESOLVED = {"prepared", "applying", "recovery_required"}


def require_no_pending_transactions(target):
    pending = [tx["transaction_id"] for tx in inspect_transactions(target)
               if tx["state"] in UNRESOLVED]
    if pending:
        raise ValueError(
            "Unresolved XAH transaction(s): " + ", ".join(pending) +
            "; inspect with xah recovery --target DIR before any new writes"
        )
