# Changelog

All notable changes to XData AgentHub are recorded here. The project follows semantic versioning while APIs remain experimental.

## [Unreleased]

### Added
- Verified MCP phase 1 (#84): `registry/mcp-servers.json` lists MCP servers with metadata imported from the official
  MCP Registry, pinned to one version and marked L0 (listed only, not verified). `scripts/import_mcp_registry.py`
  refreshes listed servers idempotently and resets an entry to L0 when its upstream version changes.
  `xah mcp list|search|inspect` and an MCP section on the catalog site show them. Nothing is installed or run.
- Weekly `MCP registry check` workflow: opens or updates a `verified-mcp` issue when listed MCP servers changed
  upstream (read-only; a maintainer runs the importer and reviews the diff).
- Demo recordings (`demos/recordings/`): VHS tapes for install, release verification, the with/without comparison
  and MCP search, rendered by the manual `Recordings` workflow as a downloadable artifact.

### Changed
- `Release validation` runs on every pull request. Its jobs are required for `main`, and the previous path
  filter left pull requests that touched only other files (for example `demos/`) without required checks.

## [0.3.0] - 2026-10-29

First signed release. Highlights: 104 security-reviewed skills (seals bound to package digests), Claude Code plugin
marketplace, `xah verify`, Sigstore-signed checksums with SLSA provenance, catalog site, EU sovereignty skills, and
measured before/after demos. Details below.

### Fixed
- `xah verify --target` failed with a path error when the same skill was installed for several agents in one project;
  each installation is now verified separately and named by its directory (found in the release walkthrough).

### Before/after demos
- `demos/`: three reproducible demos (shell script review, production migration, code review), each run with and
  without the skill. The harness gives every run an isolated agent configuration, the rubric is fixed in advance,
  and scoring is scripted with maintainer overrides published together with their evidence.
- First results (`demos/results/2026-10-29/`): no difference in planted issues found (a ceiling effect with a frontier
  model). Post-hoc, the skill runs reported their evidence more honestly and asked for approvals. Limitations are
  documented.

### Vision: Verified AI Capabilities Registry
- `docs/VERIFIED_MCP.md`: proposed verification of MCP servers as a downstream registry of the official MCP Registry — levels L0–L4 bound to exact artifacts, permission profiles, verification pipeline, skill + MCP capability bundles, public reports and badges, phases.
- `ROADMAP.md` rewritten around the vision, with current status and next priorities.
- README: single headline promise, "See it work" example from recorded runtime evidence, and a pointer to Verified MCP.

### Skills batch 3 and contributor pipeline
- 40 new original skills (104 skills, 107 resources), each through the security gate, AI review and seal process:
  languages and frameworks (Go, Rust, Java/Spring, React, Node.js, Django/FastAPI, mobile), architecture and data
  (GraphQL, event-driven, caching, data pipelines, data quality, feature flags, i18n), operations (CI/CD design,
  container images, Helm, Ansible, cloud cost, load testing, chaos engineering, DR drills, logging, release notes),
  security (cloud IAM, network segmentation, vulnerability management, OWASP ASVS, security testing scope, licence
  compliance), EU (GDPR requests, DPIA, DORA, European Accessibility Act) and AI (red teaming, multi-agent
  orchestration, structured extraction, LLM observability, embedding selection, ML deployment).
- Router and topic bundles cover the new skills.
- Contribution pipeline made explicit: CONTRIBUTING.md, pull request template, README and catalog site state that every
  skill — including community contributions — is security-reviewed before distribution.
- Repository automation: issue template configuration (private security reporting, discussions), path-based PR labels,
  first-contribution welcome, stale handling, Dependabot for GitHub Actions; private vulnerability reporting enabled.

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

### v0.3.0 RC1 preparation
- Integrated adapter destination contract for Claude Code, Codex, OpenCode and generic projects.
- Added local catalog `browse` pagination/facets and `trust` declared-provenance classification; trust output is not independent verification.
- Added `release-check` evidence-shape validation; it does not authenticate reviewers, CI or signatures.
- Added recovery tests simulating external destination edits and interrupted rollback; destination checksums are revalidated immediately before mutation.
- Added RC1 readiness checklist and release evidence requirements; release owner sign-off, frozen-SHA CI and operator walkthrough remain pending.

### v0.3.0 known limitations
- Multi-file rollback is not crash-atomic; cooperative locking cannot prevent unrelated writers, and a TOCTOU window remains.
- Native client acceptance is scenario/version-limited; catalog metadata is not independently authenticated.
- Codex CLI native loading was not re-tested for this release; Codex support is path-level (`.agents/skills/`) plus the earlier XAH-205 evidence.
- User-scope runtime discovery is not yet verified in a client.

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
