---
name: load-testing
description: Plan, run and interpret load and performance tests (k6, Locust, Gatling, JMeter) — realistic workload models, test types, environment parity, metrics and bottleneck analysis. Use before launches or traffic peaks, after architecture changes, or when capacity limits are unknown.
license: MIT
---

# Load Testing

## Goal
Know the system's capacity and failure behaviour under realistic load, with results that are reproducible and tied to SLOs.

## Inputs
- Traffic profile from production analytics (requests per second by endpoint, payload sizes, user journeys, peaks), SLOs, test environment description, data set size.

## Procedure
1. **Define questions**: maximum sustainable throughput at SLO latency; behaviour at 2× peak; recovery after overload; memory leaks over hours.
2. **Choose test types**: load (expected peak), stress (beyond peak until failure), spike (sudden jumps), soak (hours at normal load).
3. **Model the workload**: mix of journeys with think times and realistic data distribution; open model (arrival rate) for public traffic rather than a fixed number of looping users.
4. **Prepare the environment**: production-like sizing and data volume; isolated from real users; external dependencies stubbed or rate-agreed; monitoring on all tiers.
5. **Run** with warm-up, steady state and ramp-down; record client-side and server-side metrics (latency percentiles, error rate, CPU, memory, database connections, queue depth, GC).
6. **Find the bottleneck**: the first resource to saturate; confirm with profiling (see `performance-profiling`); change one thing and re-test.
7. **Report** against SLOs with the exact load-generator version, script revision, environment and data set.

## Example fixture
```js
// k6: open model, 200 requests/s for 10 minutes with thresholds
export const options = {
  scenarios: { checkout: { executor: 'constant-arrival-rate', rate: 200, timeUnit: '1s', duration: '10m', preAllocatedVUs: 300 } },
  thresholds: { http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<400'] },
};
```

## Acceptance checks
- Results include p50, p95, p99 latency, error rate and resource saturation, with the workload model documented.
- The load generator itself was not the bottleneck (its CPU and network checked).
- Negative case: at the overload point the system sheds load or degrades gracefully (errors are fast 429/503, not timeouts that cascade).

## Output
Test plan, scripts in the repository, results report, identified limits and recommendations.

## Safety
Never load-test production or third-party services without written approval and coordination; schedule tests, notify on-call, and have a stop procedure. Use synthetic data only.
