---
name: github-actions
description: Review secure GitHub Actions workflows with evidence-based findings and actionable verification.
license: MIT
---

# Github Actions

## Goal
Review secure GitHub Actions workflows. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Inventory triggers, job permissions and reusable workflows.
2. Default GITHUB_TOKEN to least privilege.
3. Review pull_request_target and workflow_run trust boundaries.
4. Pin third-party actions to immutable commits where feasible.
5. Control artifact/cache inputs and release provenance.
6. Gate deployments with environments.
7. Avoid exposing secrets to untrusted pull requests..

## Illustrative review case
A pull_request_target workflow that checks out attacker-controlled code and executes it with write token is a high-priority review finding.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
