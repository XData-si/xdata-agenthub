---
name: logging-standards
description: Define logging standards for applications and services — structured JSON logs, levels, correlation IDs, what to log for security and audit, redaction of secrets and personal data, retention and log pipeline reliability. Use when designing logging for a new service, cleaning up noisy or leaky logs, or preparing for security monitoring and GDPR compliance.
license: MIT
---

# Logging Standards

## Goal
Logs that are useful for debugging and security investigations, cheap enough to keep, and free of secrets and unnecessary personal data.

## Inputs
- Current log samples, logging libraries, log pipeline and storage, retention requirements, security monitoring needs, data protection requirements.

## Procedure
1. **Structure**: JSON lines with consistent fields — `timestamp` (UTC, ISO 8601), `level`, `service`, `version`, `environment`, `message`, `trace_id`/`request_id`, plus event-specific fields.
2. **Levels**: ERROR for failures needing attention, WARN for degraded but handled conditions, INFO for business and lifecycle events, DEBUG off in production by default. No stack traces at INFO.
3. **Correlation**: propagate request and trace IDs across services and queues (W3C Trace Context); include them in every log line and error response.
4. **Security and audit events**: authentication success and failure, authorization denials, privilege changes, administrative actions, data exports, configuration changes — with actor, target and outcome.
5. **Never log**: passwords, tokens, API keys, session cookies, full card numbers, private keys; avoid full request bodies. Add a redaction layer (field allowlist, pattern masking) and tests.
6. **Personal data**: log identifiers rather than contact details where possible; pseudonymise IP addresses if not needed in full; define retention per log type (GDPR storage limitation).
7. **Volume and cost**: sample high-volume debug logs; rate-limit repetitive errors; measure bytes per request.
8. **Pipeline reliability**: buffering and backpressure; alerts when log shipping stops; clock synchronisation on hosts.

## Example fixture
```text
INFO  User login ok email=ana@example.com password=Summer2024! ip=203.0.113.7 headers={"Authorization":"Bearer eyJ..."}
```
Expected findings: password and bearer token logged, unstructured line, contact data where a user ID would do.

## Acceptance checks
- A log schema is documented and validated in tests for at least one service.
- Redaction tests prove that tokens, passwords and card numbers are masked.
- Negative case: forcing an authentication failure produces a security event with actor, outcome and request ID, and no credential.

## Output
Logging standard document, library configuration, redaction tests, retention table.

## Safety
Searching production logs requires authorization; exports of logs with personal data must follow data protection rules. If secrets are found in existing logs, report them for rotation and restrict access to those logs.
