"""Deterministic, offline catalog filtering; metadata is not runtime evidence."""
import json


def filter_items(entries, *, query="", kind=None, tag=None, agent=None, license=None, provenance=None):
    if not isinstance(query, str):
        raise ValueError("Query must be text")
    if any(ord(c) < 32 for c in query):
        raise ValueError("Query contains control characters")
    def matches(item):
        if query.casefold() not in json.dumps(item, ensure_ascii=False, sort_keys=True).casefold():
            return False
        if kind is not None and item["type"].casefold() != kind.casefold():
            return False
        if tag is not None and tag.casefold() not in [x.casefold() for x in item.get("tags", [])]:
            return False
        if agent is not None and agent.casefold() not in [x.casefold() for x in item["targets"]]:
            return False
        if license is not None and item["license"].casefold() != license.casefold():
            return False
        if provenance is not None and provenance.casefold() not in item["source"].casefold():
            return False
        return True
    return sorted((item for item in entries if matches(item)), key=lambda item: item["id"])
