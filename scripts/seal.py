#!/usr/bin/env python3
"""XData AgentHub seal of approval: grant and check seals bound to package digests.

A seal is valid only for the exact package digest it was granted for. Any change to a sealed skill makes the seal
stale, CI fails (`seal.py check`), and a maintainer must review the new version and grant the seal again.

Usage:
  seal.py check
  seal.py grant <skill-id> <level> --by <name> --evidence <path or URL> [--note TEXT]
  seal.py list
Levels: reviewed, verified, eu-ready (see docs/SEAL.md).
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEALS = ROOT / "registry" / "seals.json"
CATALOG = ROOT / "registry" / "catalog.json"
LEVELS = {
    "reviewed": "XData Reviewed — passed the deterministic security gate, the AI review and a maintainer review",
    "verified": "XData Verified — reviewed, plus recorded runtime evidence in at least one agent client",
    "eu-ready": "EU Ready — reviewed, plus the EU sovereignty and legislation checklist",
}
REQUIRES = {"verified": "reviewed", "eu-ready": "reviewed"}


def load():
    if not SEALS.exists():
        return {"schema_version": 1, "levels": LEVELS, "seals": {}}
    return json.loads(SEALS.read_text(encoding="utf-8"))


def save(data):
    data["levels"] = LEVELS
    data["seals"] = {k: sorted(v, key=lambda s: s["level"]) for k, v in sorted(data["seals"].items())}
    SEALS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digests():
    return {item["id"]: item.get("digest", {}).get("value") for item in json.loads(CATALOG.read_text(encoding="utf-8"))["items"]}


def check(data=None, current=None):
    data, current = data or load(), current or digests()
    problems = []
    if data.get("schema_version") != 1:
        problems.append("unsupported seals schema")
    for skill_id, seals in data.get("seals", {}).items():
        levels = {s.get("level") for s in seals}
        for seal in seals:
            where = f"{skill_id}/{seal.get('level')}"
            if seal.get("level") not in LEVELS:
                problems.append(f"{where}: unknown level")
            if skill_id not in current:
                problems.append(f"{where}: skill not in catalog")
            elif seal.get("digest") != current[skill_id]:
                problems.append(f"{where}: stale — package changed since the seal was granted; re-review and grant again")
            required = REQUIRES.get(seal.get("level"))
            if required and required not in levels:
                problems.append(f"{where}: requires the '{required}' seal")
            for field in ("granted", "by", "evidence"):
                if not seal.get(field):
                    problems.append(f"{where}: missing {field}")
            evidence = seal.get("evidence", "")
            if evidence and not evidence.startswith("https://") and not (ROOT / evidence.split("#")[0]).exists():
                problems.append(f"{where}: evidence {evidence} not found")
    return problems


def grant(skill_id, level, by, evidence, note=""):
    if level not in LEVELS:
        raise SystemExit(f"unknown level {level}")
    current = digests()
    if skill_id not in current or not current[skill_id]:
        raise SystemExit(f"{skill_id}: not in catalog or no digest (run scripts/update_digests.py)")
    data = load()
    seals = [s for s in data["seals"].get(skill_id, []) if s["level"] != level]
    seals.append({"level": level, "digest": current[skill_id], "granted": datetime.date.today().isoformat(),
                  "by": by, "evidence": evidence, **({"note": note} if note else {})})
    data["seals"][skill_id] = seals
    save(data)


def main(argv):
    if not argv or argv[0] == "check":
        problems = check()
        for problem in problems:
            print("FAIL:", problem)
        sealed = load().get("seals", {})
        print(f"Seal check: {sum(len(v) for v in sealed.values())} seal(s) on {len(sealed)} skill(s), {len(problems)} problem(s)")
        return 1 if problems else 0
    if argv[0] == "list":
        for skill_id, seals in load().get("seals", {}).items():
            print(f"{skill_id:28} " + ", ".join(s["level"] for s in seals))
        return 0
    if argv[0] == "grant" and len(argv) >= 3:
        opts = {argv[i]: argv[i + 1] for i in range(3, len(argv) - 1, 2)}
        if "--by" not in opts or "--evidence" not in opts:
            raise SystemExit("grant requires --by and --evidence")
        grant(argv[1], argv[2], opts["--by"], opts["--evidence"], opts.get("--note", ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
