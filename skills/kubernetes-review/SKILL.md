---
name: kubernetes-review
description: Review Kubernetes workload and cluster manifests for security, resilience and operability.
license: MIT
---

# Kubernetes Review

## Goal
Produce an evidence-based review of Kubernetes YAML, Helm values or rendered resources without assuming cluster access.

## Inputs
- Manifest files or rendered Helm output and Kubernetes version
- Namespace, workload criticality, expected traffic, SLOs and storage needs
- Cluster policy, admission controls, ingress and network architecture

## Review procedure
1. Inventory workloads, service accounts, Secrets references, Services, Ingress/Gateway, storage and dependencies. Distinguish declared from defaulted behavior.
2. Evaluate pod/container security contexts: non-root identity, privilege escalation, capabilities, seccomp, host namespaces, hostPath and writable root filesystems. Note when compatibility must be tested.
3. Check RBAC for namespace and verb scope. Avoid wildcard permissions; identify default service account use and unnecessary token mounts.
4. Review readiness, liveness and startup probes. Ensure probe timing and endpoints reflect startup behavior; distinguish readiness from process health.
5. Review CPU/memory requests and limits, eviction risk, autoscaling signals, PodDisruptionBudgets and topology spread. Do not recommend limits without workload evidence.
6. Check NetworkPolicies for expected ingress and egress, DNS and external dependencies. Note that enforcement depends on the cluster CNI.
7. Review image provenance, pinned versions or digests, pull policy, imagePullSecrets and vulnerability scanning evidence. Never claim an image is safe based on a tag.
8. Review Secret handling, ConfigMaps, service exposure, TLS termination and certificate rotation.
9. Evaluate persistent volume access modes, backup/restore, StatefulSet identity, rolling update strategy and rollback procedures.
10. Produce prioritized findings with exact resource and field locations. Suggest offline schema checks, policy checks and staged deployment tests where available.

## Sample finding
```text
Resource: Deployment/api (namespace: demo)
Field: spec.template.spec.containers[0].securityContext
Observation: allowPrivilegeEscalation is not specified
Risk: Effective behavior depends on admission and runtime policy
Recommendation: Set false if application compatibility permits
Validation: Inspect rendered manifest and run workload in staging
Status: REVIEW - runtime behavior not verified
```

## Acceptance criteria
- Findings cite concrete manifest fields or explicitly state missing evidence.
- No claim of running cluster checks unless they actually ran.
- Recommendations include operational trade-offs and safe rollout validation.
- Missing cluster policy, runtime metrics and CNI behavior remain unknown.

## Output
Resource inventory, findings ranked by impact, suggested patches, offline/staging test plan and residual risks.

## Safety
Read-only by default. Never run kubectl apply, helm upgrade, delete or modify live clusters without explicit approval and a rollback plan.
