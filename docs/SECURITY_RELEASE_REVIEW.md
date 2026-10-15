# Security, provenance and release readiness (2026-10-15)

## Scope and limitations
This is a source-level hardening pass, **not** a penetration test, legal opinion, or security certification. Cross-platform CLI and Linux installer CI passed before the latest changes; re-run CI for this revision.

## Installer review
- Local-only installer; no network downloads or downloaded scripts executed.
- Stage content, validate the staged catalog and preserve previous installation in a uniquely named backup directory.
- Refuse symlinked installation roots and existing component symlinks.
- Overwrite only a launcher matching the exact current or legacy managed content, rather than trusting a forgeable marker.
- Remaining risk: multi-directory upgrade is not atomic; a mid-upgrade interruption can leave a partial installation. Recovery uses the preserved backup. Concurrent installs and malicious modifications by the same local user are outside the current threat model.
- Run as an unprivileged user; do not install from an untrusted clone or use sudo.

## CLI and skill packages
- Install from bundled local catalog only; no arbitrary GitHub execution.
- Validate skill IDs before destination construction; reject escaping source paths and package symlinks.
- Preflight destination collisions, use exclusive create, and roll back files created when an I/O error occurs.
- Remaining risk: local filesystem race conditions between preflight and write, and partial directory creation on failure. Avoid installation into shared writable directories.

## Licensing and provenance
- The root repository declares MIT; the 34 bundled catalog entries claim XData original / MIT.
- The automated release gate checks the declared source, license, paths, required metadata, and skill frontmatter. It cannot establish legal ownership or independently verify authorship.
- External candidate registry is discovery-only; **no external candidates are approved for bundled distribution**. Third-party import requires a human review of exact upstream revision, license text, attribution, redistribution obligations, and source integrity.
- Keep upstream version/commit and license evidence when third-party content is eventually added.

## Release gate
1. Run GitHub Actions Release validation on the final commit and record its run URL.
2. Check `python scripts/validate_release.py`, unit tests, doctor, installer and audit.
3. Run final native Claude Code / Codex / OpenCode runtime matrix and preserve redacted logs. Native skill discovery must be demonstrated separately from direct file reading.
4. Verify changelog, tag, archive SHA-256 checksums, installation from tag, rollback and GitHub settings.
5. Publish a prerelease only after steps 1–4 pass. Do not advertise a final runtime compatibility result before it is tested.

## Go / no-go
- Static provenance gate: implemented; awaiting a successful CI run after latest edits.
- Source-level installer hardening: improved, but atomic rollback/concurrency remains a documented limitation.
- Native agent runtime: pending by agreement.
- Public release: **not yet approved**.
