---
name: llm-cost-analysis
description: Model LLM cost and latency with transparent assumptions with evidence-based findings and actionable verification.
license: MIT
---

# Llm Cost Analysis

## Goal
Model LLM cost and latency with transparent assumptions. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Inventory model, provider, input/output token counts, cached tokens, tool calls, embedding, retrieval and retries.
2. Distinguish list prices from contracted rates and regional billing.
3. Calculate per-request and monthly scenarios using P50/P95 usage.
4. Account for rate limits, fallback routing and context growth.
5. Compare quality/latency tradeoffs before optimizing solely for price..

## Illustrative review case
A request with 2000 input and 500 output tokens must price each token category separately; mark unknown provider rates as missing.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
