# XAH-206 release gate evidence

The release-validation workflow runs on Ubuntu 24.04, macOS and Windows, with Python 3.10, 3.12 and 3.13 (nine combinations). Each job executes unit tests, catalog and provenance validation, heuristic audit, and `scripts/smoke_release_gates.py`.

The offline smoke gate checks compatibility-evidence schema, catalog doctor, installed-file manifest, read-only dry-run, conflict refusal, and rollback restoration after injected failure. The Linux installer gate remains separate. All jobs must pass before merge.

**Limitations:** CI does not execute native Claude Code, Codex or OpenCode clients. As of 2026-10-16, operator-reported manual tests have been recorded for Claude Code, Codex CLI and OpenCode (three methods each); generic remains `not_tested`. See [XAH-205 acceptance](integration-evidence/XAH-205-ACCEPTANCE.md). Original runtime traces were not independently audited. A passing CI run is not proof of crash consistency, concurrent update safety, or agent native discovery.

## Tested SHA and release sign-off

Do not pre-fill or invent a tested release SHA. At release-candidate sign-off, record the **exact immutable commit SHA**, the GitHub Actions workflow-run URL, matrix results, review date and approver in a dedicated release evidence entry. The workflow may run against a pull-request merge ref; that is not necessarily the final release commit. Re-run release validation against the final candidate SHA before tagging.

Existing v0.1.0 tag must remain unchanged.
