---
name: gitlab-ci
description: Review GitLab CI/CD pipelines for security and reproducibility — job permissions, protected variables, untrusted merge-request pipelines, pinned images and deploy approvals. Use when adding or changing .gitlab-ci.yml.
license: MIT
---

# GitLab CI

## Goal
Review secure and reproducible GitLab CI pipelines. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Inventory stages, includes, runners and protected branches.
2. Validate job permissions and masked/protected variables.
3. Review untrusted merge-request pipelines, artifact retention and cache poisoning.
4. Pin container images and dependency versions.
5. Separate build from deployment approvals.
6. Inspect retry, timeout and rollback behavior.
7. Check that secrets are not printed.

## Illustrative review case
A fork merge request must not receive protected deployment credentials through an untrusted job.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
