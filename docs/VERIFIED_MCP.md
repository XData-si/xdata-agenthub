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
| `listing` | `community` for a server added on request that its vendor did not publish; with `registry.status` `unlisted` it is not in the official registry at all, so it has no namespace proof and stays L0 |

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

Exception: `mcp-atlassian` (sooperset) is listed as `community` because Atlassian publishes no MCP server for Jira and
Confluence Server/Data Center (self-hosted); Atlassian's own server covers Cloud only. It is not in the official
registry, so the weekly registry check skips it and it stays L0; its OCI image is still scanned for the record.

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
for every entry with a package: identity checks, the artifact fetched and compared with its sha256 (npm tarball, PyPI
wheel, MCP bundle, OCI image by digest), `tools/list` read with `scripts/mcp_tools_list.py` from the server in a
container with `--network none`, a read-only file system, no capabilities and placeholder values for required
variables, then syft (SBOM), osv-scanner (fails on CVSS ≥ 7.0; unscored advisories are listed for the reviewer) and
gitleaks, all pinned by version and sha256. npm dependencies are installed with `--ignore-scripts`. The evidence and
raw reports are uploaded as a workflow artifact; the workflow writes nothing to the repository. PyPI packages are
scanned from their wheel, with dependencies installed as wheels only (`--only-binary`), and run in a pinned
`python:3.12-slim` container; MCP bundles (`mcpb`) of type `node` run in the Node container, and their vulnerabilities
are read from the SBOM of the bundle. NuGet packages, PyPI releases without a wheel and non-Node bundles are not
scanned yet; an entry with one stays at the level its identity evidence supports. So does a server that does not
answer `tools/list` without network access. Only fixed `packageArguments` from the registry (and required ones with
their default) are passed; options without a value are left out.

**Evidence** — `reports/mcp/<id>/<version>.json` (validated by `cli/mcp_evidence.py`, schema version 1): server id,
name and version; `artifacts` with sha256 (must equal the pinned packages in the catalog); `identity` with the three
L1 results; `scans` with the five L2 results and the tool names and versions used; and the `tools` snapshot itself.
`xah doctor` re-runs the tool checks on the snapshot and recomputes its digest, so a report cannot claim a clean scan its
snapshot contradicts, and rejects a catalog level the evidence does not support. Raising a level is a reviewed pull
request that adds the evidence file and changes `level` in the same commit.

### Results of the phase 2 set (2026-10-31)

`playwright` 0.0.82 reached L2, and L3 in phase 3. `atlassian`, `cloudflare`, `exa`, `figma`, `gitlab` and `microsoft-learn` are
remote-only and stop at L1 by design. The others did not pass every check:

| Server | Version | Level | Failed | Why |
|---|---|---|---|---|
| `github` | 2.0.3 | L1 | L2 dependencies | 13 high/critical advisories in the Debian base image (glibc) |
| `grafana` | v2.1.1 | L1 | L2 dependencies | 90 high/critical advisories in the base image (util-linux and others) |
| `sentry` | 0.42.0 | L1 | L2 dependencies, secrets, licence | `@modelcontextprotocol/sdk` 1.30.0; 4 `sentry-access-token` matches in `dist/`; FSL-1.1-ALv2 is not OSI-approved |
| `brave-search` | 2.1.3 | L1 | L2 dependencies | `@modelcontextprotocol/sdk` 1.30.0 (5 high advisories) |
| `tavily` | 0.2.15 | L1 | L2 dependencies | `@modelcontextprotocol/sdk` 1.25.2 (5 high advisories) |
| `firecrawl` | 3.36.0 | L1 | L2 dependencies | `zod` 3.25.76 (GHSA-mrhx-c7xc-m3w5, 8.2) |
| `supabase` | 0.14.0 | L1 | L2 tools | `tools/list` needs network access, so it cannot be read in the isolated container |
| `context7` | 4.4.4 | L1 | L2 dependencies, sbom | the npm package passes; the `mcpb` bundle is one bundled file whose dependencies cannot be identified or audited |
| `clickhouse` | 0.7.0 | L1 | L2 dependencies | the PyPI wheel passes (no high advisories); the OCI image has 124 high/critical advisories (authlib and others) |
| `mongodb` | 3.2.1 | L0 | L1 artifacts | the OCI image has no `org.opencontainers.image.source` label linking it to the repository ([reported](https://github.com/mongodb-js/mongodb-mcp-server/issues/1666)) |
| `terraform` | 1.4.1 | L0 | L1 artifacts | same as `mongodb`; the image also declares no licence ([reported](https://github.com/hashicorp/terraform-mcp-server/issues/631)) |
| `azure` | 3.0.0-beta.48 | L0 | L1 artifacts | NuGet is not supported; PyPI has no `3.0.0b48` |
| `litellm` | 1.0.2 | L0 | L1 repository | the declared repository `BerriAI/litellm-agent-mcp` does not exist ([reported](https://github.com/BerriAI/litellm/issues/49489)); with current dependencies the server also fails to start (`Server` has no `list_tools`) |
| `notion` | 1.0.1 | L0 | L1 repository | the registry entry declares no source repository |
| `stripe` | 0.2.4 | L0 | L1 repository | the GitHub organisation's website is `stripe.dev`, not the namespace domain `stripe.com` |
| `mcp-atlassian` | 0.23.1 | L0 | L1 namespace | community listing outside the official registry; without credentials it lists no tools, and the image has 76 high/critical advisories |

## Phase 3: L3 criteria

**L3 (runtime tested)** — L2 plus a passing run of the server's committed test plan
(`registry/mcp-plans/<id>.json`) with the same pinned artifact:

- *sandbox*: the server runs under gVisor (`runsc`, pinned release) with strace for file, network and process
  system calls, a read-only root file system, no capabilities, user nobody and no credentials, on an internal Docker
  network whose only other members are the plan's fixtures (for example a static web server). There is no route to the
  internet, so the egress allowlist is the fixture list. Fixture names are written to `/etc/hosts`.
- *plan*: positive calls against the fixtures and negative calls (a host outside the allowlist, an unknown tool,
  invalid arguments); every call must behave as the plan expects, and the plan must contain both kinds.
- *profile*: observed activity must stay within the plan's allowlist: file writes only under the allowed paths,
  connections only to fixtures and loopback, executed programs only from the allowed list. The plan's profile is the
  `permissions` of the catalog entry and is shown by `xah mcp inspect`.
- *same server*: the tools listed at runtime must have the same digest as the L2 snapshot.

**Blocked attempts** (connections the sandbox refused because there is no route) do not fail L3: the profile held.
They are listed in the evidence and by `xah mcp inspect`, so users see what the server tries to reach. Example:
Playwright's Chromium tries Google DNS (`8.8.8.8`, `8.8.4.4`) and DNS over HTTPS.

**Evidence** — the L2 evidence document gains a `runtime` section: plan path and sha256, sandbox, image, the tools
digest, every call with its expectation and result, the observed activity (written directories, connections, blocked
attempts, executed programs), mismatches and the profile. `xah doctor` rejects an L3 claim when a call failed, a case
kind is missing, there is a mismatch, the profile differs from the entry's `permissions`, the tools differ from L2, or
the committed plan changed since the run.

The `MCP runtime` workflow (`scripts/mcp_l3_run.py`) runs a plan in CI and uploads the report, the extended evidence
and the raw gVisor logs; a maintainer reviews them and raises the level in a pull request. L3 says how one version
behaved in this sandbox with synthetic data; it does not cover your environment, your data or real credentials.
Servers that need a SaaS account are not tested at L3 yet: that needs dedicated test accounts, never production ones.

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
