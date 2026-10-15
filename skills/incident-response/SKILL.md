---
name: incident-response
description: Coordinate authorized incident triage and recovery with evidence-based findings and actionable verification.
license: MIT
---

# Incident Response

## Goal
Coordinate authorized incident triage and recovery. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Confirm severity, incident commander, communication channel and evidence retention.
2. Establish timeline and impact scope.
3. Preserve logs before changing systems.
4. Contain through least-disruptive reversible action.
5. Document hypotheses separately from observed facts.
6. Verify recovery with customer-facing signals.
7. Prepare postmortem with contributing factors and prevention owners..

## Illustrative review case
For an API outage, check error rate, dependency failures and deploy timeline before attributing root cause to a recent release.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
