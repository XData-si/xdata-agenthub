---
name: slo-error-budgets
description: Define user-centred service level indicators and objectives, error budgets and burn-rate alerts that reflect real user experience. Use when setting reliability targets, reducing noisy alerts, or deciding between feature work and reliability work.
license: MIT
---

# SLOs and Error Budgets

## Goal
A small set of SLIs that measure what users experience, objectives the team agrees with, and alerts that fire when the budget is being consumed too fast — not on every blip.

## Inputs
- Critical user journeys (log in, search, checkout, API call).
- Available telemetry: load balancer or proxy logs, application metrics, synthetic checks.
- Business tolerance for failure and existing commitments (SLAs).

## Procedure
1. **Choose journeys** — at most 3–5 per service to start.
2. **Define SLIs as ratios** of good events to valid events:
   - availability: requests that are not 5xx (exclude client 4xx) ÷ all valid requests;
   - latency: requests faster than a threshold (for example 300 ms) ÷ all valid requests;
   - freshness or correctness for pipelines: runs completed within N minutes ÷ scheduled runs.
   Measure as close to the user as practical (edge or load balancer rather than inside the app).
3. **Set objectives** from historical data, slightly below current performance (for example 99.5 % over 28 days). Avoid 100 %.
4. **Compute the error budget:** (1 − SLO) × valid events. For 99.5 % over 28 days ≈ 3 h 22 min of full unavailability equivalent.
5. **Alert on burn rate,** multi-window: page when a fast burn (for example 14.4× over 1 h and 5 min) would spend about 2 % of a 30-day budget in an hour; open a ticket on a slow burn (for example 1× over 3 days). Remove cause-based alerts that do not affect SLIs, or downgrade them.
6. **Agree on a policy:** what happens when the budget is exhausted (freeze risky releases, prioritise reliability work), who decides, how exceptions work.
7. **Review monthly:** budget consumption, incidents, whether SLOs still match user expectations.

## Example fixture
```promql
# 28-day availability SLI from proxy metrics
sum(rate(http_requests_total{job="edge",code!~"5.."}[28d]))
/ sum(rate(http_requests_total{job="edge",code!~"4.."}[28d]))
```
Note: this denominator excludes 4xx; document such choices explicitly.

## Acceptance checks
- Each SLI is a ratio with an explicit definition of good and valid events and its data source.
- Objectives are justified by data; the error budget is calculated and visible on a dashboard.
- Paging alerts are burn-rate based; a simulated or historical incident would have triggered them (backtest), and normal noise would not.
- The error budget policy is written down and agreed by product and engineering.

## Output
SLO document per service (journeys, SLIs, objectives, budget, alerting, policy), queries and dashboards.

## Safety
Do not change production alert routing without informing the on-call rotation; run new alerts in notify-only mode first.
