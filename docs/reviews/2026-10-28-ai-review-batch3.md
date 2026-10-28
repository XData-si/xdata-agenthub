# AI skill review — batch 3 (2026-10-28)

40 new skills and the updated `agenthub-router` were reviewed with `scripts/ai_skill_review.py` (model `xdata-default`, DeepSeek V4 Flash 0731 through an EU-operated LiteLLM gateway with masking). Round 1: 30 pass, 11 needs_review. Fixes: Django REST Framework default permission statement corrected (`AllowAny`), mandatory DPO approval before erasure and disclosure in `gdpr-dsar-handling`, explicit approvals for production, cost and publication steps, GDPR notes. Round 2: all 11 pass. Machine-readable rounds: [2026-10-28-ai-review-batch3.json](2026-10-28-ai-review-batch3.json).

## AgentHub AI skill review (advisory)

Model: `xdata-default`. The deterministic security gate is authoritative; this review is advisory and the reviewed content was treated as untrusted data.

| Skill | Verdict | EU ready | Summary |
|---|---|---|---|
| `agenthub-router` | ✅ pass | yes | agenthub-router is a safe, well-scoped routing meta-skill with clear procedures, approval-gated safety, and EU-aware routing, containing no injection, exfiltration, or unsafe instructions. |
| `ai-red-teaming` | ✅ pass | yes | Skill provides a well-scoped, safety-conscious red-teaming procedure with authorization requirements, non-production constraints, and regression testing; no security issues found. |
| `ansible-review` | ✅ pass | yes | The ansible-review skill is a well-structured, safe review checklist for Ansible playbooks with appropriate safety and quality controls. |
| `caching-strategy` | ✅ pass | yes | The caching-strategy skill is well-structured, secure, and safe, with clear guidance on cache design, per-user isolation, failure behaviour, and requiring approval for production cache flushing. |
| `chaos-engineering` | ✅ pass | yes | Well-structured chaos engineering skill with explicit safety controls and no security or accuracy issues. |
| `ci-cd-pipeline-design` | ✅ pass | yes | Ci-cd-pipeline-design is a clear, safe CI/CD design skill with approval gates, secrets handling and a negative-case acceptance check; no security issues found. |
| `cloud-cost-optimization` | ✅ pass | yes | Well-scoped FinOps skill with explicit approval gates, rollback expectations, and no untrusted or exfiltration instructions. |
| `cloud-iam-least-privilege` | ✅ pass | yes | Well-structured cloud IAM least-privilege skill with clear safety, approval, acceptance and GDPR-aware guidance; no blocking issues found. |
| `container-image-optimization` | ✅ pass | yes | The container-image-optimization skill is a benign, well-structured guide with no security, safety, accuracy, or EU concerns. |
| `data-pipeline-review` | ✅ pass | yes | A clean, well-structured pipeline-review skill with clear approval gates for production-affecting actions and no prompt injection, exfiltration, or unsafe execution paths. |
| `data-quality-checks` | ✅ pass | yes | This skill provides a safe, well-scoped methodology for implementing data quality checks, with approval required for production-impacting actions and appropriate personal-data safeguards. |
| `disaster-recovery-drill` | ✅ pass | yes | Skill is well-scoped, safe, and EU-aware; no security issues found. |
| `dora-readiness` | ✅ pass | yes | The dora-readiness skill is a well-structured, accurate, and safety-aware guide for DORA readiness assessments with no security, safety, accuracy, or EU issues found. |
| `dpia` | ✅ pass | yes | The dpia skill provides a sound GDPR DPIA workflow with clear safety, quality, and EU-aligned guidance; no security, safety, accuracy, or EU concerns found. |
| `embedding-model-selection` | ✅ pass | yes | Well-structured skill with clear safety controls for data handling, cost approval, and production migration; no security, safety, accuracy, or EU issues found. |
| `european-accessibility-act` | ✅ pass | yes | The european-accessibility-act skill is accurate, safety-conscious, and contains no security or prompt-injection risks, so it can be approved. |
| `event-driven-architecture` | ✅ pass | yes | Skill provides sound, safety-conscious guidance for event-driven design with no security, safety, accuracy, or EU concerns. |
| `feature-flags` | ✅ pass | yes | Feature-flags skill is safe, well-scoped guidance with approval, testing, security and cleanup steps; no security or safety issues found. |
| `gdpr-dsar-handling` | ✅ pass | yes | The skill provides a safe, approval-gated GDPR DSAR workflow with correct deadlines, identity verification, exemptions, evidence handling, and explicit safety controls. |
| `go-development` | ✅ pass | yes | The go-development skill is a well-structured, safe review checklist with no security, safety, accuracy, or EU concerns. |
| `graphql-api-review` | ✅ pass | yes | The GraphQL API review skill is well-structured, security-conscious, and includes appropriate safety and quality guidance. |
| `helm-chart-review` | ✅ pass | yes | The helm-chart-review skill is a well-structured, safe review checklist with proper safety and GDPR guidance and no security issues. |
| `i18n-localization` | ✅ pass | yes | The i18n-localization skill is a safe, well-structured guide to internationalization with clear acceptance checks and appropriate safeguards for legal and confidential translations. |
| `java-spring-review` | ✅ pass | yes | A defensible, well-structured Spring Boot security review skill with accurate technical guidance, a clear safety section, and no prompt injection or harmful instructions. |
| `llm-observability` | ✅ pass | yes | The skill is a well-structured observability guide with explicit privacy and approval safeguards, no harmful instructions found. |
| `llm-structured-extraction` | ✅ pass | yes | The skill is a safe, well-structured extraction guide with privacy controls, validation, human review, and no security issues. |
| `load-testing` | ✅ pass | yes | Load-testing skill is safe, clear and actionable, with explicit approval requirements and a negative acceptance case. |
| `logging-standards` | ✅ pass | yes | The logging-standards skill is safe and high-quality: it mandates structured JSON logs, redaction of secrets and personal data, audit events, retention limits, and authorization for production log access, with no security, safety, accuracy, or EU concerns found. |
| `ml-model-deployment` | ✅ pass | yes | The ml-model-deployment skill is a well-structured MLOps guide with clear approval gates, rollback, monitoring, and appropriate EU/GDPR references; no security, safety, quality, accuracy, or EU issues found. |
| `mobile-app-review` | ✅ pass | yes | The mobile-app-review skill is a well-scoped, safety-guarded mobile security assessment checklist with accurate OWASP, GDPR/ePrivacy, and platform references; no adversarial instructions were found. |
| `multi-agent-orchestration` | ✅ pass | yes | The skill is a safe, well-structured design guide for multi-agent systems that includes security, safety, approval, and EU obligations. |
| `network-segmentation` | ✅ pass | yes | Defensive network segmentation skill with clear procedure, negative acceptance checks and explicit safety guardrails; no security, safety, accuracy or EU issues found. |
| `node-backend-review` | ✅ pass | yes | The node-backend-review skill is a well-scoped security review checklist with clear procedures, acceptance checks, and an explicit safety section requiring authorized non-production testing. |
| `open-source-license-compliance` | ✅ pass | yes | Safe, well-structured open-source license compliance skill with clear procedures, negative-case acceptance checks, and a legal disclaimer; no security, safety, accuracy, or EU-specific issues found. |
| `owasp-asvs-review` | ✅ pass | yes | The owasp-asvs-review skill is a well-structured security assessment procedure with proper safety controls, no prompt injection or unsafe actions. |
| `python-web-review` | ✅ pass | yes | The python-web-review skill provides a sound and safe Django/FastAPI security review checklist with clear procedure, acceptance checks, example fixture, and GDPR awareness; no prompt injection, exfiltration, destructive commands, or regulatory issues were found. |
| `react-component-review` | ✅ pass | yes | The react-component-review skill is a well-structured, safe code-review checklist with no security, safety, accuracy, or EU concerns. |
| `release-notes` | ✅ pass | yes | Release-notes skill is a benign, well-scoped documentation task with clear approval and disclosure safeguards. |
| `rust-review` | ✅ pass | yes | rust-review is a well-scoped, security-aware Rust code review skill with clear checklist, example, acceptance tests, and approval safeguards; no prompt injection or harmful behavior found. |
| `security-testing-scope` | ✅ pass | yes | The security-testing-scope skill is a well-structured, safety-conscious template for authorized penetration testing with clear scope, authorization, data handling, and stop conditions, and no security, safety, accuracy, or EU issues. |
| `vulnerability-management` | ✅ pass | yes | The vulnerability-management skill is well-scoped, prioritises by risk and exploitation evidence, requires approval for production changes, includes negative-case acceptance checks, and has no security or EU concerns. |

### `data-pipeline-review`
- **low / eu** — The data-protection guidance is substantively GDPR-aligned but never names the GDPR, so EU users reviewing pipeline compliance may miss the legal hook; adding an explicit reference to GDPR Articles 5 and 17 (and noting ePrivacy where applicable) would strengthen EU compliance awareness, though this is an enhancement rather than a blocker. (evidence: `retention and deletion requests propagate to derived tables; access by role; no production personal data in development environments`)

### `java-spring-review`
- **low / eu** — Snyk is a US SaaS, but it is only one of several listed options ('or similar') and is not a mandatory dependency, so the skill does not force use of a non-EU service. Teams using Snyk should note that project manifests may be processed outside the EU; self-hosted or EU-hosted alternatives exist. (evidence: `dependency check (OWASP Dependency-Check, Snyk or similar)`)
- **low / accuracy** — The runtime guidance is vague without a concrete verification method; recommend adding an acceptance or load-test step so thread pool sizing is testable rather than an unsupported claim. (evidence: `virtual threads or thread pools sized for the workload`)
