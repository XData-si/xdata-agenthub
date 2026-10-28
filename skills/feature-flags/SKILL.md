---
name: feature-flags
description: Use feature flags safely for progressive delivery, experiments and kill switches — flag types, targeting, defaults when the flag service fails, ownership, audit and removal of stale flags. Use when introducing a flag system, rolling out risky changes gradually, or cleaning up flag debt.
license: MIT
---

# Feature Flags

## Goal
Decouple deploy from release so risky changes reach users gradually and can be switched off in seconds — without letting flags become permanent, untested complexity.

## Inputs
- Flag tool (self-hosted or SaaS, for example an open-source flag service), environments, user segments, compliance requirements for audit.

## Procedure
1. **Classify each flag**: release (temporary), experiment (temporary, with a metric), ops kill switch (long-lived), permission/entitlement (long-lived, belongs in authorization). Record type, owner and expiry date at creation.
2. **Safe defaults**: the code path when the flag service is unreachable is defined and tested — usually the old, known-good behaviour; evaluation is local with cached rules, not a network call per request.
3. **Progressive rollout**: internal users → small percentage (1–5 %) → wider, with sticky bucketing by user ID; watch error rate, latency and business metrics at each step (see `slo-error-budgets`).
4. **Kill switches** for features with external dependencies or high cost (for example LLM calls); tested in production-like environments.
5. **Testing**: test both states of each active flag in CI; avoid combinatorial explosion by limiting concurrent flags in one code path.
6. **Security**: flags are not a security boundary — a hidden feature still needs authorization; client-side flag payloads must not leak unreleased data or other users' targeting.
7. **Audit**: who changed which flag when; changes to production flags reviewed like deploys for high-risk features.
8. **Removal**: delete the flag and dead code when rollout reaches 100 % and is stable; enforce expiry with a report of stale flags.

## Example fixture
```text
Flag new-checkout: created 2025-03-01, at 100 % since 2025-04-10, still referenced in 14 files, owner left the company.
```
Expected action: assign an owner, remove the flag and old path, test, and deploy.

## Acceptance checks
- Every flag has type, owner and expiry; no release flag older than its expiry without justification.
- Negative case: with the flag service unreachable, the application serves the documented default (test).
- Rollout steps have recorded metrics and a rollback trigger.

## Output
Flag inventory, rollout plan, tests for both states, cleanup tickets.

## Safety
Changing production flags is a production change: follow the same approval rules as deploys for high-risk features. Do not use flags to bypass authorization or review.
