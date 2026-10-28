---
name: owasp-asvs-review
description: Assess a web application or API against the OWASP Application Security Verification Standard (ASVS) — choose the level, map requirements to evidence, test key controls and report gaps. Use when security requirements must be verifiable (procurement, customers, certification preparation) or as a structured complement to code review and penetration tests.
license: MIT
---

# OWASP ASVS Review

## Goal
Turn "is the application secure?" into a checklist of verifiable requirements with evidence, using the OWASP ASVS as the reference.

## Inputs
- Application description and architecture, data sensitivity, authentication and session design, existing tests and documentation, the ASVS version the organisation uses (record it — requirement numbering changes between versions).

## Procedure
1. **Pick the level**: Level 1 (baseline, all applications), Level 2 (applications handling sensitive data — most business systems), Level 3 (high-value or critical systems).
2. **Scope**: components, interfaces (web, API, mobile backends), and out-of-scope items with reasons.
3. **Map requirements to evidence** chapter by chapter (for example architecture, authentication, session management, access control, validation and encoding, cryptography, error handling and logging, data protection, communication, configuration, API and web service). Evidence types: code reference, configuration, automated test, manual test result, design document.
4. **Test critical controls** directly: access control on object level, session handling, password and MFA flows, input handling for injection, security headers, error responses, logging of security events.
5. **Record status** per requirement: pass, fail, partial, not applicable (with reason), not verified.
6. **Prioritise gaps** by risk and effort; link to fixes and owners.
7. **Re-verify** after fixes; keep the matrix as living documentation tied to releases.

## Example fixture
```text
Requirement (access control): "Verify that the application enforces access control at a trusted service layer for every object request."
Evidence: integration test test_invoice_idor (user A cannot GET user B's invoice → 404). Status: pass.
Requirement (logging): "Verify that authentication failures are logged." Evidence: none found. Status: fail → ticket SEC-142.
```

## Acceptance checks
- The chosen ASVS version and level are stated; every in-scope requirement has a status.
- "Pass" statuses have concrete evidence; "not verified" is used instead of guessing.
- Negative case: at least the access-control and authentication requirements were tested with attempts that should fail.

## Output
Requirement-to-evidence matrix, gap list with priorities, test cases added.

## Safety
Test only systems in scope with written authorization. ASVS results are not a certification; do not present them as one.
