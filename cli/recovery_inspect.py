"""Read-only inspection of XAH transaction journals; never repairs or unlocks."""
import hashlib
import json
from pathlib import Path
from recovery_journal import validate_journal
from installed_manifest import _relative

STORE = ".xah-transactions"


def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_transactions(target):
    root = Path(target).resolve()
    store = root / STORE
    if store.is_symlink():
        raise ValueError("Symlink transaction store refused")
    if not store.exists():
        return []
    if not store.is_dir():
        raise ValueError("Invalid transaction store")
    results = []
    for tx in sorted(store.iterdir(), key=lambda p: p.name):
        if tx.is_symlink() or not tx.is_dir():
            raise ValueError("Unsafe transaction directory")
        journal = tx / "journal.json"
        if journal.is_symlink() or not journal.is_file():
            raise ValueError("Missing or symlinked transaction journal")
        if journal.stat().st_size > 2_000_000:
            raise ValueError("Oversized transaction journal")
        data = validate_journal(json.loads(journal.read_text(encoding="utf-8")))
        if data["transaction_id"] != tx.name:
            raise ValueError("Transaction directory ID mismatch")
        originals = tx / "originals"
        if originals.is_symlink() or not originals.is_dir():
            raise ValueError("Unsafe originals directory")
        operations = []
        for index, op in enumerate(data["operations"]):
            destination = root / op["path"]
            try:
                if _relative(root, destination) != op["path"]:
                    raise ValueError("Invalid destination path")
            except ValueError:
                raise ValueError("Unsafe recovery destination: " + op["path"])
            if destination.is_symlink():
                status = "unsafe_symlink"
            elif not destination.exists():
                status = "missing"
            elif not destination.is_file():
                status = "unsafe_type"
            else:
                actual = _hash(destination)
                if actual == op["intended_sha256"]:
                    status = "intended"
                elif op["original_sha256"] is not None and actual == op["original_sha256"]:
                    status = "original"
                else:
                    status = "modified"
            backup = tx / "originals" / str(index)
            if backup.is_symlink():
                backup_status = "unsafe_symlink"
            elif op["action"] == "add":
                backup_status = "unexpected" if backup.exists() else "not_applicable"
            elif not backup.is_file():
                backup_status = "missing"
            else:
                backup_status = ("verified" if _hash(backup) == op["backup_sha256"]
                                 else "tampered")
            operations.append({"path": op["path"], "action": op["action"],
                               "completed": op["completed"], "file_state": status,
                               "backup_state": backup_status})
        results.append({"transaction_id": tx.name, "state": data["state"],
                        "item_id": data["item_id"], "operations": operations})
    return results
