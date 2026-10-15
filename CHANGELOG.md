# Changelog

All notable changes to XData AgentHub are recorded here. The project follows semantic versioning while APIs remain experimental.

## [Unreleased]
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
