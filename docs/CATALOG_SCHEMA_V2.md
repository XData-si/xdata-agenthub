# Catalog schema v2 — design specification (XAH-201)

Status: **draft design; implementation and tests pending**. The released v0.1.0 catalog is schema_version 1 and MUST remain readable.

## Existing v1 document

Top-level JSON object: `{"schema_version":1,"items":[...]}`. Current entries contain `id`, `type`, `name`, `description`, `path`, `license`, `source`, `targets`. The CLI reads `items` directly; `doctor` currently checks duplicate IDs and local paths but does not enforce a complete schema.

## Proposed v2 document

- Top-level required: `schema_version: 2` (integer), `items` (array).
- Optional top-level: `catalog_id` (stable slug), `catalog_version` (string), `generated_at` (RFC3339 timestamp; informational only).
- Required per-item: same eight v1 fields; existing meaning retained.
- Optional per-item:
  - `version`: opaque version string, not assumed to follow SemVer.
  - `digest`: object `{"algorithm":"sha256","value":"<64 lowercase hex>"}`; digest of item entry file bytes only, not a whole skill package. Package hashing requires a separate explicit canonical manifest in later work.
  - `upstream`: object with optional `url`, `revision` and `license_url`; descriptive provenance, **not trusted or fetched automatically**.
  - `tags`: unique lowercase slugs for later search filtering.
  - `compatibility`: map from client key (`claude`, `codex`, `opencode`, etc.) to an object with `status` (`untested`, `direct-read`, `native-observed`), optional `tested_version`, `platform`, and `evidence`. A declared status is not an independent certification.

## Validation rules

- Accept v1 and v2. Reject unknown `schema_version` values; never silently downgrade.
- Validate top-level object and item array, unique item IDs, known types (`skill`, `instruction`, `workflow`, `agent`), non-empty strings for required text fields and arrays for targets.
- IDs and tags: `[a-z0-9]+(?:-[a-z0-9]+)*`; reject duplicates.
- Item paths: relative POSIX paths only; no empty, `.`, `..`, absolute paths, backslashes or NUL. Existing runtime source-path and symlink checks remain mandatory.
- Digest: algorithm must be `sha256`; value exactly 64 lowercase hex digits. Digest validation is separate from syntax validation and must check file bytes before any trust-dependent action.
- Reject unknown fields initially to catch typos; future extensions require explicit versioning. Decide whether to allow `x-` vendor extensions before implementation.
- No network calls or external dependencies during local validation.

## Backward compatibility

- Existing v1 catalog remains untouched in this issue until the v2 parser/validator and fixtures are proven.
- CLI must accept v1 unchanged. All v0.1.0 CLI commands retain their current output and behavior on v1.
- v2 optional fields do not alter install paths or cause automatic updates.
- Schema migration should be an explicit separate operation, never an implicit write on read.

## Test fixtures and gates

1. Valid real v1 catalog (34 items).
2. Minimal valid v2 with only v1-required fields.
3. Full v2 including version, digest, upstream, tags and compatibility.
4. Invalid: missing fields, duplicate IDs/tags, unknown schema, wrong types, unsafe paths, bad digests, unsupported compatibility statuses, extra fields.
5. Regression: CLI list/search/inspect/init/doctor against v1 and v2 fixtures; no writes during validation.
6. Run on Python 3.10, 3.12, 3.13 and relevant OS CI runners.

## Security and follow-on boundaries

A checksum detects changes relative to a known value; it does not establish publisher authenticity. Remote updates, pinning, package-wide manifests, local-modification detection and rollback belong to XAH-202–204 and XAH-209. Do not treat schema declarations as proof that an agent actually loaded a skill natively.

## Implementation checklist

- [ ] Review and approve schema decisions, including strict unknown-field behavior.
- [ ] Implement standard-library validator and version dispatch.
- [ ] Add valid and invalid JSON fixtures.
- [ ] Wire validator into CLI without breaking v1.
- [ ] Add cross-platform regression tests.
- [ ] Record CI evidence and close #1 only when acceptance criteria pass.
