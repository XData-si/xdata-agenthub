---
name: performance-profiling
description: Diagnose performance problems with controlled, reproducible measurements and profilers before optimising. Use when something is slow, CPU or memory usage is high, or before and after optimisation work.
license: MIT
---

# Performance Profiling

## Purpose
Diagnose performance with controlled measurements. Follow project conventions and explicitly state assumptions.

## Inputs
Relevant source and configuration, desired behavior, supported versions, operating environment, ownership and constraints.

## Procedure
1. Define workload and SLO.
2. Capture baseline P50/P95/P99 and hardware.
3. Profile CPU, memory, I/O and dependency waits.
4. Control warmup, caching and concurrency.
5. Optimize measured bottleneck.
6. Compare results and regression risk.

## Example judgment
A single local timing is not proof of production latency improvement.

## Required output
Summarize scope, prioritized findings, affected artifacts, observed evidence, recommendations, verification steps and residual risks. Mark tests as PASS, FAIL, NOT RUN or BLOCKED; never infer a passing test from a proposed command.

## Acceptance checks
- Findings cite a concrete artifact or a clearly labeled assumption.
- At least one negative or boundary case is covered when relevant.
- Recommendations consider compatibility and operational cost.
- Unverified behavior is not represented as an observed fact.

## Safety
Read-only by default. Do not expose credentials, execute untrusted code, access unrelated data or make production changes without explicit authorization. Prefer disposable fixtures.
