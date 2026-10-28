---
name: threat-modeling
description: Produce a lightweight, evidence-based threat model — data flows, trust boundaries, STRIDE threats, risk ranking and mitigations — for a system or feature. Use when designing a new service, exposing an API, adding an AI agent or tool integration, or before a security review.
license: MIT
---

# Threat Modeling

## Goal
Answer four questions with artefacts the team can maintain: *What are we building? What can go wrong? What are we doing about it? Did we do a good job?*

## Inputs
- Architecture description or diagram, deployment environment, data classification.
- Actors (users, administrators, services, AI agents), external dependencies, compliance requirements.

## Procedure
1. **Scope.** One feature or service per model. Write assumptions explicitly (for example "the cloud provider is trusted").
2. **Data flow diagram.** External entities, processes, data stores and flows, with **trust boundaries** where privilege or control changes (internet → API, service → database, agent → tool). Text or Mermaid is fine.
3. **Enumerate threats per element and boundary with STRIDE** (see [`references/stride.md`](references/stride.md)). For AI features add prompt injection, tool misuse, data exfiltration through model output and over-broad agent permissions.
4. **Rate risk** with a simple, consistent scale: likelihood × impact (1–3 each), or the organisation's standard. Record the reasoning, not just the number.
5. **Decide per threat:** mitigate (control and owner), accept (who accepted it and why), transfer, or eliminate (remove the feature or data).
6. **Map mitigations to verification:** a test, configuration check, monitoring alert or review step.
7. **Revisit** when architecture, data classification or exposure changes; keep the model next to the code.

## Example fixture
```text
Flow: Browser --(HTTPS, session cookie)--> API --(SQL)--> Postgres
Boundary: internet | API
T1 Spoofing: stolen session cookie reused → mitigation: HttpOnly+Secure+SameSite, short idle timeout, re-auth for sensitive actions
T2 Tampering: order total modified client-side → mitigation: server recalculates totals; test rejects mismatched total
T3 Info disclosure: verbose errors leak stack traces → mitigation: generic error responses; test asserts no trace in 500 body
```

## Acceptance checks
- Every trust boundary has at least one threat considered for each relevant STRIDE category, or a written reason why it does not apply.
- Each high-risk threat has an owner and a verification method.
- Accepted risks name who accepted them and when.
- Assumptions are listed and reviewable.

## Output
Diagram, threat table (ID, element, STRIDE category, scenario, likelihood, impact, decision, mitigation, verification, owner) and open questions.

## Safety
A threat model is analysis, not authorization to test. Do not perform active exploitation of systems without an explicit, scoped authorization.
