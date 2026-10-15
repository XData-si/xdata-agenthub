# External sources and responsible skill intake

External directories are **discovery sources**, not trusted executable registries. XData AgentHub does not automatically copy, run or certify their content.

## Candidate sources

| Source | Intended use | Notes |
|---|---|---|
| https://agentskillshub.dev/skills/ | Discover projects, categories and linked upstream repositories | Directory entries include MCP servers and projects, not only installable skills. Treat grades as unverified signals. |
| https://agentskills.io/home | Agent Skills format guidance | Align SKILL.md authoring with the published format. |
| https://doc.agentskillhub.dev/guide/publishing | Compare import and packaging practices | This is a different site/domain from agentskillshub.dev; do not assume common ownership. |

## Intake procedure

1. Record the directory listing URL, upstream source repository URL, author, category and date reviewed.
2. Inspect the **upstream repository**, not only the directory listing. Locate the actual SKILL.md and any referenced scripts, assets or dependencies.
3. Verify license at the source, including attribution, notice requirements and compatibility. A directory listing does not grant reuse rights.
4. Check whether the candidate is a Markdown skill, an MCP server, a CLI package or merely a collection. Do not present these as equivalent.
5. Review instructions for unsafe execution, secret exposure, hidden network calls, privilege escalation and prompt injection. Do not execute untrusted scripts during intake.
6. Prefer original XData-authored implementations unless upstream content is intentionally imported with license clearance and provenance.
7. If imported, record immutable upstream commit, source URL, license, local modifications and checksum. Keep notices and required attribution.
8. Add catalog metadata and a minimal offline example. Defer full per-agent runtime certification until the final compatibility test cycle.

## Candidate record

```yaml
id: candidate-id
directory_url: https://example.invalid/listing
upstream_repository: https://github.com/owner/repo
upstream_commit: pending
kind: skill
license: unverified
review_status: discovery-only
risk_notes: []
decision: defer
```

Never label a skill security-certified solely because a third-party directory labels it verified. Avoid mass copying text, descriptions or proprietary editorial content from directories. Link to sources and write independent summaries.

## Publishing XData skills elsewhere

Before submitting XData AgentHub to external catalogs, check the current import rules, public repository visibility, supported folder paths and whether a third-party service snapshots files. Submit only approved, public and license-cleared content.
