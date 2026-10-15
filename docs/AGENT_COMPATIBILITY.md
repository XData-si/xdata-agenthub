# Agent compatibility (alpha)

The CLI copies portable Markdown instructions into native project paths. It does not convert agent-specific semantics, install plugins, configure MCP servers, or guarantee feature parity.

| Agent | Skill destination | Project guidance |
|---|---|---|
| Claude Code | `.claude/skills/<id>/SKILL.md` | `CLAUDE.md` |
| Codex | `.agents/skills/<id>/SKILL.md` | `AGENTS.md` |
| OpenCode | `.opencode/skills/<id>/SKILL.md` | `AGENTS.md` (generic guidance; verify client behavior) |
| Generic | `skills/<id>/SKILL.md` | `instructions/AGENTS.md` |

## Example

```bash
mkdir -p /tmp/agenthub-claude
python3 cli/xah.py init --agent claude --profile developer --target /tmp/agenthub-claude --dry-run
python3 cli/xah.py init --agent claude --profile developer --target /tmp/agenthub-claude
```

No file is overwritten. The current implementation installs project guidance as a plain Markdown copy; future releases should provide native, validated agent-specific instructions.

References: [Claude skills](https://code.claude.com/docs/en/skills), [OpenCode skills](https://docs.opencode.ai/docs/skills/), [OpenAI agents examples](https://github.com/openai/openai-agents-python).
