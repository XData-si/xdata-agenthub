---
name: log-analysis
description: Investigate application, proxy and system logs to establish what happened — correlating timestamps and request IDs, quantifying error patterns and separating signal from noise. Use when triaging an incident, explaining a failed job or request, or verifying that a fix worked.
license: MIT
---

# Log Analysis

## Goal
Turn raw logs into a defensible account: what failed, when it started, how often, for whom, and what changed — with queries others can rerun.

## Inputs
- Time window (with timezone), affected service and environment, and an example request ID, user or job ID if known.
- Log sources: application, reverse proxy or load balancer, database, container runtime, system journal, cloud audit logs.

## Procedure
1. **Normalise time.** Convert everything to UTC; note clock skew between hosts; widen the window a little before the reported start.
2. **Start from the edge.** Proxy or load balancer logs show status codes, latency and upstream errors per request; then follow the request ID into application logs.
3. **Quantify before reading deeply.** Count by status code, error type, endpoint and host per minute. Find the first occurrence and the shape (spike, step, gradual).
4. **Correlate with changes:** deploys, configuration changes, scaling events, certificate renewals, dependency incidents, cron schedules.
5. **Group errors by signature** (exception class and message with IDs removed) and rank by count and user impact.
6. **Read representative examples** in full, including the log lines just before the first error.
7. **Check for missing logs:** gaps can mean a crash, disk full, rotation or a logging pipeline failure.
8. **Write conclusions** with the query used for each claim; label hypotheses separately.

## Example fixture
```bash
# Requests per minute by status from a JSON proxy log
jq -r 'select(.ts >= "2024-10-01T09:00" and .ts < "2024-10-01T10:00")
       | "\(.ts[0:16]) \(.status)"' access.log | sort | uniq -c
# Top error signatures in application logs (IDs stripped)
grep ERROR app.log | sed -E 's/[0-9a-f]{8}-[0-9a-f-]{27}/<uuid>/g; s/[0-9]+/<n>/g' | sort | uniq -c | sort -rn | head
```

## Acceptance checks
- Every claim includes the query or command and the time window used.
- The first occurrence and the change correlation are stated, or explicitly unknown.
- Counts distinguish affected requests or users from total log lines.
- Personal data and secrets found in logs are reported as findings, not copied into the report.

## Output
Summary (what, when, scope, likely trigger), supporting queries and results, open questions and recommended logging improvements.

## Safety
Access logs under least privilege; do not export logs containing personal data to external tools without authorization; redact before sharing.
