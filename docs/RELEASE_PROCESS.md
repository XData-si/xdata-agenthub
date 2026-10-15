# Release process

The project is a public alpha. A tagged release should only be published after its source commit passes CI and the final per-agent compatibility suite.

## Release gate
1. Verify catalog entries, file paths, Markdown frontmatter and license provenance.
2. Run `python3 -m unittest discover -s tests -v`, `python3 cli/xah.py doctor` and `python3 cli/xah.py audit --target .`.
3. Test the installer in a disposable home directory on Linux and macOS; review Windows/WSL behavior.
4. Run the end-to-end matrix for Claude Code, Codex and OpenCode; preserve redacted evidence and distinguish native loading from direct file reads.
5. Review symlink handling, upgrades, backups and rollback; inspect changes since previous tag.
6. Verify README, quickstart, changelog, license, known limitations and version compatibility.
7. Create an annotated semantic-version tag, publish release notes and source archives; generate checksums for distributed artifacts.
8. Verify fresh installation from the release tag and update documentation links.

## Versioning
Use `v0.x.y` while API and catalog formats may change. Document breaking CLI changes and migration steps. Do not call a release stable merely because the unit tests pass.

## Rollback
Restore the previous tag or the installer-preserved backup after verifying integrity. Avoid overwriting user-owned project files. Preserve release evidence and incident notes.
