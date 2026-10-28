---
name: secrets-management
description: Review the lifecycle of secrets and credentials — storage, injection, scoping, rotation, revocation and leak detection. Use when adding credentials to an application or CI, after a suspected leak, or when auditing access.
license: MIT
---

# Secrets Management

## Goal
Review secrets lifecycle and access controls. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Inventory secret owners, consumers and classification without copying values.
2. Assess issuance, scoped identities, short-lived credentials and rotation.
3. Inspect injection via environment, mounted files and secret managers.
4. Ensure no exposure in logs, builds, support bundles or repository history.
5. Validate revocation and break-glass access.
6. Plan zero-downtime rotation and audit.

## Illustrative review case
A token removed from the latest commit may still exist in Git history; revoke it before cleanup.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible.
