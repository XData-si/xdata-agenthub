---
name: runbook-authoring
description: Write operational runbooks that an on-call engineer or agent can follow under pressure — triggers, diagnosis, safe actions, escalation and verification. Use when creating alerts, after an incident revealed missing procedures, or when handing over a service to operations.
license: MIT
---

# Runbook Authoring

## Goal
Someone unfamiliar with the service can safely resolve or escalate a known problem at 3 a.m. using only the runbook and the access it lists.

## Inputs
- The alert or symptom the runbook covers, service architecture, dashboards and log locations.
- Past incidents and the commands that actually worked.
- Access model: who can run what, and where approvals are needed.

## Structure
```markdown
# <Alert or symptom name>
**Severity / impact:** what users experience
**Trigger:** alert expression or how the problem is noticed
**Prerequisites:** access, tools, VPN, roles
## 1. Confirm (read-only)
<commands with expected healthy vs unhealthy output>
## 2. Diagnose
<decision tree: if X → section 3a, if Y → 3b>
## 3. Mitigate
### 3a <action>  ⚠ impact, approval needed?, rollback
## 4. Verify recovery
<signals that prove resolution>
## 5. Escalate
<who, when (time-box), what information to include>
## History
<links to incidents where this was used>
```

## Procedure
1. **One runbook per alert or symptom;** link it from the alert annotation.
2. **Lead with read-only checks** and show expected output, so the reader can tell healthy from broken.
3. **Make actions explicit:** exact commands with placeholders marked (`<pod-name>`), the impact of each action, whether it needs approval, and how to undo it.
4. **Time-box:** "if not resolved within 15 minutes, escalate".
5. **Test the runbook** in a game day or staging failure, ideally run by someone other than the author; fix every step that was unclear.
6. **Maintain:** owner and last-reviewed date; review after every incident that used it.

## Example fixture
```markdown
## 1. Confirm
`curl -s -o /dev/null -w '%{http_code}' https://api.example.com/health` → healthy: `200`; unhealthy: `502` or timeout
## 3a Restart the API container  ⚠ ~10 s of 502s; no approval needed during an active incident
`docker compose -f /srv/api/compose.yml restart api`  · Undo: not applicable · Verify: step 4
```

## Acceptance checks
- Every action lists its impact and rollback; destructive actions require explicit confirmation or approval.
- Read-only diagnosis comes before any change.
- A dry run by a second person succeeded or produced documented fixes.
- No secrets in the runbook; it names where credentials are obtained.

## Output
Runbook files linked from alerts, with owner, review date and test record.

## Safety
Runbooks must never instruct bypassing access controls or deleting data without backups and approval.
