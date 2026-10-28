---
name: ansible-review
description: Review Ansible playbooks and roles for idempotency, safety and secret handling — check mode and diff, privilege escalation, module choice over shell commands, Ansible Vault, inventory hygiene and testing with Molecule. Use when writing or reviewing configuration management code or before running playbooks against production hosts.
license: MIT
---

# Ansible Review

## Goal
Playbooks that converge to the same state on every run, show their changes before applying them, keep secrets encrypted and can be tested without touching production.

## Inputs
- Playbooks, roles, inventories per environment, variables and vault files, Ansible and collection versions, target operating systems.

## Review checklist
1. **Idempotency**: modules (`ansible.builtin.package`, `template`, `lineinfile`, `systemd`) instead of `shell`/`command`; where commands are unavoidable, use `creates`, `removes` or `changed_when`; a second run reports zero changes.
2. **Check and diff**: tasks support `--check --diff`; the run against production is preceded by a check-mode run that a human reviews.
3. **Privilege**: `become` only where needed, not globally; no running as root by default; sudo rules for automation users scoped.
4. **Secrets**: Ansible Vault or an external secret lookup; `no_log: true` on tasks handling secrets; no secrets in inventory files or command lines.
5. **Inventory**: environments separated (no shared inventory that mixes staging and production); host patterns explicit; `--limit` used for staged rollouts.
6. **Safety controls**: `serial` for rolling changes, `max_fail_percentage`, handlers for restarts, pre-checks (disk, connectivity) and post-checks (service health).
7. **Code quality**: `ansible-lint` clean, fully qualified collection names, pinned collection versions (`requirements.yml`), role defaults documented.
8. **Testing**: Molecule scenarios on containers or VMs for each role, including an idempotency step.

## Example fixture
```yaml
- name: install nginx
  shell: apt-get install -y nginx && echo "password=S3cret" > /etc/app.conf
  become: yes
```
Expected findings: shell instead of the package module (not idempotent, no check mode), secret written in plain text in the playbook and logs.

## Acceptance checks
- `ansible-lint` passes; Molecule converge plus idempotence step shows zero changes on the second run.
- Negative case: running with `--check --diff` against a test host changes nothing on it.
- Production runs follow a reviewed check-mode diff and use `serial` with health checks.

## Output
Findings, revised tasks or roles, Molecule scenarios, run plan for production.

## Safety
Never run untested playbooks against production. Production runs require approval, a reviewed diff and a limited first batch.
