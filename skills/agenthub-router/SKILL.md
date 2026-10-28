---
name: agenthub-router
description: Pick the right XData AgentHub skill (or a short sequence of skills) for the task at hand and apply it with its acceptance checks. Use at the start of any non-trivial engineering, security, operations or AI task when several AgentHub skills are installed, or when the user asks which skill or workflow to use.
license: MIT
---

# AgentHub Router

## Goal
Route each task to the most specific installed skill, chain skills when a task spans phases, and make sure the chosen skill's acceptance checks are reported — not just its steps.

## Procedure
1. **Classify the task** by its main artefact: new feature, bug, review, infrastructure change, incident, AI or agent system, documentation.
2. **Pick from the routing table** below. Prefer the most specific skill; use at most three skills in sequence.
3. **Announce the plan** in one line: which skills, in which order, and why.
4. **Apply each skill fully,** including its decision points and safety section; stop and ask where a skill requires approval.
5. **Report against acceptance checks** of every skill used: met, not met, or NOT RUN with the reason.
6. **No match?** Proceed with general good practice and say that no AgentHub skill covered the task.

## Routing table
| Task | Skills (in order) |
|---|---|
| New feature or vague request | `spec-driven-development` → `test-driven-development` → `code-review` |
| First work in an unknown repository | `repository-onboarding` |
| Bug, failing test, production error | `debugging-root-cause` → `test-driven-development` |
| Clean-up without behaviour change | `refactoring-safety` |
| Framework, runtime or base-image upgrade | `dependency-upgrade` → `dependency-audit` |
| Schema or data change | `database-migrations` → `sql-review` |
| Review a pull or merge request | `code-review` (+ `security-review`, `error-handling-review`, `frontend-review` as relevant) |
| Commits, branches, conflicts | `git-workflow` |
| Shell or install script | `shell-script-review` |
| New service or exposed API | `threat-modeling` → `api-design` → `security-review` |
| Login, SSO, tokens | `oauth-oidc-review` |
| Credentials, rotation, leaks | `secrets-management` |
| Release pipeline, signing, SBOM | `supply-chain-provenance` → `release-management` |
| Personal data, GDPR | `data-privacy` |
| AI feature offered in the EU | `eu-ai-act-readiness` → `data-privacy` |
| Choosing cloud, SaaS or AI providers for EU data | `eu-data-sovereignty` → `data-privacy` |
| NIS2 sector organisation or its supplier | `nis2-readiness` → `incident-response` |
| Software or device sold in the EU | `cyber-resilience-act` → `supply-chain-provenance` |
| New server or VPS | `linux-server-hardening` → `docker-hardening` |
| Publishing a service on a domain | `reverse-proxy-tls` |
| Mail lands in spam, spoofing | `email-deliverability` |
| Containers, Kubernetes, Terraform | `docker-hardening`, `kubernetes-review`, `terraform-review` |
| CI pipelines | `gitlab-ci` or `github-actions` |
| Reliability targets, noisy alerts | `slo-error-budgets` → `observability` |
| Active incident | `incident-response` → `log-analysis` → `postmortem` |
| Missing operational procedure | `runbook-authoring` |
| Backups and restore tests | `backup-restore` |
| Slow code or queries | `performance-profiling`, `postgres-performance` |
| Prompt or LLM feature change | `prompt-design-review` → `llm-output-evaluation` |
| RAG assistant | `rag-ingestion-design` → `rag-evaluation` |
| Agent with tools or credentials | `agent-guardrails` → `prompt-injection-defense` → `agent-evaluation` |
| Building or reviewing an MCP server | `mcp-server-development` / `mcp-review` |
| Self-hosted models, GPU sizing | `local-llm-serving` |
| Several model providers, keys, budgets | `llm-gateway-routing` → `llm-cost-analysis` |
| Go, Rust, Java/Spring, React, Node.js, Django/FastAPI, mobile code | `go-development`, `rust-review`, `java-spring-review`, `react-component-review`, `node-backend-review`, `python-web-review`, `mobile-app-review` |
| GraphQL API | `graphql-api-review` → `security-review` |
| Queues, events, async processing | `event-driven-architecture` |
| Slow reads, adding a cache | `caching-strategy` |
| ETL/ELT, warehouse, wrong report numbers | `data-pipeline-review` → `data-quality-checks` |
| Gradual rollout, kill switch | `feature-flags` |
| Multiple languages in a product | `i18n-localization` |
| New or slow CI/CD pipeline | `ci-cd-pipeline-design` → `gitlab-ci` / `github-actions` |
| Large or vulnerable container images | `container-image-optimization` → `docker-hardening` |
| Helm charts, Ansible playbooks | `helm-chart-review`, `ansible-review` |
| Rising cloud or AI bill | `cloud-cost-optimization` → `llm-cost-analysis` |
| Cloud or Kubernetes permissions | `cloud-iam-least-privilege` |
| Firewall rules, network zones | `network-segmentation` |
| Capacity before launch | `load-testing` → `performance-profiling` |
| Proving resilience or recovery | `chaos-engineering`, `disaster-recovery-drill` |
| Logging design or leaky logs | `logging-standards` |
| Preparing a release announcement | `release-notes` → `release-management` |
| Scanner backlog, new critical CVE | `vulnerability-management` |
| Verifiable security requirements | `owasp-asvs-review` |
| Commissioning a penetration test | `security-testing-scope` |
| Licences of dependencies | `open-source-license-compliance` |
| GDPR access or erasure request | `gdpr-dsar-handling` |
| High-risk personal data processing | `dpia` |
| Financial entity or its ICT provider in the EU | `dora-readiness` |
| Consumer product or service accessibility in the EU | `european-accessibility-act` → `accessibility-review` |
| Attacking an LLM feature before launch | `ai-red-teaming` → `agent-guardrails` |
| Several cooperating agents | `multi-agent-orchestration` |
| Extracting fields from documents with an LLM | `llm-structured-extraction` |
| Monitoring LLM cost and behaviour | `llm-observability` |
| Choosing embeddings for search or RAG | `embedding-model-selection` → `rag-evaluation` |
| Putting an ML model into production | `ml-model-deployment` |
| Documentation | `documentation`, `technical-writing` |
| Architecture choice | `architecture-decision` |
| Writing a new skill | `skill-authoring` |

## Acceptance checks
- The chosen skills and the reason are stated before work starts.
- Each used skill's acceptance checks appear in the final report with a status.
- Approval-gated steps from any skill were not executed without approval.

## Safety
Routing never widens permissions: the strictest safety section among the chosen skills applies.
