# Public launch checklist

- [x] Public standalone GitHub repository
- [x] Working local-first Python CLI and installer
- [x] README, contributing, security and MIT license
- [x] CI workflow committed
- [x] Baseline cross-platform CI passed (run 38812938810; prior to latest release changes)
- [x] Release-validation workflow independently verified: https://github.com/XData-si/xdata-agenthub/actions/runs/38816859904 (11/11 jobs successful; tested SHA `57650e6aef515e4f03b4ab65c71c482fc25b3e42`)
- [ ] Verify macOS, Linux and Windows/WSL behavior
- [x] Source-level review of installer, launcher and symlink protections (see SECURITY_RELEASE_REVIEW.md)
- [ ] Verify interrupted-upgrade recovery and restore from backup
- [ ] Commission original logo, terminal GIF and social preview
- [x] Curated catalog includes 31 skills and 3 supporting templates
- [ ] Publish tested compatibility matrix for each supported agent
- [ ] Configure repository description, topics, Discussions and social preview in GitHub settings
- [ ] Prepare a demo and community launch without artificial stars or spam

## v0.1.0 release blockers
- [x] Final release validation on exact release commit, including workflow provenance and audit gates (run 38816859904; 11/11 jobs successful)
- [x] Claude Code, Codex and OpenCode code-review smoke-test evidence documented (native invocation observed for Claude/OpenCode; Codex used SKILL.md directly; OpenCode discovery partial). See docs/integration-evidence/2026-10-15-runtime-results.md
- [x] Fresh install from `v0.1.0-rc.1` succeeded (Python 3.14.7; 34/34 catalog entries); candidate archive SHA-256 `26dc4caf1e57e7983650f2fb8f036136e2a6b2926e569ed3e595c19612d1d6a6`
- [x] Published GitHub release `v0.1.0` (2026-10-15) at validated SHA `57650e6aef515e4f03b4ab65c71c482fc25b3e42`

## v0.1.0 post-release verification (2026-10-15)

- [x] Annotated final tag `v0.1.0` resolves to validated SHA `57650e6aef515e4f03b4ab65c71c482fc25b3e42`.
- [x] Public GitHub release published: https://github.com/XData-si/xdata-agenthub/releases/tag/v0.1.0
- [x] Fresh clone from final tag at exact validated SHA; `detached HEAD` expected.
- [x] Isolated Linux install on Python 3.14.7; `xah doctor` validated all 34 catalog entries and `xah list` displayed them.
- [x] `xah search security` returned `code-review` and `security-review`; `xah inspect code-review` displayed skill metadata and instructions.
- [x] `xah init --agent claude --profile developer` generated `CLAUDE.md`, `.claude/skills/code-review/SKILL.md`, and `.claude/skills/documentation/SKILL.md` in a disposable project.
- [x] Final tag archive SHA-256: `5d154f1b1309aa9976800593322040e456d3d02431e1d9bf052d54cdd8a28c43` (`xdata-agenthub-v0.1.0.tar.gz`). Operator verified `sha256sum -c SHA256SUMS` => `OK`.
- [x] `SHA256SUMS` attached to GitHub Release, independently confirmed through GitHub API.

Evidence: operator-provided terminal transcripts in release conversation; no raw log archive or cryptographic signature. This checklist update is post-release documentation on `main`, **not part of immutable v0.1.0 tag**. SHA-256 provides integrity checking against the published value, not independent publisher authenticity.
