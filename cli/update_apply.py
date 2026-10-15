"""Conservative transactional update with rollback for tracked local files."""
import os
import tempfile
from installed_manifest import load_manifest, save_manifest, _relative, _digest
from update_plan import plan_update


def apply_update(target, item_id, planned, *, fail_after=None):
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
    changed = []
    try:
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
            data["files"][rel] = {"sha256": _digest(dest), "item_id": item_id}
            if fail_after is not None and len(changed) >= fail_after:
                raise RuntimeError("Injected update failure")
        if changed:
            save_manifest(target, data)
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
        if errors:
            raise RuntimeError("ROLLBACK INCOMPLETE; manual recovery required: " + "; ".join(errors))
        raise
    return actions
