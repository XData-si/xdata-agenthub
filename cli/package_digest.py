"""Deterministic SHA-256 digest of a catalog item's package (all files of a skill, or the single file of other items).

The digest is the SHA-256 of a manifest with one line per file, sorted by POSIX relative path:
``<sha256 of file>  <relative/path>\\n`` (the same layout as ``sha256sum`` output). It is independent of file system
order, timestamps and absolute paths. Line endings are hashed as stored; the repository pins LF in .gitattributes.
"""
import hashlib
from pathlib import Path, PurePosixPath


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def digest_from_entries(entries):
    """entries: iterable of (POSIX relative path, file sha256). Returns the package digest."""
    entries = list(entries)
    if len({rel for rel, _ in entries}) != len(entries):
        raise ValueError("Duplicate package path")
    for rel, _ in entries:
        if rel.startswith("/") or ".." in PurePosixPath(rel).parts:
            raise ValueError(f"Unsafe package path: {rel}")
    lines = "".join(f"{sha}  {rel}\n" for rel, sha in sorted(entries))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def package_digest(files):
    """files: iterable of (absolute path, relative path)."""
    return digest_from_entries((PurePosixPath(*Path(rel).parts).as_posix(), file_sha256(path)) for path, rel in files)
