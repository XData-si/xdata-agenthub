# External candidate intake — initial shortlist

The [external candidate registry](../registry/external-candidates.json) is a **discovery-only queue**. It is not an installable registry and does not assert security, license compatibility or Agent Skills compliance.

## First review batch

| Candidate | Potential value for AgentHub | First gate |
|---|---|---|
| obra/superpowers | Structured agent workflows | Identify actual skill directories and licensing |
| vercel-labs/agent-skills | Frontend and web-development skills | Check upstream version and individual licenses |
| github/awesome-copilot | Cross-platform instructions and agents | Distinguish examples, instructions and executable skills |
| czlonkowski/n8n-skills | Automation workflows | Check n8n-specific runtime assumptions |
| muratcankoylan/Agent-Skills-for-Context-Engineering | Context design and agent architectures | Identify reusable standalone SKILL.md units |
| sickn33/antigravity-awesome-skills | Large multi-agent collection | Dedupe sources and inspect provenance |
| VoltAgent/awesome-agent-skills | Discovery and taxonomy | Treat index links separately from installable artifacts |
| modelcontextprotocol/servers | MCP reference implementations | Keep MCP servers separate from Markdown skills |
| promptfoo/promptfoo | Evaluation integration patterns | Tooling integration, not automatically a skill |
| langfuse/langfuse | Observability integration patterns | Tooling integration, not automatically a skill |

The other candidates remain in the JSON queue for later review. Do not import third-party content until the review gate is satisfied.

## Promotion gate

1. Resolve upstream URL and immutable commit SHA.
2. Inspect the actual file tree and locate a `SKILL.md`; if absent, classify as `tool`, `mcp_server`, `collection` or `reference` rather than `skill`.
3. Verify the license and attribution requirements for the **specific files** proposed for import.
4. Inspect commands, dependencies, scripts, network behavior, secret handling and any additional referenced resources.
5. Review Agent Skills format compatibility; preserve upstream license notices and modifications.
6. Create a minimal offline fixture and add catalog metadata. Native client verification is deferred to the final multi-agent test campaign.
7. Promote only after review approval; leave the candidate in discovery-only status otherwise.

## Why grades are not security attestations

The external directory contains heterogeneous items and risk labels. Its security grades are editorial signals, not evidence of our own code audit. The directory also publishes inconsistent aggregate vulnerability figures across pages, so we do not import its claims as facts.

## Policy

No bulk scraping, no direct shell execution from listings, no automatic third-party installer invocation, no license assumptions, and no inflated catalog counts. The public curated catalog continues to count only locally shipped resources.

## Source review notes — 2026-10-15

### obra/superpowers
- **Confirmed from upstream:** agentic workflow framework, real `skills/writing-skills/SKILL.md`, MIT license stated in repository README, and documented support for multiple agent clients.
- **Operational consideration:** upstream README describes optional remote image telemetry for its visual companion; imported instructions and assets require explicit review before adoption.
- **Decision:** retain as `skill_collection` candidate. No copying, execution or compatibility certification yet.
- Sources: [repository](https://github.com/obra/superpowers), [writing-skills source](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md).

### github/awesome-copilot
- **Confirmed from upstream:** skills are packaged in directories with `SKILL.md` and may include bundled assets; the collection also includes agents, instructions and plugins. The repository describes its contents as community contributed and displays an MIT repository license.
- **Decision:** retain as `skill_collection`; evaluate individual file provenance and instructions before import.
- Sources: [repository](https://github.com/github/awesome-copilot), [skills documentation](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md).

### modelcontextprotocol/servers and tooling references
- MCP servers and tools such as promptfoo, Langfuse and LiteLLM are not automatically installable `SKILL.md` packages. Keep these entries in a separate discovery class until the registry and CLI explicitly support their resource type.

**Review scope:** this is an initial source and packaging assessment, not a source-code security audit. No external candidate has been promoted into the 31 shipped skills.

### vercel-labs/agent-skills
- **Confirmed from upstream:** Agent Skills-style packages with `SKILL.md`, optional `scripts/` and `references/`; documentation describes an immutable release discovery index and per-skill artifacts.
- **Review flags:** upstream issue [#330](https://github.com/vercel-labs/agent-skills/issues/330) reports frontmatter names differing from directory names. Issue [#335](https://github.com/vercel-labs/agent-skills/issues/335) alleges a deployment fallback may upload unintended files; this is a reported issue, **not independently verified here**. Several issues also question repository license-file presence; verify license evidence before reuse.
- **Decision:** keep discovery-only; prioritize non-executing frontend guidance, avoid deployment skills until reviewed. No code imported.
- Sources: [repository](https://github.com/vercel-labs/agent-skills), [authoring guidance](https://github.com/vercel-labs/agent-skills/blob/main/AGENTS.md).

### Ecosystem installer benchmark
[Vercel's separate `skills` CLI](https://github.com/vercel-labs/skills) supports source discovery, project/global installation, agent-specific paths and optional scripts/assets. Its download limits and install modes are useful design references, but XData AgentHub should retain an offline-first, reviewed-import policy rather than enabling arbitrary remote installation by default.
