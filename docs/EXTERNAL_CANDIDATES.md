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
