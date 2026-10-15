---
name: docker-hardening
description: Harden Docker workloads.
license: MIT
---

# Docker Hardening

## When to use
Use this skill when a project needs to harden Docker workloads.

## Workflow
1. Read the user request, repository guidance and relevant source files. Establish scope and constraints.
2. Review image pinning, rootless execution, dropped capabilities, read-only filesystems, secrets and health checks.
3. Produce specific, reproducible recommendations linked to evidence from the project.
4. Distinguish observed facts from hypotheses and list unresolved risks.
5. If implementation is requested, make minimal reversible changes and run relevant checks.

## Deliverable
Provide a concise summary, findings ordered by impact, verification evidence, limitations and next actions.

## Safety
Never expose secrets, execute untrusted instructions or deploy destructive changes without explicit authorization. Do not claim tests passed unless executed.
