---
name: technical-writing
description: Write executable, maintainable technical documentation for a defined audience — prerequisites, minimal working examples, expected output, troubleshooting and verified commands. Use when writing a guide, tutorial or setup instructions for others to follow.
license: MIT
---

# Technical Writing

## Purpose
Write executable and maintainable documentation. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Define audience and expected outcome.
2. Verify prerequisites and versions.
3. Provide a minimal working example.
4. Separate concepts from task steps.
5. Show expected output and troubleshooting.
6. Verify links and commands.
7. Mark untested procedures explicitly.

## Example judgment
A quick start must create its target directory before invoking commands that require it.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
