---
name: postmortem
description: Write a blameless incident postmortem with an accurate timeline, impact, contributing factors and tracked corrective actions. Use after an outage, security incident, data issue or near miss once the service is stable.
license: MIT
---

# Blameless Postmortem

## Goal
Learn why the system allowed the incident and reduce the chance or impact of recurrence, without assigning personal blame.

## Inputs
- Alerts, chat logs, deployment history, dashboards and logs covering the incident window.
- Notes from responders and affected teams, customer reports, support tickets.

## Procedure
1. **Start within days** while memory is fresh; assign an author who coordinates, not the person "responsible".
2. **Timeline in UTC** from first trigger to full resolution: detection, escalation, key decisions, mitigation, recovery. Every entry has a source (log line, message link).
3. **Impact:** duration, affected users or requests (numbers), data integrity, SLO budget consumed, financial or contractual effects. State uncertainty explicitly.
4. **Contributing factors** rather than a single root cause: technical triggers, latent conditions (missing alert, risky default), process gaps (review, change management), detection and response delays. Use "5 whys" or a causal tree, and stop at actionable system factors, not individuals.
5. **What went well** and where the team was lucky.
6. **Corrective actions:** specific, owned, with due dates and a ticket; categorise as prevent, detect or mitigate. Prefer system changes (guardrails, automation, tests) over "be more careful".
7. **Review meeting** with responders; correct facts; agree on actions.
8. **Publish and track** actions to completion; reference the postmortem from runbooks and changed code.

## Language guide
Write "the deploy pipeline allowed a migration without a lock timeout", not "Alex ran a bad migration". Describe what information people had at the time.

## Example fixture
```markdown
| Time (UTC) | Event | Source |
|---|---|---|
| 09:12 | Deploy 2024.10.3 started | CI job #4512 |
| 09:14 | Error rate 18 % on /checkout | dashboard link |
| 09:31 | On-call paged (17 min detection gap: alert threshold 25 %) | pager log |
| 09:40 | Rollback completed; error rate < 0.5 % | CI job #4513 |
Action: lower the checkout alert to a burn-rate alert (owner: SRE, due 2024-11-01, TICKET-881)
```

## Acceptance checks
- Every timeline entry cites a source; impact uses measured numbers or states ranges.
- No individual is blamed; contributing factors are systemic and actionable.
- Each corrective action has an owner, a due date and a ticket; at least one targets detection.
- Security incidents follow disclosure and legal requirements before broad publication.

## Output
Postmortem document, action tickets, and updates to runbooks or alerts.

## Safety
Redact personal data, credentials and exploit details before sharing widely. Coordinate external communication with the incident owner.
