# v0.3.0 RC1 — candidate readiness (not a release)

**Status:** preparation only. No v0.3.0-rc1 tag, GitHub Release, or signed release approval exists as a result of this document.

## Scope and integration baseline

- Integration: [PR #67](https://github.com/XData-si/xdata-agenthub/pull/67), squash-merged into main as `929242dbc27663fcf1c9c5ad8a2e50c39e5ed785`.
- Included: adapter destination contract, catalog browse/filter/pagination, declared provenance trust reporting, evidence-based release-check CLI, recovery fault-injection tests and pre-mutation checksum revalidation.
- PRs #63–#66 were integrated through #67; do not merge their old branches again.
- **Important:** freeze and record a fresh RC candidate SHA after this documentation PR is reviewed and merged. The integration commit is not automatically the final candidate SHA.

## Evidence gates (no self-attested approvals)

| Gate | Current evidence | Status |
| --- | --- | --- |
| Unit tests | GitHub Actions Tests succeeded for #67 head `53e5591cbccc7beef6c4dfe4794a9a952469fd5f` | Historical integration evidence; rerun on frozen RC SHA |
| Release validation / CI matrix | GitHub Actions Release validation succeeded for same #67 head | Historical integration evidence; rerun on frozen RC SHA |
| Integration tests | Integration CLI tests included in #67 | Verify on frozen RC SHA |
| Security review | Recovery fault-injection and external edit tests added | **Pending manual review and risk acceptance** |
| Operator walkthrough | No RC1-specific walkthrough recorded here | **Pending** |
| Native-client compatibility | Existing evidence in `docs/integration-evidence/` | Reconfirm supported versions and claims for RC1 |
| Documentation | RC1 readiness draft | **Pending final review** |
| Release owner approval | Not provided | **Pending** |

`xah release-check` validates **only evidence JSON structure**. It does not verify CI, signatures, reviewer identities, or approvals. Never set a gate to `passed: true` solely because this checklist exists.

## Reproducible operator validation

Run from a **fresh checkout at the frozen commit**, with Python 3.10+:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_release.py
python3 cli/xah.py doctor
python3 cli/xah.py list
python3 cli/xah.py browse --kind skill --limit 5 --json
python3 cli/xah.py trust --json
python3 cli/xah.py audit --target .
python3 cli/xah.py release-check --help
```

Perform an isolated install and update/rollback rehearsal against a disposable project; do not run destructive operations against a working repository. Save logs with secrets redacted. Check Python 3.10/3.12/3.13 and available Linux/macOS/Windows CI results for the **exact** frozen SHA.

## Recovery risk acceptance

The XAH writer lock is cooperative: unrelated processes can still change files concurrently. Destination hashes are checked immediately before each rollback mutation, but a time-of-check/time-of-use race remains. A crash partway through a multi-file rollback may leave a partially restored project and unresolved journal. Do not advertise crash-atomic rollback, comprehensive concurrency protection, or security certification. Keep independent full-project backups (including hidden directories and manifest) and require operator inspection on recovery errors.

## Release decision

Before any RC tag or publication:

1. Freeze the final candidate SHA and confirm green CI for **that exact SHA**.
2. Complete manual security review and operator walkthrough, including interruption, external edits and restoration from independent backup.
3. Validate native agent loading with recorded client versions, or explicitly limit claims to path-level adapter behavior.
4. Update README, migration notes, changelog and release notes to distinguish shipped vs development behavior.
5. Collect actual evidence references and named reviewer approvals; run `xah release-check --evidence <reviewed-file> --json`.
6. Obtain explicit release-owner authorization **separately** before tagging or publishing.

See [release process](RELEASE_PROCESS.md), [operator runbook](OPERATOR_RUNBOOK.md), [compatibility evidence](AGENT_COMPATIBILITY_EVIDENCE.md), and [XAH-308 gates](XAH-308_RELEASE_GATES.md).

## Final release record (v0.3.0, 2026-10-29)

The RC1 preparation above was superseded by a direct v0.3.0 release. The release commit is the merge commit of the
release pull request; the `v0.3.0` tag points at it, and `release.yml` re-runs every gate on that exact commit before
it signs anything.

| Gate | Evidence | Status |
| --- | --- | --- |
| Unit, integration and release tests | `Tests` and `Release validation` (Linux, macOS, Windows × Python 3.10/3.12/3.13) on the release PR, then re-run by `release.yml` on the tagged commit | Passed on the PR; the tag run is linked from the release |
| Catalog, digests, seals, security gate | `validate_release.py`, `update_digests.py --check`, `seal.py check` (137 seals on 104 skills), `skill_security_check.py` (104 skills, 0 failed) | Passed |
| Operator walkthrough | [2026-10-29 walkthrough](integration-evidence/2026-10-29-v0.3.0-operator-walkthrough.md): fresh checkout, installer twice in a disposable home, multi-agent install, tamper detection, conflict-safe update, user scope | Passed after one fix (`xah verify` with the same skill for several agents) |
| Native-client compatibility | [2026-10-28 runtime results](integration-evidence/2026-10-28-runtime-results.md): Claude Code 2.1.308 and OpenCode 1.19.4 with native loading traces; [before/after demos](../demos/results/2026-10-29/RESULTS.md) | Claude Code and OpenCode verified for the tested scenarios; Codex path-level only for this release |
| Security review and risk acceptance | Known limitations below and in the changelog; no new code execution paths since v0.2.0 (skills stay instructions only) | Accepted by the release owner with the release decision |
| Release owner approval | John Aleksander Jazbec requested the v0.3.0 release on 2026-10-29; approval is final when the release pull request is merged and the draft release is published | Pending publication |

Risks accepted for v0.3.0: rollback is not crash-atomic across multiple files; the writer lock is cooperative; catalog
metadata and seals are maintainer statements bound to digests, not third-party certification; Codex CLI native loading
and user-scope runtime discovery were not re-tested for this release.
