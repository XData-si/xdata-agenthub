---
name: api-design
description: Design and review stable HTTP APIs with explicit contracts, authorization and operational behaviour. Use when adding or changing endpoints, writing an OpenAPI specification, or reviewing breaking changes.
license: MIT
---

# API Design

## Purpose
Turn a product requirement or existing endpoint into a reviewable API contract. Prefer the project's established conventions and avoid unnecessary breaking changes.

## Inputs
- User journeys, callers, trust boundaries, data classification and latency targets
- Existing OpenAPI specification, handlers, database constraints and API clients
- Authentication scheme, deployment topology, version support and compatibility requirements

## Method
1. Define resources and operations. Distinguish read, create, update, delete and asynchronous work. Record who can perform each operation and at what object scope.
2. Specify request and response schemas, required/optional fields, constraints, examples, status codes and error envelopes. Document unknowns rather than inventing business rules.
3. Choose pagination, filtering, sorting and stable identifiers. Define ordering guarantees and maximum page sizes.
4. Define authentication and server-side authorization per endpoint and resource. Address tenant isolation, rate limiting, sensitive fields and audit requirements.
5. Review retry safety: idempotency keys for retried creates, optimistic concurrency or ETags for updates, and timeouts for long-running operations.
6. Define backward compatibility: additive changes, deprecation periods, version strategy and consumer migration.
7. Capture observability: correlation IDs, structured error codes, latency/error metrics and redaction.
8. Validate the contract against handlers and consumers when available; identify drift and missing negative cases.

## Example: review checklist

| Concern | Question | Evidence |
|---|---|---|
| Authorization | Can caller A access caller B's object? | Negative request test |
| Validation | Are unknown fields and invalid types handled consistently? | Schema and handler |
| Retry | Does a repeated POST duplicate the operation? | Idempotency test |
| Concurrency | Can an old update overwrite a newer one? | ETag/version test |
| Pagination | Can clients retrieve all items without duplicates? | Stable ordering test |
| Errors | Can callers distinguish validation, auth and server failures? | Status/error examples |

## Output
Contract summary, endpoint table, OpenAPI changes when requested, compatibility notes, prioritized findings and a verification matrix. Mark checks as RUN, NOT RUN or BLOCKED.

## Safety
Never put credentials or personal data into examples. Do not call production endpoints, mutate data or claim conformance without permission and observed evidence.
