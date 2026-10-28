---
name: error-handling-review
description: Review how code detects, propagates, reports and recovers from errors — exceptions, retries, timeouts, partial failure and user-facing messages. Use when reviewing service code, integrations, background jobs or after incidents caused by swallowed or misleading errors.
license: MIT
---

# Error Handling Review

## Goal
Failures are visible, attributable and handled at the right layer; the system degrades predictably instead of corrupting data or hiding problems.

## Inputs
- Code under review and its callers, logging and metrics conventions, retry and timeout configuration.
- Known failure modes of dependencies (network, database, third-party APIs, file system).

## Review checklist
1. **No silent swallowing.** Flag broad `catch`/`except` blocks that log nothing, return defaults or continue. Each catch either handles a specific error meaningfully or re-raises with context.
2. **Context preserved.** Wrapped errors keep the cause (`raise … from err`, `%w`, `cause`); messages include identifiers (order ID), not secrets or personal data.
3. **Right layer.** Low-level code reports; the boundary (HTTP handler, job runner) decides the user response, the retry and the alert.
4. **Timeouts everywhere.** Every network or IPC call has a timeout shorter than the caller's; there are no unbounded waits.
5. **Retries are safe.** Only idempotent operations or those with idempotency keys; exponential backoff with jitter; a maximum number of attempts; no retry on validation or authorization errors.
6. **Partial failure.** Multi-step operations use transactions, compensation or an outbox; consider what state remains if the process dies between steps.
7. **Resource cleanup.** Files, locks, connections and temporary data are released on error paths (`finally`, `with`, `defer`).
8. **User-facing errors.** Clear, actionable, without stack traces or internal hostnames; a stable error code for support.
9. **Observability.** Errors are logged once (not at every layer), with severity, a correlation ID and a metric suitable for alerting.

## Example fixture
```python
def charge(order):
    try:
        gateway.charge(order.total)
    except Exception:
        pass                     # swallowed: order shipped without payment
    order.mark_paid()
```
Expected findings: broad exception swallowed, state updated after failure, no timeout or idempotency key, no log or metric.

## Acceptance checks
- Every finding names the failure scenario and its consequence (data loss, duplicate charge, silent outage).
- Recommendations specify which errors to catch, where, and what the caller observes.
- At least one negative test is proposed per critical path (dependency timeout, partial failure).

## Output
Findings ordered by impact, a patch suggestion, and proposed failure-injection tests.

## Safety
Do not test failure handling by breaking shared or production dependencies; use fakes, fault injection in disposable environments, or recorded responses.
