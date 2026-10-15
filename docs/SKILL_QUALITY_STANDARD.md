# Skill quality standard

A catalog entry is not automatically production-ready because it has a `SKILL.md` file.

## Required for a mature skill
1. Clear purpose and triggering conditions.
2. Explicit inputs, assumptions and permissions.
3. Domain-specific steps with meaningful decision points.
4. A small example or fixture users can reproduce.
5. Observable acceptance criteria, including negative cases.
6. Explicit safety boundaries and prohibited actions.
7. Expected deliverables and limitations.
8. Review by a maintainer familiar with the domain.

## Maturity labels
- **Scaffold**: portable structure, generic guidance, not yet validated.
- **Curated**: practical methodology, examples and acceptance checks, reviewed in repository.
- **Verified**: demonstrated in a named agent/client version and recorded with reproducible test evidence.

Do not call a skill Verified based on Markdown checks or unit tests of file copying.

## First curated candidates
- `rag-evaluation`
- `prompt-injection-defense`
- `docker-hardening`
- `security-review`
- `agent-evaluation`

These are documentation-level curated drafts. Runtime integration testing and specialist review are still required.

## Review template
```text
Skill:
Reviewer:
Date:
Agent/version:
Fixture:
Expected:
Observed:
Negative case:
Risks:
Decision: accept / revise / reject
```
