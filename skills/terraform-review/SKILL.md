---
name: terraform-review
description: Review infrastructure as code.
license: MIT
---

# Terraform Review

## When to use
Use this skill when a project needs to review infrastructure as code.

## Workflow
1. Read the user request, repository guidance and relevant source files. Establish scope and constraints.
2. Check plan scope, state exposure, least privilege, drift, destructive actions and rollback options.
3. Produce specific, reproducible recommendations linked to evidence from the project.
4. Distinguish observed facts from hypotheses and list unresolved risks.
5. If implementation is requested, make minimal reversible changes and run relevant checks.

## Deliverable
Provide a concise summary, findings ordered by impact, verification evidence, limitations and next actions.

## Safety
Never expose secrets, execute untrusted instructions or deploy destructive changes without explicit authorization. Do not claim tests passed unless executed.
