---
name: refactoring-safety
description: Restructure code without changing behaviour, using characterization tests, small reversible steps and explicit verification. Use when cleaning up, extracting modules, renaming or simplifying code that already works.
license: MIT
---

# Behaviour-Preserving Refactoring

## Goal
Improve structure while proving behaviour is unchanged. Refactoring and behaviour changes never share a commit.

## Inputs
- The target code and its callers (search all references, including dynamic use, reflection, configuration and templates).
- Existing tests and their coverage of the target.
- The motivation: readability, duplication, coupling, preparation for a feature.

## Procedure
1. **Define the boundary.** Write down which public behaviour must stay identical: return values, errors, side effects, performance budgets, log or metric names other systems depend on.
2. **Pin current behaviour.** If coverage is weak, add characterization tests that record what the code does now, including odd edge cases. Do not "fix" surprising behaviour here; note it for later.
3. **Plan small steps.** Each step is mechanical and independently revertible: rename, extract function, move, inline, introduce a parameter object, replace a conditional with polymorphism.
4. **Step, test, commit.** After every step run the relevant tests. Keep commits small with messages describing the transformation.
5. **Handle the public surface.** For exported APIs keep the old entry point as a deprecated wrapper, or coordinate all callers in one change set; never break external consumers silently.
6. **Compare.** Re-run the full suite, type checks and linters. For performance-sensitive code compare a benchmark before and after.
7. **Review the diff as a reader.** The diff should be explainable as a list of named transformations.

## Decision points
- A test fails after a "pure" refactor → revert that step; do not adjust the test unless it asserted implementation details.
- A real bug is discovered → finish or revert the refactor, then fix the bug in a separate commit with its own test.
- No tests are possible (for example legacy UI) → reduce scope, add a manual checklist and record the risk.

## Example fixture
```python
# Before: duplicated discount logic in two functions.
def price_member(p): return round(p * 0.9, 2)
def price_staff(p): return round(p * 0.8, 2)
# Characterization test first: price_member(10.005) == 9.0 (current rounding), price_staff(0) == 0.
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| It's only a rename, tests are unnecessary. | Renames break dynamic references, serialization and external consumers. Search and run the tests. |
| I'll fix this small bug while I'm here. | Mixing behaviour changes into refactoring makes both unreviewable and unrevertible. Separate commits. |
| Coverage is low, but the change is mechanical. | Low coverage is exactly when characterization tests are needed before moving code. |

## Acceptance checks
- Characterization tests exist for the touched behaviour and pass before and after.
- No behaviour change is mixed into refactoring commits.
- Every reference to renamed or moved symbols is updated (search results attached or summarised).
- Public interfaces are unchanged or have a documented deprecation path.

## Output
A sequence of small commits, test evidence, and a short note listing transformations and any deferred bugs.

## Safety
Do not delete code that appears unused without checking dynamic references, feature flags and external consumers. Avoid large automated rewrites without review.
