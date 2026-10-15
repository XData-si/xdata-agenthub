"""Opt-in, pinned catalog refresh. Never execute source content."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen
from catalog_schema import validate_catalog


def refresh_catalog(destination, *, source_url, revision, sha256, approve=False, offline=False):
    if not approve:
        raise ValueError("Explicit --approve required")
    if not isinstance(revision, str) or not revision.strip() or any(c.isspace() for c in revision):
        raise ValueError("Nonempty pinned revision required")
    if not isinstance(sha256, str) or len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
        raise ValueError("Expected SHA-256 must be 64 lowercase hex characters")
    url = urlparse(source_url)
    if url.scheme != "https" or not url.netloc or url.username or url.password or url.fragment:
        raise ValueError("Only HTTPS sources without embedded credentials are supported")
    if revision not in source_url:
        raise ValueError("Source URL must explicitly contain the pinned revision")
    if offline:
        raise ValueError("Offline mode: refusing network access; local catalog unchanged")
    destination = Path(destination)
    if destination.is_symlink() or not destination.is_file():
        raise ValueError("Destination must be an existing regular catalog file")
    with urlopen(source_url, timeout=15) as response:
        if response.geturl() != source_url:
            raise ValueError("Redirects refused: pinned URL changed")
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Catalog exceeds 2 MB")
    if hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError("Catalog checksum mismatch; original preserved")
    parsed = json.loads(data.decode("utf-8"))
    validate_catalog(parsed)
    fd, name = tempfile.mkstemp(prefix=".xah-catalog-", dir=str(destination.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, destination.stat().st_mode & 0o777)
        if destination.is_symlink():
            raise ValueError("Destination became a symlink")
        os.replace(name, destination)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return sha256
