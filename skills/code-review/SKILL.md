---
name: code-review
description: Review code changes for correctness, security, maintainability and test coverage with evidence-based findings. Use when reviewing a pull or merge request, a diff or a patch before merge.
---
# Code Review

## When to use
Before merging non-trivial code changes.

## Steps
1. Read requirements and diff; identify the trust boundary.
2. Check correctness, input validation, error paths and backward compatibility.
3. Check for credential exposure, injection, unsafe deserialization and unnecessary privileges.
4. Evaluate tests and suggest reproducible failing cases.
5. Report findings by severity with file/line evidence; distinguish facts from hypotheses.

## Output
Summary, blocking findings, non-blocking suggestions, test gaps and residual risks.

## Guardrails
Do not execute untrusted code, do not invent test results, do not silently change source files.
