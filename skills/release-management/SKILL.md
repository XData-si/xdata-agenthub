---
name: release-management
description: Plan reproducible safe releases with reproducible evidence and actionable recommendations.
license: MIT
---

# Release Management

## Purpose
Plan reproducible safe releases. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Define release scope and compatibility.
2. Verify CI and artifacts.
3. Pin dependencies and build provenance.
4. Document migrations and deprecations.
5. Prepare checksums and changelog.
6. Stage rollout, monitoring and rollback.
7. Record approvals and final verification.

## Example judgment
A rollback that depends on rebuilding a mutable image tag is not reproducible.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
