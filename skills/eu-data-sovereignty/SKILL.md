---
name: eu-data-sovereignty
description: Assess and improve the digital sovereignty of a system for European organisations — where data, keys, operations and AI processing reside, exposure to non-EU jurisdiction, GDPR international transfers, provider lock-in and exit plans. Use when choosing cloud, SaaS or AI providers, handling personal or confidential data in the EU, or answering customer and procurement questions about sovereignty. Not legal advice.
license: MIT
---

# EU Data Sovereignty

## Goal
Give decision makers an evidence-based map of who can access or control the system's data and operations, under which jurisdiction, and how to reduce dependence where it matters — without assuming that "hosted in an EU region" is the same as "sovereign".

## Inputs
- Architecture and data-flow diagram, data classification (personal, confidential, regulated), and the list of providers (cloud, SaaS, CDN, email, monitoring, support tools, AI and model APIs, CI/CD).
- Contracts and data processing agreements, sub-processor lists, support and access models of each provider.
- Customer, sector or public-procurement requirements (for example national cloud qualifications).

## Procedure
1. **Inventory processing locations** for every provider: storage region, processing region (including AI inference, logs, backups, support access), and sub-processors. "EU region" with global support or telemetry is not EU-only processing.
2. **Map jurisdiction**: the legal seat of each provider and its parent. Providers controlled from outside the EU can be subject to foreign disclosure laws (for example the US CLOUD Act or FISA section 702) regardless of where the data is stored. Record it as a risk, not as a verdict.
3. **Check GDPR Chapter V transfers** for personal data leaving the EEA, including remote access: adequacy decision (for the US, the EU-US Data Privacy Framework applies only to certified recipients), or standard contractual clauses with a transfer impact assessment. **Verify the current legal status** of adequacy decisions; they have been challenged before.
4. **Control the keys**: encryption at rest and in transit, with keys held by the organisation (HYOK or external key management in the EU) for confidential data; record who can decrypt and under which process.
5. **AI and model APIs**: prompts can contain personal data and trade secrets. Prefer EU-hosted or self-hosted models (see `local-llm-serving`), route through a gateway that enforces data classes and no-retention settings (see `llm-gateway-routing`), and mask secrets and personal data before external calls.
6. **Operations and support**: who administers the platform, from where, with which access logging; whether break-glass access by the provider is possible and notified.
7. **Lock-in and exit**: data export formats, documented migration path, open standards and open-source components, contract terms for switching (the EU Data Act requires cloud providers to support switching and is phasing out switching charges — check the dates that apply to your contracts).
8. **Classify and decide** per data class: which providers are acceptable for public, internal, confidential and regulated data; where a sovereign alternative (EU-controlled provider, self-hosting) is required; and the accepted residual risks with an owner.
9. **Evidence**: certifications and qualifications relevant to the customer (ISO/IEC 27001, national schemes such as SecNumCloud or C5, sector requirements), with dates and scope.

## Example fixture
```text
Data class: confidential (customer contracts). Provider: US-parented SaaS e-signature, EU region.
Findings: support access from outside EU; parent subject to US disclosure law; DPA with SCCs, no TIA on file; vendor-held keys.
Options: (a) keep, add TIA + customer-held keys if offered; (b) move confidential contracts to an EU-controlled provider; (c) self-host open-source signing.
Decision: (b) for confidential, (a) acceptable for internal documents. Owner: CISO. Review: annually or on provider change.
```

## Acceptance checks
- Every provider has storage and processing locations, legal seat of parent, and transfer mechanism recorded — or `UNKNOWN` with a follow-up owner.
- AI/model providers are included, with retention and training settings documented.
- Each data class has an explicit decision on acceptable providers.
- Negative case: a provider that only states "EU region" without sub-processor and support-access information is not marked sovereign.
- The report states that it is not legal advice and lists questions for counsel.

## Output
Provider and data-flow register, jurisdiction and transfer analysis, decision table per data class, exit plan, and accepted risks with owners.

## Safety
Do not export personal or confidential data to test providers. Do not present jurisdictional risk as a legal conclusion; involve legal counsel for transfer assessments and contracts.
