# XAH-304 — security threat model and review queue

**Status:** release-owner security review with dispositions (see [Review 2026-10-31](#review-2026-10-31)); **not** an
independent security audit or certification.
**Baseline:** v0.3.0 development following v0.2.0 alpha; reviewed again at v0.4.0 (`ce2c994`).

## Trust boundaries

1. **Local curated catalog:** metadata, paths and markdown must be treated as untrusted input, even if distributed with the repository.
2. **Project target:** existing user files and symlinks are not controlled by AgentHub; writes must be explicit and conflict-safe.
3. **HTTPS catalog refresh:** network responses, URLs and redirects are untrusted. SHA-256 integrity does not authenticate the publisher by itself.
4. **Native agents:** consuming a SKILL.md is client-dependent. Markdown can contain hostile instructions; native runtime behavior is not certified.

## Initial source observations

- `cli/xah.py` checks local catalog source resolution and rejects symlinked skill package members; install planning refuses existing destinations and symlinked parents.
- `cli/update_plan.py` marks modified/untracked destinations and symlinks as conflicts.
- `cli/update_apply.py` stages writes and attempts rollback on ordinary exceptions. Its own docstring explicitly excludes crash consistency.
- `cli/catalog_refresh.py` requires `--approve`, HTTPS, pinned revision text, lowercase SHA-256, rejects redirects, limits payload size to 2 MB and validates catalog JSON before replacing the local catalog.
- These are code-review observations, **not** evidence that all attack paths have been tested.

## Review queue (must resolve or explicitly accept)

| ID | Scenario | Existing mitigation | Further evidence needed |
|---|---|---|---|
| SEC-01 | Symlink/path traversal in catalog and install destinations | Local path and symlink checks | Negative tests for nested paths, symlink swaps and platform-specific paths |
| SEC-02 | Concurrent writer replaces destination between check and write | Preflight and some revalidation | Document race limitations; assess file-descriptor-safe approach |
| SEC-03 | Process crash during multi-file update | Exception rollback only | Fault-injection crash rehearsal and recovery runbook |
| SEC-04 | Untrusted HTTPS catalog or malicious metadata | Pinned checksum, schema validation, redirect refusal | Publisher authentication/trust policy and malicious fixture tests |
| SEC-05 | Catalog-refresh race or local catalog tampering | Temporary file + replace | Concurrency and file ownership/permission threat review |
| SEC-06 | Prompt injection in skill markdown | Inspectable, local-first catalog | Review guidance and provenance/approval UX; never call markdown safe by default |
| SEC-07 | Leaked credentials in native-client traces | Sanitized acceptance docs | Diff/secret scan and trace-retention policy |
| SEC-08 | Unsubstantiated compatibility claims | Operator evidence with stated limitations | Independent sampling of sanitized original evidence where feasible |
| SEC-09 | Verified MCP scans execute untrusted server packages (added 2026-10-31) | Isolated container, install scripts disabled | Review of the CI isolation and of what evidence can claim |
| SEC-10 | Compromised GitHub Action or workflow change (added 2026-10-31) | Pinned versions, least-privilege tokens | SHA pinning, dependency review, static analysis |

## Proposed verification

1. Run full cross-platform tests and release validation against exact candidate SHA.
2. Add targeted negative fixtures for SEC-01, SEC-04 and SEC-05.
3. Run repository secret scanning; review provenance and license declarations.
4. Rehearse failure recovery and document residual concurrency/crash limitations.
5. Record reviewer, scope, date, severity, disposition and explicit approval or rejection.

## Review 2026-10-31

Scope: the CLI (`cli/`), installer, catalog refresh, release workflow, skill review pipeline and the Verified MCP
tooling at v0.4.0 (`ce2c994`). Method: code reading against the queue above, the named tests (run on Linux, macOS and
Windows with Python 3.10, 3.12 and 3.13 for every pull request) and the recorded evidence. Severity is the impact if the
mitigation failed, for a single-user local installation.

| ID | Severity | Mitigations and evidence | Residual risk | Disposition |
|---|---|---|---|---|
| SEC-01 | High | Install and update planning reject `..`, absolute destinations outside the target, symlinked parents, destinations and manifests (`tests/test_security_install_paths.py`, 7 tests); package paths are checked by `xah verify` (`tests/test_verify.py::test_rejects_unsafe_and_duplicate_paths`) | Windows junctions and case-insensitive collisions have no dedicated test (the general suite runs on Windows and macOS) | Mitigated; residual accepted |
| SEC-02 | Medium | Destinations are revalidated after planning: changed files, swapped symlinks and new untracked files are refused (`tests/test_security_update_races.py`); cooperative writer lock for `add`, `init` and `update` (`tests/test_update_lock.py`, `tests/test_writer_lock_cli.py`) | A process that ignores the lock can still race the final check-and-replace; no file-descriptor-relative (`openat`) writes | Accepted, documented in README known limitations |
| SEC-03 | Medium | Staged writes with rollback on exceptions (`tests/test_security_update_safety.py::test_injected_failure_restores_bytes_and_manifest`); recovery journal, `xah recovery` inspect/preflight/execute (`tests/test_recovery_*.py`); hard-exit rehearsal leaves a lock and a detectable journal (`tests/test_security_crash_rehearsal.py`); runbooks `XAH-304_EXPLICIT_RECOVERY.md`, `XAH-304_INTERRUPTED_UPDATE_RECOVERY.md` | Multi-file updates are not crash-atomic; recovery after power loss needs an operator | Accepted, documented; never described as crash-safe |
| SEC-04 | High | `catalog-refresh` requires `--approve`, HTTPS without credentials, the pinned revision in the URL, a lowercase SHA-256, refuses redirects and payloads over 2 MB and validates the schema before replacing (`tests/test_security_catalog_refresh.py`, 6 tests); optional trusted sources policy limits URLs and additional catalog directories (`tests/test_trusted_sources.py`, XAH-303) | A matching checksum proves equality, not publisher identity; refresh does not verify the release's Sigstore signature | Accepted for v0.4.0; follow-up: verify the Sigstore bundle during refresh |
| SEC-05 | Medium | Refresh writes a temporary file, `fsync`s and `os.replace`s it, checking for symlinks before and after; `xah doctor` and `xah verify` detect changed catalog entries and installed packages against SHA-256 digests | Concurrent catalog writers are not locked; file ownership and permissions are not enforced | Accepted, documented in `TRUSTED_CATALOG_REFRESH.md` |
| SEC-06 | High | Every skill passes the deterministic security gate (hidden Unicode, prompt injection, exfiltration, piped downloads, executable content: `tests/test_skill_security.py`), an advisory AI review whose malformed output never passes (`tests/test_ai_skill_review.py`) and a maintainer review; seals are bound to package digests and go stale on change (`tests/test_seal.py`) | Pattern detection cannot prove Markdown harmless; agents may still follow hostile text | Accepted; skills are never called safe, only reviewed |
| SEC-07 | Medium | Compatibility evidence with unredacted or incomplete content is rejected (`tests/test_compat_evidence.py`); repository secret scanning with push protection (enabled 2026-10-31); gitleaks on MCP artifacts | Raw native-client traces kept by operators outside the repository are not covered | Accepted; operators keep raw traces local and commit sanitized evidence only |
| SEC-08 | Low | Runtime evidence records client and version (`docs/integration-evidence/`); the *verified* seal is held by 3 skills only; README and release notes state the tested scope | Operator evidence is not independently sampled | Accepted |
| SEC-09 | Medium | Verified MCP scans run untrusted packages only in CI: npm with `--ignore-scripts`, PyPI as wheels only, the server in a container without network, capabilities or write access, `tools/list` only; evidence is bound to the pinned sha256 and re-checked by `xah doctor` (`tests/test_mcp_*.py`); nothing is installed or run by `xah` | Dependency download on the runner trusts npm and PyPI; a clean scan does not prove tool descriptions harmless | Accepted; L1/L2 are statements about one version, not certification |
| SEC-10 | Medium | Workflow supply chain: every action pinned to a commit SHA, Dependabot updates, dependency review on pull requests, CodeQL, OpenSSF Scorecard, least-privilege `permissions` per workflow, Sigstore-signed releases with SLSA provenance | Single maintainer: no second reviewer for workflow changes | Accepted; revisit when a second maintainer joins |

## Decision

- **Security reviewer:** John Aleksander Jazbec (release owner; not independent of the project)
- **Date:** 2026-10-31, scope v0.4.0 (`ce2c994`)
- **Approval:** granted for the scope above, recorded by the reviewer merging the pull request that adds this review
- **Open risks:** none unaddressed; residual risks SEC-01 to SEC-10 are accepted as listed
- **Follow-ups:** verify the Sigstore bundle during `catalog-refresh` (SEC-04); dedicated Windows junction and
  case-collision tests (SEC-01)
- **Release impact:** do not describe the project as security-certified or the update path as crash-safe
