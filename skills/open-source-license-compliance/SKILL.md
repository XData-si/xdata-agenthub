---
name: open-source-license-compliance
description: Check open-source licence compliance for software you distribute or offer as a service — dependency licence inventory (SBOM, SPDX identifiers), compatibility, copyleft obligations (GPL, LGPL, AGPL, MPL), attribution and notice files, and policy exceptions. Use before releasing software, shipping containers or devices, accepting new dependencies, or answering customer due-diligence questions. Not legal advice.
license: MIT
---

# Open-Source Licence Compliance

## Goal
Know every licence in what you ship, meet its obligations, and avoid surprises in releases, sales or acquisitions.

## Inputs
- How the software is delivered (SaaS, on-premise, mobile app, container image, device firmware), dependency manifests and lockfiles, container images, existing licence policy, your own outbound licence.

## Procedure
1. **Inventory**: generate an SBOM including licences (Syft, ScanCode, ORT or package-manager tools); include container base images and vendored code.
2. **Normalise** licences to SPDX identifiers; flag unknown, custom or missing licences for manual review.
3. **Apply policy** by distribution model:
   | Licence family | Typical obligations |
   |---|---|
   | permissive (MIT, BSD, Apache-2.0) | keep copyright and licence notices; Apache-2.0 also NOTICE file and patent terms |
   | weak copyleft (LGPL, MPL-2.0) | share modifications of the licensed files or library; allow relinking (LGPL) |
   | strong copyleft (GPL) | when distributing, provide corresponding source of the combined work under GPL |
   | network copyleft (AGPL) | offering modified software over a network triggers source-sharing to users |
   | source-available / non-commercial | often not open source; check restrictions on use |
4. **Check compatibility** with your outbound licence and business model; record decisions for borderline cases.
5. **Fulfil obligations**: third-party notices file, licence texts in distributions and images, source offers where required, attribution in apps' "about" screens.
6. **Gate new dependencies**: CI check against the policy (deny lists, review lists).
7. **Contributions**: confirm your own project's licence, contributor terms (DCO or CLA) and that copied code snippets are compatible.

## Example fixture
```text
SaaS product adds a modified AGPL-3.0 PDF library to its backend.
Finding: modification + network use → obligation to offer the modified source to users; decide: publish changes, replace library, or obtain a commercial licence.
```

## Acceptance checks
- SBOM with licences exists for the release artifact, with no unknown licences left unreviewed.
- Third-party notices are included in the shipped artifact (checked in the built package or image).
- Negative case: CI rejects a test dependency with a denied licence.

## Output
Licence inventory, policy decisions, notices file, CI policy check, open legal questions.

## Safety
This is not legal advice; involve counsel for incompatible licences, commercial licensing and acquisitions. Do not remove licence or copyright notices from third-party code.
