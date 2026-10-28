---
name: frontend-review
description: Review frontend code for correctness and resilience — state and async transitions, forms and validation, untrusted rendering, keyboard and responsive layout, loading and network failures. Use when reviewing UI changes or a new frontend component.
license: MIT
---

# Frontend Review

## Purpose
Review frontend correctness, accessibility and resilience. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Inspect state management and async transitions.
2. Verify forms, validation and error feedback.
3. Review untrusted rendering and navigation.
4. Test keyboard and responsive layouts.
5. Assess loading performance and network failures.
6. Document actual browser coverage.

## Example judgment
A success message shown before server confirmation can misrepresent a failed save.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
