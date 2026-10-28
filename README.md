# XData AgentHub

**One place. Every agent capability.**

> Discover, inspect and install portable AI agent instructions, skills and workflow templates. Open source, vendor-neutral, and security-conscious.

[![Status](https://img.shields.io/badge/status-alpha-orange)](#roadmap) [![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![Made by XData](https://img.shields.io/badge/maintained%20by-XData-111827)](https://xdata.si)

**XData AgentHub is a public alpha project.** No unsupported claims of certification or compatibility. This project currently ships a dependency-free Python CLI and local curated templates; it does **not** install arbitrary remote code.

**63 curated local resources · 60 skills · 3 additional templates** — all inspectable, offline-first and MIT-licensed.

## Why
AI development instructions are scattered across repositories and incompatible conventions. AgentHub starts with a small, inspectable catalog and a local-first installer.

## Quick start

```bash
# Run from this directory; Python 3.10+
python3 cli/xah.py list
python3 cli/xah.py search review
python3 cli/xah.py doctor
mkdir -p /tmp/xah-demo
python3 cli/xah.py init --agent claude --profile developer --target /tmp/xah-demo --dry-run
python3 cli/xah.py init --agent claude --profile developer --target /tmp/xah-demo
python3 cli/xah.py inspect code-review
python3 cli/xah.py add mcp-review --agent claude --target /tmp/xah-demo
python3 cli/xah.py audit --target /tmp/xah-demo
```

Install the CLI to your user directory (no sudo):

```bash
bash scripts/install.sh
xah --help
```

## v0.3.0 RC1 preparation (not published)

The development `main` branch now includes `xah browse`, `xah trust`, `xah release-check`, the shared adapter destination contract, and additional recovery tests. `browse` supports local catalog facets/pagination; `trust` reports **declared metadata only**, not verified publisher identity; `release-check` validates evidence-file structure, not reviewer authenticity. None of these commands downloads or executes third-party code.

**No v0.3.0 RC1 tag or GitHub Release has been published.** The [RC1 readiness checklist](docs/RC1_v0.3.0_READINESS.md) lists pending operator, security and frozen-SHA verification. Rollback remains non-atomic across multiple files and its lock cannot prevent writes by unrelated processes.

## v0.2.0 development migration and operations

For safe v0.1.0-to-development migration, read the [migration guide](docs/MIGRATION_v0.2.0.md) and [operator runbook](docs/OPERATOR_RUNBOOK.md). They cover backups (including hidden files and manifests), conflict-safe updates, recovery, troubleshooting and release sign-off. **The v0.2.0 migration guide describes development behavior, not proof of a published release**; operator-accepted native compatibility evidence is recorded for Claude Code, Codex CLI and OpenCode, with documented provenance limitations and no independent source-trace audit. See [XAH-205 acceptance](docs/integration-evidence/XAH-205-ACCEPTANCE.md).

## Supported project layouts

| Target | Skill path | Guidance |
|---|---|---|
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Codex | `.agents/skills/` | `AGENTS.md` |
| OpenCode | `.opencode/skills/` | `AGENTS.md` |

Skills can also be installed at user scope (`add --scope user`: `~/.claude/skills`, `~/.agents/skills`,
`~/.config/opencode/skills`), and private skills can live in [additional local catalogs](docs/ADDITIONAL_CATALOGS.md)
(`--catalog` / `XAH_CATALOGS`) without forking this repository.

See [compatibility details](docs/AGENT_COMPATIBILITY.md) and [demo storyboard](docs/SHOWCASE.md). These are path-level adapters, not full semantic conversions.

See the [categorized skill catalog](docs/CATALOG.md) for all entries and their intended uses.

## What's included
- **Skills**: reusable capabilities for code review, testing, API design, infrastructure, security and agent workflows; quality and depth vary by entry.
- **Instructions**: portable AGENTS.md starter for repositories.
- **Agents**: example agent roles, not running autonomous services.
- **Workflows**: transparent checklists for human-reviewed delivery.
- **Registry**: a small JSON index with provenance and local paths.
- **CLI**: local catalog browsing, search, inspection, declared-provenance trust reporting, add/init/update, recovery inspection and explicit rollback, doctor, heuristic audit and evidence checklist; local-first, standard-library Python.

## Design principles
1. Useful without registration, telemetry or a hosted service.
2. No remote shell pipelines, no hidden execution, no automatic code execution.
3. Explicit origin, license and risk review before third-party content is added.
4. Portable markdown first; adapter-specific support later.
5. No misleading star counters, fake usage statistics or inflated catalog counts.

## Roadmap
See [TODO.md](TODO.md), [ROADMAP.md](ROADMAP.md), [architecture](docs/ARCHITECTURE.md) and the [release process](docs/RELEASE_PROCESS.md).

## Community
See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md). Contributions are welcome. See [Quickstart](docs/QUICKSTART.md) and [Launch checklist](docs/LAUNCH_CHECKLIST.md).

---

Maintained by [XData](https://xdata.si) · **Accessible premium AI engineering** · [Contact](https://xdata.si)
