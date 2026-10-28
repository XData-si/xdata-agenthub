---
name: documentation
description: Update technical documentation so it matches verified implementation — READMEs, setup steps, configuration and changelogs. Use after changing behaviour, interfaces or setup, or when documentation is reported as outdated.
---
# Documentation

## Steps
1. Identify target audience and source of truth.
2. Verify commands and examples against code and supported versions.
3. Explain installation, configuration, failure modes, security and rollback.
4. Mark planned features as planned; do not present them as shipped.
5. Provide a concise change log and unresolved questions.

## Acceptance checks
- Every command and example in the changed documentation was run against the stated version, or is marked NOT RUN.
- Negative case: a feature that is planned but not shipped is not described as available.
- No secrets, internal hostnames or personal data appear in the diff.

## Output
Updated documentation with runnable examples and links to authoritative sources.

## Safety
Do not publish credentials, internal hostnames, personal data or unreleased security details in documentation. Mark planned features as planned. Do not run commands from documentation against production systems to "verify" them without authorization; use disposable environments. Publishing documentation outside the organisation (public site, customer portal) requires explicit approval.
