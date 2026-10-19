"""Explicit, conservative rollback of an interrupted XAH update.

Requires the normal cooperative writer lock. Does not clear stale locks.
A journal is marked resolved only after destination files and manifest match
their original tracked state. Refuses unknown file contents and metadata.
"""
from pathlib import Path
import os
import tempfile

from installed_manifest import _relative, _digest, load_manifest, save_manifest
from recovery_inspect import inspect_transactions
from recovery_journal import transition_journal
from update_lock import update_lock


def rollback_transaction(target, transaction_id):
    root = Path(target).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Target must be an existing directory")
    with update_lock(root):
        return _rollback_locked(root, transaction_id)


def _rollback_locked(root, transaction_id):
    matches = [tx for tx in inspect_transactions(root)
               if tx["transaction_id"] == transaction_id]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous transaction ID")
    tx = matches[0]
    if tx["state"] not in ("prepared", "applying", "recovery_required"):
        raise ValueError("Transaction not eligible for rollback")
    # Do not resolve one transaction while another is pending.
    others = [entry["transaction_id"] for entry in inspect_transactions(root)
              if entry["transaction_id"] != transaction_id
              and entry["state"] in ("prepared", "applying", "recovery_required")]
    if others:
        raise ValueError("Other unresolved transactions exist")
    manifest = load_manifest(root)
    new_manifest = {"schema_version": 1, "files": dict(manifest["files"])}
    operations = []
    journal_root = root / ".xah-transactions" / transaction_id
    for index, op in enumerate(tx["operations"]):
        rel = op["path"]
        dest = root / rel
        if _relative(root, dest) != rel:
            raise ValueError("Unsafe destination path")
        state = op["file_state"]
        record = manifest["files"].get(rel)
        # A manifest can be old or fully updated if a crash occurred around
        # save_manifest. Never accept a digest unrelated to this journal.
        from recovery_journal import validate_journal
        import json
        metadata = validate_journal(json.loads((journal_root / "journal.json").read_text()))
        original_digest = metadata["operations"][index]["original_sha256"]
        intended_digest = metadata["operations"][index]["intended_sha256"]
        if op["action"] == "update":
            if op["backup_state"] != "verified" or state not in ("original", "intended"):
                raise ValueError("Unsafe update destination or backup: " + rel)
            if record is None or record["item_id"] != tx["item_id"] or record["sha256"] not in (original_digest, intended_digest):
                raise ValueError("Unexpected installed manifest record: " + rel)
            backup = journal_root / "originals" / str(index)
            new_manifest["files"][rel] = {"sha256": original_digest, "item_id": tx["item_id"]}
            operations.append(("restore" if state == "intended" else "unchanged", dest, backup, intended_digest))
        else:
            if op["backup_state"] != "not_applicable" or state not in ("missing", "intended"):
                raise ValueError("Unsafe added destination: " + rel)
            if record is not None and (record["item_id"] != tx["item_id"] or record["sha256"] != intended_digest):
                raise ValueError("Unexpected installed manifest record: " + rel)
            new_manifest["files"].pop(rel, None)
            operations.append(("remove" if state == "intended" else "unchanged", dest, None, intended_digest))
    # All metadata and backup checks complete before first destination write.
    for action, dest, backup, expected in reversed(operations):
        _relative(root, dest)
        if action == "unchanged":
            continue
        if not dest.is_file() or dest.is_symlink() or _digest(dest) != expected:
            raise ValueError("Destination changed during rollback: " + str(dest))
        if action == "remove":
            dest.unlink()
        else:
            # Check backup again immediately before reading it.
            if backup.is_symlink() or not backup.is_file():
                raise ValueError("Backup changed during rollback")
            content = backup.read_bytes()
            import hashlib
            if hashlib.sha256(content).hexdigest() != metadata["operations"][operations.index((action, dest, backup, expected))]["backup_sha256"]:
                raise ValueError("Backup changed during rollback")
            fd, stage = tempfile.mkstemp(prefix=".xah-rollback-", dir=str(dest.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chmod(stage, dest.stat().st_mode & 0o777)
                os.replace(stage, dest)
            finally:
                if os.path.exists(stage):
                    os.unlink(stage)
    # Re-read manifest to avoid silently clobbering out-of-band edits.
    if load_manifest(root) != manifest:
        raise ValueError("Manifest changed during rollback; operator review required")
    if new_manifest != manifest:
        save_manifest(root, new_manifest)
    transition_journal(journal_root, "resolved")
    return {"transaction_id": transaction_id, "state": "resolved",
            "operations": len(operations)}
