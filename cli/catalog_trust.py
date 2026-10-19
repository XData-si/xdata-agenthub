"""Local-only catalog provenance classification; never fetches remote code."""
from urllib.parse import urlparse

def classify_provenance(item):
    if not isinstance(item, dict):
        raise ValueError("Catalog entry must be an object")
    source = item.get("source")
    license_name = item.get("license")
    if not isinstance(source, str) or not source.strip():
        return {"trust": "review_required", "reason": "missing_source"}
    if not isinstance(license_name, str) or not license_name.strip():
        return {"trust": "review_required", "reason": "missing_license"}
    parsed = urlparse(source)
    if parsed.scheme == "http":
        return {"trust": "review_required", "reason": "insecure_source"}
    if parsed.scheme and parsed.scheme != "https":
        return {"trust": "review_required", "reason": "unsupported_scheme"}
    return {"trust": "declared_only", "reason": "metadata_not_independently_verified"}
