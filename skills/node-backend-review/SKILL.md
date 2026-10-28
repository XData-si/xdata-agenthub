---
name: node-backend-review
description: Review Node.js backends (Express, Fastify, NestJS) for security and reliability — input validation, authentication middleware, async error handling, event-loop blocking, dependency risk, and secure HTTP defaults. Use when reviewing or hardening a Node.js API, or when it crashes on unhandled rejections or stalls under load.
license: MIT
---

# Node.js Backend Review

## Goal
A Node.js service that validates every input, never crashes on unhandled promises, keeps the event loop responsive and ships with secure defaults.

## Inputs
- Node.js version (an active LTS line), framework, `package.json` and lockfile, deployment model (container, serverless), TypeScript configuration.

## Review checklist
1. **Validation**: schema validation for body, query and params (zod, ajv, Fastify schemas, class-validator); reject unknown fields; limit body size.
2. **Authentication and authorization**: middleware applied to routes by default, with explicit public routes; object-level checks in handlers; session cookies `HttpOnly`, `Secure`, `SameSite`.
3. **Async errors**: every async route handler's errors reach the error middleware (Express 5 or a wrapper); `unhandledRejection` and `uncaughtException` log and exit so the supervisor restarts the process — never continue in an unknown state.
4. **Event loop**: no synchronous file system or crypto calls on request paths; CPU-heavy work in worker threads or a queue; monitor event-loop delay (`perf_hooks.monitorEventLoopDelay`).
5. **Injection and prototype pollution**: parameterized queries; no `eval`/`Function` on input; avoid merging untrusted objects into prototypes (`Object.create(null)`, validated schemas); safe regular expressions (ReDoS).
6. **HTTP defaults**: security headers (`helmet` or framework equivalent), rate limiting on login and expensive routes, trust proxy configured correctly, timeouts on outbound requests (`AbortSignal.timeout`).
7. **Dependencies**: `npm audit` or equivalent in CI, lockfile committed, `npm ci` in builds, postinstall scripts reviewed for new dependencies.
8. **Operations**: graceful shutdown on `SIGTERM` (stop accepting, finish in-flight requests, close pools); structured logs without secrets.

## Example fixture
```js
app.post('/login', async (req, res) => {
  const user = await db.query(`SELECT * FROM users WHERE email='${req.body.email}'`);
  if (bcrypt.compareSync(req.body.password, user.hash)) res.json({ token: sign(user) });
});
```
Expected findings: SQL injection, no validation, synchronous bcrypt blocks the event loop, missing user crashes on `user.hash`, async error not handled, no rate limit.

## Acceptance checks
- Tests cover invalid input (400), unauthorized access (401/403) and a dependency failure (5xx without stack trace).
- No synchronous blocking calls on request paths (search results attached).
- Negative case: a login brute-force test hits the rate limit.

## Output
Findings, patches, test additions and tool results.

## Safety
Run load and security tests only against non-production environments you are authorized to test. Do not log request bodies that may contain credentials. Services that process personal data must also follow GDPR: minimal data, defined retention, and support for access and erasure requests (see `gdpr-dsar-handling`).
