---
name: observability
description: Design actionable telemetry — metrics, logs, traces, dashboards and alerts tied to user impact. Use when instrumenting a service, building dashboards, or when incidents were detected late.
license: MIT
---

# Observability

## Goal
Design actionable service telemetry. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Start from service SLOs and user journeys.
2. Define golden signals and cardinality budgets.
3. Connect logs, metrics and traces through trace IDs.
4. Protect personal data and secrets.
5. Define alert thresholds using error budgets and sustained windows.
6. Validate alert routing, silence policy and runbook links.
7. Test dashboards against representative failures.

## Illustrative review case
An alert on raw CPU alone is not proof of user impact; correlate saturation with latency and errors.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
