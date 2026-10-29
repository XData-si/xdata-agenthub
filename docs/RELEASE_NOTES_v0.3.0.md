# XData AgentHub v0.3.0

**The first signed release.** Give your AI coding agent 104 security-reviewed skills in minutes, for Claude Code,
Codex, OpenCode and any client that reads the Agent Skills format.

## Highlights

- **104 original skills**: engineering workflow, security, operations, AI systems and EU regulation (GDPR, NIS2, DORA,
  the Cyber Resilience Act, the AI Act and the European Accessibility Act). See the [catalog](https://xdata-si.github.io/xdata-agenthub/).
- **Every skill is security-reviewed, including community contributions.** Each one passes a deterministic CI security
  gate, an advisory AI review and a maintainer review. Seals (*reviewed* 104, *eu-ready* 30, *verified* 3) are bound
  to each package's SHA-256 digest, and any change makes the seal stale.
- **Verifiable supply chain.** `SHA256SUMS` is signed with Sigstore (keyless, this repository's release workflow
  identity), the archives and catalog carry SLSA build provenance, and `xah verify` checks installed skills against the
  catalog digests. See [VERIFYING.md](https://github.com/XData-si/xdata-agenthub/blob/v0.3.0/docs/VERIFYING.md).
- **Install in one command.** Use `/plugin marketplace add XData-si/xdata-agenthub` in Claude Code, with six bundles:
  all, engineering, security, ops, AI and EU. Other clients can use the dependency-free `xah` CLI (project or user
  scope, additional private catalogs).
- **Measured, not claimed.** [Before/after demos](https://github.com/XData-si/xdata-agenthub/tree/v0.3.0/demos) with
  18 runs and a rubric fixed in advance. A frontier model found the same planted issues with and without skills; the
  skills changed the process (honest evidence, residual risks, approvals).
- **Next: Verified MCP.** See the [specification](https://github.com/XData-si/xdata-agenthub/blob/v0.3.0/docs/VERIFIED_MCP.md).

## Verify this release

Requirements: [cosign](https://docs.sigstore.dev/cosign/system_config/installation/) and the [GitHub CLI](https://cli.github.com/) (macOS: `brew install cosign gh`; `gh auth login` once).

```sh
VERSION=v0.3.0
mkdir agenthub-$VERSION && cd agenthub-$VERSION
gh release download $VERSION --repo XData-si/xdata-agenthub
cosign verify-blob --bundle SHA256SUMS.sigstore.json \
  --certificate-identity "https://github.com/XData-si/xdata-agenthub/.github/workflows/release.yml@refs/tags/$VERSION" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com SHA256SUMS
sha256sum -c SHA256SUMS    # macOS without coreutils: shasum -a 256 -c SHA256SUMS
gh attestation verify xdata-agenthub-$VERSION.tar.gz --repo XData-si/xdata-agenthub
```

## Known limitations

- Rollback is not crash-atomic across multiple files, and the writer lock is cooperative.
- Seals are maintainer statements bound to digests, not third-party certification.
- Native loading is verified for the recorded scenarios in Claude Code 2.1.308 and OpenCode 1.19.4. Codex CLI is
  supported at path level and was not re-tested for this release, and user-scope discovery is not yet runtime-verified.

Full details are in the [changelog](https://github.com/XData-si/xdata-agenthub/blob/v0.3.0/CHANGELOG.md).
