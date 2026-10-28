---
name: sql-review
description: Review SQL for correctness, security and performance — injection, transactions, NULL handling, indexes and query plans. Use when writing or reviewing queries, views or stored procedures.
license: MIT
---

# SQL Review

## Purpose
Review SQL correctness, security and performance. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Identify dialect and schema.
2. Check joins, null semantics and aggregation.
3. Verify parameter binding and transaction boundaries.
4. Inspect pagination and index assumptions.
5. Test edge cases and concurrency.
6. Validate execution plans only in authorized environments.

## Example judgment
A LEFT JOIN with a right-table predicate in WHERE can silently filter unmatched rows.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
