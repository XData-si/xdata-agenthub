---
name: data-pipeline-review
description: Review batch and streaming data pipelines (ETL/ELT, dbt, Airflow, Dagster, Spark) for correctness and operability — idempotent re-runs, incremental logic, late data, schema drift, backfills, lineage and data protection. Use when building or reviewing a data pipeline or investigating wrong or missing numbers in reports.
license: MIT
---

# Data Pipeline Review

## Goal
Pipelines that produce the same result when re-run, handle late and changed data explicitly, and make failures visible before stakeholders see wrong numbers.

## Inputs
- Sources, transformations and targets; orchestration tool; schedules and SLAs; data volumes; consumers (dashboards, ML features, exports); data classification.

## Review checklist
1. **Idempotency**: re-running a task for the same interval produces the same output (overwrite partitions or merge on keys; no blind appends).
2. **Incremental logic**: watermark column and its reliability (updated timestamps, change data capture); late-arriving data handled with a lookback window; deletes in the source propagated.
3. **Schema drift**: contracts on source schemas, alerts on new, removed or retyped columns; downstream models fail loudly rather than silently filling nulls.
4. **Backfills**: documented procedure, bounded parallelism, isolation from production SLAs, verification of row counts and totals after backfill.
5. **Tests**: uniqueness, not-null, accepted values and referential tests on key models (dbt tests or equivalent); reconciliation of totals against the source (see `data-quality-checks`).
6. **Orchestration**: retries with backoff, timeouts, alerts on failure and on SLA misses; tasks small enough to retry cheaply; dependencies explicit.
7. **Lineage and ownership**: each table has an owner and a description; lineage known from source to dashboard.
8. **Data protection**: personal data minimised and pseudonymised where possible; retention and deletion requests propagate to derived tables; access by role; no production personal data in development environments.

## Example fixture
```sql
INSERT INTO daily_revenue
SELECT order_date, SUM(amount) FROM orders WHERE order_date = CURRENT_DATE - 1 GROUP BY 1;
```
Expected findings: re-running duplicates rows (no overwrite or merge); late orders for that date are missed forever; refunds and cancellations not handled.

## Acceptance checks
- A re-run test for one interval yields identical output.
- Reconciliation against the source for a sample period within the agreed tolerance.
- Negative case: an injected schema change in a source fails the pipeline with an alert instead of producing nulls.

## Output
Findings, revised models or tasks, tests, runbook for backfills and incidents.

## Safety
Backfills and deletes on production warehouses need approval and a snapshot or time-travel window. Do not copy personal data into personal sandboxes.
