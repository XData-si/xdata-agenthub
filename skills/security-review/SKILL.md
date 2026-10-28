---
name: security-review
description: Perform an evidence-based security review of code or a design — injection, authentication, authorization, data exposure and unsafe defaults. Use when reviewing security-sensitive changes or before exposing a service.
license: MIT
---

# Security Review

## Goal
Find exploitable risks with evidence, prioritize fixes and avoid overstating security guarantees.

## Workflow
1. Identify assets, actors, entry points, deployment assumptions and trust boundaries.
2. Inspect authentication, authorization, session handling, data validation and error paths.
3. Trace untrusted input into SQL, shell commands, templates, files, network requests and LLM tools.
4. Check SSRF, path traversal, unsafe deserialization, secret leakage, dependency provenance and supply-chain permissions.
5. For each finding record: affected path/line, preconditions, plausible impact, reproduction in a safe test, severity rationale and remediation.
6. Propose least-disruptive changes and verify with positive and negative tests.
7. Separate confirmed vulnerabilities from hypotheses requiring further investigation.

## Example finding format
```text
ID: SEC-001
Title: Missing object-level authorization
Evidence: API handler accepts object_id without verifying ownership
Impact: Cross-account data disclosure
Reproduction: Two dummy accounts in a local fixture
Remediation: Enforce server-side authorization on each object
Verification: Unauthorized request returns 403; authorized request succeeds
Status: Needs verification
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| This is internal, so it doesn't need authentication. | Internal networks get breached and misconfigured. Require authentication and authorization. |
| The input comes from our own frontend. | Attackers call the API directly. Validate on the server. |
| It's only a hypothetical finding. | Then label it a hypothesis with the test that would confirm it; do not silently drop it. |

## Acceptance checks
- No real customer data is accessed during testing.
- Critical findings include concrete mitigation and verification criteria.
- Findings do not claim exploitability without supporting evidence.
- Security testing remains within explicitly authorized scope.

## Output
Threat model summary, prioritized findings, patch plan, verification evidence and residual risks.
