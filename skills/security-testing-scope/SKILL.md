---
name: security-testing-scope
description: Prepare an authorized security test or penetration test engagement — scope, rules of engagement, written authorization, test windows, data handling, communication and stop conditions — and review the resulting report. Use before commissioning or running penetration tests, red-team exercises or bug bounty programs, or when an AI agent is asked to perform security testing.
license: MIT
---

# Security Testing Scope

## Goal
Every security test is authorized, bounded and safe for production and data, and its results are actionable.

## Inputs
- Business objective of the test, systems and their owners, hosting contracts (some providers require notification), data sensitivity, testing team or vendor.

## Procedure
1. **Objective**: what question the test answers (for example "can an external attacker reach customer data?", "is the new API safe to launch?").
2. **Scope**: exact hostnames, IP ranges, applications, APIs, accounts and environments in scope; explicit **out of scope** (third-party SaaS, payment providers, production databases, denial of service, social engineering — unless explicitly included).
3. **Written authorization** from someone with authority over each asset; confirm ownership of IPs and domains; check hosting and cloud provider policies.
4. **Rules of engagement**: allowed techniques, test windows, rate limits, source IPs of testers, test accounts, handling of discovered credentials and personal data, prohibition of data exfiltration beyond proof.
5. **Communication**: points of contact on both sides, emergency stop procedure, immediate reporting of critical findings, how to tell test traffic from a real attack.
6. **Data handling**: minimal access to personal data, encrypted storage of evidence, deletion after the engagement, confidentiality agreement.
7. **Report review**: each finding with reproduction steps, impact, affected assets, risk rating and recommendation; retest after fixes.

## Example fixture
```text
In scope: app.example.com, api.example.com (staging and production read-only), test accounts T1–T4.
Out of scope: payment provider, email gateway, DoS, phishing.
Window: Mon–Thu 09:00–17:00 CET, max 50 requests/s, tester IP 198.51.100.20.
Stop: any sign of production data modification or service degradation → call contact X immediately.
```

## Acceptance checks
- Signed authorization and scope exist before any testing starts.
- Every target tested appears in the scope list (negative case: a finding on an out-of-scope host is reported but not exploited further).
- Critical findings were reported immediately, and retest results are recorded.

## Output
Scope and rules-of-engagement document, authorization record, findings tracker, retest record.

## Safety
Never test systems without written authorization, even if a vulnerability seems obvious. AI agents must refuse active testing that is not covered by a recorded scope and must stop on the stop conditions.
