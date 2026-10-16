# XAH-304 — security threat model and review queue

**Status:** initial code-informed review; **not** an independent security audit or approval.
**Baseline:** v0.3.0 development following v0.2.0 alpha. Reviewer and date: pending.

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

## Proposed verification

1. Run full cross-platform tests and release validation against exact candidate SHA.
2. Add targeted negative fixtures for SEC-01, SEC-04 and SEC-05.
3. Run repository secret scanning; review provenance and license declarations.
4. Rehearse failure recovery and document residual concurrency/crash limitations.
5. Record reviewer, scope, date, severity, disposition and explicit approval or rejection.

## Decision

- **Security reviewer:** pending
- **Approval:** NOT GRANTED
- **Open risks:** SEC-01 through SEC-08 require review/disposition
- **Release impact:** do not describe the project as security-certified or the update path as crash-safe
