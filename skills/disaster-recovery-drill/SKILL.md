---
name: disaster-recovery-drill
description: Plan and run disaster recovery exercises that prove recovery time and data loss objectives — scenarios, recovery runbooks, dependencies and credentials, restore in an isolated environment, timing and gaps. Use when DR plans exist only on paper, before audits (NIS2, DORA, ISO 27001), or after major infrastructure changes.
license: MIT
---

# Disaster Recovery Drill

## Goal
Demonstrate, with timing, that critical services can be recovered within agreed RTO and RPO after realistic disasters — and fix what the drill reveals.

## Inputs
- Service catalogue with criticality, RTO and RPO; backup and replication setup (see `backup-restore`); runbooks; dependencies (DNS, identity provider, secrets store, registries); contacts.

## Procedure
1. **Pick a scenario**: loss of a server or VPS, a whole provider region or account, ransomware with encrypted primary data, deleted database, lost access to the identity provider or secrets store.
2. **Map dependencies** of the chosen service: what must exist first (network, DNS, certificates, secrets, container registry, identity). Recovery often fails on these, not on the database.
3. **Prepare an isolated target** environment; never restore over production during a drill.
4. **Execute from the runbook only** — the person running it should not be the author. Record a timeline: declaration, decision points, each restore step, verification.
5. **Verify**: application works end to end; data restored up to the expected point (RPO measured from the newest restored record); integrity checks pass.
6. **Measure** actual recovery time and data loss versus objectives.
7. **Improve**: update runbooks, automate slow manual steps, fix missing access (for example credentials stored only in the failed system), schedule the next drill.

## Example fixture
```text
Scenario: VPS hosting the ticketing system lost. RTO 4 h, RPO 1 h.
Observed: restore of DB 40 min; blocked 2 h because the backup encryption key was only in the lost VPS's environment file.
Fix: key escrow in the secrets manager with break-glass access; repeat drill.
```

## Acceptance checks
- Measured RTO and RPO are recorded for each drilled service and compared with objectives.
- The drill used only documented steps and credentials available outside the failed environment.
- Negative case: at least one dependency failure (for example primary DNS or identity provider unavailable) is part of the scenario or explicitly ruled out with a reason.

## Output
Drill plan, timeline, results versus RTO/RPO, gap list with owners, updated runbooks.

## Safety
Use isolated environments and synthetic or properly protected copies of data. Restored personal data in test environments must be deleted after the drill. Production failover tests require approval and a rollback plan.
