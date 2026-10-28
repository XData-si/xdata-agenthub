---
name: dora-readiness
description: Prepare an engineering-level readiness assessment for DORA, the EU Digital Operational Resilience Act (Regulation (EU) 2022/2554) — ICT risk management, major incident classification and reporting, resilience testing, ICT third-party risk and the register of information. Use when you are a financial entity in the EU or an ICT provider serving one, or when preparing for DORA supervision or audits. Not legal advice.
license: MIT
---

# DORA Readiness

## Goal
Map DORA obligations to concrete technical and organisational evidence, and close the gaps that regulators and auditors will ask about first. DORA has applied since **17 January 2025**; detailed rules are in regulatory and implementing technical standards — verify the current versions.

## Inputs
- Entity type (bank, payment institution, insurer, investment firm, crypto-asset service provider, or ICT third-party provider to them), critical or important functions, ICT asset inventory, incident process, ICT contracts, existing frameworks (ISO 27001, NIS2 work).

## Procedure
1. **Scope and proportionality**: entity type and size; whether the simplified ICT risk framework applies; for providers, whether customers are financial entities and which functions you support.
2. **ICT risk management framework**: governance with management body responsibility; asset and dependency inventory linked to business functions; protection and prevention; detection; response and recovery (business continuity and ICT continuity plans with tested RTO/RPO, see `disaster-recovery-drill`); learning and communication.
3. **Incident management and reporting**: classify ICT-related incidents with the regulatory criteria (clients affected, duration, data losses, criticality, economic impact, geographic spread); for major incidents submit initial notification, intermediate report and final report within the deadlines set in the technical standards; voluntary reporting of significant cyber threats.
4. **Digital operational resilience testing**: annual testing programme (vulnerability assessments, scenario tests, performance and recovery tests); threat-led penetration testing (TLPT) at least every three years for entities designated by authorities.
5. **ICT third-party risk**: due diligence before contracting, contractual provisions required by DORA (service levels, locations of data processing, access and audit rights, termination and exit), concentration risk, exit plans for critical services.
6. **Register of information**: maintain the register of all contractual arrangements with ICT providers in the required format, ready for submission.
7. **Information sharing**: participation in threat-intelligence sharing arrangements where useful.

## Example fixture
```text
Payment institution, 80 employees. Gaps: no register of information; cloud contract lacks audit and exit clauses; incident classification thresholds not defined; continuity plan never tested.
First steps: build register from procurement data; renegotiate cloud addendum; define classification matrix and reporting runbook; run a recovery test for the payments service.
```

## Acceptance checks
- Every critical or important function maps to ICT assets, providers, continuity plans and test evidence.
- Major-incident reporting runbook names owners and deadlines from the current technical standards, and was exercised.
- Negative case: a critical ICT contract without exit plan or audit rights is flagged as a gap, even if the provider is certified.

## Output
Scope memo, requirements-to-evidence matrix, register of information draft, incident classification and reporting runbook, testing programme, gap plan.

## Safety
This is not legal advice; confirm scope and obligations with compliance and legal teams and supervisory guidance. Resilience and penetration tests on production require formal authorization (see `security-testing-scope`).
