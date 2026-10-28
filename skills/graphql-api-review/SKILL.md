---
name: graphql-api-review
description: Review GraphQL APIs for authorization, abuse resistance and performance — field-level authorization, query depth and cost limits, introspection in production, batching, N+1 resolvers and schema evolution. Use when building or reviewing a GraphQL server or gateway.
license: MIT
---

# GraphQL API Review

## Goal
A GraphQL API where every field enforces authorization, expensive queries are bounded, and resolvers do not multiply database calls.

## Inputs
- Schema (SDL), server implementation, authentication context, persisted-query or gateway setup, clients that depend on the schema.

## Review checklist
1. **Authorization in resolvers or a policy layer**, per object and per field — not only at the HTTP endpoint. Nested paths (`user { orders { customer { email } } }`) must not bypass checks.
2. **Abuse limits**: maximum query depth, cost or complexity analysis, limits on list sizes (`first: Int = 20` with a maximum), alias and batch-operation limits, request timeouts.
3. **Introspection and errors**: introspection disabled or restricted in production unless the API is public by design; error messages without stack traces or SQL; field suggestions disabled for private APIs.
4. **Persisted queries** for first-party clients where possible, rejecting arbitrary queries on high-risk endpoints.
5. **Performance**: DataLoader (or equivalent batching) per request for related objects; avoid per-field database calls in lists; cache keys include the user when results are user-specific.
6. **Inputs**: custom scalars validated (email, URL, dates); mutations idempotent where retried; file uploads limited (and CSRF considered for multipart uploads).
7. **Schema evolution**: additive changes; deprecate fields with `@deprecated(reason:)` before removal; track field usage before deleting; schema diff checks in CI.
8. **Observability**: log operation names (not full variables with personal data), per-resolver timing, rejected-query counts.

## Example fixture
```graphql
query { users(first: 10000) { orders { items { product { reviews { author { email } } } } } } }
```
Expected findings: no maximum on `first`, unbounded depth, author email exposed without a field-level rule, N+1 explosion without batching.

## Acceptance checks
- Tests prove a non-admin cannot read restricted fields through any nesting path.
- Negative case: a query above the depth or cost limit is rejected with a clear error before execution.
- Resolver database call counts for a list query are measured before and after batching.

## Output
Findings, schema and resolver changes, limit configuration, tests.

## Safety
Do not run abusive queries against production; use a staging environment and agreed limits.
