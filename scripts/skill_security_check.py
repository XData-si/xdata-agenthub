#!/usr/bin/env python3
"""Deterministic security gate for skill packages (no network, standard library only).

AgentHub skills are *instructions only*. This gate rejects content that is commonly used to attack agents or the
people running them: executable payloads, hidden Unicode, hidden HTML comments, piped downloads, encoded blobs,
plain-HTTP or shortened links and prompt-injection phrasing outside of quoted examples.

Usage: skill_security_check.py [--json] [skill-id ...]   (default: every skill in registry/catalog.json)
Exit status: 0 = no errors, 1 = at least one error. Warnings never fail the gate.
"""
import json
import pathlib
import re
import stat
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".csv", ".svg", ".png"}
MAX_FILE_BYTES = 200_000
HIDDEN_CHARS = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿­]")
AUDIT_MARKER = "<!-- xah-audit: fixture -->"

# Patterns that are errors anywhere in a text file, including code blocks.
ALWAYS = [
    ("piped-download", re.compile(r"(curl|wget|iwr|Invoke-WebRequest)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", re.I)),
    ("piped-download", re.compile(r"\b(iex|Invoke-Expression)\b.*\b(DownloadString|iwr|Invoke-WebRequest)\b", re.I)),
    ("decode-and-execute", re.compile(r"base64\s+(-d|--decode)[^\n]*\|\s*(ba)?sh\b", re.I)),
    ("plain-http-download", re.compile(r"\b(curl|wget)\b[^\n]*\bhttp://", re.I)),
    ("encoded-blob", re.compile(r"[A-Za-z0-9+/]{240,}={0,2}")),
]
# Patterns that are errors in prose but allowed inside fenced code blocks or inline code (quoted fixtures).
PROSE_ONLY = [
    ("prompt-injection", re.compile(r"\b(ignore|disregard|forget)\b[^.\n]{0,30}\b(previous|prior|above|all)\b[^.\n]{0,20}\b(instructions?|rules|prompts?)\b", re.I)),
    ("prompt-injection", re.compile(r"\byou are now\b|\bnew system prompt\b|\breveal (your|the) system prompt\b", re.I)),
    ("exfiltration", re.compile(r"\b(send|upload|post|exfiltrate)\b[^.\n]{0,40}\b(secrets?|credentials?|tokens?|api keys?|\.env|ssh keys?)\b[^.\n]{0,40}\b(to|at)\s+https?://", re.I)),
]
CREDENTIAL_FILES = re.compile(r"(~/\.aws/credentials|~/\.ssh/id_\w+|\.npmrc|~/\.docker/config\.json|~/\.kube/config|\.netrc|\bid_rsa\b)")
URL = re.compile(r"\b(https?)://([^\s)>\]\"'`]+)")
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "rebrand.ly", "cutt.ly"}
RAW_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}(:\d+)?(/|$)")


def strip_code(text):
    """Remove fenced code blocks and inline code spans so prose-only rules see prose."""
    text = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$", "", text)
    return re.sub(r"`[^`\n]+`", "", text)


def marked_fixture_lines(text):
    """Line numbers inside a fenced block that directly follows the audit fixture marker (documented test data)."""
    lines, marked, in_fence, fence, armed = text.splitlines(), set(), False, "", False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_fence and stripped == AUDIT_MARKER:
            armed = True
            continue
        opener = re.match(r"^\s*(`{3,}|~{3,})", line)
        if opener and not in_fence:
            in_fence, fence, current = True, opener.group(1), armed
            armed = False
            continue
        if opener and in_fence and opener.group(1)[0] == fence[0]:
            in_fence = False
            continue
        if in_fence and current:
            marked.add(number)
        if not in_fence and stripped:
            armed = False
    return marked


def check_skill(skill_dir):
    errors, warnings = [], []
    rel = lambda p: p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
    files = sorted(skill_dir.rglob("*"))
    if not (skill_dir / "SKILL.md").is_file():
        errors.append(("structure", rel(skill_dir), "missing SKILL.md"))
    for path in files:
        if path.is_symlink():
            errors.append(("symlink", rel(path), "symlinks are not allowed in skill packages"))
            continue
        if path.is_dir():
            if path.name in {"scripts", "bin", "hooks"}:
                errors.append(("executable-content", rel(path), "skills are instructions only; no scripts/bin/hooks"))
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            errors.append(("file-type", rel(path), f"file type {path.suffix or '(none)'} not allowed"))
            continue
        if path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            errors.append(("executable-bit", rel(path), "file is marked executable"))
        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(("size", rel(path), f"larger than {MAX_FILE_BYTES} bytes"))
        if path.suffix.lower() == ".png":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fixture_lines = marked_fixture_lines(text)
        for number, line in enumerate(text.splitlines(), 1):
            if HIDDEN_CHARS.search(line):
                errors.append(("hidden-unicode", f"{rel(path)}:{number}", "zero-width or bidirectional control character"))
            for name, pattern in ALWAYS:
                if number not in fixture_lines and pattern.search(line):
                    errors.append((name, f"{rel(path)}:{number}", line.strip()[:120]))
            for scheme, rest in URL.findall(line):
                host = rest.split("/")[0].lower()
                if scheme == "http" and not host.startswith(("localhost", "127.0.0.1")):
                    warnings.append(("plain-http-link", f"{rel(path)}:{number}", f"http://{rest[:80]}"))
                if host in SHORTENERS:
                    errors.append(("shortened-link", f"{rel(path)}:{number}", host))
                if RAW_IP.match(rest) and not rest.startswith(("127.", "10.", "192.168.")):
                    warnings.append(("raw-ip-link", f"{rel(path)}:{number}", rest[:80]))
        comments = [c for c in re.findall(r"(?s)<!--.*?-->", text) if c.strip() != AUDIT_MARKER]
        if comments:
            errors.append(("hidden-comment", rel(path), f"{len(comments)} HTML comment(s); visible text only"))
        prose = strip_code(text)
        for match in CREDENTIAL_FILES.finditer(prose):
            warnings.append(("credential-file-reference", rel(path), f"mentions {match.group(0)}; confirm it never asks to read or share it"))
        for name, pattern in PROSE_ONLY:
            for match in pattern.finditer(prose):
                errors.append((name, rel(path), match.group(0)[:120]))
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        body = skill_md.read_text(encoding="utf-8")
        if not re.search(r"(?m)^## (Safety|Guardrails)\b", body):
            errors.append(("missing-safety", rel(skill_md), "a '## Safety' (or '## Guardrails') section is required"))
        if not re.search(r"(?m)^## (Acceptance checks|Completion criteria)\b", body):
            warnings.append(("missing-acceptance", rel(skill_md), "no '## Acceptance checks' section"))
    return errors, warnings


def main(argv):
    as_json = "--json" in argv
    ids = [a for a in argv if not a.startswith("--")]
    catalog = json.loads((ROOT / "registry/catalog.json").read_text(encoding="utf-8"))
    skills = ids or [i["id"] for i in catalog["items"] if i["type"] == "skill"]
    report = {}
    for skill_id in skills:
        skill_dir = ROOT / "skills" / skill_id
        if not skill_dir.is_dir():
            report[skill_id] = {"errors": [("structure", f"skills/{skill_id}", "skill directory not found")], "warnings": []}
            continue
        errors, warnings = check_skill(skill_dir)
        report[skill_id] = {"errors": errors, "warnings": warnings}
    failed = [s for s, r in report.items() if r["errors"]]
    if as_json:
        print(json.dumps({s: {k: [list(x) for x in v] for k, v in r.items()} for s, r in report.items()}, indent=2))
    else:
        for skill_id, result in report.items():
            for kind, label in (("errors", "ERROR"), ("warnings", "WARN")):
                for rule, where, detail in result[kind]:
                    print(f"{label:5} {skill_id}: [{rule}] {where} — {detail}")
        print(f"Skill security gate: {len(report)} skill(s), {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
