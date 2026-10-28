---
name: docker-hardening
description: Harden Dockerfiles, images and container runtime settings — minimal base images, non-root users, pinned digests, capabilities and secrets handling. Use when writing or reviewing a Dockerfile or Compose file, or before deploying containers.
license: MIT
---

# Docker Hardening

## Goal
Reduce container attack surface without breaking application behavior.

## Review checklist
1. Identify base image and pin a specific release or digest; document update cadence.
2. Check runtime user with `docker image inspect IMAGE --format '{{json .Config.User}}'`. Prefer non-root where supported.
3. Inspect mounts, published ports, environment variables, network connectivity and writable directories.
4. Review Linux capabilities; drop unnecessary capabilities, disallow privilege escalation and use a read-only root filesystem when feasible.
5. Configure memory/CPU limits, health checks, restart policy and log rotation.
6. Move secrets out of Dockerfiles and image layers; use approved secret delivery.
7. Run vulnerability and SBOM tooling appropriate to the environment; record versions and findings.
8. Test startup, health, graceful shutdown, upgrade and rollback in a disposable environment.

## Example Compose baseline
```yaml
services:
  app:
    image: example/app:1.2.3 # replace with verified digest for production
    user: "10001:10001"
    read_only: true
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    tmpfs: ["/tmp:rw,noexec,nosuid,size=64m"]
    pids_limit: 256
    mem_limit: 512m
    restart: unless-stopped
```
This is an illustrative baseline; adjust writable paths, UID and probes to the actual image.

## Acceptance checks
- Application works under the intended non-root identity.
- No privileged mode, host PID/network or Docker socket mounts without documented exception.
- Only required ports and mounts are exposed.
- Rollback and data persistence are tested.

## Output
Risk-ranked findings, evidence, recommended changes and test results.
