---
name: data-privacy
description: Review privacy requirements and data handling with evidence-based findings and actionable verification.
license: MIT
---

# Data Privacy

## Goal
Review privacy requirements and data handling. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Map data subjects, purposes, data categories and processors.
2. Record lawful-basis decisions for qualified reviewers.
3. Trace collection, access, transfer, retention and deletion.
4. Apply minimization and pseudonymization where suitable.
5. Check cross-border transfer assumptions, access logging and breach escalation.
6. Define data subject request verification and deletion evidence..

## Illustrative review case
A retention period must be justified by the actual purpose and applicable obligations, not invented from a template.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
