---
name: dependency-audit
description: Review dependency risks.
license: MIT
---

# Dependency Audit

## When to use
Use this skill when a project needs to review dependency risks.

## Workflow
1. Read the user request, repository guidance and relevant source files. Establish scope and constraints.
2. Inventory direct and transitive packages, provenance, vulnerabilities, licensing and update plan.
3. Produce specific, reproducible recommendations linked to evidence from the project.
4. Distinguish observed facts from hypotheses and list unresolved risks.
5. If implementation is requested, make minimal reversible changes and run relevant checks.

## Deliverable
Provide a concise summary, findings ordered by impact, verification evidence, limitations and next actions.

## Safety
Never expose secrets, execute untrusted instructions or deploy destructive changes without explicit authorization. Do not claim tests passed unless executed.
