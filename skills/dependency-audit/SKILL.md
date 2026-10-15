---
name: dependency-audit
description: Audit dependency and supply-chain risk with reproducible evidence and actionable recommendations.
license: MIT
---

# Dependency Audit

## Purpose
Audit dependency and supply-chain risk. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Inventory direct and transitive dependencies and lockfiles.
2. Compare installed versions to relevant advisories.
3. Distinguish reachable production code from test-only packages.
4. Verify provenance, integrity and license constraints.
5. Propose minimal updates with regression checks.
6. Document accepted exceptions with owners and expiration.

## Example judgment
A vulnerable transitive dependency is not necessarily exploitable in this deployment; record the affected code path.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
