# Verified MCP — specification (proposed)

Status: **phase 1 implemented** (catalog format, import, search; all entries are L0). **Phase 2 in progress**: the
evidence format and the tool checks are implemented, the verifier workflow and the curated set follow. Later phases are
proposed.
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
The `MCP registry check` workflow runs this comparison every Monday and opens or updates an issue labelled
`verified-mcp` when listed servers changed upstream; it never writes to the repository.

Browse: `xah mcp list`, `xah mcp search <text> [--level L0] [--transport stdio]`, `xah mcp inspect <id>`, and the
"MCP servers (preview)" section of the catalog site.

## Phase 2: L1 and L2 criteria
Decisions for phase 2: the initial set contains only servers published by the vendor of the service they connect to
(namespace owned by that vendor); servers without a package (remote endpoints only) can reach L1 at most, because their
code cannot be scanned; the verifier starts a packaged server only to read `tools/list` (isolated container, no
network, no credentials, no tool calls — exercising tools is L3); heavier scanners run in CI, never in `xah`.

**L1 (identity)** — all three must pass:
- *namespace*: the official registry lists the server as active under this name (its namespace proof is the
  registry's GitHub or DNS/HTTP verification);
- *repository*: the source repository exists, is not archived, and belongs to the namespace owner (`io.github.<owner>/`
  → the GitHub owner; a domain namespace → the vendor's own organisation, linked from the vendor's website);
- *artifacts*: every package is pinned by version and its sha256 is recorded (npm tarball, PyPI file, OCI digest).

`scripts/verify_mcp_identity.py <id>…` (or `--all`) runs the three L1 checks with the registry, GitHub/GitLab and
package registry APIs (npm tarball checked against its sha512 integrity, PyPI file against its published sha256, OCI
manifest against its digest, an MCP bundle (`mcpb`, GitHub release assets only) against the registry's `fileSha256`,
plus the package's link back to the repository). Nothing is installed or run. `--write` pins the sha256 values in the
catalog and writes the evidence document; it never changes `level`. A domain namespace passes only when the repository
is on that domain or its GitHub organisation's website is; anything else (for example an organisation website on a
different domain) fails and stays L0 rather than being guessed.

**L2 (security scan)** — L1 plus five passing scans of the same artifact:
- *tools*: the `tools/list` snapshot has no errors from `cli/mcp_tool_scan.py`. Description rules: hidden or
  bidirectional characters, instruction tags (`<IMPORTANT>`, `<system>`), prompt injection, concealment ("do not tell the
  user"), credential-file references (`~/.ssh/`, `mcp.json`, …) and encoded blobs; warnings for cross-tool behaviour
  instructions, mentions of other tools, URLs and very long descriptions. Schema rules: tool names
  `[A-Za-z0-9_-]{1,64}`, unique; `inputSchema` an object schema without top-level `oneOf`/`anyOf`/`allOf`/`enum`/…;
  `required` names declared; no remote `$ref`;
- *dependencies*: no known vulnerability of high or critical severity without a documented exception;
- *sbom*: an SBOM was generated for the artifact;
- *secrets*: no secrets found in the artifact;
- *licence*: an OSI-approved licence is declared and matches the repository.

The patterns detect known techniques. A clean scan is not proof that descriptions are harmless.

The `MCP verify` workflow (manual, or on pull requests that change the verifier) runs `scripts/mcp_l2_scan.py <id>`
for every entry with a package: identity checks, the artifact fetched and compared with its sha256 (npm tarball, OCI
image by digest), `tools/list` read with `scripts/mcp_tools_list.py` from the server in a container with `--network
none`, a read-only file system, no capabilities and placeholder values for required variables, then syft (SBOM),
osv-scanner (fails on CVSS ≥ 7.0; unscored advisories are listed for the reviewer) and gitleaks, all pinned by version
and sha256. npm dependencies are installed with `--ignore-scripts`. The evidence and raw reports are uploaded as a
workflow artifact; the workflow writes nothing to the repository. PyPI, NuGet and `mcpb` packages are not scanned yet;
an entry with one stays at the level its identity evidence supports. So does a server that does not answer
`tools/list` without network access. Only fixed `packageArguments` from the registry (and required ones with their
default) are passed; options without a value are left out.

**Evidence** — `reports/mcp/<id>/<version>.json` (validated by `cli/mcp_evidence.py`, schema version 1): server id,
name and version; `artifacts` with sha256 (must equal the pinned packages in the catalog); `identity` with the three
L1 results; `scans` with the five L2 results and the tool names and versions used; and the `tools` snapshot itself.
`xah doctor` re-runs the tool checks on the snapshot and recomputes its digest, so a report cannot claim a clean scan its
snapshot contradicts, and rejects a catalog level the evidence does not support. Raising a level is a reviewed pull
request that adds the evidence file and changes `level` in the same commit.

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
