---
name: api-integration
description: Design reliable third-party API integrations with reproducible evidence and actionable recommendations.
license: MIT
---

# Api Integration

## Purpose
Design reliable third-party API integrations. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Document authentication, scopes, rate limits and data boundaries.
2. Define retries, exponential backoff, timeouts and idempotency.
3. Verify webhook signatures, replay protection and pagination.
4. Test sandbox and mocked failures.
5. Specify observability, credential rotation and graceful degradation.

## Example judgment
A timeout after a mutating request is ambiguous; do not blindly retry without an idempotency strategy.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
