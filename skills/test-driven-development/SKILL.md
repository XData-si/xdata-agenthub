---
name: test-driven-development
description: Implement features and bug fixes test-first with the red-green-refactor cycle, choosing the right test level and proving each test can fail. Use when writing new logic or fixing a bug where behaviour can be specified in advance.
license: MIT
---

# Test-Driven Development

## Goal
Let tests express the required behaviour before the implementation exists, so that every line of new code is justified by a failing test.

## Inputs
- Acceptance criteria or a bug reproduction.
- The project's test framework, conventions and how to run a single test quickly.

## Procedure
1. **Pick the next behaviour.** One small, concrete example from the acceptance criteria — the simplest case first, then boundaries, then errors.
2. **Red.** Write one test that describes the behaviour through the public interface. Run it and confirm it fails **for the expected reason** (assertion failure, not an import error or typo).
3. **Green.** Write the minimum code that makes the test pass. Hard-coding is acceptable briefly; the next test will force generalisation.
4. **Refactor.** Remove duplication and improve names with all tests green (see `refactoring-safety`).
5. **Repeat** with the next example. Add negative cases: invalid input, empty collections, limits, permission denied, timeouts.
6. **Finish.** Run the full suite, linters and type checks. Review whether the tests read like a specification.

## Choosing the test level
| Situation | Level |
|---|---|
| Pure logic, calculations, parsing | unit |
| Database queries, serialization, framework wiring | integration with real dependency in a container or in-memory equivalent |
| Critical user journeys | a few end-to-end tests |

Mock only at system boundaries you do not own (payment provider, email). Over-mocking produces tests that pass while the system is broken.

## Bug fixes
Write the test that reproduces the bug first, show that it fails, then fix. The test name describes the bug scenario.

## Example fixture
```python
def test_split_bill_rounds_remainder_to_first_person():
    assert split_bill(total_cents=1000, people=3) == [334, 333, 333]

def test_split_bill_rejects_zero_people():
    with pytest.raises(ValueError):
        split_bill(total_cents=1000, people=0)
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| I'll add tests after it works. | Tests written afterwards tend to assert what the code does, not what it should do, and are never seen failing. |
| This is too simple to test. | Simple code is cheap to test; the test documents the contract and catches the next change. |
| I saw the test pass, so it works. | A test that was never observed failing may not test anything. Show red before green. |
| Mocking everything keeps tests fast. | Over-mocked tests pass while the integration is broken. Mock only boundaries you do not own. |

## Acceptance checks
- Each new test was observed failing before the implementation (or the report states it was written after and why).
- Tests use the public interface and do not assert private implementation details.
- At least one negative or boundary test per behaviour.
- The suite is deterministic: no real network, clock or random values without control.

## Output
Tests and implementation in small commits, plus the exact commands and results.

## Safety
Never weaken or delete an existing test to make new code pass without explaining why the old expectation was wrong.
