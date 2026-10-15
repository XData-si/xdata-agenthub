# XData AgentHub

**One place. Every agent capability.**

> Discover, inspect and install portable AI agent instructions, skills and workflow templates. Open source, vendor-neutral, and security-conscious.

[![Status](https://img.shields.io/badge/status-alpha-orange)](#roadmap) [![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![Made by XData](https://img.shields.io/badge/maintained%20by-XData-111827)](https://xdata.si)

**XData AgentHub is a public alpha project.** No unsupported claims of certification or compatibility. This project currently ships a dependency-free Python CLI and local curated templates; it does **not** install arbitrary remote code.

## Why
AI development instructions are scattered across repositories and incompatible conventions. AgentHub starts with a small, inspectable catalog and a local-first installer.

## Quick start

```bash
# Run from this directory; Python 3.10+
python3 cli/xah.py list
python3 cli/xah.py search review
python3 cli/xah.py doctor
mkdir -p /tmp/xah-demo
python3 cli/xah.py init --profile developer --target /tmp/xah-demo --dry-run
python3 cli/xah.py init --profile developer --target /tmp/xah-demo
python3 cli/xah.py inspect code-review
python3 cli/xah.py add code-review --target /path/to/your/project
python3 cli/xah.py audit --target /path/to/your/project
```

Install the CLI to your user directory (no sudo):

```bash
bash scripts/install.sh
xah --help
```

## What's included
- **Skills**: focused reusable agent capabilities, starting with code review and documentation.
- **Instructions**: portable AGENTS.md starter for repositories.
- **Agents**: example agent roles, not running autonomous services.
- **Workflows**: transparent checklists for human-reviewed delivery.
- **Registry**: a small JSON index with provenance and local paths.
- **CLI**: `list`, `search`, `inspect`, `add`, `init`, `doctor`, `audit`; local-only, no external dependencies.

## Design principles
1. Useful without registration, telemetry or a hosted service.
2. No remote shell pipelines, no hidden execution, no automatic code execution.
3. Explicit origin, license and risk review before third-party content is added.
4. Portable markdown first; adapter-specific support later.
5. No misleading star counters, fake usage statistics or inflated catalog counts.

## Roadmap
See [TODO.md](TODO.md), [ROADMAP.md](ROADMAP.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Community
See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md). Contributions are welcome. See [Quickstart](docs/QUICKSTART.md) and [Launch checklist](docs/LAUNCH_CHECKLIST.md).

---

Maintained by [XData](https://xdata.si) · **Accessible premium AI engineering** · [Contact](https://xdata.si)
