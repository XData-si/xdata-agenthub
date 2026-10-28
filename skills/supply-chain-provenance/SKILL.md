---
name: supply-chain-provenance
description: Establish build provenance for software artefacts — pinned inputs, SBOMs, signatures, attestations and verification at deploy time (SLSA-style). Use when hardening CI/CD release pipelines, publishing container images or packages, or deciding whether an artefact can be trusted.
license: MIT
---

# Supply-Chain Provenance

## Goal
Be able to answer for any deployed artefact: *which source, which build, which dependencies, who signed it*, and refuse to deploy artefacts that cannot answer.

## Inputs
- Build pipeline definitions, artefact types (container images, packages, binaries), registries and deploy tooling.
- Current dependency management (lockfiles, base images) and existing signing, if any.

## Procedure
1. **Pin inputs.** Lockfiles committed; container base images by digest (`image@sha256:…`); CI actions or templates by commit SHA or protected tag; toolchain versions explicit.
2. **Hermetic and reproducible where feasible.** The build fetches only declared dependencies; no `latest`; record build parameters.
3. **Generate an SBOM** per artefact (SPDX or CycloneDX, for example with Syft) and store it with the artefact.
4. **Sign artefacts** (for example Sigstore cosign with keyless OIDC identity, or a managed key in KMS). Keys never live in the repository.
5. **Attest provenance:** source repository, commit, builder identity, build instructions (SLSA provenance, in-toto attestations).
6. **Scan** the SBOM and image for known vulnerabilities (Grype, Trivy) with a defined policy: which severities block, how exceptions expire.
7. **Verify at deploy time.** Admission policy or deploy script checks signature, identity (issuer, subject) and digest; unsigned or unexpectedly signed artefacts are rejected.
8. **Protect the pipeline itself:** least-privilege CI tokens, protected branches and tags, review for pipeline changes, no untrusted code with access to signing credentials.

## Example fixture
```bash
cosign sign --yes registry.example.com/app@sha256:abc...
cosign verify registry.example.com/app@sha256:abc... \
  --certificate-identity-regexp 'https://ci.example.com/org/app/.+' \
  --certificate-oidc-issuer https://ci.example.com
# Negative test: verify an image pushed manually without signing → must fail and block deploy
```

## Acceptance checks
- Every production artefact is referenced by digest and has an SBOM and a signature.
- Deployment rejects an unsigned artefact (demonstrated negative test).
- Signing identity is restricted to the release pipeline on protected refs.
- The vulnerability policy and exception process are written down, with expiry dates.

## Output
Gap analysis against these steps (or SLSA levels), pipeline changes, verification policy and evidence of the negative test.

## Safety
Do not export signing keys or CI tokens for testing. Rotate credentials immediately if a pipeline compromise is suspected.
