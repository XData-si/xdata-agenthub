---
name: linux-server-hardening
description: Audit and harden a Linux server — SSH, users and sudo, patching, firewall, exposed services, logging and file permissions — with verification and a safe rollback path. Use when provisioning a new server or VPS, after an incident, or when reviewing an existing host's security baseline.
license: MIT
---

# Linux Server Hardening

## Goal
A minimal, patched host where only intended services are reachable, administrative access is strong and auditable, and changes did not lock anyone out.

## Inputs
- Distribution and version, role of the host, required inbound ports, administrative users, management access path (VPN, bastion, provider console).
- Any compliance baseline (CIS Benchmark level) the organisation follows.

## Procedure
1. **Inventory first, read-only:** `ss -tulpn` (listening services), `systemctl list-units --type=service --state=running`, users with shells, `sudoers`, cron and timers, installed packages, kernel version, uptime and pending reboots.
2. **Secure a fallback** before changing access: an open root console via the provider, or a second SSH session that stays connected while you test.
3. **SSH.** Keys only (`PasswordAuthentication no`, `KbdInteractiveAuthentication no`), `PermitRootLogin no` or `prohibit-password`, `AllowUsers`/`AllowGroups`, modern ciphers by default. Validate with `sshd -t` and test a new session before closing the old one.
4. **Users and sudo.** Named accounts, no shared logins; sudo with logging; remove stale accounts and keys from `authorized_keys`.
5. **Patching.** Apply updates; enable unattended security updates where appropriate; schedule reboots for kernel updates.
6. **Firewall.** Default deny inbound; allow only required ports and source ranges. On Docker hosts, published container ports bypass host `INPUT` rules — filter in the `DOCKER-USER` chain or bind ports to `127.0.0.1`.
7. **Reduce attack surface.** Disable unused services; bind databases and admin interfaces to localhost or a private network; never expose admin APIs publicly.
8. **Logging and detection.** Persistent journal, time sync (chrony or systemd-timesyncd), login and sudo logs shipped off-host; fail2ban or an equivalent for exposed SSH.
9. **File system.** Correct permissions on `/etc/shadow`, SSH keys and application secrets (`0600`); no world-writable files in system paths.
10. **Verify externally** with a port scan from outside (only against hosts you are authorised to scan) and compare with intended exposure.

## Example fixture
```text
ss -tulpn shows: 0.0.0.0:5432 (postgres), 0.0.0.0:8001 (admin API), 0.0.0.0:22
Expected findings: database and admin API publicly bound → bind to 127.0.0.1 or a private network and add DOCKER-USER rules; verify with an external scan.
```

## Acceptance checks
- Listening services match the intended list; each exception is justified.
- Password SSH login is rejected (tested), key login works from a new session.
- External scan shows only intended ports.
- Changes are documented with rollback commands.

## Output
Before/after inventory, applied changes, verification evidence, and remaining risks.

## Safety
Never apply SSH or firewall changes without a tested fallback session or console. Scan only systems you are authorised to test. Get approval before rebooting production hosts.
