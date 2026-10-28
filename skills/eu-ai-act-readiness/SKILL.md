---
name: eu-ai-act-readiness
description: Prepare an engineering-level readiness assessment for the EU AI Act (Regulation (EU) 2024/1689) — inventory AI systems, determine role and risk category, map obligations and evidence gaps. Use when an AI feature is offered in or to users in the EU, or when compliance, procurement or customers ask about AI Act status. Not legal advice.
license: MIT
---

# EU AI Act Readiness

## Goal
Give legal and product owners an accurate, evidence-based picture of which AI systems exist, which AI Act category each probably falls into, and what technical evidence is missing. Final classification is a legal decision.

## Inputs
- List of AI features, models and providers, including third-party APIs and open-weight models.
- Intended purpose, users, affected persons, deployment countries, and whether the organisation develops, fine-tunes or only uses each system.
- Existing documentation: model cards, data sheets, risk assessments, logs, human-oversight procedures.

## Procedure
1. **Inventory** every AI system and general-purpose AI (GPAI) model in use: purpose, inputs and outputs, decision impact, provider, version.
2. **Determine the role** per system: *provider* (develops or places on the market under its own name), *deployer* (uses under its authority), importer or distributor. Substantial modification or rebranding can turn a deployer into a provider.
3. **Screen for prohibited practices** (Article 5), for example manipulative techniques causing harm, social scoring, untargeted facial-image scraping, emotion recognition in workplaces and education with narrow exceptions. Any hit → escalate immediately.
4. **Screen for high-risk** (Article 6, Annex I product safety and Annex III use cases such as employment, education, essential services and credit scoring, critical infrastructure, law enforcement, migration, justice). Record the reasoning and any Article 6(3) derogation argument.
5. **Check transparency duties** (Article 50): people are told they interact with AI; synthetic audio, image, video or text is marked machine-readably where required; deepfakes are disclosed.
6. **GPAI obligations** apply to providers of general-purpose models (technical documentation, copyright policy, training-data summary; more for systemic-risk models). Deployers using a GPAI API mainly need the provider's documentation.
7. **Map evidence for high-risk systems:** risk management, data governance, technical documentation, logging, transparency to deployers, human oversight, accuracy, robustness and cybersecurity, quality management, post-market monitoring. Deployers: use according to instructions, human oversight, input-data relevance, log retention, and a fundamental-rights impact assessment where required.
8. **AI literacy** (Article 4): staff operating AI systems have appropriate training; record it.
9. **Timeline check.** The Act entered into force on 1 August 2024; prohibitions and AI literacy have applied since 2 February 2025, GPAI obligations since 2 August 2025, and most remaining obligations apply from 2 August 2026 (some product-related high-risk rules from 2027). **Verify the current dates in official sources** — amendments and simplification proposals may change them.

## Example fixture
```text
System: CV screening assistant (ranks applicants), built on a third-party LLM API.
Role: provider of the AI system (own product), deployer of the GPAI model.
Category: likely high-risk (Annex III, employment) → legal review required.
Gaps: no human-oversight procedure, no bias evaluation on representative data, logs kept only 7 days.
```

## Acceptance checks
- Every system has a role, a probable category with reasoning, and an owner.
- Prohibited-practice and high-risk screening are documented even when the result is "not applicable".
- Each gap has evidence status (exists / partial / missing) and a proposed artefact.
- The report states clearly that it is not legal advice and lists questions for counsel.

## Output
AI system register, classification rationale, obligation-to-evidence matrix, gap list with owners, and questions for legal review.

## Safety
Do not present the assessment as a legal opinion or a conformity assessment. Do not include personal data of applicants or users in the analysis.
