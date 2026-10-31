# Roadmap

**Vision: the Verified AI Capabilities Registry** — the first place developers go for agent capabilities they can trust:
skills today, MCP servers next, and tested combinations of both. Fewer entries, each with reproducible evidence.

## Where we are

| Phase | Outcome | Status |
|---|---|---|
| Alpha | Local curated templates and CLI (list, search, inspect, add, audit; offline; no overwrite) | done |
| Beta | Agent compatibility: Claude Code, Codex, OpenCode adapters, user scope, runtime evidence | done for tested scenarios; more evidence ongoing |
| Registry | Trusted catalog: provenance, package digests, `xah verify`, Sigstore-signed releases with SLSA provenance | done (v0.3.0) |
| Review | Security gate, AI review and maintainer review for every skill; seals bound to digests | done |
| Hub | Searchable catalog site, Claude Code plugin marketplace with topic bundles | done |
| Community | Contribution pipeline: every contribution security-reviewed before distribution | done; growing |
| Verified MCP | MCP catalog from the official registry; identity (L1) and security scanning (L2) with evidence for 23 servers | done (v0.4.0) |

## Next

| Priority | Item | Tracking |
|---|---|---|
| P0 | **Verified MCP** phase 3: sandbox runtime tests (L3) and permission profiles | [#86](https://github.com/XData-si/xdata-agenthub/issues/86), `verified-mcp` |
| P1 | Skill + MCP capability bundles | [#87](https://github.com/XData-si/xdata-agenthub/issues/87), `verified-mcp` |
| P1 | Public verification reports and badges for skill and MCP authors | `verified-mcp` |
| P1 | "Before / after" demonstrations: the same task with and without a skill, with measured differences | `demo` |
| P1 | More runtime-verified skills (Codex, OpenCode, Claude Code), starting with the most used | `verification` |
| P2 | Continuous verification and revocation (L4); private self-hosted registry for organisations | `verified-mcp` |

## How we measure progress
Stars are a signal, not the goal. We track successful installs reported by users, verified skills and servers,
external contributions that pass review, issue quality and response times.
