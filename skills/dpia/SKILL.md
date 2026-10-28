---
name: dpia
description: Prepare a GDPR Data Protection Impact Assessment (DPIA) for high-risk processing — screening, systematic description, necessity and proportionality, risks to individuals, mitigating measures and consultation — producing evidence for the controller and DPO. Use when introducing processing likely to be high risk (large-scale personal data, monitoring, profiling, new technologies such as AI, sensitive data). Not legal advice.
license: MIT
---

# Data Protection Impact Assessment

## Goal
Give the controller and the data protection officer a clear, evidence-based DPIA draft that identifies risks to people's rights and the measures that bring them to an acceptable level — before processing starts.

## Inputs
- Description of the project or system, data categories and subjects, purposes, legal basis, data flows and processors, retention, security measures, involvement of AI or automated decisions.

## Procedure
1. **Screening**: is a DPIA required? Indicators include systematic monitoring, large-scale processing of special categories, profiling with significant effects, innovative technology (for example AI), combining datasets, vulnerable subjects. Check the national supervisory authority's list of processing that requires a DPIA. Record the screening result either way.
2. **Systematic description**: purposes, legal basis per purpose, data categories, data subjects, sources, recipients and processors, international transfers (see `eu-data-sovereignty`), retention, systems and data-flow diagram.
3. **Necessity and proportionality**: why each data category is needed, minimisation options considered, accuracy, transparency to individuals, how rights are exercised (see `gdpr-dsar-handling`).
4. **Risks to individuals** (not to the company): illegitimate access, unwanted modification, loss, discrimination, loss of control, chilling effects. Rate likelihood and severity with reasons.
5. **Measures**: technical (encryption, pseudonymisation, access control, logging, retention automation) and organisational (training, contracts, human review of automated decisions); map each measure to the risks it reduces and rate residual risk.
6. **Consult**: DPO advice recorded; views of data subjects or their representatives where appropriate; if high residual risk remains, prior consultation with the supervisory authority is required before processing.
7. **Approve and review**: sign-off by the accountable owner; review when processing changes or at a set interval.

## Example fixture
```text
Project: AI assistant that summarises customer support tickets (contains names, contact data, occasionally health information).
Screening: new technology + possible special-category data → DPIA required.
Key risks: special-category data sent to an external model provider; summaries retained indefinitely.
Measures: masking before model calls, EU-hosted model with no retention, 90-day summary retention, opt-out channel. Residual risk: medium → DPO approval.
```

## Acceptance checks
- Screening decision is recorded with reasons, even when no DPIA is required.
- Every identified risk has measures and a residual risk rating; high residual risks trigger the prior-consultation step.
- Negative case: a purpose without a legal basis or a data category without necessity justification is flagged, not accepted silently.

## Output
DPIA document (description, necessity, risk table, measures, residual risk, DPO opinion, approval), action list.

## Safety
Use descriptions and samples without real personal data. This is not legal advice; the controller and DPO own the assessment and its conclusions.
