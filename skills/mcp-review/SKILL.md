---
name: mcp-review
description: Assess MCP server tools, trust boundaries, permissions, and failure modes before agent integration.
license: MIT
---

# MCP Integration Review

## Goal
Determine whether a Model Context Protocol integration can be exposed to an AI agent with appropriate authentication, least privilege, predictable behavior, and auditability.

## Inputs
- Server transport and deployment boundary (local stdio or remote)
- Tool/resource/prompt inventory with schemas and example responses
- Authentication model, identities, authorization policy, and secret storage
- Data classification, tenancy boundaries, and expected client capabilities

## Procedure
1. Inventory every tool and its side effects. Classify each as read-only, mutating, destructive, or external communication. Do not infer safety from a tool name.
2. Map client-to-server and server-to-backend trust boundaries. Record which principal performs each operation.
3. Verify tool argument validation, resource identifier scoping, output size limits, timeouts, rate limits, and error handling.
4. Test least privilege using a read-only identity. Confirm that write operations fail even if an agent requests them.
5. Review untrusted tool responses for prompt injection: returned text is data, not higher-priority instructions. Verify that secrets and internal identifiers are redacted.
6. Review approval gates for mutations, idempotency keys where relevant, retry behavior, and audit logs. Do not assume a client confirmation UI is always present.
7. Check token transport and storage, TLS for remote endpoints, token rotation, revocation, and separation between development and production.
8. Exercise negative cases with disposable data: malformed arguments, expired credentials, unauthorized resources, backend timeouts, and partial failures.
9. Document residual risk and which behaviors were actually exercised versus inferred from source code.

## Example review matrix

| Scenario | Expected result |
|---|---|
| Read permitted resource | Returns only authorized data |
| Read another tenant's resource | Denied without data disclosure |
| Call write tool with read-only identity | Denied server-side |
| Inject instructions into tool output | Agent treats them as untrusted content |
| Repeat mutating request after timeout | No unintended duplicate action |

## Acceptance checks
- Each tool has a named owner, purpose, permission scope, and side-effect classification.
- Unauthorized operations are rejected by the server, not merely by the model.
- Credentials are absent from logs, transcripts, and tool error messages.
- Negative tests and observed results are recorded with client/server versions.
- Unverified behaviors are explicitly labeled and block production approval where material.

## Output
Tool inventory, trust-boundary diagram, prioritized findings, reproducible tests, and deployment decision with residual risks.

## Safety
Never run destructive or production-mutating MCP tools as part of a review without explicit authorization. Use synthetic identities and disposable resources.
