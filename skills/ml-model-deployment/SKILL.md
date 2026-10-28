---
name: ml-model-deployment
description: Deploy and operate machine-learning models in production (MLOps) — model registry and versioning, reproducible training, packaging and serving, staged rollout (shadow, canary), monitoring for data and prediction drift, retraining triggers and rollback. Use when taking a trained model to production or when a deployed model degrades silently.
license: MIT
---

# ML Model Deployment

## Goal
Every production prediction can be traced to a specific model version, training data and code; new models are rolled out safely; degradation is detected and reversible.

## Inputs
- Model type and framework, training pipeline, data sources, latency and throughput needs, serving platform, evaluation metrics, business owner.

## Procedure
1. **Reproducibility**: version training code, data snapshot or query, parameters and environment; record them in a model registry (for example MLflow) with the evaluation results.
2. **Promotion gates**: offline evaluation against the current production model on the same holdout data, including slices (segments, languages, edge cases) and fairness checks where decisions affect people.
3. **Packaging**: model artifact plus inference code in a versioned container; input schema validation; pinned dependencies (see `supply-chain-provenance`).
4. **Serving**: online (REST/gRPC) or batch; resource sizing and autoscaling; timeouts and fallbacks (for example rules or the previous model) when the model service fails.
5. **Staged rollout**: shadow mode (predict without acting, compare), then canary on a small share, then full; automatic rollback on metric regressions.
6. **Monitoring**: input data drift, prediction distribution drift, latency, error rate, and — when labels arrive — real accuracy; alerts with owners.
7. **Retraining**: triggers (drift, schedule, performance drop) and the same gates as the first deployment; never auto-deploy retrained models without evaluation.
8. **Governance**: model card (intended use, limits, data, metrics); for AI systems in the EU, check AI Act duties (see `eu-ai-act-readiness`); personal data in training data handled per GDPR (see `dpia`).

## Example fixture
```text
Churn model v7 deployed directly, replacing v6. Two weeks later, campaign conversions drop 30 %.
Findings: no shadow or canary phase, no drift monitoring (a source field changed units), no rollback path.
Fix: registry with v6 still deployable, input schema check catching the unit change, shadow → canary policy.
```

## Acceptance checks
- The production model version links to code, data snapshot, parameters and evaluation in the registry.
- Rollback to the previous version was executed in staging.
- Negative case: an input with a changed schema or out-of-range values is rejected or flagged by validation (test).

## Output
Deployment pipeline, registry entries, monitoring dashboards and alerts, model card, rollback runbook.

## Safety
Production deployment of models that make or support decisions about people requires owner approval and documented evaluation. Do not copy production personal data into experimentation environments without a legal basis and safeguards.
