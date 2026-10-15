---
name: accessibility-review
description: Review accessibility with observable evidence with reproducible evidence and actionable recommendations.
license: MIT
---

# Accessibility Review

## Purpose
Review accessibility with observable evidence. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Inspect semantic structure, accessible names and keyboard focus.
2. Check contrast, text scaling and reduced motion.
3. Verify forms and error announcements.
4. Test keyboard and screen reader when available.
5. Map findings to relevant WCAG criteria.
6. Distinguish static checks from runtime observations.

## Example judgment
A clickable div without keyboard interaction is not equivalent to a button.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
