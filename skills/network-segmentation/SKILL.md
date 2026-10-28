---
name: network-segmentation
description: Design and review network segmentation and firewall rules — zones, allowed flows, management access, east-west traffic, Kubernetes network policies, VPN and zero-trust access — with verification from outside and inside. Use when planning network layout, reviewing firewall or security-group rules, or containing lateral movement after an incident.
license: MIT
---

# Network Segmentation

## Goal
Only intended flows are possible between zones, administrative interfaces are reachable only through controlled paths, and a compromised host cannot reach everything else.

## Inputs
- Network diagram, zones and subnets, firewall rules and security groups, VPN or zero-trust access, Kubernetes network policies, inventory of services and their ports.

## Procedure
1. **Define zones** by trust and function: internet edge, DMZ or ingress, application, data, management, CI/runners, office or user networks.
2. **Write the flow matrix**: source zone → destination zone → port/protocol → purpose → owner. Everything not in the matrix is denied.
3. **Management plane**: SSH, RDP, hypervisor, database and admin UIs reachable only from a bastion, VPN or zero-trust proxy with MFA; never from the internet.
4. **East-west control**: default-deny between application services where feasible (Kubernetes NetworkPolicies, security groups referencing groups instead of CIDRs).
5. **Egress control**: restrict outbound internet from servers and CI to required destinations or through a proxy — this limits data exfiltration and malware callbacks.
6. **Container hosts**: remember that Docker-published ports bypass host firewalls; filter in the `DOCKER-USER` chain or bind to private addresses (see `linux-server-hardening`).
7. **Review rules**: remove `any/any`, duplicate and shadowed rules; each rule has an owner and a ticket; review annually.
8. **Verify** from outside (authorized port scan of public IPs) and from inside each zone (attempt forbidden connections); compare with the matrix.

## Example fixture
```text
Rule 14: allow 0.0.0.0/0 → 10.0.2.0/24 tcp/5432 "temporary for migration" (created 2024-02).
```
Expected finding: database open to the internet via an expired temporary rule; remove and restrict to the application zone.

## Acceptance checks
- A flow matrix exists and every firewall rule maps to a line in it.
- External scan shows only intended public ports; internal tests show forbidden zone-to-zone connections fail.
- Negative case: from a test host in the application zone, management ports of other zones are unreachable.

## Output
Zone diagram, flow matrix, rule changes with owners, verification results.

## Safety
Firewall changes can cut off access, including your own: keep an out-of-band console, apply in maintenance windows with approval, and stage changes. Scan only networks you are authorized to test.
