"""Offline catalog metadata risk classification.

A classification is NOT a security certification or independent verification.
Catalog source may be descriptive text rather than a URL.
"""
from urllib.parse import urlparse


def _url_risk(value):
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate:
        return None
    if candidate.startswith("//"):
        return "scheme_relative_url"
    parsed = urlparse(candidate)
    if parsed.scheme == "http":
        return "insecure_source"
    if parsed.scheme and parsed.scheme != "https":
        return "unsupported_scheme"
    if parsed.scheme == "https" and (not parsed.netloc or parsed.username or parsed.password):
        return "invalid_https_source"
    return None


def classify_provenance(item):
    if not isinstance(item, dict):
        raise ValueError("Catalog entry must be an object")
    source = item.get("source")
    license_name = item.get("license")
    if not isinstance(source, str) or not source.strip():
        return {"trust": "review_required", "reason": "missing_source"}
    if not isinstance(license_name, str) or not license_name.strip():
        return {"trust": "review_required", "reason": "missing_license"}
    risk = _url_risk(source)
    if risk:
        return {"trust": "review_required", "reason": risk}
    upstream = item.get("upstream")
    if isinstance(upstream, dict):
        risk = _url_risk(upstream.get("url"))
        if risk:
            return {"trust": "review_required", "reason": "upstream_" + risk}
    return {"trust": "declared_only", "reason": "metadata_not_independently_verified"}
