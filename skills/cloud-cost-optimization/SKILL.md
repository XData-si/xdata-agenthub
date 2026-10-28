---
name: cloud-cost-optimization
description: Find and reduce cloud and hosting spend with evidence (FinOps) — cost allocation and tagging, idle and oversized resources, storage lifecycle, data transfer, commitments, and AI/LLM usage costs — without hurting reliability. Use when bills grow unexpectedly, before budgeting, or when asked to cut infrastructure costs.
license: MIT
---

# Cloud Cost Optimization

## Goal
Lower cost per unit of value (per customer, request or environment) with changes that are measured, reversible and agreed with service owners.

## Inputs
- Billing exports for at least 3 months, resource inventory, tags or labels, utilization metrics, reliability targets, contracts and commitments, LLM gateway usage reports.

## Procedure
1. **Allocate costs**: tag or label resources by service, environment and owner; report untagged spend as its own line; express costs per unit where possible.
2. **Find waste first**: unattached volumes and IPs, old snapshots and images, idle load balancers, stopped instances still billing storage, non-production running 24/7, forgotten test environments.
3. **Right-size**: compare requested CPU/memory with p95 usage over representative periods; downsize stepwise with monitoring; consider ARM instances where software supports them.
4. **Storage**: lifecycle rules to cheaper tiers and deletion after retention; compress logs; reduce log verbosity and retention where compliant.
5. **Data transfer**: identify cross-region and internet egress, NAT gateway charges and CDN opportunities; co-locate chatty services.
6. **Commitments**: reserved instances, savings plans or longer-term VPS contracts for steady baseline load only, after right-sizing.
7. **Schedules**: stop development and test environments outside working hours; scale to zero where the platform supports it.
8. **AI and LLM spend**: route by task to cheaper models, cache, cap tokens, set per-key budgets (see `llm-gateway-routing`, `llm-cost-analysis`).
9. **Governance**: budgets and anomaly alerts per team; monthly review of top changes.

## Example fixture
```text
Monthly bill +38 %. Top changes: +2 TB snapshots (no lifecycle), staging cluster running 24/7 at 6 % CPU, NAT egress from a log shipper.
Plan: snapshot lifecycle (−X €), schedule staging off-hours, ship logs through a private endpoint; owners and rollback for each.
```

## Acceptance checks
- Every recommendation has estimated savings, owner, risk and rollback.
- Savings are verified on the next bill or cost report, not only estimated.
- Negative case: right-sizing changes are rejected if p95 utilization after the change would exceed the agreed threshold or SLOs degrade.

## Output
Cost allocation report, prioritized savings plan, implemented changes with measured results.

## Safety
Deleting resources, snapshots or data is irreversible: confirm ownership, backups and retention obligations, and get approval. Do not change production capacity without the service owner. Purchasing commitments or reservations, changing schedules that stop environments, and resizing production need explicit approval from the budget and service owners, with an exit or rollback plan.
