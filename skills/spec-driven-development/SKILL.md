---
name: spec-driven-development
description: Turn a feature request into a reviewed specification, technical plan and ordered task list before writing code. Use when starting a new feature, a multi-step change, or when requirements are vague or disputed.
license: MIT
---

# Spec-Driven Development

## Goal
Make intent explicit and reviewable **before** implementation, so that code, tests and review all trace back to agreed requirements. The specification describes *what* and *why*; the plan describes *how*; tasks are small, verifiable steps.

## When to use
- New features or changes touching several components.
- Requirements arrive as a chat message, ticket title or screenshot.
- Stakeholders disagree, or acceptance is unclear.

Skip for one-line fixes with an obvious, testable outcome.

## Inputs
- The request in the requester's own words, plus links to tickets and prior decisions.
- Repository conventions (`AGENTS.md`, `CONTRIBUTING.md`, existing ADRs).
- Constraints: deadlines, budgets, compliance, supported platforms.

## Procedure
1. **Specification (`spec.md`).** Problem statement, users, user stories, acceptance criteria written as observable behaviour (EARS form works well: *When <trigger>, the system shall <response>*), out of scope, open questions. No technology choices unless they are real constraints.
2. **Clarify.** List every ambiguity as a numbered question with options and a recommendation. Stop and ask when an answer changes scope, data model, security or cost; otherwise record the assumption explicitly.
3. **Plan (`plan.md`).** Architecture touch points, data model changes, interfaces, migration and rollback, test strategy, risks. Reference ADRs for significant decisions, or create one (`architecture-decision`).
4. **Tasks (`tasks.md`).** Ordered, each completable in one review: ID, description, files touched, dependency, verification command. Mark tasks that can run in parallel.
5. **Review gate.** The requester approves the spec; a maintainer approves the plan. Record approvals with date.
6. **Implement task by task.** Each commit or pull request references the task ID; tests derive from acceptance criteria.
7. **Close the loop.** When behaviour changes during implementation, update the spec first, then the code. At completion, mark every acceptance criterion with its evidence (test name, screenshot, log).

## Decision points
- Criterion cannot be tested → rewrite it or move it to non-goals.
- Plan needs an irreversible step (data deletion, public API removal) → explicit approval and rollback plan before tasks are scheduled.
- Spec grows past ~2 pages → split into separate specs with their own acceptance.

## Example fixture
```markdown
## Acceptance criteria
- AC-1 When a signed-in user requests an export, the system shall email a CSV link valid for 24 hours.
- AC-2 When the export exceeds 100 000 rows, the system shall split it into files of at most 100 000 rows.
- AC-3 (negative) When an unauthenticated client requests an export, the system shall return 401 and send no email.
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| The request is obvious, a spec is overhead. | Obvious requests hide the expensive questions (permissions, limits, errors). A half-page spec takes minutes; rework takes days. |
| I'll write the spec after the code. | A spec written afterwards documents what was built, not what was needed, and cannot catch misunderstandings. |
| Edge cases can wait for review. | Reviewers check what is in front of them. Negative criteria not written down are usually not tested. |
| The stakeholder approved it in chat. | Record the approval with the spec version; chat agreement is not traceable when scope is disputed later. |

## Acceptance checks
- Every acceptance criterion is observable and has at least one negative or boundary case.
- Every task maps to at least one criterion; no criterion lacks a task.
- Open questions are either answered or recorded as assumptions with an owner.
- Final report lists each criterion with evidence or `NOT VERIFIED`.

## Output
`spec.md`, `plan.md`, `tasks.md` (or the project's equivalent), approval record, and a traceability table at completion.

## Safety
Do not invent requirements, legal obligations or stakeholder approvals. Do not start irreversible work before the plan is approved.
