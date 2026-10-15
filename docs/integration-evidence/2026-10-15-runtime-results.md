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
