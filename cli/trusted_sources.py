"""Operator trust policy for catalog sources (XAH-303). Opt-in: without a policy file nothing changes.

The policy is a JSON file named by XAH_TRUSTED_SOURCES (or `xah --trusted-sources PATH`). When it is set:
- `catalog-refresh` accepts only HTTPS URLs that start with one of `refresh_url_prefixes`;
- every additional catalog (`--catalog`, XAH_CATALOGS) must lie inside one of `catalog_dirs`.

    {"schema_version": 1,
     "refresh_url_prefixes": ["https://raw.githubusercontent.com/XData-si/xdata-agenthub/"],
     "catalog_dirs": ["~/org-skills"]}

The policy narrows where content may come from; it does not authenticate a publisher. Pinned revisions and SHA-256
checks still apply to every refresh.
"""
import json
import pathlib
from urllib.parse import urlparse

POLICY_ENV = "XAH_TRUSTED_SOURCES"
FIELDS = {"schema_version", "refresh_url_prefixes", "catalog_dirs"}


def _prefix(value, where):
    if not isinstance(value, str):
        raise ValueError(f"{where} must be a string")
    url = urlparse(value)
    # A prefix must end at a path boundary, otherwise https://host/org would also admit https://host/org-evil/.
    if url.scheme != "https" or not url.netloc or url.username or url.password or url.query or url.fragment \
            or not value.endswith("/") or "@" in url.netloc:
        raise ValueError(f"{where} must be an https URL prefix ending with '/', without credentials or query")
    return value


def load_policy(path):
    """Return the validated policy from PATH, or None when PATH is empty."""
    if not path:
        return None
    file = pathlib.Path(path).expanduser()
    if file.is_symlink() or not file.is_file():
        raise ValueError(f"Trusted sources policy must be a regular file: {file}")
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or set(data) - FIELDS:
        raise ValueError(f"Trusted sources policy {file}: schema_version 1 with fields {sorted(FIELDS - {'schema_version'})}")
    prefixes = data.get("refresh_url_prefixes", [])
    dirs = data.get("catalog_dirs", [])
    if not isinstance(prefixes, list) or not isinstance(dirs, list):
        raise ValueError(f"Trusted sources policy {file}: refresh_url_prefixes and catalog_dirs must be arrays")
    resolved = []
    for idx, value in enumerate(dirs):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"catalog_dirs[{idx}] must be a nonempty path")
        directory = pathlib.Path(value).expanduser()
        if not directory.is_absolute():
            directory = file.parent / directory
        resolved.append(directory.resolve())
    return {"file": file, "refresh_url_prefixes": [_prefix(v, f"refresh_url_prefixes[{i}]") for i, v in enumerate(prefixes)],
            "catalog_dirs": resolved}


def check_refresh_url(policy, url):
    if policy is None:
        return
    if not any(url.startswith(prefix) for prefix in policy["refresh_url_prefixes"]):
        raise ValueError(f"Refresh URL is not allowed by the trusted sources policy {policy['file']}")


def check_catalog(policy, path):
    if policy is None:
        return
    resolved = pathlib.Path(path).resolve()
    if not any(resolved.is_relative_to(directory) for directory in policy["catalog_dirs"]):
        raise ValueError(f"Additional catalog {resolved} is outside the trusted catalog_dirs of {policy['file']}")


def describe(policy):
    if policy is None:
        return f"Trusted sources: no policy ({POLICY_ENV} not set); any pinned HTTPS refresh and local catalog allowed"
    return (f"Trusted sources: {policy['file']} — {len(policy['refresh_url_prefixes'])} refresh URL prefixes, "
            f"{len(policy['catalog_dirs'])} catalog directories")
