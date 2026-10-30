# Verified MCP — specification (proposed)

Status: **phase 1 implemented** (catalog format, import, search; all entries are L0). Later phases are proposed.
This document describes how AgentHub will extend from verified *skills* to
verified *Model Context Protocol (MCP) servers* — becoming a **Verified AI Capabilities Registry**. Tracking issues are
labelled `verified-mcp`.

## Why
MCP servers give agents real capabilities: files, databases, APIs, payments. The
[official MCP Registry](https://github.com/modelcontextprotocol/registry) is the place where servers are published
and discovered, and it verifies **namespace ownership** (GitHub login or OIDC, DNS or HTTP challenges). It does not
review server code or behaviour — that is left to downstream registries and tools. AgentHub will be such a downstream
registry, focused on one question: **which MCP servers can I trust, why, and under which conditions?**

AgentHub will not try to be the largest MCP directory. It will publish fewer servers, each with reproducible evidence.

## Verification levels
Each level applies to **one exact artifact** (package version, image digest or commit) and a **documented
configuration**. A new version starts unverified until it is checked again.

| Level | Label | What it establishes | What it does *not* establish |
|---|---|---|---|
| L0 | Listed | Known to AgentHub, metadata imported from the official registry | anything about safety |
| L1 | Identity verified | Publisher owns the namespace (official registry proof) and the source repository; artifact digest recorded | that the code is safe |
| L2 | Security scanned | Static analysis, dependency vulnerabilities and licences (SBOM), tool descriptions scanned for injection and hidden instructions, tool input schemas valid for major model providers, no secrets in the artifact | runtime behaviour |
| L3 | Runtime tested | Started in an isolated sandbox without production credentials and with restricted network; tools listed and exercised with positive and negative cases; observed file, network and process activity matches the declared permission profile | behaviour in your environment with your data |
| L4 | Continuously verified | L3 repeated on every new version and periodically; tool-description hashes tracked to detect silent changes ("rug pulls"); status revoked on regressions | absence of all vulnerabilities |

No level is a certification. Reports always state what was tested, how, and the limits.

## Permission profile
Every verified server gets a human-readable profile, shown before installation:

| Capability | Values |
|---|---|
| File system | none / read (paths) / write (paths) |
| Network | none / allowlisted hosts / any |
| Data | read-only / can modify / can delete |
| External actions | none / sends messages / spends money / changes infrastructure |
| Credentials | none / user-supplied token (scopes) / shared service account |
| Transport | stdio / Streamable HTTP (auth method) |

## Verification pipeline
1. **Import** server metadata incrementally from the official registry API (preview, v0.1 API freeze) — no scraping.
2. **Pin** the artifact: package version and integrity hash, container digest or commit SHA.
3. **Identity** (L1): confirm namespace proof from the registry and that the source repository belongs to the publisher.
4. **Static checks** (L2): dependency audit and SBOM, secret scanning, licence check, tool-description analysis (for
   example with an open-source MCP scanner, run in local mode so tool data is not sent to third parties), and schema
   compatibility checks — a single tool with a top-level `oneOf` can disable an agent with some model providers.
5. **Sandbox run** (L3): disposable container or VM, no host credentials, egress allowlist, synthetic test accounts;
   `tools/list` snapshot; scripted positive and negative tool calls; activity recorded.
6. **Report**: a JSON evidence document bound to the artifact digest plus a human-readable page; published with the
   signed AgentHub release.
7. **Monitor** (L4): re-run on new versions and on a schedule; compare tool-description hashes; revoke on failures.

## Skills + MCP: verified capability bundles
A bundle combines a skill with the MCP server it needs and a policy, tested together:

```yaml
bundle: gitlab-code-review
skill: code-review
mcp: gitlab (read-only tools only)
policy: no write tools enabled; token scope read_api
tested_with: [claude-code 2.1.x, opencode 1.19.x]
evidence: reports/bundles/gitlab-code-review.json
```

This is where AgentHub differs from directories: users get a capability that is known to work safely as a whole.

## Public verification reports and badges
Each verified server gets a report page and a badge its authors can embed in their README, linking back to the
evidence. Reports are reproducible: anyone can re-run the published test plan.

## Catalog format (phase 1)
`registry/mcp-servers.json` (validated by `cli/mcp_catalog.py`, schema version 1) holds one entry per server:

| Field | Meaning |
|---|---|
| `id` | AgentHub slug, used by `xah mcp inspect` |
| `name`, `title`, `description`, `repository`, `website` | as declared in the official registry; rejected if they contain control, zero-width or bidirectional characters |
| `version` | the one upstream version the entry describes |
| `artifacts` | pinned packages (`npm`, `pypi`, `oci`, `nuget`, `mcpb`; version, transport, optional `sha256`) and remote endpoints (https only) |
| `environment` | variables the server asks for, with `required` and `secret` flags |
| `registry` | upstream status and publish/update timestamps |
| `level` | `L0`–`L4`; anything above L0 requires `evidence` and a `sha256` for every package, L3+ also a `permissions` profile |
| `permissions`, `evidence` | permission profile (values from the table above) and a repository path to the evidence report |

Import: `python3 scripts/import_mcp_registry.py --add <registry name> --id <slug>` starts listing a server;
`python3 scripts/import_mcp_registry.py` refreshes all listed servers from the registry's `versions/latest` endpoint
and rewrites only entries whose upstream record changed, so a second run is a no-op. A new upstream version resets the
entry to L0 and drops its evidence. A record that fails validation or is missing upstream leaves the entry unchanged
with a warning. `--check` exits 1 when a refresh would change the catalog. Only listed servers are imported:
AgentHub curates, it does not mirror the registry.

Browse: `xah mcp list`, `xah mcp search <text> [--level L0] [--transport stdio]`, `xah mcp inspect <id>`, and the
"MCP servers (preview)" section of the catalog site.

## Phases
| Phase | Scope | Priority |
|---|---|---|
| 1 | MCP catalog format, import from the official registry, search in `xah` and the site | P0 |
| 2 | Identity (L1) and security scanning (L2) for an initial set of 20–30 curated open-source servers | P0 |
| 3 | Sandbox runtime tests (L3) and permission profiles | P1 |
| 4 | Skill + MCP capability bundles | P1 |
| 5 | Public verification reports and badges | P1 |
| 6 | Continuous verification and revocation (L4) | P1 |
| 7 | Private (self-hosted) registry for organisations, using their own identity and secrets management | P2 |

## Non-goals
- No automatic installation or execution of MCP servers by `xah`.
- No claims of complete security; no paid placement; no ranking by popularity.
- The open-source core stays dependency-free; heavier scanning runs in CI or a separate verifier.
