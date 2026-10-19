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
