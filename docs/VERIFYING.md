# Verifying what you install

AgentHub gives you three independent checks. None of them requires trusting this README: each uses data you can
recompute or a signature tied to this repository's release workflow.

## 1. Package digests (offline, every install)

Every catalog entry in `registry/catalog.json` (schema v2) carries a `digest`: the SHA-256 of the item's *package*
— all files of a skill, sorted by path, in `sha256sum` layout (see [`cli/package_digest.py`](../cli/package_digest.py)).
CI fails when a skill changes without its digest being updated (`scripts/update_digests.py --check`).

```bash
python3 cli/xah.py verify                                   # local catalog sources match their digests
python3 cli/xah.py verify --target /path/to/project         # skills installed into a project
python3 cli/xah.py verify --scope user                      # skills installed at user scope
python3 cli/xah.py inspect threat-modeling --json           # package_sha256 and digest_matches for one item
```

Installed items are reported as:

| State | Meaning |
|---|---|
| `verified` | installed files are exactly the current catalog package |
| `outdated` | unchanged since install, but the catalog now has a different version — review with `xah update --dry-run` |
| `modified` | a file was edited, removed **or added** after install (an added script is a modification) |
| `unknown` | not in the catalog, or the catalog declares no digest |

`xah verify` exits with status 2 unless every item is `verified`, so it can run in CI or a pre-commit hook.

## 2. Signed releases (Sigstore, keyless)

Each tagged release is built by [`.github/workflows/release.yml`](../.github/workflows/release.yml). The workflow
re-runs all release gates, then publishes:

- `xdata-agenthub-<version>.tar.gz` and `.zip` — source archives of the tagged commit;
- `catalog-<version>.json` — the catalog with all package digests;
- `SHA256SUMS` — checksums of the files above;
- `SHA256SUMS.sigstore.json` — a Sigstore bundle signing `SHA256SUMS` with the workflow's GitHub OIDC identity
  (no long-lived keys exist; the signature is recorded in the public Rekor transparency log).

Verify a download. You need [cosign](https://docs.sigstore.dev/cosign/system_config/installation/) and the
[GitHub CLI](https://cli.github.com/) (macOS: `brew install cosign gh`, then `gh auth login` once):

```bash
VERSION=v0.3.0
mkdir agenthub-$VERSION && cd agenthub-$VERSION
gh release download $VERSION --repo XData-si/xdata-agenthub   # or download the assets from the release page
cosign verify-blob --bundle SHA256SUMS.sigstore.json \
  --certificate-identity "https://github.com/XData-si/xdata-agenthub/.github/workflows/release.yml@refs/tags/$VERSION" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  SHA256SUMS
sha256sum --check SHA256SUMS      # macOS: shasum -a 256 -c SHA256SUMS
```

A valid signature proves that `SHA256SUMS` was produced by this repository's release workflow for that tag; the
checksum check then proves the archives and catalog are the ones it built.

## 3. Build provenance (SLSA attestation)

The same workflow attests SLSA build provenance for the archives and the catalog with GitHub artifact attestations:

```bash
gh attestation verify xdata-agenthub-$VERSION.tar.gz --repo XData-si/xdata-agenthub
```

From the next release on, the same attestation is also attached as `xdata-agenthub-$VERSION.intoto.jsonl`, so it can
be checked offline against the downloaded archive:

```bash
gh attestation verify xdata-agenthub-$VERSION.tar.gz --repo XData-si/xdata-agenthub \
  --bundle xdata-agenthub-$VERSION.intoto.jsonl
```

## What this does and does not prove

- It proves integrity (nothing changed) and origin (built by this repository's workflow from a tagged commit).
- It does **not** prove that a skill is correct or safe for your environment. Read skills before use; see the
  [skill quality standard](SKILL_QUALITY_STANDARD.md) and [runtime evidence](integration-evidence/).
- Installing through the Claude Code plugin marketplace or `npx skills` fetches files from git directly; run
  `xah verify --target` (or compare against a verified `catalog-<version>.json`) if you need the same guarantee there.
