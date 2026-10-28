---
name: nis2-readiness
description: Prepare an engineering-level NIS2 readiness assessment — scope and entity type, management accountability, the cybersecurity risk-management measures, supply-chain security, and the 24-hour / 72-hour / one-month incident reporting process. Use when an organisation operates in a NIS2 sector in the EU, supplies such organisations, or is asked by customers or regulators about NIS2. Not legal advice.
license: MIT
---

# NIS2 Readiness

## Goal
Show which NIS2 obligations apply, what evidence already exists, and the concrete gaps, so management can decide and engineering can execute. NIS2 is Directive (EU) 2022/2555; obligations come from **national transposition laws** (for example, in Slovenia the Information Security Act, ZInfV-1), which must be checked for local details.

## Inputs
- Sector and services offered, legal entity size (employees, turnover, balance sheet), EU countries of operation.
- Existing security policies, risk register, incident response plan, supplier list, ISO/IEC 27001 or similar certifications.

## Procedure
1. **Scope**: check whether the services fall into the sectors of Annex I (high criticality, e.g. energy, transport, banking, health, digital infrastructure, ICT service management, public administration) or Annex II (e.g. postal, waste, manufacturing of certain products, digital providers). Generally medium and large entities are in scope; some (for example DNS service providers, TLD registries, qualified trust service providers) are in scope regardless of size. Determine **essential** or **important** entity status under the national law, and whether registration with the national authority is required.
2. **Management accountability** (Article 20): management bodies approve the risk-management measures, oversee them, can be held liable, and must attend training. Record approvals and training dates.
3. **Risk-management measures** (Article 21) — assess each with evidence: risk analysis and information-system security policies; incident handling; business continuity (backups, disaster recovery, crisis management); supply-chain security; security in acquisition, development and maintenance, including vulnerability handling and disclosure; effectiveness assessment; basic cyber hygiene and training; cryptography and encryption; human-resources security, access control and asset management; multi-factor or continuous authentication and secured communications.
4. **Incident reporting** (Article 23) for significant incidents: early warning within **24 hours** of becoming aware, incident notification within **72 hours**, final report within **one month**, plus intermediate reports on request. Build the process: who decides significance, who reports to the CSIRT or authority, templates, and a test.
5. **Supply chain**: classify suppliers by criticality, contractual security requirements, evidence collection (certifications, SBOMs where relevant), and exit plans.
6. **Gap plan**: for each gap — owner, effort, deadline, and evidence that will close it. Prioritise reporting capability, MFA, backups and asset inventory.
7. **Sanctions awareness**: administrative fines can reach at least EUR 10 million or 2 % of worldwide turnover for essential entities and EUR 7 million or 1.4 % for important entities (national laws may set details); management can be held accountable.

## Example fixture
```text
Entity: managed service provider, 120 employees, operating in SI and HR → Annex I "ICT service management (B2B)", medium size → in scope (verify national classification).
Gaps: no documented significance criteria for incidents; MFA missing on 3 admin portals; supplier list without criticality; management not trained.
First 30 days: reporting procedure + tabletop test; MFA everywhere; management training session.
```

## Acceptance checks
- Scope decision cites the sector, size test and national law consulted, or is marked `NEEDS LEGAL CONFIRMATION`.
- Each Article 21 measure has status (implemented / partial / missing) and evidence.
- The 24 h / 72 h / one-month reporting flow has named owners and has been exercised at least once (tabletop counts).
- Negative case: a policy document without evidence of implementation is marked partial, not implemented.

## Output
Scope memo, measure-by-measure evidence matrix, incident reporting runbook, supplier criticality list and a prioritised gap plan.

## Safety
Do not perform intrusive tests to "prove" measures without authorization. Treat incident details as confidential. The assessment is not legal advice; confirm scope and obligations with counsel and the national authority's guidance.
