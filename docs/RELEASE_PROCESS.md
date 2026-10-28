# Release process

The project is a public alpha. A tagged release should only be published after its source commit passes CI and the final per-agent compatibility suite.

## Release gate
1. Verify catalog entries, file paths, Markdown frontmatter and declared license provenance with `python3 scripts/validate_release.py`. The check is not proof of copyright ownership.
2. Run `python3 -m unittest discover -s tests -v`, `python3 cli/xah.py doctor` and `python3 cli/xah.py audit --target .`.
3. Test the installer in a disposable home directory on Linux and macOS; review Windows/WSL behavior.
4. Run the end-to-end matrix for Claude Code, Codex and OpenCode; preserve redacted evidence and distinguish native loading from direct file reads.
5. Review symlink handling, upgrades, backups and rollback; inspect changes since previous tag.
6. Verify README, quickstart, changelog, license, known limitations and version compatibility.
7. Create an annotated semantic-version tag, publish release notes and source archives; generate checksums for distributed artifacts.
8. Verify fresh installation from the release tag and update documentation links.

## Signed release (automated)
Push an annotated tag `vX.Y.Z` on the release commit. [`release.yml`](../.github/workflows/release.yml) re-runs the gates (tests, release metadata, digest check, `xah doctor`, `xah verify`), builds the archives and `catalog-<version>.json`, writes `SHA256SUMS`, signs it with Sigstore keyless signing, verifies the signature, attests SLSA build provenance and opens a **draft** release. A maintainer reviews the draft and publishes it. Verification for users: [VERIFYING.md](VERIFYING.md).

## Versioning
Use `v0.x.y` while API and catalog formats may change. Document breaking CLI changes and migration steps. Do not call a release stable merely because the unit tests pass.

## Rollback
Restore the previous tag or the installer-preserved backup after verifying integrity. Avoid overwriting user-owned project files. Preserve release evidence and incident notes.

## v0.1.0 candidate notes
- Scope: 34 bundled local resources, dependency-free CLI, offline installation, and path adapters for Claude Code, Codex and OpenCode.
- GitHub Actions `Release validation` must pass for the exact release commit; save its run URL.
- Native runtime tests are a separate required gate and must record agent/client versions and observed skill invocation.
- The installer preserves previous components in `.xah-backup.*` but upgrades are not fully atomic; validate recovery before publication.
- After all gates pass, create annotated tag `v0.1.0` and publish a GitHub release with documented SHA-256 archive checksum(s).
- Do not describe the first release as security-certified or as supporting unverified native agent behaviors.
