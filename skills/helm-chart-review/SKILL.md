---
name: helm-chart-review
description: Review Helm charts for safe defaults and maintainability — values schema, templating pitfalls, security context, resources and probes, secrets handling, upgrade and rollback behaviour, and chart dependencies. Use when writing, upgrading or consuming a Helm chart, including third-party charts before installing them in a cluster.
license: MIT
---

# Helm Chart Review

## Goal
A chart that renders valid, secure manifests by default, documents its values, and upgrades and rolls back predictably.

## Inputs
- Chart source (`Chart.yaml`, `values.yaml`, templates), target Kubernetes version, values used per environment, dependencies.

## Review checklist
1. **Render and lint**: `helm lint`, `helm template` with each environment's values, validate output with `kubeconform` against the cluster version; review the rendered YAML, not only templates.
2. **Values contract**: `values.schema.json` for types and required values; documented defaults; no secret values in `values.yaml`.
3. **Secure defaults**: `securityContext` with `runAsNonRoot`, `allowPrivilegeEscalation: false`, dropped capabilities, read-only root file system where possible; no `hostNetwork`, `hostPath` or privileged mode unless documented and optional (see `kubernetes-review`).
4. **Resources and probes**: requests and limits set by default; readiness, liveness and startup probes configurable.
5. **Secrets**: references to existing Secrets or external secret operators instead of rendering secrets from values; avoid `lookup` tricks that break GitOps diffs.
6. **Templating**: quote strings (`| quote`), consistent labels (`app.kubernetes.io/*`), `checksum/config` annotations to roll pods on config changes, no logic that silently ignores misspelled values.
7. **Upgrades**: immutable fields (selectors) unchanged between versions; hooks idempotent with delete policies; CRDs handled deliberately (Helm does not upgrade CRDs in `crds/`); `helm upgrade --atomic` or GitOps health checks.
8. **Dependencies**: pinned chart versions and digests of images; third-party charts reviewed for RBAC and cluster-wide resources before install.

## Example fixture
```yaml
# values.yaml
image: { repository: myapp, tag: latest }
database: { password: "changeme" }
```
Expected findings: mutable `latest` tag, default password in values, no schema, likely no security context or resources.

## Acceptance checks
- Rendered manifests for every environment pass schema validation and policy checks (for example kube-linter or Kyverno/OPA policies).
- Negative case: installing with a missing required value fails at render time with a clear message (schema test).
- Upgrade from the previous chart version tested in a disposable cluster, plus rollback.

## Output
Findings, chart diffs, values schema, upgrade test record.

## Safety
Install and upgrade third-party charts in a test namespace or cluster first. Cluster-wide resources (CRDs, ClusterRoles) need administrator approval. For charts that deploy services processing personal data, check that storage locations, log retention and backups configured in values meet GDPR requirements.
