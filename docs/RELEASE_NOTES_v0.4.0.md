# XData AgentHub v0.4.0

**Verified MCP.** A curated catalog of MCP servers in which every level is backed by evidence: who published the
server, which exact artifact it is, and what a scan of that artifact found.

## Highlights

- **23 MCP servers, 16 verified above L0.** 22 servers published by the vendor of the service they connect to (GitHub,
  Grafana, Sentry, Atlassian, Cloudflare, GitLab, Playwright, MongoDB, Supabase, Terraform and others) and one
  community listing (`mcp-atlassian`, for Jira and Confluence Server/Data Center). `playwright` reached **L2**, 15
  servers **L1**; 7 stay at L0 with the reason stated. See `xah mcp list` and the
  [results table](https://github.com/XData-si/xdata-agenthub/blob/v0.4.0/docs/VERIFIED_MCP.md#results-of-the-phase-2-set-2026-10-31).
- **L1, identity:** the official MCP Registry lists the exact version, the source repository belongs to the namespace
  owner, and every package is pinned by sha256 (npm, PyPI, OCI, MCP bundles) and links back to that repository.
- **L2, security scan of the same artifact:** the server is started in a container without network, credentials or
  capabilities and only `tools/list` is read; tool descriptions and schemas are checked for tool poisoning (hidden
  characters, instruction tags, prompt injection, credential-file references) and for schemas model providers reject;
  plus SBOM (syft), known vulnerabilities (osv-scanner, CVSS ≥ 7 fails), secrets (gitleaks) and an OSI licence check.
  npm, PyPI wheels, OCI images and Node MCP bundles are covered.
- **Evidence you can check.** One evidence document per server and version in `reports/mcp/`, bound to the pinned
  sha256; `xah doctor` re-runs the tool checks on the stored snapshot and rejects any level the evidence does not
  support. Nothing is installed or run on your machine.
- **Findings go upstream.** Missing image provenance labels and a broken repository link were reported to MongoDB,
  HashiCorp and LiteLLM.
- **Repository hardening.** Every GitHub Action pinned to a commit SHA, CodeQL, secret scanning with push protection,
  dependency review on pull requests, weekly OpenSSF Scorecard, and the SLSA provenance bundle attached to this release.

## Verify this release

Requirements: [cosign](https://docs.sigstore.dev/cosign/system_config/installation/) and the [GitHub CLI](https://cli.github.com/) (macOS: `brew install cosign gh`; `gh auth login` once).

```sh
VERSION=v0.4.0
mkdir agenthub-$VERSION && cd agenthub-$VERSION
gh release download $VERSION --repo XData-si/xdata-agenthub
cosign verify-blob --bundle SHA256SUMS.sigstore.json \
  --certificate-identity "https://github.com/XData-si/xdata-agenthub/.github/workflows/release.yml@refs/tags/$VERSION" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com SHA256SUMS
sha256sum -c SHA256SUMS    # macOS without coreutils: shasum -a 256 -c SHA256SUMS
gh attestation verify xdata-agenthub-$VERSION.tar.gz --repo XData-si/xdata-agenthub \
  --bundle xdata-agenthub-$VERSION.intoto.jsonl
```

## Known limitations

- L1 and L2 are statements about one pinned version, not certification. A clean scan does not prove that tool
  descriptions are harmless, and remote-only servers can reach L1 at most because their code cannot be scanned.
- No tool is called yet: runtime behaviour in a sandbox (L3) and permission profiles are the next phase.
- NuGet packages, PyPI releases without a wheel and non-Node MCP bundles are not scanned.
- The skill catalog is unchanged from v0.3.0 (104 skills); its known limitations still apply.

Full details are in the [changelog](https://github.com/XData-si/xdata-agenthub/blob/v0.4.0/CHANGELOG.md).
