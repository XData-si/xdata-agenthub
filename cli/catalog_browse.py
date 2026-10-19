"""Deterministic offline catalog facet counts and pagination."""
from collections import Counter

def facets(entries):
    counts = {"type": Counter(), "license": Counter(), "tag": Counter()}
    for item in entries:
        counts["type"][item["type"]] += 1
        counts["license"][item["license"]] += 1
        for tag in set(item.get("tags", [])):
            counts["tag"][tag] += 1
    return {key: dict(sorted(value.items())) for key, value in counts.items()}


def page(entries, *, offset=0, limit=20):
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Invalid catalog pagination")
    ordered = sorted(entries, key=lambda item: item["id"])
    return {"total": len(ordered), "offset": offset, "limit": limit,
            "items": ordered[offset:offset + limit]}
