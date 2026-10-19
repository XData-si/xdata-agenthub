"""Prepare a validated write-ahead journal and verified original-file backups.

Preparation is opt-in and does not modify installed destination files.
No automatic recovery, locking, or crash-consistency guarantee is provided here.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets

from recovery_journal import validate_journal
from installed_manifest import _relative

STORE = ".xah-transactions"


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _write_new(path, content):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _sync_directory(path):
    if os.name != "posix":
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def prepare_journal(target, item_id, operations):
    """Create a new transaction with validated metadata and immutable backups.

    operations: iterable of (action, source, destination), with action add/update.
    Caller must hold the XAH writer lock and validate planned conflicts.
    """
    root = Path(target).resolve()
    if not root.is_dir():
        raise ValueError("Target must be a directory")
    if not isinstance(item_id, str) or not item_id or len(item_id) > 256:
        raise ValueError("Invalid item ID")
    entries = []
    backups = []
    for action, source, destination in operations:
        rel = _relative(root, destination)
        if action not in ("add", "update"):
            raise ValueError("Invalid action")
        dest = root / rel
        if dest.is_symlink():
            raise ValueError("Symlink destination refused")
        intended = Path(source).read_bytes()
        original = None
        if action == "update":
            if not dest.is_file():
                raise ValueError("Update destination missing")
            original = dest.read_bytes()
        elif dest.exists():
            raise ValueError("Add destination exists")
        entries.append({"action": action, "path": rel,
                        "original_sha256": _sha(original) if original is not None else None,
                        "intended_sha256": _sha(intended),
                        "backup_sha256": _sha(original) if original is not None else None,
                        "completed": False})
        backups.append(original)
    if not entries:
        raise ValueError("No journal operations")
    txid = secrets.token_hex(16)
    metadata = {"schema_version": 1, "transaction_id": txid,
                "item_id": item_id, "state": "prepared", "operations": entries}
    validate_journal(metadata)
    store = root / STORE
    if store.is_symlink():
        raise ValueError("Symlink transaction store refused")
    store.mkdir(mode=0o700, exist_ok=True)
    tx = store / txid
    tx.mkdir(mode=0o700)
    backup_dir = tx / "originals"
    backup_dir.mkdir(mode=0o700)
    for index, original in enumerate(backups):
        if original is not None:
            _write_new(backup_dir / str(index), original)
    _sync_directory(backup_dir)
    _write_new(tx / "journal.json", (json.dumps(metadata, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    _sync_directory(tx)
    _sync_directory(store)
    return tx
