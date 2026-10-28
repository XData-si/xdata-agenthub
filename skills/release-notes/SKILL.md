---
name: release-notes
description: Write accurate, user-focused release notes and changelogs from commits, merged pull requests and issues — grouped changes, breaking changes with migration steps, security fixes, deprecations and known issues. Use when preparing a release, a changelog entry or customer-facing update notes.
license: MIT
---

# Release Notes

## Goal
Readers learn what changed for them, what they must do, and what risks remain — without reading commit logs.

## Inputs
- Version and release date, merged changes since the last release (pull requests, commits, issues), breaking changes, security advisories, known issues, audience (developers, operators, end users).

## Procedure
1. **Collect** changes since the previous tag; link each item to its pull request or issue.
2. **Classify** (Keep a Changelog style): Added, Changed, Deprecated, Removed, Fixed, Security. Drop internal-only refactors unless they affect behaviour or performance.
3. **Breaking changes first**: what breaks, who is affected, the exact migration steps with before/after examples, and how to detect impact.
4. **Security fixes**: describe impact and affected versions without exploit details; reference advisories or CVE IDs once public; coordinate timing with disclosure.
5. **Write for the reader**: describe the effect ("Exports now include the invoice number column"), not the implementation; keep each item to one or two sentences.
6. **Versioning**: semantic version consistent with the changes (breaking change → major, unless pre-1.0 policy states otherwise).
7. **Verify** every claim against the actual release build: feature flags enabled? migrations included? documentation updated?
8. **Known issues and upgrade notes**: workarounds and tracking links.

## Example fixture
```markdown
## [2.0.0] - 2025-11-03
### Breaking
- The `/v1/export` endpoint is removed. Use `/v2/exports` (asynchronous). Migration: replace synchronous calls with job creation + polling; see docs/exports.md.
### Security
- Fixed an authorization check in invoice downloads affecting 1.4.0–1.9.2. Upgrade recommended.
```

## Acceptance checks
- Every item links to a pull request or issue; every breaking change has migration steps.
- Negative case: a feature hidden behind a disabled flag is not announced as available.
- The version number matches the changes according to the project's versioning policy.

## Output
Changelog entry and release notes text, plus a short summary for announcements.

## Safety
Do not disclose unpatched vulnerability details, internal hostnames or customer names. Publishing release notes externally requires approval from the release owner.
