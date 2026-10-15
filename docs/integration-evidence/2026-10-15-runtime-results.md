# Runtime skill integration results (2026-10-15)

Scope: developer profile, local disposable workspaces, code-review skill only. Evidence supplied as terminal excerpts by the operator; raw machine logs not retained in this repository.

| Client | Version | Discovery | Skill usage | Negative test | Status |
|---|---|---|---|---|---|
| Claude Code | 2.1.301 | PASS | Agent reported native Skill invocation; direct trace not provided | PASS | Provisional |
| Codex CLI | 0.162.1 | PASS | Read local code-review SKILL.md in tool trace | PASS | Verified for tested scenario |
| OpenCode | 2.0.11 | PASS | Native Skill tool invocation visible | PASS | Verified for tested scenario |

All three identified a defect in a sample add function returning subtraction and proposed addition. Claude Code additionally reported executing the corrected function with add(2,3)==5. OpenCode ran using Nemotron 3.5 Super VL Free. The model versions for other clients were not recorded.

Verified means only the specified scenario was demonstrated. It does not certify every skill, every client version, or production safety. Claude Code requires an independently visible native Skill invocation trace to upgrade its status.

Next: collect redacted raw traces, model identifiers, and repeat tests with other skills. See docs/AGENT_RUNTIME_TESTS.md.

## MCP review: Codex CLI 0.162.1

Operator-provided transcript, 2026-10-15. The agent read `.agents/skills/mcp-review/SKILL.md` and `EXTENDED_SKILL_TESTS.md` via direct local file reads. The agent explicitly reported this was **not native skill loading**. No external service or MCP tool was called, and no files were modified according to the transcript.

Result: **PASS for skill-instruction consumption and synthetic scenario assessment; native loading NOT VERIFIED**.

Observed output identified missing tenant checks for invoice reads, shared service-account identity, destructive invoice deletion without approval, insufficient audit attribution, and unverified transport/authentication properties. It distinguished fixture assertions from real server findings and proposed eight negative tests, all explicitly **NOT RUN**. Production approval was withheld pending actual implementation evidence.

Limitations: transcript was supplied by the operator, not independently captured by this repository. No live MCP integration or negative-case execution was demonstrated.

## Security review: Codex CLI 0.162.1

Operator-provided transcript, 2026-10-15. Codex read `.agents/skills/security-review/SKILL.md` and `EXTENDED_SKILL_TESTS.md` using direct shell file reads, explicitly **not** a native skill-loader verification.

Result: **PASS for skill-instruction consumption and static analysis of the synthetic fixture; native loading NOT VERIFIED**.

The review identified concatenation of untrusted input into SQL as a potential injection risk, distinguished source-observed concatenation from conditional exploitability, noted unknown database adapter and input validation, and recommended adapter-specific parameter binding. It proposed a recording-fake-database test and isolated in-memory regression checks. No code or tests were executed and no files were modified according to the transcript.

Limitations: operator-supplied transcript only; no real application assessed, no exploitability demonstrated, and no regression test executed.

## Python testing: Codex CLI 0.162.1

Operator-provided transcript, 2026-10-15. Codex directly read `.agents/skills/python-testing/SKILL.md`, `AGENTS.md`, and `EXTENDED_SKILL_TESTS.md`; native skill-loader invocation was **not verified**.

Result: **PASS for skill-instruction consumption and regression-test execution**. In the disposable `calculator-regression-disposable` directory, the agent created `calculator.py` with intentionally incorrect subtraction and `test_calculator.py` asserting `add(2, 3) == 5`. It ran:

```sh
python -B -m unittest discover -s /tmp/xah-runtime-codex/calculator-regression-disposable -p 'test_*.py' -v
```

Observed test process exit code **1**, one test run, one expected assertion failure: `AssertionError: -1 != 5`. The agent reported no changes outside the disposable directory and did not fix the intentionally incorrect implementation. A failing regression test is the expected successful outcome for this fixture.

Limitations: operator-supplied transcript; no cross-client testing of this skill yet.

## Final three-client smoke test (operator transcript, 2026-10-15)

Fresh disposable workspaces initialized with the developer profile: `/tmp/xah-test-claude`, `/tmp/xah-test-codex`, `/tmp/xah-test-opencode`. Each contained `sample.py` with `def add(a, b): return a - b`. The operator provided session transcripts; independent raw log archives and exact client versions for this fresh run were not supplied.

| Client | Discovery | Correctness review | Missing-file negative case | Outcome |
|---|---|---|---|---|
| Claude Code | Reported two skills in session-native catalog; paths confirmed by filesystem find | Visible `Skill(code-review)` succeeded; correctly proposed `a + b`; no edits | Visible `Skill(code-review)` succeeded; checked missing `nonexistent.py`; no invented review or edits | PASS for three smoke scenarios |
| Codex | Reported two skills from native catalog, without reading skill files for discovery | Read `.agents/skills/code-review/SKILL.md` directly; correctly proposed `a + b`; no edits | Verified file missing; reused previously read skill instructions; no edits | PASS for three smoke scenarios; native invocation tool not observed |
| OpenCode (Nemotron 3.5 Super VL Free) | `code-review` and `documentation` visible in `<available_skills>`; explicit `search(namespace=skills)` failed; exact path confirmed by filesystem inspection | Visible native `Skill "code-review"` call, reported `skill(id="code-review")` returned skill content; correctly proposed `a + b`; no edits | Verified file missing; reused prior skill context without another invocation; no edits | PASS for review and negative case; discovery mechanism partially verified |

The OpenCode search-tool failure does **not** negate the successful native skill invocation in the next turn. Discovery-tool availability remains an evidence limitation, not a demonstrated incompatibility. The tests validate only the `code-review` skill and disposable local workflows; they do not establish comprehensive compatibility for all 31 skills, other models, or platforms. No release tag was created by this documentation update.
