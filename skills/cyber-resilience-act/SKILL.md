---
name: cyber-resilience-act
description: Prepare software and connected products for the EU Cyber Resilience Act (Regulation (EU) 2024/2847) — scope and role, essential security requirements, vulnerability handling, SBOM, support period, conformity assessment, and the reporting of actively exploited vulnerabilities and severe incidents. Use when you sell or distribute software or devices in the EU, maintain open-source software used commercially, or plan secure development and release processes. Not legal advice.
license: MIT
---

# Cyber Resilience Act Readiness

## Goal
Turn CRA obligations into engineering work: secure-by-design development, vulnerability handling and reporting that can actually meet the deadlines, and the documentation a conformity assessment needs.

## Timeline
The CRA entered into force on 10 December 2024. **Reporting obligations apply from 11 September 2026**; most other obligations apply from **11 December 2027**. Verify dates and implementing acts in official sources before relying on them.

## Inputs
- Product list (software, firmware, devices, remote data processing that is part of the product), how each is placed on the market (sold, licensed, bundled, free), and target customers.
- Development and release process, dependency management, existing vulnerability disclosure policy and security update practice.

## Procedure
1. **Scope and role** per product: is it a product with digital elements made available on the EU market in the course of a commercial activity? Are you the **manufacturer**, importer or distributor? Free and open-source software developed outside commercial activity is generally out of scope; organisations that systematically support such software for commercial use may be **open-source stewards** with lighter obligations. Products covered by specific regimes (for example certain medical devices or vehicles) may be excluded — record the reasoning.
2. **Product category**: default products (self-assessment), **important** products (class I or II, for example identity management, password managers, VPNs, firewalls, operating systems — harmonised standards or third-party assessment), or **critical** products. Check the annex lists.
3. **Essential requirements (Annex I, part I)**: risk assessment documented; secure by default configuration; no known exploitable vulnerabilities at release; protection of confidentiality and integrity; data minimisation; access control; availability and resilience; minimised attack surface; logging of security-relevant events; ability to receive security updates, automatically where appropriate, with user opt-out.
4. **Vulnerability handling (Annex I, part II)**: SBOM in a commonly used machine-readable format (at least top-level dependencies); coordinated vulnerability disclosure policy and a contact address; timely security updates free of charge, separate from feature updates where feasible; public advisories after fixes; regular testing.
5. **Support period**: define and publish it; generally at least five years unless the expected use time is shorter. Security updates must be available for the support period.
6. **Reporting** (from 11 September 2026): actively exploited vulnerabilities and severe incidents affecting the product's security must be reported through the single reporting platform to the designated CSIRT and ENISA — early warning within **24 hours**, notification within **72 hours**, and a final report (for vulnerabilities within 14 days after a corrective measure is available; for severe incidents within one month). Inform affected users. Build and test this process now.
7. **Documentation and conformity**: technical documentation, risk assessment, SBOM, test evidence, EU declaration of conformity and CE marking for in-scope products; keep documentation for ten years or the support period, whichever is longer.
8. **Supply chain**: due diligence on third-party and open-source components; track vulnerabilities in dependencies (see `dependency-audit`, `supply-chain-provenance`).

## Example fixture
```text
Product: on-premise backup appliance software, sold to EU businesses → manufacturer, default category (verify it is not on the important list).
Gaps: no SBOM; security fixes shipped only with feature releases; no public CVD policy; no 24 h reporting owner.
Plan: CycloneDX SBOM in CI; security patch branch; security.txt + CVD policy; reporting runbook tested by 11 Sep 2026.
```

## Acceptance checks
- Each product has a scope decision, role and category with reasoning, or `NEEDS LEGAL CONFIRMATION`.
- Every Annex I requirement maps to evidence or a gap with an owner.
- The reporting process names who reports, to whom, within which deadlines, and was exercised once.
- Negative case: a product without a defined support period is marked non-compliant, even if it is actively maintained.

## Output
Product register with scope and category, requirements-to-evidence matrix, SBOM and CVD setup, reporting runbook, and documentation checklist for conformity.

## Safety
Do not publish vulnerability details before fixes and coordinated disclosure. This is not legal advice; confirm scope, category and deadlines with counsel and official guidance.
