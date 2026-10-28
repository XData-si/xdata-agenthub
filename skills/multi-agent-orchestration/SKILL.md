---
name: multi-agent-orchestration
description: Design and review multi-agent systems — when to split work across agents, orchestrator and worker roles, task contracts, shared state, isolation of tools and credentials, budgets, human checkpoints and evaluation. Use when building agent teams (planner/coder/reviewer, research swarms, support triage) or when a multi-agent setup is slow, expensive or unpredictable.
license: MIT
---

# Multi-Agent Orchestration

## Goal
Use several agents only where it improves results or safety, with clear contracts between them, bounded cost and the same guardrails as a single agent.

## Inputs
- Task types and volumes, quality and latency targets, available models and tools, budget, risk of actions, existing single-agent baseline.

## Procedure
1. **Start with a baseline**: a single agent with good tools and prompts. Add agents only when evaluation shows a benefit (parallelism, specialised context, independent review).
2. **Choose a pattern**:
   | Pattern | Use when |
   |---|---|
   | orchestrator → workers | tasks decompose into independent subtasks (parallel research, per-file changes) |
   | pipeline | fixed stages (extract → transform → review) |
   | generator + reviewer | quality gate before output or action |
   | router | different task types need different tools or models |
3. **Task contracts**: each subtask has an explicit input, expected output schema, done criteria and limits — not free-form chat between agents.
4. **Context and state**: pass minimal, structured context; shared state in a store with ownership rules (who writes what); avoid agents silently overwriting each other's work (branches, locks, separate work directories).
5. **Isolation**: each agent gets only the tools and credentials for its role; reviewers cannot be overridden by the agent they review; outputs from one agent are untrusted input for the next (prompt-injection boundary).
6. **Budgets and termination**: per-task step, token, time and cost limits; maximum fan-out; detection of loops and repeated failures; a global kill switch.
7. **Human checkpoints** for irreversible or external actions (see `agent-guardrails`).
8. **Observability**: trace the full tree of agent calls with costs and decisions (see `llm-observability`).
9. **Evaluate** end-to-end against the baseline on the same task set (see `agent-evaluation`): quality, cost, latency, failure modes.

## Example fixture
```text
Design: planner splits a feature into 6 subtasks → 6 coder agents edit the same branch in parallel → reviewer approves.
Findings: parallel edits conflict (no isolation), reviewer reads only the final diff (no task contracts), no cost cap (one run used 3 M tokens).
Fix: one branch per subtask + merge step, contracts with tests per subtask, budget 300 k tokens per run.
```

## Acceptance checks
- The multi-agent design beats the single-agent baseline on the evaluation set, or is not adopted.
- Every agent role has a tool and credential list and a budget.
- Negative case: an injected instruction in one worker's output does not cause another agent to perform an unauthorized action (test).

## Output
Architecture with roles and contracts, budgets, guardrail mapping, evaluation results.

## Safety
More agents means more autonomous actions: keep approval gates for irreversible operations, and never let agents grant themselves or each other additional permissions. Agent systems that process personal data must follow GDPR, and AI systems offered in the EU may have AI Act obligations (see `eu-ai-act-readiness`, `dpia`).
