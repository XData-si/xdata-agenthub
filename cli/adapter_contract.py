"""Pure, declarative runtime adapter contract for XAH installations."""
from pathlib import PurePosixPath

ADAPTERS = {
    "generic": {"skills": "skills", "instructions": "AGENTS.md"},
    "claude": {"skills": ".claude/skills", "instructions": "CLAUDE.md"},
    "codex": {"skills": ".agents/skills", "instructions": "AGENTS.md"},
    "opencode": {"skills": ".opencode/skills", "instructions": "AGENTS.md"},
}


def adapter_spec(agent):
    if agent not in ADAPTERS:
        raise ValueError("Unsupported agent adapter: " + str(agent))
    return dict(ADAPTERS[agent])


def destination_for(agent, item_id, kind):
    spec = adapter_spec(agent)
    if kind == "instruction":
        return PurePosixPath(spec["instructions"])
    if kind != "skill":
        raise ValueError("Unsupported adapter item type")
    if not isinstance(item_id, str) or not item_id or any(
            c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in item_id
    ) or item_id.startswith("-") or item_id.endswith("-") or "--" in item_id:
        raise ValueError("Unsafe skill identifier")
    return PurePosixPath(spec["skills"]) / item_id
