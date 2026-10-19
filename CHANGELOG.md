# Changelog

All notable changes to XData AgentHub are recorded here. The project follows semantic versioning while APIs remain experimental.

## [Unreleased]

### v0.3.0 RC1 preparation (not tagged or published)
- Integrated adapter destination contract for Claude Code, Codex, OpenCode and generic projects.
- Added local catalog `browse` pagination/facets and `trust` declared-provenance classification; trust output is not independent verification.
- Added `release-check` evidence-shape validation; it does not authenticate reviewers, CI or signatures.
- Added recovery tests simulating external destination edits and interrupted rollback; destination checksums are revalidated immediately before mutation.
- Added RC1 readiness checklist and release evidence requirements; release owner sign-off, frozen-SHA CI and operator walkthrough remain pending.

### v0.3.0 known limitations
- Multi-file rollback is not crash-atomic; cooperative locking cannot prevent unrelated writers, and a TOCTOU window remains.
- Native client acceptance is scenario/version-limited; catalog metadata is not independently authenticated.
- No RC1 release approval, tag or publication has occurred.

### Earlier development work

### Added
- Offline-first Python CLI with list, search, inspect, add, init, doctor and heuristic audit.
- Curated local registry with 31 skills and 3 supporting templates.
- Native-path installation for Claude Code, Codex and OpenCode.
- Multi-file skill package installation including references and assets.
- Cross-platform CI matrix and manual release validation workflow.
- Release metadata and provenance validation script.
- External candidate discovery registry (discovery only; no third-party imports).

### Security
- Reject symlinked package entries and unsafe skill IDs.
- Restrict installer launcher replacement to exact managed content.
- Preflight collisions and avoid overwriting project files.

### Known limitations
- Native end-to-end agent compatibility matrix not yet completed.
- Installer multi-directory upgrade is not atomic; previous-version backup is retained.
- Heuristic audit is not a comprehensive security scanner.
- External candidates have not been licensed, audited or approved for import.

## v0.1.0 (planned)
Do not tag or publish until release validation and native runtime compatibility tests pass.
