---
name: mcp-server-development
description: Design and build a Model Context Protocol (MCP) server with well-scoped tools, input validation, authentication, safe defaults and tests. Use when exposing an internal API, database or service to AI agents through MCP, or when extending an existing MCP server.
license: MIT
---

# MCP Server Development

## Goal
An MCP server that gives agents exactly the capabilities they need, with clear tool contracts, enforced permissions and observable behaviour. For reviewing an existing server, use `mcp-review`.

## Inputs
- Use cases: which questions or actions agents need, and who the end users are.
- The backing system's API, data sensitivity and existing authorization model.
- Target clients and transport: local stdio, or remote Streamable HTTP behind a gateway.

## Procedure
1. **Design tools from tasks, not endpoints.** Fewer, purposeful tools (`search_orders`, `get_order`) beat a one-to-one API mirror. Separate read-only tools from tools with side effects.
2. **Write tool contracts:** a name in verb_noun form, a description that says *when* to use the tool and what it returns, a JSON Schema for inputs with types, enums, bounds and required fields; return concise, structured output with stable identifiers.
3. **Read-only by default.** Write or destructive tools are opt-in by configuration, mark side effects in the description and annotations, and support confirmation or dry-run parameters.
4. **Authentication and authorization.** Remote servers authenticate clients (OAuth 2.1 per the MCP authorization specification, or a gateway with API keys); every call is authorised as the end user or a scoped service identity — never a shared admin token behind the scenes. Tenant and object-level checks are in the server code.
5. **Validate and bound inputs:** schema validation, maximum lengths, pagination with limits, timeouts on backend calls, rate limits per client.
6. **Treat outputs as untrusted for the agent:** data returned may contain text that looks like instructions; do not include secrets or internal URLs; truncate large payloads with a continuation token.
7. **Errors** return actionable messages ("order not found", "limit must be ≤ 100") without stack traces.
8. **Observability:** log tool name, caller identity, duration and result status with a request ID; never log tokens or full sensitive payloads.
9. **Test:** unit tests per tool including authorization-denied and invalid-input cases; protocol-level tests with the MCP Inspector or SDK client; a contract test listing tools and schemas so changes are visible in review.
10. **Package and document:** pinned dependencies, container image or package, a configuration reference, and examples for the main clients.

## Example fixture
```json
{"name":"get_invoice","description":"Fetch one invoice the current user may access. Use after search_invoices; returns totals and status, not line items.",
 "inputSchema":{"type":"object","properties":{"invoice_id":{"type":"string","pattern":"^INV-[0-9]{6}$"}},"required":["invoice_id"],"additionalProperties":false}}
```
Negative tests: an invoice of another tenant → `not found` (no existence leak); a malformed ID → validation error; no token → 401.

## Acceptance checks
- Each tool has a schema with `additionalProperties: false` and bounded inputs.
- Authorization tests prove that a user cannot read or modify another tenant's or user's objects.
- Tools with side effects are disabled by default or need explicit confirmation.
- The tool list and schemas are covered by a snapshot or contract test.

## Output
Server code, tool reference, configuration documentation, tests and a short threat model (see `threat-modeling`).

## Safety
Do not expose shell execution, arbitrary SQL or file-system access as generic tools. Do not publish servers that embed credentials. Servers that expose personal data must apply GDPR data protection by design: minimal fields in tool results, access logging without payloads, retention limits and support for erasure.
