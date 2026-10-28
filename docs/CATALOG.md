# Skill catalog

XData AgentHub ships **61 local skills**, plus three non-skill resources. Entries are authored locally, inspectable and not automatically executed.

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
- `eu-ai-act-readiness` — AI system inventory, risk category and evidence gaps (not legal advice)
- `mcp-review` — MCP permissions and integration risks
- `architecture-decision` — trade-offs and architecture records

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

## Reliability and incidents
- `observability` — service signals, metrics and traces
- `slo-error-budgets` — user-centred SLIs, objectives and burn-rate alerts
- `log-analysis` — reproducible log investigation and correlation
- `incident-response` — incident triage and recovery
- `runbook-authoring` — on-call runbooks with safe, verified actions
- `postmortem` — blameless incident reviews with tracked actions

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
The catalog is a curated **alpha**, not a certification. Skill depth varies. Individual agent compatibility evidence and remaining gaps are documented in [integration results](integration-evidence/2026-10-15-runtime-results.md) and [runtime test plan](AGENT_RUNTIME_TESTS.md).
