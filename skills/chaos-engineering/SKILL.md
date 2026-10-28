---
name: chaos-engineering
description: Run controlled failure experiments to verify resilience — steady-state hypotheses, blast-radius control, fault injection (instance loss, latency, dependency failure, DNS, disk), abort conditions and learning reviews. Use when validating redundancy, failover, timeouts and alerts before relying on them, or after resilience-related incidents.
license: MIT
---

# Chaos Engineering

## Goal
Replace assumptions about resilience with evidence, by injecting realistic faults in a controlled way and stopping before customers are harmed.

## Inputs
- Architecture and dependencies, SLOs and dashboards, runbooks, previous incidents, available fault-injection tools (for example Chaos Mesh, Litmus, Toxiproxy or simple scripts), on-call schedule.

## Procedure
1. **Prerequisites**: monitoring that shows steady state; alerts and runbooks in place; a game-day owner; start in non-production.
2. **Hypothesis**: "When one of three API instances is terminated, p95 latency stays below 400 ms and no requests fail beyond retries."
3. **Choose the fault**: instance or pod termination, added latency or errors from a dependency, DNS failure, full disk, expired certificate, cache outage, region or zone loss (later).
4. **Limit the blast radius**: one service, small traffic share, short duration; define **abort conditions** (SLO burn, error threshold) and a tested way to stop the fault immediately.
5. **Run** with observers watching dashboards; record timeline, alerts fired, operator actions.
6. **Analyse**: hypothesis confirmed or refuted; gaps in detection, automation and runbooks; create tickets with owners.
7. **Grow gradually**: repeat fixed experiments regularly (automated where safe); extend to production only with maturity and approval.

## Example fixture
```text
Experiment: inject 2 s latency on calls from checkout to the tax service (staging, 10 minutes).
Expected: circuit breaker opens, checkout falls back to cached tax rates, alert "tax-service-latency" fires within 5 minutes.
Observed: no timeout configured → checkout threads exhausted after 90 s; no alert. Hypothesis refuted → tickets: timeout 500 ms, breaker, alert.
```

## Acceptance checks
- Every experiment has a written hypothesis, blast radius, abort conditions and stop procedure before it starts.
- Results and follow-up tickets are recorded, including refuted hypotheses.
- Negative case: the abort procedure was tested before the first experiment (fault stops within the stated time).

## Output
Experiment plans, results log, follow-up actions, updated runbooks and alerts.

## Safety
Production experiments require explicit approval, an active on-call engineer, customer-impact limits and a business-hours schedule. Never run experiments on systems you do not own or during incidents.
