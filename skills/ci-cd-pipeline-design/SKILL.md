---
name: ci-cd-pipeline-design
description: Design CI/CD pipelines that are fast, reproducible and safe to deploy from — stage layout, caching, test pyramid in CI, artifact promotion across environments, approvals, secrets handling and rollback. Use when creating or restructuring a pipeline on any CI system (GitLab CI, GitHub Actions, Jenkins, Woodpecker) or when pipelines are slow, flaky or deploy untested builds.
license: MIT
---

# CI/CD Pipeline Design

## Goal
Every change is built once, tested at the right levels, and the **same artifact** is promoted through environments with explicit gates and a tested rollback.

## Inputs
- Repository layout, build tools, test suites and durations, environments, deployment targets, compliance requirements, current pipeline metrics (duration, failure rate, flaky tests).

## Procedure
1. **Stages**: lint and unit tests (minutes) → build artifact once (image or package, tagged by commit SHA, pushed by digest) → integration tests against the artifact → security scans (dependencies, image, secrets) → deploy to staging → smoke and end-to-end tests → gated deploy to production.
2. **Speed**: run independent jobs in parallel; cache dependencies keyed on lockfiles; run only affected parts in monorepos; target under 10–15 minutes for the merge request pipeline.
3. **Reproducibility**: pinned tool and base-image versions; no network-fetched scripts at build time without checksums; builds hermetic where feasible (see `supply-chain-provenance`).
4. **Promotion, not rebuild**: staging and production deploy the identical digest; configuration differs by environment variables or config files, not by rebuilding.
5. **Gates**: protected branches and tags; manual approval or change window for production where required; separation of duties for regulated systems.
6. **Secrets**: short-lived credentials via OIDC federation where the cloud supports it; protected variables only on protected refs; untrusted merge requests from forks never get deploy secrets.
7. **Deploy strategy**: rolling, blue-green or canary with automatic health checks; database migrations compatible with both versions (see `database-migrations`); one-command rollback to the previous digest.
8. **Flaky tests**: quarantine with an owner and deadline instead of blanket retries; track the flake rate.
9. **Observability**: pipeline duration, failure causes and deployment frequency, lead time and change failure rate (DORA metrics).

## Example fixture
```text
Current: build in each environment job (3 builds), tests after deploy to staging, prod deploy from any branch with a shared token.
```
Expected redesign: build once by digest, tests before deploy, prod only from protected tags with OIDC credentials and an approval gate.

## Acceptance checks
- Production deploys only artifacts that passed the earlier stages (digest traceable from merge request to production).
- Negative case: a pipeline from an unprotected branch or fork cannot access production credentials (test run shows variables absent).
- Rollback to the previous release was executed in staging and timed.

## Output
Pipeline design diagram, pipeline configuration changes, metrics before and after, rollback runbook.

## Safety
Changing production deploy jobs, protected variables or runner configuration requires approval. Test pipeline changes on a branch before merging.
