# Community catalogs — specification (XAH-306)

Status: **proposed**, opt-in. Builds on [additional local catalogs](ADDITIONAL_CATALOGS.md), package digests and signed
releases ([VERIFYING.md](VERIFYING.md)). Nothing in this specification installs or executes anything automatically.

## Goals and non-goals
- Let organisations and communities publish their own skill catalogs that operators can add next to the official one.
- Keep the official catalog's guarantees visible: users always see which catalog an item comes from and whether it is
  sealed by XData.
- Non-goals: a central registry, automatic discovery, automatic updates, executing code from catalogs, ranking by
  popularity.

## Catalog format
A community catalog is the same JSON as `registry/catalog.json`, **schema v2**, with these additional rules:

| Field | Rule |
|---|---|
| `catalog_id` | required; lowercase slug; must not be `xdata-agenthub` |
| `catalog_version` | required; monotonically increasing (semantic version or integer) |
| item `id` | must start with the catalog's namespace prefix (for example `acme-`), so IDs never collide with official ones |
| item `digest` | required for every item (SHA-256 package digest) |
| item `path` | relative to the catalog file, inside its directory; no symlinks (already enforced) |
| skill packages | must pass the [skill security gate](../scripts/skill_security_check.py); no `scripts/`, `bin/`, `hooks/` or executable files |

## Distribution and pinning
A community catalog is distributed as a directory (git repository or release archive). Operators pin it in one of two ways:

1. **Signed release** (preferred): `catalog-<version>.json` plus `SHA256SUMS` and a Sigstore bundle, verified with the
   publisher's expected certificate identity (repository + workflow + tag), like AgentHub's own releases.
2. **Git commit**: a full commit SHA; the operator records it next to the catalog path.

`xah` only reads local files (`--catalog` / `XAH_CATALOGS`). Fetching and signature verification are explicit operator
steps (`git clone` at a SHA, or download + `cosign verify-blob`). A future `xah catalog add` would reuse the rules of
[trusted catalog refresh](TRUSTED_CATALOG_REFRESH.md): HTTPS only, full revision in the URL, expected SHA-256 supplied
out of band, no redirects, explicit `--approve`.

## Operator-controlled approval
- A catalog is used only when the operator lists it; there is no default community catalog.
- `xah list/search/browse` show the source catalog of each item; `xah trust` reports declared provenance only.
- Installing an item from a community catalog prints the catalog ID, version and item digest; `xah verify --target`
  later confirms the installed files still match.
- Operators can keep an allowlist of catalog IDs and certificate identities in their own configuration management.

## Failure modes
| Failure | Behaviour |
|---|---|
| catalog file missing or unreadable | error; no partial loading (already enforced) |
| schema invalid, unsafe path, symlink | catalog rejected (already enforced) |
| duplicate ID with any loaded catalog | error; no shadowing (already enforced) |
| digest mismatch for an item | `xah verify` / `doctor` report `mismatch`; install refused once installs check digests |
| item without digest | reported `unknown`; installs require `--allow-unverified` (future) |
| catalog version lower than the last accepted one | warning: possible rollback (future, operator state file) |
| signature does not verify | operator does not add the catalog (out-of-band step) |

## Threat assessment
| Threat | Mitigation |
|---|---|
| malicious skill instructions (prompt injection, exfiltration, piped downloads) | security gate rules applied to community packages; AI review recommended; skills never execute code; seals only from XData maintainers |
| tampering in transit or at rest | package digests, signed checksums, `xah verify` |
| impersonation of official skills | mandatory namespace prefix, duplicate-ID refusal, visible source catalog, XData seals bound to official digests |
| rollback to an older vulnerable catalog | monotonic `catalog_version`, operator-recorded last version |
| compromised publisher | keyless signing tied to a repository workflow identity; operators pin the identity, not just a key |
| path traversal or symlink escape | schema validation, containment checks (tested) |
| denial of service via huge files | size limits in the security gate; catalogs are local files |

## Acceptance for implementation
Implementing this specification needs: namespace and `catalog_id` validation for additional catalogs, digest
enforcement on install, source catalog shown in listings, the rollback check, and negative tests for each failure mode.
