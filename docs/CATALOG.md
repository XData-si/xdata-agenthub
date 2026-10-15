# Skill catalog

XData AgentHub ships **31 local skills**, plus three non-skill resources. Entries are authored locally, inspectable and not automatically executed.

## Development and quality
- `code-review` — review correctness and security of changes
- `documentation` — maintain project documentation
- `api-design` — API contracts, permissions and compatibility
- `api-integration` — retries, authentication and third-party integration
- `python-testing` — isolated Python regression tests
- `typescript-testing` — TypeScript runtime and type testing
- `technical-writing` — accurate, executable documentation
- `sql-review` — SQL correctness and performance
- `frontend-review` — frontend reliability and accessibility
- `accessibility-review` — keyboard and assistive-technology checks
- `performance-profiling` — reproducible profiling

## Security and governance
- `security-review` — security findings with evidence
- `prompt-injection-defense` — agent instruction/data trust boundaries
- `dependency-audit` — dependency and supply-chain review
- `secrets-management` — credentials lifecycle
- `data-privacy` — data protection and retention
- `mcp-review` — MCP permissions and integration risks
- `architecture-decision` — trade-offs and architecture records

## Infrastructure and operations
- `docker-hardening` — container hardening
- `kubernetes-review` — cluster resource review
- `terraform-review` — infrastructure plan review
- `postgres-performance` — PostgreSQL query diagnosis
- `incident-response` — incident triage and recovery
- `observability` — service signals, metrics and traces
- `gitlab-ci` — GitLab pipeline security
- `github-actions` — GitHub Actions security
- `release-management` — releases and rollback
- `backup-restore` — recovery validation

## AI systems
- `rag-evaluation` — grounded retrieval evaluation
- `llm-cost-analysis` — model usage and cost scenarios
- `agent-evaluation` — agent behavior evaluation

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
