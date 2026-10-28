---
name: java-spring-review
description: Review Java and Spring Boot services for security, transactions, persistence performance and operability — Spring Security configuration, input validation, JPA N+1 queries, transaction boundaries, Actuator exposure and dependency risk. Use when reviewing or hardening a Spring Boot application or upgrading Spring versions.
license: MIT
---

# Java and Spring Boot Review

## Goal
A Spring service that authorizes every endpoint, validates input, uses transactions deliberately, queries efficiently and exposes only safe operational endpoints.

## Inputs
- Spring Boot and Java versions, build file (Maven or Gradle), security configuration, entity model, `application.yml` per environment.

## Review checklist
1. **Security configuration**: a `SecurityFilterChain` bean with deny-by-default (`anyRequest().authenticated()`); method security (`@PreAuthorize`) for object-level rules; CSRF enabled for browser sessions, deliberately disabled only for stateless token APIs; CORS restricted to known origins.
2. **Validation**: request DTOs with Bean Validation (`@Valid`, `@NotNull`, `@Size`); entities are not bound directly from requests (mass assignment); error handler returns problem details without stack traces.
3. **Injection**: JPQL/SQL with parameters, never string concatenation; no SpEL evaluation of user input; safe deserialization (no default typing in Jackson for untrusted data).
4. **Transactions**: `@Transactional` on service methods, not controllers; read-only where applicable; self-invocation does not bypass proxies; no remote calls inside long transactions.
5. **Persistence performance**: detect N+1 queries (enable SQL logging or Hibernate statistics in tests); use fetch joins or entity graphs; paginate collections; open-session-in-view disabled (`spring.jpa.open-in-view=false`).
6. **Actuator**: only `health` and `info` exposed publicly; `env`, `heapdump`, `configprops` and `loggers` never public; management port or authentication for the rest.
7. **Configuration and secrets**: secrets from environment or a secret manager, not committed `application.yml`; profiles do not enable debug features in production.
8. **Dependencies and runtime**: dependency check (OWASP Dependency-Check, Snyk or similar); supported Spring Boot line; virtual threads or thread pools sized for the workload.

## Example fixture
```java
@GetMapping("/orders/{id}")
public Order get(@PathVariable Long id) { return repo.findById(id).orElseThrow(); }
```
Expected findings: no ownership check (IDOR), entity returned directly (field exposure), unhandled not-found returns 500.

## Acceptance checks
- Every endpoint has an explicit authorization rule; a test proves a user cannot read another user's resource.
- Actuator exposure verified from outside (negative test: `/actuator/env` returns 401/404).
- N+1 checks on the main list endpoints with query counts recorded.

## Output
Findings with file and line, configuration changes, tests added.

## Safety
Test against non-production data. Never enable sensitive Actuator endpoints publicly, even temporarily, to debug.
