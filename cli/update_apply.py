"""Conservative transactional update with rollback for tracked local files."""
import os
import tempfile
from installed_manifest import load_manifest, save_manifest, _relative, _digest
from update_plan import plan_update
from update_lock import update_lock
from journal_prepare import prepare_journal
from recovery_journal import transition_journal


def apply_update(target, item_id, planned, *, fail_after=None):
    target = target.resolve()
    with update_lock(target):
        return _apply_update_locked(target, item_id, planned, fail_after=fail_after)


def _apply_update_locked(target, item_id, planned, *, fail_after=None):
    """Apply a conflict-free plan; restore all changed files on ordinary failures.

    Not a crash-consistent transaction: process termination/power loss needs manual recovery.
    """
    target = target.resolve()
    actions = plan_update(target, item_id, planned)
    if any(action == "conflict" for action, _ in actions):
        raise ValueError("Update refused: conflicts found; run update --dry-run")
    if len({rel for _, rel in actions}) != len(actions):
        raise ValueError("Duplicate update destination")
    by_path = {_relative(target, dest): (src, dest) for src, dest in planned}
    data = load_manifest(target)
    original = {rel: dest.read_bytes() for action, rel in actions
                if action == "update" for _, dest in [by_path[rel]]}
    journal = None
    pending = [(action, *by_path[rel]) for action, rel in actions if action != "skip"]
    if pending:
        journal = prepare_journal(target, item_id, pending)
    changed = []
    if journal is not None:
        transition_journal(journal, "applying")
    try:
        journal_index = 0
        for action, rel in actions:
            if action == "skip":
                continue
            src, dest = by_path[rel]
            _relative(target, dest)  # Revalidate against symlink changes.
            if action == "update" and _digest(dest) != data["files"][rel]["sha256"]:
                raise ValueError("File changed during update: " + rel)
            if action == "add" and (dest.exists() or dest.is_symlink()):
                raise ValueError("Destination appeared during update: " + rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            content = src.read_bytes()
            fd, name = tempfile.mkstemp(prefix=".xah-stage-", dir=str(dest.parent))
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                if action == "update":
                    os.chmod(name, dest.stat().st_mode & 0o777)
                os.replace(name, dest)
            finally:
                if os.path.exists(name):
                    os.unlink(name)
            changed.append((action, rel))
            if journal is not None:
                transition_journal(journal, "applying", completed=journal_index)
                journal_index += 1
            data["files"][rel] = {"sha256": _digest(dest), "item_id": item_id}
            if fail_after is not None and len(changed) >= fail_after:
                raise RuntimeError("Injected update failure")
        if changed:
            save_manifest(target, data)
        if journal is not None:
            transition_journal(journal, "committed")
        # Preserve journal for explicit operator review; no automatic cleanup.
    except Exception:
        errors = []
        for action, rel in reversed(changed):
            _, dest = by_path[rel]
            try:
                if action == "add":
                    dest.unlink()
                else:
                    fd, name = tempfile.mkstemp(prefix=".xah-restore-", dir=str(dest.parent))
                    try:
                        with os.fdopen(fd, "wb") as handle:
                            handle.write(original[rel])
                            handle.flush()
                            os.fsync(handle.fileno())
                        os.replace(name, dest)
                    finally:
                        if os.path.exists(name):
                            os.unlink(name)
            except OSError as exc:
                errors.append(f"{rel}: {exc}")
        if journal is not None:
            try:
                transition_journal(journal, "recovery_required")
            except Exception as journal_error:
                errors.append("journal: " + str(journal_error))
        if errors:
            raise RuntimeError("ROLLBACK INCOMPLETE OR JOURNAL ERROR; manual recovery required: " + "; ".join(errors))
        raise
    return actions
