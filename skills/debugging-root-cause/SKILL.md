---
name: debugging-root-cause
description: Systematically find the root cause of a bug, failing test or production error through reproduction, hypotheses and evidence before changing code. Use when something fails and the cause is not yet proven.
license: MIT
---

# Debugging to Root Cause

## Goal
Fix the cause, not the symptom. Every fix is backed by a reproduction that failed before and passes after.

## Inputs
- Exact error text, stack trace, logs, failing command or test, and when it started.
- Environment: versions, configuration, data shape, recent changes (commits, deploys, dependency updates).

## Procedure
1. **Reproduce.** Write down the smallest command, request or test that shows the failure. If it is intermittent, measure the failure rate (for example 7 of 50 runs). No reproduction means the next step is collecting evidence, not editing code.
2. **Read the evidence completely.** The whole stack trace, the first error rather than the last, logs around the timestamp. Note what is *observed* separately from what is *assumed*.
3. **Find what changed.** Compare a working and a failing state: `git log` and `git bisect`, dependency lock diffs, configuration and environment differences, input data.
4. **Hypothesise.** List 2–4 candidate causes, each with a test that would confirm or eliminate it. Test the cheapest discriminating one first.
5. **Narrow down.** Add targeted logging or assertions, shrink the input, isolate components. Change one variable at a time and record results.
6. **Confirm the root cause.** You can explain the full chain from trigger to symptom, and a deliberate change to the suspected cause toggles the failure.
7. **Fix and protect.** Add a regression test that fails without the fix. Make the minimal change, then run the related test suites. Search for the same pattern elsewhere.
8. **Clean up.** Remove temporary logging, and document the cause in the commit or PR description.

## Decision points
- Three failed fix attempts → stop patching; return to step 2 and question the architecture or assumptions.
- The cause is in a dependency → pin or work around locally, and report upstream with the minimal reproduction.
- Only reproducible in production → collect read-only evidence; do not experiment on production without authorization.

## Anti-patterns
Changing several things at once; catching and ignoring the exception; adding retries or sleeps to hide races; "works on my machine" without an environment diff; declaring success without rerunning the original reproduction.

## Example fixture
```text
Symptom: test_invoice_total fails on CI only, passes locally.
Hypotheses: (1) timezone differs (CI=UTC) (2) locale decimal separator (3) test order dependency.
Discriminator: run locally with TZ=UTC → fails → hypothesis 1 confirmed; date boundary at 23:30 local time.
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| I know what it is, let me just fix it. | Fixing without a reproduction means you cannot prove the fix. Write the failing reproduction first; it takes minutes. |
| Adding a retry or sleep makes it pass. | That hides a race or dependency failure and makes it rarer, not gone. Find the mechanism. |
| It only fails on CI, so CI is broken. | CI differs in a specific, discoverable way (timezone, parallelism, versions). Diff the environments. |
| Three attempts failed, one more tweak will do it. | Repeated failed patches mean the mental model is wrong. Return to the evidence and question assumptions. |

## Acceptance checks
- A reproduction exists and its before/after result is reported exactly.
- The root cause statement explains the mechanism, not only the location.
- A regression test fails without the fix (shown or stated as NOT RUN with a reason).
- No unrelated changes are included.

## Output
Reproduction, evidence log, root cause, fix, regression test, and any remaining risk.

## Safety
Do not run destructive commands, alter production data or disable security controls to "see if it helps". Redact secrets from logs before sharing them.
