# Changelog

All notable changes to XData AgentHub are recorded here. The project follows semantic versioning while APIs remain experimental.

## [Unreleased]

### Skill review, seal of approval and EU
- `scripts/skill_security_check.py`: deterministic security gate for skill packages (executable content, hidden Unicode and HTML comments, piped downloads, decode-and-execute, encoded blobs, shortened or plain-HTTP links, prompt-injection and exfiltration phrasing outside quoted fixtures, required Safety section). Fixed four skills without a Safety section.
- `scripts/ai_skill_review.py`: advisory AI review through any OpenAI-compatible endpoint; skill content treated as untrusted; malformed or manipulated output never becomes a pass; PR comments are neutralized. GitHub Models was retired on 2026-07-30, so the endpoint is configurable (`AI_REVIEW_BASE_URL`, `AI_REVIEW_API_KEY`, `AI_REVIEW_MODEL`).
- `.github/workflows/skill-review.yml`: required security gate plus digest and seal checks; advisory AI review with a PR comment (skipped for forks).
- Seal of approval (`registry/seals.json`, `scripts/seal.py`, `docs/SEAL.md`): XData Reviewed, XData Verified, EU Ready — bound to package digests, stale on any change; shown on the catalog site.
- EU: new skills `eu-data-sovereignty`, `nis2-readiness`, `cyber-resilience-act`; new `xdata-eu` plugin bundle; `docs/EU_SOVEREIGNTY.md` (64 skills, 67 resources).

### Verification and signing
- Catalog schema v2 with a SHA-256 **package digest** for every item (`cli/package_digest.py`); `scripts/update_digests.py --check` and the release gate fail on stale digests; `xah doctor` and `xah inspect` compare package digests.
- New `xah verify` for catalog sources, project installs (`--target`) and user-scope installs (`--scope user`): states verified / outdated / modified / unknown; added files in an installed skill count as modifications; exit status 2 unless everything is verified.
- `release.yml`: on version tags, re-run gates, build archives and catalog, `SHA256SUMS` signed with Sigstore keyless signing (verified in the workflow), SLSA build provenance attestation, draft GitHub release. `docs/VERIFYING.md` explains user-side verification.
- `.gitattributes` pins LF line endings so digests are identical on every platform.

### Site, branding and skill depth
- Searchable static catalog site generated from `registry/catalog.json` (`scripts/build_site.py`, standard library only) and a GitHub Pages workflow.
- Logo and social preview image (`docs/assets/`).
- Runtime evidence (2026-10-28): `agenthub-router`, `shell-script-review`, `threat-modeling` and `database-migrations` verified for tested scenarios in Claude Code 2.1.308 and OpenCode 1.19.4 with native skill-loading traces.
- "Common rationalizations" tables in ten workflow skills (spec-driven development, debugging, refactoring, TDD, git, code review, migrations, upgrades, security review, incident response).

### Distribution
- Claude Code plugin marketplace: `/plugin marketplace add XData-si/xdata-agenthub`, with an all-skills plugin and four topic bundles (`xdata-engineering`, `xdata-security`, `xdata-ops`, `xdata-ai`); validated with `claude plugin validate` and a local install.
- New `agenthub-router` meta-skill that routes tasks to skills and requires reporting their acceptance checks (61 skills, 64 resources).
- Tests for Agent Skills specification limits (name, description length and trigger phrase, body size, reference depth) and for marketplace consistency.
- README install table and positioning; `docs/COMPARISON.md`.

### Changed skill metadata
- Rewrote all 31 existing skill `description` fields to state what the skill does **and when to use it**, so agents select skills reliably; fixed title casing (API, GitHub, GitLab CI, LLM, PostgreSQL, SQL) and doubled full stops in workflow steps. No procedure changes.

### Added skills (batch 2)
- 29 new original skills (catalog: 60 skills, 63 resources): engineering workflow (`spec-driven-development`, `repository-onboarding`, `git-workflow`, `debugging-root-cause`, `test-driven-development`, `refactoring-safety`, `dependency-upgrade`, `skill-authoring`), quality (`error-handling-review`, `shell-script-review`, `database-migrations`), security (`threat-modeling`, `oauth-oidc-review`, `supply-chain-provenance`, `eu-ai-act-readiness`), operations (`linux-server-hardening`, `reverse-proxy-tls`, `email-deliverability`, `slo-error-budgets`, `log-analysis`, `runbook-authoring`, `postmortem`) and AI systems (`prompt-design-review`, `llm-output-evaluation`, `rag-ingestion-design`, `agent-guardrails`, `mcp-server-development`, `llm-gateway-routing`, `local-llm-serving`).
- All new entries are documentation-level drafts following the skill quality standard (example fixture, negative acceptance checks, safety section); none is marked Verified.

### Added after v0.3.0 RC1 preparation
- Additional local catalogs via repeatable `--catalog PATH` and `XAH_CATALOGS`; item paths resolve relative to each catalog file, duplicate IDs across catalogs are refused.
- `add`/`update --scope user` installs skills into user-level client directories (`~/.claude/skills`, `~/.agents/skills`, `~/.config/opencode/skills`); instructions and the generic adapter are refused at user scope. User-scope runtime discovery is not yet verified.

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
