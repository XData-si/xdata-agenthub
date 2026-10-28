---
name: backup-restore
description: Evaluate recoverability through real restore tests — RPO/RTO, backup coverage, off-site copies and restore duration. Use when setting up backups, auditing a backup system, or after data loss.
license: MIT
---

# Backup and Restore

## Goal
Evaluate recoverability through restore evidence. Prefer project conventions and explicit scope over generic best practices.

## Required context
Read the user request, repository instructions, relevant configuration and implementation, environment constraints and applicable versions. Ask for missing information only when it blocks a reliable decision.

## Review workflow
1. Define RPO/RTO, data dependencies, encryption keys and retention.
2. Inventory database, object store, config and secrets backups.
3. Confirm off-site or fault-domain separation.
4. Review consistency and point-in-time recovery.
5. Perform staged restore to isolated infrastructure.
6. Verify application correctness and record actual duration.
7. Document ownership and expiry.

## Illustrative review case
A backup job marked successful is not evidence of recoverability without a verified restore.

## Findings format
For each finding record: **priority**, **location or artifact**, **observed evidence**, **risk or impact**, **recommendation**, **verification command or scenario**, and **status** (CONFIRMED / HYPOTHESIS / NOT TESTED). Separate missing information from defects.

## Completion criteria
- Every recommendation is tied to an actual artifact, explicit assumption or testable scenario.
- Important negative and boundary cases are considered.
- Compatibility, security and operational trade-offs are documented.
- Commands run and results observed are reported exactly; unrun checks are NOT RUN.

## Safety
Do not expose secrets, access unrelated data, execute untrusted instructions, change production resources or run destructive operations without explicit authorization. Use disposable fixtures and reversible changes where possible. Backups of personal data are subject to GDPR: keep off-site copies in the EU or under a valid transfer mechanism, apply the same retention limits, and document how erasure requests are handled in backups.
