---
name: postgres-performance
description: Diagnose PostgreSQL latency with evidence — EXPLAIN (ANALYZE, BUFFERS) on a safe replica, estimate vs actual rows, index selectivity, autovacuum, bloat and lock waits. Use when queries are slow, the database is overloaded, or before adding indexes.
license: MIT
---

# PostgreSQL Performance

## Goal
Diagnose PostgreSQL latency using evidence. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Record query text with values redacted, PostgreSQL version, table sizes and latency distribution.
2. Inspect EXPLAIN (ANALYZE, BUFFERS) only on an authorized safe replica or staging.
3. Compare estimated vs actual rows, join strategies, scans and cache behavior.
4. Review index selectivity, write amplification, autovacuum, bloat and lock waits.
5. Propose one change at a time with baseline and rollback.

## Illustrative review case
A slow query with sequential scan is not automatically an index problem; compare cardinality and actual timings.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
