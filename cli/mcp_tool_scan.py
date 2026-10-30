"""Deterministic checks for an MCP server's tools/list snapshot (standard library only, no network).

Two groups of checks, both part of Verified MCP level L2 (docs/VERIFIED_MCP.md):
- tool-description analysis: text an agent reads as instructions (names, descriptions, parameter descriptions) is
  searched for hidden characters, instruction tags, prompt injection, concealment, credential-file references and
  encoded blobs ("tool poisoning");
- schema compatibility: tool names and input schemas must be accepted by major model providers. A single tool with
  a top-level `oneOf`, for example, can make every tool of the server unusable with some providers.

Findings are (rule, severity, tool, location, detail) tuples; severity is "error" or "warning". The patterns find
known techniques; a clean result is not proof that descriptions are harmless.
"""
import hashlib
import json
import re


# Like mcp_catalog.HIDDEN, but descriptions may contain line breaks and tabs.
HIDDEN = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")
TOOL_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
TOOL_FIELDS = ("name", "title", "description", "inputSchema", "outputSchema", "annotations")
TOP_LEVEL_FORBIDDEN = ("oneOf", "anyOf", "allOf", "not", "enum", "const", "if", "then", "else")
MAX_DESCRIPTION = 2000
MAX_SCHEMA_DEPTH = 10
MAX_SCHEMA_BYTES = 100_000

TEXT_RULES = [
    ("instruction-tag", "error",
     re.compile(r"<\s*/?\s*(important|system|instructions?|secret|hidden|admin)\b[^>]*>|\[/?(INST|SYSTEM)\]", re.I)),
    ("prompt-injection", "error",
     re.compile(r"\b(ignore|disregard|forget|override)\b[^.\n]{0,30}\b(previous|prior|above|all|other|system)\b"
                r"[^.\n]{0,20}\b(instructions?|rules|prompts?|guidelines)\b", re.I)),
    ("prompt-injection", "error", re.compile(r"\byou are now\b|\bnew system prompt\b|\breveal (your|the) system prompt\b", re.I)),
    ("concealment", "error",
     re.compile(r"\b(do not|don't|never|without)\s+(tell|telling|mention|mentioning|show|showing|reveal|revealing|"
                r"inform|informing|notify|notifying|alert|alerting)\b[^.\n]{0,30}\b(the )?(user|human|operator)s?\b", re.I)),
    ("credential-file", "error",
     re.compile(r"~/\.aws/credentials|~/\.ssh/|\bid_(rsa|ed25519|ecdsa)\b|\.npmrc\b|~/\.docker/config\.json|"
                r"~/\.kube/config|\.netrc\b|\bmcp\.json\b|claude_desktop_config\.json|~/\.cursor/", re.I)),
    ("encoded-blob", "error", re.compile(r"[A-Za-z0-9+/]{240,}={0,2}")),
    ("behaviour-instruction", "warning",
     re.compile(r"\b(when|before|after|whenever)\b[^.\n]{0,40}\b(call|calling|use|using|invok\w*|run|running)\b"
                r"[^.\n]{0,60}\b(always|must|instead|first|otherwise|read|send|pass|include|attach)\b", re.I)),
    ("url", "warning", re.compile(r"\bhttps?://[^\s)>\]\"'`]+", re.I)),
]


def _texts(tool):
    """Yield (location, text) for every string an agent may read: names, titles and descriptions, recursively."""
    for field in ("name", "title", "description"):
        if isinstance(tool.get(field), str):
            yield field, tool[field]
    annotations = tool.get("annotations")
    if isinstance(annotations, dict) and isinstance(annotations.get("title"), str):
        yield "annotations.title", annotations["title"]

    def walk(node, where):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("description", "title") and isinstance(value, str):
                    yield f"{where}.{key}", value
                elif key in ("enum", "examples", "default") and isinstance(value, list):
                    for idx, item in enumerate(value):
                        if isinstance(item, str):
                            yield f"{where}.{key}[{idx}]", item
                elif key == "properties" and isinstance(value, dict):
                    for prop, schema in value.items():
                        yield f"{where}.properties.{prop}", prop
                        yield from walk(schema, f"{where}.properties.{prop}")
                else:
                    yield from walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                yield from walk(item, f"{where}[{idx}]")
    for field in ("inputSchema", "outputSchema"):
        yield from walk(tool.get(field), field)


def _depth(node):
    if isinstance(node, dict):
        return 1 + max((_depth(v) for v in node.values()), default=0)
    if isinstance(node, list):
        return 1 + max((_depth(v) for v in node), default=0)
    return 0


def _refs(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                yield value
            else:
                yield from _refs(value)
    elif isinstance(node, list):
        for item in node:
            yield from _refs(item)


def scan_text(tool_name, tools_names, tool):
    findings = []
    for where, text in _texts(tool):
        if HIDDEN.search(text):
            findings.append(("hidden-unicode", "error", tool_name, where, "control, zero-width or bidirectional character"))
        for rule, severity, pattern in TEXT_RULES:
            match = pattern.search(text)
            if match:
                findings.append((rule, severity, tool_name, where, match.group(0)[:120]))
        if where == "description" and len(text) > MAX_DESCRIPTION:
            findings.append(("long-description", "warning", tool_name, where, f"{len(text)} characters"))
        if where == "description":
            others = sorted(n for n in tools_names if n != tool_name and len(n) > 3 and re.search(rf"\b{re.escape(n)}\b", text))
            if others:
                findings.append(("mentions-other-tool", "warning", tool_name, where, ", ".join(others)[:120]))
    return findings


def scan_schema(tool_name, tool):
    findings = []
    if not isinstance(tool_name, str) or not TOOL_NAME.fullmatch(tool_name):
        findings.append(("tool-name", "error", str(tool_name), "name", "must match [A-Za-z0-9_-]{1,64}"))
    schema = tool.get("inputSchema")
    if not isinstance(schema, dict) or schema.get("type") != "object":
        findings.append(("schema-root-type", "error", tool_name, "inputSchema", 'must be an object schema ("type": "object")'))
        return findings
    for key in TOP_LEVEL_FORBIDDEN:
        if key in schema:
            findings.append(("schema-top-level-combinator", "error", tool_name, f"inputSchema.{key}",
                             "rejected at the top level by some model providers"))
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        findings.append(("schema-properties", "error", tool_name, "inputSchema.properties", "must be an object"))
        properties = {}
    required = schema.get("required", [])
    if not isinstance(required, list) or not all(isinstance(r, str) for r in required):
        findings.append(("schema-required", "error", tool_name, "inputSchema.required", "must be an array of names"))
    else:
        missing = sorted(set(required) - properties.keys())
        if missing:
            findings.append(("schema-required", "error", tool_name, "inputSchema.required",
                             f"not in properties: {', '.join(missing)}"[:120]))
    for ref in _refs(schema):
        if not ref.startswith("#"):
            findings.append(("schema-remote-ref", "error", tool_name, "inputSchema", f"$ref {ref[:100]}"))
    if _depth(schema) > MAX_SCHEMA_DEPTH:
        findings.append(("schema-depth", "warning", tool_name, "inputSchema", f"nested deeper than {MAX_SCHEMA_DEPTH}"))
    size = len(json.dumps(schema, ensure_ascii=False))
    if size > MAX_SCHEMA_BYTES:
        findings.append(("schema-size", "warning", tool_name, "inputSchema", f"{size} bytes"))
    return findings


def scan_tools(tools):
    """Scan a tools/list result (the `tools` array). Returns findings sorted for stable reports."""
    if not isinstance(tools, list) or not all(isinstance(t, dict) for t in tools):
        raise ValueError("tools must be an array of objects")
    names = [t.get("name") for t in tools]
    findings = []
    for name in sorted({n for n in names if names.count(n) > 1}, key=str):
        findings.append(("duplicate-tool", "error", str(name), "name", f"{names.count(name)} tools share this name"))
    valid_names = {n for n in names if isinstance(n, str)}
    for tool in tools:
        name = tool.get("name")
        findings += scan_schema(name, tool)
        findings += scan_text(str(name), valid_names, tool)
    return sorted(findings, key=lambda f: (f[2], f[3], f[0], f[4]))


def tools_digest(tools):
    """sha256 over the fields an agent sees, independent of order: detects silent description changes."""
    snapshot = sorted(({k: t[k] for k in TOOL_FIELDS if k in t} for t in tools), key=lambda t: str(t.get("name")))
    canonical = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
