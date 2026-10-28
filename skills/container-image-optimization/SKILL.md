---
name: container-image-optimization
description: Make container images smaller, faster to build and pull, and with fewer vulnerabilities — multi-stage builds, minimal base images, layer ordering and cache mounts, .dockerignore, non-root runtime and reproducible tags. Use when images are large or slow to build, when scanners report many base-image CVEs, or when preparing images for production.
license: MIT
---

# Container Image Optimization

## Goal
A small, reproducible runtime image that contains only what the application needs at run time, builds quickly from cache and runs as non-root.

## Inputs
- Current Dockerfile, image size and layer breakdown (`docker history`, `dive`), build time, vulnerability scan results, runtime requirements (shell, CA certificates, time zone data).

## Procedure
1. **Measure**: size per layer, total build time, cold and warm cache; scan with Trivy or Grype and note base-image versus application findings.
2. **Multi-stage build**: compile and install build dependencies in a builder stage; copy only artifacts into the runtime stage.
3. **Minimal base**: distroless, `-slim` or Alpine (check musl compatibility for your language), or `scratch` for static binaries; pin by digest and update deliberately.
4. **Layer ordering**: copy dependency manifests and install dependencies before copying source code; use BuildKit cache mounts (`RUN --mount=type=cache,...`) for package caches.
5. **Context hygiene**: `.dockerignore` excludes `.git`, local environments, test data, secrets and build outputs.
6. **Remove build tools from runtime**: compilers, package managers (pip, npm) and shells where the application does not need them; clean package caches in the same layer that creates them.
7. **Runtime hardening**: `USER` non-root with a fixed UID; read-only root file system compatibility; health check; correct signal handling (exec form `CMD`, or a tiny init).
8. **Reproducibility**: no `latest` tags; `SOURCE_DATE_EPOCH` and pinned versions where supported; label images with source revision (`org.opencontainers.image.revision`).

## Example fixture
```dockerfile
FROM python:3.13
COPY . /app
RUN pip install -r /app/requirements.txt
CMD python /app/main.py
```
Expected findings: full base image (~1 GB), source copied before dependencies (cache busts on every change), `.git` and tests in image, root user, shell-form CMD.

## Acceptance checks
- Size, build time and vulnerability counts recorded before and after, with the same scanner version.
- The optimized image passes the application's smoke tests and runs as non-root.
- Negative case: a code-only change rebuilds without reinstalling dependencies (cache hit shown in build log).

## Output
Revised Dockerfile, `.dockerignore`, measurements and scan comparison.

## Safety
Do not push optimized images to production tags before tests pass. Never copy secrets into images, even into builder stages — use build secrets.
