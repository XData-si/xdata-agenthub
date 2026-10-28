---
name: architecture-decision
description: Record architectural decisions as ADRs with context, options, trade-offs and consequences. Use when choosing between technologies, patterns or designs that are expensive to reverse.
license: MIT
---

# Architecture Decision

## Purpose
Document architectural decisions with trade-offs. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Capture context and constraints.
2. Compare viable alternatives and operational cost.
3. Consider security, resilience, data residency and vendor lock-in.
4. State decision and rejected options.
5. Identify consequences and migration path.
6. Define measurable revisit criteria.

## Example judgment
A managed service decision must include operational savings and portability costs.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
