---
name: llm-gateway-routing
description: Design an LLM gateway layer — one OpenAI-compatible endpoint with per-team keys, model aliases, routing and fallbacks, budgets, rate limits, caching and logging policy (for example LiteLLM, Portkey, Envoy AI Gateway or a cloud gateway). Use when several applications or agents consume models from multiple providers, or when costs and keys are getting out of control.
license: MIT
---

# LLM Gateway and Routing

## Goal
Applications call stable model aliases through one controlled entry point, while the platform team manages providers, keys, spend, reliability and data policy centrally.

## Inputs
- Consumers (applications, agents, teams), their models, volumes and data sensitivity.
- Providers and self-hosted endpoints, contracts and data-processing terms, budget owners.

## Procedure
1. **Model aliases.** Applications use names such as `chat-default`, `chat-reasoning`, `embed-default`; the gateway maps aliases to concrete provider models and versions. Changing the provider does not require application releases.
2. **Keys per consumer.** Virtual keys per application or agent with allowed aliases, rate limits (requests and tokens per minute) and budgets; provider keys stay only in the gateway's secret store.
3. **Routing and fallback.** Define a primary and fallback per alias (another region, provider or local model); fall back on timeouts, 429 and 5xx only — not on 4xx validation errors; cap retries; make sure fallbacks satisfy the same data-policy class.
4. **Data policy classes.** For example *public*, *internal*, *confidential*: confidential traffic routes only to approved providers or self-hosted models; enforce by key or metadata rather than by convention.
5. **Budgets and alerts.** Per key and per team, with soft alerts (80 %) and hard limits; daily cost reports by alias and consumer.
6. **Caching.** Exact or semantic caching only where answers are not user-specific; scope the cache by tenant; set TTLs.
7. **Logging.** Metadata by default (consumer, alias, model, tokens, latency, cost, status); prompt and response logging only where approved, with retention limits and redaction.
8. **Reliability.** Health checks per backend, timeouts per alias, and dashboards for error rate, latency and fallback rate.
9. **Change management.** Alias remapping goes through review with an evaluation run (see `llm-output-evaluation`), and is announced to consumers.

## Example fixture
```yaml
aliases:
  chat-default:
    primary: provider-a/model-x-2024-08
    fallback: [self-hosted/model-y-awq]
    data_class: internal
keys:
  support-bot: {aliases: [chat-default], tpm: 200000, monthly_budget_eur: 300}
```
Negative test: the `support-bot` key requesting `chat-reasoning` is refused; a confidential-class key never routes to a non-approved provider even during a fallback.

## Acceptance checks
- No application holds a provider key directly (repository and configuration search).
- Each key has scoped aliases, rate limits and a budget; exceeding them is tested.
- Fallback behaviour is tested by simulating a primary outage, and respects data classes.
- Logging policy and retention are documented and match the configuration.

## Output
Gateway configuration, alias and key matrix, data-policy mapping, dashboards and test results.

## Safety
The gateway concentrates sensitive traffic: protect its admin interface and API (never public without authentication), rotate provider keys, and restrict who can read logs. Prompts and responses often contain personal data: before routing or logging them through a provider, confirm a data processing agreement, the processing location (EU or a valid GDPR transfer mechanism) and retention; route personal and confidential data classes only to approved EU or self-hosted endpoints, and for AI systems offered in the EU check AI Act duties (see `eu-ai-act-readiness`, `eu-data-sovereignty`).
