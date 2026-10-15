# Public launch checklist

- [x] Public standalone GitHub repository
- [x] Working local-first Python CLI and installer
- [x] README, contributing, security and MIT license
- [x] CI workflow committed
- [x] Baseline cross-platform CI passed (run 38812938810; prior to latest release changes)
- [x] Release-validation workflow reported successful by operator on 2026-10-15 (cross-platform and Linux installer); exact run URL/SHA still to be recorded
- [ ] Verify macOS, Linux and Windows/WSL behavior
- [x] Source-level review of installer, launcher and symlink protections (see SECURITY_RELEASE_REVIEW.md)
- [ ] Verify interrupted-upgrade recovery and restore from backup
- [ ] Commission original logo, terminal GIF and social preview
- [x] Curated catalog includes 31 skills and 3 supporting templates
- [ ] Publish tested compatibility matrix for each supported agent
- [ ] Configure repository description, topics, Discussions and social preview in GitHub settings
- [ ] Prepare a demo and community launch without artificial stars or spam

## v0.1.0 release blockers
- [ ] Final release validation on exact release commit, including provenance gate and audit
- [x] Claude Code, Codex and OpenCode code-review smoke-test evidence documented (native invocation observed for Claude/OpenCode; Codex used SKILL.md directly; OpenCode discovery partial). See docs/integration-evidence/2026-10-15-runtime-results.md
- [ ] Fresh install from release candidate tag and documented archive SHA-256
- [ ] Publish GitHub release only after checks pass
