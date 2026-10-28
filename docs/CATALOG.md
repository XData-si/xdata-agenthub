# Skill catalog

XData AgentHub ships **104 local skills**, plus three non-skill resources. Entries are authored locally, inspectable and not automatically executed.

## Start here
- `agenthub-router` — route a task to the right AgentHub skills and report their acceptance checks

## Engineering workflow
- `spec-driven-development` — specification, plan and tasks before code
- `repository-onboarding` — evidence-based map of an unfamiliar codebase
- `git-workflow` — clean branches, atomic commits and safe history
- `debugging-root-cause` — reproduce, hypothesise and prove root causes
- `test-driven-development` — red-green-refactor with failing tests first
- `refactoring-safety` — behaviour-preserving refactoring in small steps
- `dependency-upgrade` — incremental framework and runtime upgrades
- `skill-authoring` — write skills agents load and follow reliably
- `release-notes` — user-focused changelogs and migration steps

## Languages and frameworks
- `go-development` — idiomatic Go: errors, context, goroutines, races, tests
- `rust-review` — unsafe, panics, errors, async and dependency hygiene
- `java-spring-review` — spring Security, transactions, JPA N+1, Actuator
- `react-component-review` — hooks, state, rendering, accessibility and XSS
- `node-backend-review` — validation, async errors, event loop, secure defaults
- `python-web-review` — django and FastAPI security, ORM and async pitfalls
- `mobile-app-review` — iOS/Android storage, network, privacy and release

## Architecture and data
- `graphql-api-review` — field authorization, query limits, batching, schema evolution
- `event-driven-architecture` — idempotent consumers, outbox, ordering, DLQ, schemas
- `caching-strategy` — keys, invalidation, stampedes and per-user isolation
- `data-pipeline-review` — idempotent ETL/ELT, late data, schema drift, backfills
- `data-quality-checks` — data contracts, freshness, volume and reconciliation checks
- `feature-flags` — progressive delivery, kill switches and flag cleanup
- `i18n-localization` — iCU plurals, locale formats, pseudo-localization

## Development and quality
- `code-review` — review correctness and security of changes
- `error-handling-review` — timeouts, retries, partial failure and error reporting
- `documentation` — maintain project documentation
- `technical-writing` — accurate, executable documentation
- `api-design` — API contracts, permissions and compatibility
- `api-integration` — retries, authentication and third-party integration
- `python-testing` — isolated Python regression tests
- `typescript-testing` — TypeScript runtime and type testing
- `shell-script-review` — safe, portable Bash and POSIX scripts
- `sql-review` — SQL correctness and performance
- `database-migrations` — zero-downtime schema and data migrations
- `frontend-review` — frontend reliability and accessibility
- `accessibility-review` — keyboard and assistive-technology checks
- `performance-profiling` — reproducible profiling

## Security and governance
- `security-review` — security findings with evidence
- `threat-modeling` — data flows, trust boundaries and STRIDE threats
- `oauth-oidc-review` — OAuth 2 and OpenID Connect flows and token validation
- `prompt-injection-defense` — agent instruction/data trust boundaries
- `dependency-audit` — dependency and supply-chain review
- `supply-chain-provenance` — SBOMs, signatures and deploy-time verification
- `secrets-management` — credentials lifecycle
- `data-privacy` — data protection and retention
- `mcp-review` — MCP permissions and integration risks
- `architecture-decision` — trade-offs and architecture records
- `cloud-iam-least-privilege` — wildcards, escalation paths, keys and access reviews
- `network-segmentation` — zones, flow matrix, management access, verification
- `vulnerability-management` — cVSS, EPSS, KEV, reachability, SLAs and exceptions
- `owasp-asvs-review` — requirement-to-evidence verification by ASVS level
- `security-testing-scope` — authorized pentest scope, rules of engagement
- `open-source-license-compliance` — sBOM licences, copyleft obligations, notices (not legal advice)

## European sovereignty and legislation
- `eu-data-sovereignty` — data residency, jurisdiction, GDPR transfers, keys and exit plans (not legal advice)
- `eu-ai-act-readiness` — AI system inventory, risk category and evidence gaps (not legal advice)
- `nis2-readiness` — NIS2 scope, risk-management measures and 24h/72h reporting (not legal advice)
- `cyber-resilience-act` — CRA scope, essential requirements, SBOM and vulnerability reporting (not legal advice)
- `gdpr-dsar-handling` — data subject requests across systems (not legal advice)
- `dpia` — data protection impact assessments (not legal advice)
- `dora-readiness` — financial-sector ICT resilience obligations (not legal advice)
- `european-accessibility-act` — eAA scope, EN 301 549/WCAG and statements (not legal advice)

## Infrastructure and operations
- `linux-server-hardening` — SSH, firewall, patching and exposure baseline
- `docker-hardening` — container hardening
- `kubernetes-review` — cluster resource review
- `terraform-review` — infrastructure plan review
- `reverse-proxy-tls` — proxy, certificates, headers and upstream exposure
- `email-deliverability` — SPF, DKIM, DMARC and sender reputation
- `postgres-performance` — PostgreSQL query diagnosis
- `gitlab-ci` — GitLab pipeline security
- `github-actions` — GitHub Actions security
- `release-management` — releases and rollback
- `backup-restore` — recovery validation
- `ci-cd-pipeline-design` — build once, promote by digest, gates and rollback
- `container-image-optimization` — multi-stage, minimal bases, cache, non-root
- `helm-chart-review` — values schema, secure defaults, upgrades and CRDs
- `ansible-review` — idempotency, check mode, vault and Molecule tests
- `cloud-cost-optimization` — finOps: allocation, waste, right-sizing, AI spend

## Reliability and incidents
- `observability` — service signals, metrics and traces
- `slo-error-budgets` — user-centred SLIs, objectives and burn-rate alerts
- `log-analysis` — reproducible log investigation and correlation
- `incident-response` — incident triage and recovery
- `runbook-authoring` — on-call runbooks with safe, verified actions
- `postmortem` — blameless incident reviews with tracked actions
- `load-testing` — workload models, test types, bottlenecks and SLOs
- `chaos-engineering` — hypotheses, blast radius, abort conditions
- `disaster-recovery-drill` — prove RTO/RPO with isolated restores
- `logging-standards` — structured logs, correlation, redaction, retention

## AI systems and agents
- `prompt-design-review` — structured, testable and injection-aware prompts
- `llm-output-evaluation` — evaluation harness with calibrated judges and release gates
- `rag-ingestion-design` — parsing, chunking, ACLs and incremental indexing
- `rag-evaluation` — grounded retrieval evaluation
- `agent-evaluation` — agent behavior evaluation
- `agent-guardrails` — permissions, approvals, sandboxing and audit for agents
- `mcp-server-development` — scoped tools, authorization and tests for MCP servers
- `llm-gateway-routing` — model aliases, keys, budgets and fallbacks
- `local-llm-serving` — GPU sizing, quantization and benchmarking for self-hosted models
- `llm-cost-analysis` — model usage and cost scenarios
- `ai-red-teaming` — authorized LLM and agent attack testing with regressions
- `multi-agent-orchestration` — roles, task contracts, isolation and budgets
- `llm-structured-extraction` — schemas, validation, grounding and review queues
- `llm-observability` — traces, tokens, cost, quality signals and privacy
- `embedding-model-selection` — multilingual evaluation, cost, hosting and migration
- `ml-model-deployment` — registry, staged rollout, drift and rollback

## Other resources
- `project-agents` — portable AGENTS.md instruction template
- `devops-review` — workflow template
- `research-agent` — agent role template

## Usage

```sh
python3 cli/xah.py search security
python3 cli/xah.py inspect mcp-review
python3 cli/xah.py add mcp-review --agent codex --target /path/to/existing/project
```

Use `--agent claude`, `--agent codex`, `--agent opencode` or the generic default. Installation copies local Markdown only and refuses overwriting existing files.

## Quality status
Seals (XData Reviewed, XData Verified, EU Ready) are listed in [`registry/seals.json`](../registry/seals.json) and explained in [SEAL.md](SEAL.md).

**Verified scenarios** (native skill loading captured in Claude Code 2.1.308 and OpenCode 1.19.4, see [2026-10-28 results](integration-evidence/2026-10-28-runtime-results.md)): `agenthub-router`, `shell-script-review`, `threat-modeling`, `database-migrations`. Earlier scenario evidence: `code-review` (Codex, OpenCode), `mcp-review`, `security-review`, `python-testing` (Codex; skill instructions consumed, native loading not verified) — see [2026-10-15 results](integration-evidence/2026-10-15-runtime-results.md).

The catalog is a curated **alpha**, not a certification. Skill depth varies. Individual agent compatibility evidence and remaining gaps are documented in [integration results](integration-evidence/2026-10-15-runtime-results.md) and [runtime test plan](AGENT_RUNTIME_TESTS.md).
