"""Pure, declarative runtime adapter contract for XAH installations."""
from pathlib import PurePosixPath

# Bump when destinations or semantics change; adapters and tests reference it so changes are explicit in review.
CONTRACT_VERSION = 2  # 1: project scope (v0.3.0 RC1), 2: user scope added

ADAPTERS = {
    "generic": {"skills": "skills", "instructions": "AGENTS.md"},
    "claude": {"skills": ".claude/skills", "instructions": "CLAUDE.md"},
    "codex": {"skills": ".agents/skills", "instructions": "AGENTS.md"},
    "opencode": {"skills": ".opencode/skills", "instructions": "AGENTS.md"},
}

# User-level skill directories, relative to the home directory, as documented by each client.
# Only skills are supported at user scope: the bundled instruction template is project guidance.
USER_ADAPTERS = {
    "claude": {"skills": ".claude/skills"},
    "codex": {"skills": ".agents/skills"},
    "opencode": {"skills": ".config/opencode/skills"},
}
SCOPES = {"project": ADAPTERS, "user": USER_ADAPTERS}


def adapter_spec(agent, scope="project"):
    if scope not in SCOPES:
        raise ValueError("Unsupported install scope: " + str(scope))
    if agent not in SCOPES[scope]:
        raise ValueError(f"Unsupported agent adapter for {scope} scope: {agent}")
    return dict(SCOPES[scope][agent])


def destination_for(agent, item_id, kind, scope="project"):
    spec = adapter_spec(agent, scope)
    if kind == "instruction":
        if "instructions" not in spec:
            raise ValueError(f"{scope} scope supports skill items only")
        return PurePosixPath(spec["instructions"])
    if kind != "skill":
        raise ValueError("Unsupported adapter item type")
    if not isinstance(item_id, str) or not item_id or any(
            c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in item_id
    ) or item_id.startswith("-") or item_id.endswith("-") or "--" in item_id:
        raise ValueError("Unsafe skill identifier")
    return PurePosixPath(spec["skills"]) / item_id
