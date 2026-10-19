"""Read-only diagnostic of XAH writer locks; never removes a lock.

PID checks are advisory only: PID reuse, remote hosts and race conditions mean
this cannot prove a lock is safe to remove.
"""
import os
from pathlib import Path


def inspect_writer_lock(target):
    root = Path(target).resolve()
    lock = root / ".xah-update.lock"
    if lock.is_symlink():
        return {"status": "unsafe_symlink", "pid": None, "removal_safe": False}
    if not lock.exists():
        return {"status": "absent", "pid": None, "removal_safe": False}
    if not lock.is_dir():
        return {"status": "unsafe_type", "pid": None, "removal_safe": False}
    pid_file = lock / "pid"
    if pid_file.is_symlink() or not pid_file.is_file():
        return {"status": "unverifiable", "pid": None, "removal_safe": False}
    if pid_file.stat().st_size > 32:
        return {"status": "unverifiable", "pid": None, "removal_safe": False}
    raw = pid_file.read_text(encoding="ascii").strip()
    if not raw.isdecimal() or len(raw) > 12 or int(raw) < 1:
        return {"status": "unverifiable", "pid": None, "removal_safe": False}
    pid = int(raw)
    if os.name != "posix":
        return {"status": "unknown_platform", "pid": pid, "removal_safe": False}
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        status = "pid_not_found"
    except PermissionError:
        status = "pid_exists_or_inaccessible"
    else:
        status = "pid_exists"
    return {"status": status, "pid": pid, "removal_safe": False}
