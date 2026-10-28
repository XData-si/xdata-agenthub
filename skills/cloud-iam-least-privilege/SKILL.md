---
name: cloud-iam-least-privilege
description: Review and reduce cloud and platform permissions to least privilege — human and workload identities, wildcard policies, long-lived keys, cross-account trust, privilege escalation paths, break-glass and access reviews. Use when auditing AWS, Azure, GCP or Kubernetes RBAC permissions, after an incident, or when onboarding automation such as CI or AI agents.
license: MIT
---

# Cloud IAM Least Privilege

## Goal
Every human and workload has only the permissions it uses, through short-lived credentials, with escalation paths closed and access reviewed regularly.

## Inputs
- Identity inventory (users, groups, roles, service accounts, CI identities, agent identities), policies, access logs or "last used" data, organization structure.

## Procedure
1. **Inventory identities**: humans via SSO only; workloads via roles or managed identities; list every long-lived access key and service-account key with owner and last use.
2. **Find dangerous grants**: wildcard actions or resources (`*`), owner/admin roles on broad scopes, permissions that allow escalation (creating keys, attaching policies, passing roles, impersonation, editing their own IAM).
3. **Use evidence**: reduce permissions to those used in the last 90 days (access analyzers or audit logs), keeping documented exceptions.
4. **Short-lived credentials**: workload identity federation (OIDC) for CI and external workloads instead of static keys; rotate or delete unused keys.
5. **Separate duties**: production write access separate from development; deployment identities cannot modify IAM; break-glass accounts with MFA, alerting on use and sealed credentials.
6. **Cross-account and external trust**: external IDs or conditions on trust policies; no trust of whole external accounts without conditions.
7. **Guardrails**: organization policies or service control policies for invariants (no public buckets, allowed regions — for example EU-only), permission boundaries for delegated administration.
8. **Review cycle**: quarterly access reviews by owners; automatic removal of leavers through the identity provider.

## Example fixture
```json
{"Effect": "Allow", "Action": "*", "Resource": "*"}   // attached to the CI deploy role
```
Expected findings: CI role is effectively administrator (can modify IAM and exfiltrate data); replace with deployment-scoped actions on named resources and OIDC trust limited to the protected branch.

## Acceptance checks
- No wildcard admin grants except documented break-glass roles.
- Every long-lived key has an owner and a rotation date, or is removed.
- Negative case: the reduced role is tested to fail on a forbidden action (for example creating an IAM user) while the deployment still succeeds.

## Output
Identity and permission inventory, risk list, policy changes and access review schedule.

## Safety
Permission changes can break production workloads: apply in stages with monitoring and a rollback copy of each policy. Never remove break-glass access without a replacement. Get approval for production IAM changes. Identity inventories and access logs are personal data: restrict access, keep them in the EU or under a valid transfer mechanism, and apply retention limits (GDPR).
