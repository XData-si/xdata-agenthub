---
name: typescript-testing
description: Design reproducible TypeScript tests for runtime behaviour, types and asynchronous failure paths (Vitest, Jest or node:test). Use when adding tests to TypeScript or JavaScript code or making them reliable.
license: MIT
---

# TypeScript Testing

## Goal
Create focused regression tests that reveal incorrect behavior, run deterministically and respect the project's existing test framework.

## Inputs
- Expected behavior, reproduction and supported Node/TypeScript versions
- package.json, lockfile, tsconfig, existing test framework and CI commands
- Runtime boundaries (filesystem, HTTP, database, timers, queues) and fixture policy

## Procedure
1. Inspect the project's package manager and test runner (Vitest, Jest, node:test or another existing choice). Do not add a framework by default.
2. Identify observable behavior and type-level contracts separately. Define happy, boundary, malformed, unauthorized and retry cases where applicable.
3. Reproduce the defect with a focused failing test before changing production code; record the failure text and exit status.
4. Isolate time, randomness, HTTP, database and filesystem. Use the runner's supported fake timers and mocks; restore them after each test.
5. Test async success and rejection explicitly. Await promises and verify cleanup to avoid tests that pass before asynchronous work finishes.
6. Cover TypeScript contracts with `tsc --noEmit` or established type tests when relevant. A runtime passing test does not prove type safety.
7. Verify ESM/CJS and path alias behavior in the actual project configuration. Do not assume transpilation matches production.
8. Run focused tests, then the project suite and typecheck. Distinguish observed passes, expected regression failures, skipped cases and unrun commands.
9. Keep fixtures synthetic and avoid snapshot churn that obscures behavior. Review portability across supported Node versions.

## Example matrix

| Case | Expected result |
|---|---|
| Valid request | Correct return value and side effects |
| Missing required input | Stable validation error |
| Dependency rejects | Rejection propagated or handled as specified |
| Two concurrent calls | No unintended shared-state interference |
| Retry after timeout | No duplicate mutation when idempotency is required |
| Type mismatch | Compiler or type-test failure |

## Output
Test matrix, exact commands, observed results, changes, coverage gaps and remaining risks. Prefer small reproducible tests over broad unverified claims.

## Safety
Use disposable paths and mocked services. Never run destructive integration tests against real services or claim success without executing the command.
