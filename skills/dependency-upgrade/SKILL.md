---
name: dependency-upgrade
description: Plan and execute major dependency, framework or runtime upgrades in verified incremental steps with changelog review and rollback. Use when bumping a framework major version, language runtime, base image or a dependency with breaking changes.
license: MIT
---

# Dependency and Framework Upgrades

## Goal
Reach the target version with every intermediate step green, and known breaking changes handled deliberately rather than discovered in production.

## Inputs
- Current and target versions, lockfiles, and the support or end-of-life dates driving the upgrade.
- Upstream changelogs, migration guides and deprecation lists.
- Test suite health and coverage of affected areas.

## Procedure
1. **Baseline.** Record that the current suite is green; note flaky tests separately so they are not blamed on the upgrade.
2. **Read upstream notes** for every version between current and target. Extract a checklist: breaking changes, removed APIs, new defaults (security, serialization, timezones), minimum runtime versions, peer dependency changes.
3. **Map impact.** Search the codebase for each removed or changed API. Estimate the work per item.
4. **Order the path.** Upgrade one major version at a time when deprecations are removed between majors. Upgrade the runtime separately from the framework where possible.
5. **Fix deprecations first** on the current version, so the version bump itself is small.
6. **Bump and adapt.** Update the lockfile, apply codemods if the project provides them, and fix compile, type and test failures. Keep commits per concern.
7. **Verify beyond unit tests.** Run integration and end-to-end tests, a smoke test of the built artefact or image, performance comparison on critical paths, and a container or OS vulnerability scan.
8. **Release safely.** Canary or staged rollout; keep the previous artefact deployable; monitor error rate and latency.

## Decision points
- A transitive dependency blocks the upgrade → check for a compatible release, temporarily pin or override, and record the reason and an expiry.
- An upstream bug is found → minimal reproduction, report upstream, and pin to the last good version.
- Upgrade too large for one change → feature flags or adapters that let old and new paths coexist.

## Example fixture
```text
Upgrade: web framework 4.x -> 6.x (runtime 18 -> 22)
Step 1: runtime 18 -> 20 (framework 4.x supports it) — suite green
Step 2: fix 14 deprecation warnings on 4.x
Step 3: framework 4 -> 5 (codemod), step 4: 5 -> 6, step 5: runtime 20 -> 22
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| Let's jump straight to the latest major. | Skipping majors skips the deprecation warnings that tell you what will break. Step through versions. |
| The changelog is long, the tests will tell us. | Tests do not cover changed defaults (timezones, security, serialization). Read the breaking-change list. |
| Pin the transitive dependency forever. | Pins without an owner and expiry become the next vulnerability. Record why and when to remove them. |

## Acceptance checks
- Every breaking change from the upstream notes is listed with its status: handled, not applicable, deferred.
- No new deprecation warnings are introduced; existing ones are reduced or documented.
- Test, build and smoke results reported per step.
- The rollback artefact and procedure are identified.

## Output
Upgrade plan, per-step commits or pull requests, a breaking-change checklist and verification evidence.

## Safety
Do not update production lockfiles or base images outside review. Verify package names and sources to avoid typosquatted packages (see `dependency-audit`).
