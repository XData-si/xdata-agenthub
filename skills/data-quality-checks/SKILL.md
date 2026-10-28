---
name: data-quality-checks
description: Define and implement data quality checks and data contracts — freshness, volume, schema, uniqueness, validity, referential integrity and reconciliation — with owners, thresholds and alerting. Use when stakeholders distrust a dataset, before exposing data to ML or reports, or when introducing data contracts between teams.
license: MIT
---

# Data Quality Checks

## Goal
Detect broken data before people or models use it, with checks that are owned, cheap to run and tuned to avoid alert fatigue.

## Inputs
- Critical datasets and their consumers, known past incidents, current tests, tooling (dbt tests, Great Expectations, Soda, SQL checks), alert routing.

## Procedure
1. **Pick critical data elements**: the tables and columns behind key decisions, reports or models. Start with 5–10, not everything.
2. **Write a data contract** per dataset: schema, semantics of key columns, freshness SLA, allowed values, owner, change process.
3. **Implement check types**:
   | Dimension | Example check |
   |---|---|
   | freshness | max(updated_at) within 2 h of now |
   | volume | daily row count within ±30 % of the 28-day median |
   | schema | expected columns and types present |
   | uniqueness | primary key has no duplicates |
   | completeness | `customer_id` not null in 100 % of orders |
   | validity | `country` in ISO 3166 list; amounts ≥ 0 |
   | integrity | every `order.customer_id` exists in customers |
   | reconciliation | warehouse revenue matches source system within 0.5 % |
4. **Severity**: blocking checks stop downstream jobs (or quarantine data); warning checks notify the owner.
5. **Thresholds** from history, not guesses; review false positives monthly.
6. **Alert routing** to the dataset owner with context (failed rows sample, query link) — without personal data in the alert.
7. **Track**: incidents and check failures over time; add a check for every incident that reached consumers.

## Example fixture
```sql
-- volume anomaly check
SELECT COUNT(*) AS n FROM orders WHERE order_date = CURRENT_DATE - 1;
-- compare with median of previous 28 days; fail if outside ±30 %
```

## Acceptance checks
- Each critical dataset has a contract, an owner and at least freshness, volume and key checks.
- Negative case: injecting duplicate keys or a stale load in a test environment triggers the expected blocking check.
- Thresholds are justified by historical data, documented next to the check.

## Output
Contracts, checks in code, alert routing, and a dashboard of check status.

## Safety
Run checks with read-only credentials. Failed-row samples can contain personal data — store them with restricted access and short retention. Enabling blocking checks (which stop downstream jobs) or new alert routes changes production behaviour: agree them with the dataset owner and consumers first.
