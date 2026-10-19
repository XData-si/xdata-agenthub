"""Portable cooperative lock for XAH update writers.

Atomic directory creation is used instead of OS-specific advisory locking.
An interrupted writer may leave a lock behind; operators must inspect it.
"""
import contextlib
import os
from pathlib import Path

LOCK_NAME = ".xah-update.lock"


@contextlib.contextmanager
def update_lock(target):
    root = Path(target).resolve()
    lock = root / LOCK_NAME
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ValueError(
            "Update lock exists; another writer may be active. "
            "Inspect .xah-update.lock before manual recovery."
        ) from exc
    try:
        # Diagnostic only; ownership is represented by the lock directory.
        (lock / "pid").write_text(str(os.getpid()) + "\n", encoding="ascii")
        yield
    finally:
        (lock / "pid").unlink(missing_ok=True)
        lock.rmdir()
