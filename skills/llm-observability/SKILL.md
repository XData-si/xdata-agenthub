---
name: llm-observability
description: Instrument LLM applications and agents for production — traces of prompts, retrieval and tool calls, token usage and cost, latency, errors, user feedback and quality signals — with privacy controls and sampling (for example with OpenTelemetry GenAI conventions, Langfuse or similar). Use when running LLM features in production, debugging agent behaviour, or controlling AI costs.
license: MIT
---

# LLM Observability

## Goal
Be able to answer for any request: what the model saw, which tools ran, how long and how much it cost, whether the answer was good — without leaking personal data into logs.

## Inputs
- Application architecture (models, gateway, retrieval, tools, agents), existing observability stack, privacy requirements, cost budgets.

## Procedure
1. **Trace structure**: one trace per user request or agent task; spans for model calls, retrieval, reranking, tool calls and sub-agents; propagate trace IDs from the application.
2. **Attributes** per model span: provider, model and version, prompt template ID and version, input/output token counts, cost, latency (time to first token and total), finish reason, retries and fallbacks. Follow the OpenTelemetry GenAI semantic conventions where possible.
3. **Content capture policy**: decide per environment whether prompts and completions are stored; when stored, apply masking of secrets and personal data, access control and short retention; metadata-only is the default for sensitive applications.
4. **Quality signals**: user feedback (thumbs, edits), automatic evaluations on samples (groundedness, format validity), guardrail triggers, refusal rates.
5. **Dashboards and alerts**: cost per day and per feature, token anomalies, latency percentiles, error and fallback rates, tool failure rates, loop detection in agents.
6. **Sampling**: full traces for errors and flagged sessions, sampled traces for normal traffic.
7. **Close the loop**: link traces to evaluation datasets — interesting production failures become test cases (see `llm-output-evaluation`).

## Example fixture
```text
Alert: cost per conversation +300 % since prompt v14.
Trace analysis: retrieval now returns 40 chunks instead of 8 (config change) → input tokens ×5.
Fix: restore top-k=8, add a guardrail alert on input tokens > 20 k per call.
```

## Acceptance checks
- Every model and tool call in a sample request appears in the trace with tokens, cost and latency.
- Content capture follows the documented policy (negative case: a test prompt containing a fake API key appears masked in the stored trace).
- Cost and anomaly alerts fired in a test.

## Output
Instrumentation changes, content policy, dashboards, alerts.

## Safety
Traces with prompts are sensitive data stores: restrict access, encrypt, and set retention. Do not send traces to third-party observability services without a data processing agreement and approval.
