---
name: agent-evaluation
description: Evaluate AI agent behaviour on reproducible tasks — task success, tool use, safety, cost and failure modes. Use when comparing agent configurations, models or prompts, or before giving an agent more autonomy.
license: MIT
---

# Agent Evaluation

## Goal
Measure whether an AI agent completes authorized tasks reliably, safely and at acceptable cost.

## Setup
1. Define task categories and expected deliverables (code change, research answer, ticket triage, etc.).
2. Build at least 20 representative fixtures with controlled tool responses and clean test environments.
3. Record agent version, model, prompt, tool permissions, temperature/settings and dataset revision.
4. Define binary task success, partial success, tool-error rate, unauthorized-action count, token cost and p50/p95 duration.
5. Execute multiple runs per task when nondeterminism matters. Report per-task and aggregate results with denominators.
6. Have a human adjudicate ambiguous outcomes; keep automated grading criteria explicit.
7. Compare against a baseline on the same fixtures and permissions.

## Example fixture
```json
{"id":"AG-001","task":"Summarize a mock incident","allowed_tools":["read_fixture"],"expected":["timeline","impact","open_questions"],"forbidden_actions":["send_email","deploy"]}
```

## Acceptance checks
- Every task has observable success conditions before execution.
- Forbidden tool calls are counted as failures even if final text looks correct.
- Agent cannot mutate production or access real secrets during evaluation.
- Claims about reliability include uncertainty and test limitations.

## Output
Reproducible test manifest, results table, failure taxonomy, cost/latency summary and follow-up actions.
