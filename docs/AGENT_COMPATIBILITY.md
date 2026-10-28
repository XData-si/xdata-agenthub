# Agent compatibility (alpha)

The CLI copies portable Markdown instructions into native project paths. It does not convert agent-specific semantics, install plugins, configure MCP servers, or guarantee feature parity.

| Agent | Skill destination | Project guidance |
|---|---|---|
| Claude Code | `.claude/skills/<id>/SKILL.md` | `CLAUDE.md` |
| Codex | `.agents/skills/<id>/SKILL.md` | `AGENTS.md` |
| OpenCode | `.opencode/skills/<id>/SKILL.md` | `AGENTS.md` (generic guidance; verify client behavior) |
| Generic | `skills/<id>/SKILL.md` | `instructions/AGENTS.md` |

## User scope (skills only)

`add` and `update` accept `--scope user` to install a skill into the client's user-level directory under the home
directory instead of a project. An explicit `--target` replaces the home directory (useful for containers and tests).

| Agent | User skill destination |
|---|---|
| Claude Code | `~/.claude/skills/<id>/SKILL.md` |
| Codex | `~/.agents/skills/<id>/SKILL.md` |
| OpenCode | `~/.config/opencode/skills/<id>/SKILL.md` |

```bash
python3 cli/xah.py add code-review --agent claude --scope user
python3 cli/xah.py update code-review --agent claude --scope user --dry-run
```

- Only `skill` items are supported; instruction templates are project guidance and are refused at user scope.
- The `generic` adapter has no user scope.
- The install manifest (`.xah-installed.json`) and update lock are written in the home directory (the target).
- Paths follow each client's documentation; runtime discovery at user scope has **not** been verified yet.

## Example

```bash
mkdir -p /tmp/agenthub-claude
python3 cli/xah.py init --agent claude --profile developer --target /tmp/agenthub-claude --dry-run
python3 cli/xah.py init --agent claude --profile developer --target /tmp/agenthub-claude
```

No file is overwritten. The current implementation installs project guidance as a plain Markdown copy; future releases should provide native, validated agent-specific instructions.

References: [Claude skills](https://code.claude.com/docs/en/skills), [OpenCode skills](https://docs.opencode.ai/docs/skills/), [OpenAI agents examples](https://github.com/openai/openai-agents-python).

## Runtime verification

Use [AGENT_RUNTIME_TESTS.md](AGENT_RUNTIME_TESTS.md) to record real skill discovery and invocation for each client version. The compatibility table above documents intended installation paths, **not** verified runtime compatibility.

## Recorded integration results

See [2026-10-15 runtime results](integration-evidence/2026-10-15-runtime-results.md) for the tested client versions, evidence and limitations. Only the `code-review` scenario was exercised.
