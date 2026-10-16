#!/usr/bin/env python3
"""Prepare isolated, offline AgentHub runtime-test workspaces; never launch an agent."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = ("claude", "codex", "opencode")
PROMPTS = {
    "discovery": "List the project skills you can discover without opening files manually. Identify code-review and how it was discovered.",
    "native_invocation": "Invoke the installed code-review skill using the client's native skill mechanism to review sample.py. Report how the skill was loaded. Do not modify files.",
    "direct_read": "Open and read the installed SKILL.md file explicitly. Quote only its heading and report the path. This does not count as native discovery.",
    "negative_missing_file": "Review a file named definitely-not-present.py. Do not invent its contents.",
    "negative_unrelated": "Without opening files manually, tell me whether a skill named definitely-not-installed is available. Do not invent one.",
}


def prepare(base):
    base = Path(base).expanduser().resolve()
    if base.exists() and any(base.iterdir()):
        raise ValueError("Output directory must be empty; refusing to overwrite test artifacts")
    base.mkdir(parents=True, exist_ok=True)
    for client in CLIENTS:
        target = base / client
        target.mkdir()
        cmd = [sys.executable, str(ROOT / "cli/xah.py"), "add", "code-review",
               "--agent", client, "--target", str(target)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        (target / "sample.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        skill = {"claude": ".claude", "codex": ".agents", "opencode": ".opencode"}[client]
        record = {
            "client": client, "client_version": "RECORD_AFTER_REAL_RUN",
            "os": platform.system(), "os_version": platform.release(),
            "model": "RECORD_AFTER_REAL_RUN",
            "workspace": client, "skill_path": f"{skill}/skills/code-review/SKILL.md",
            "methods": {key: {"prompt": value, "result": "not_tested", "redacted_evidence": ""}
                        for key, value in PROMPTS.items()},
            "redaction_reviewed": False,
            "notes": "Template only: no native client was executed by this script.",
        }
        (target / "observations.template.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        print("Prepared:", prepare(args.output))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Preparation failed: {exc}\n")


if __name__ == "__main__":
    main()
