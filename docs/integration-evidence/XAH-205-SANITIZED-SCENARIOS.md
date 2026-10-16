# XAH-205 — Sanitized scenario excerpts for review

**Provenance:** User-pasted, operator-reported client outputs in a ChatGPT conversation on 2026-10-16. The excerpts below are manually selected and sanitized; **no original logs are published**. This document is a review aid, **not independent verification** of runtime execution. Model reported for OpenCode: **LL Alpha Free** (operator recollection, not independently verified). Models for Claude Code and Codex CLI are **unknown**. Permission modes and precise per-test UTC timestamps were not collected. Do not infer a precise UTC timestamp from the conversation's displayed local times.

| Client | Version | A: discovery | B: native invocation | C: direct read | D: missing file | E: unknown skill |
|---|---|---|---|---|---|---|
| Claude Code | 2.1.301 | PASS | PASS | PASS | PASS | PASS |
| Codex CLI | 0.162.1 | PASS | PASS | PASS | PASS | PASS (discovery-only) |
| OpenCode | 2.0.11 | PASS | PASS | PASS | PASS | PASS |

## Claude Code — reported observations

- **A / discovery:** Startup available project skill catalog included `code-review`; agent reported discovery without opening SKILL.md.
- **B / native invocation:** Tool trace `Skill(code-review)` reported successful skill loading, followed by review of `sample.py`. Blocking finding: `return a - b`; proposed `return a + b`.
- **C / direct read:** File-reading trace opened project `.claude/skills/code-review/SKILL.md` and reported 21 lines with skill frontmatter and sections.
- **D / missing file:** Agent checked `definitely-not-present.py`, acknowledged absence, and declined to invent findings.
- **E / unknown skill:** `Skill(definitely-not-installed)` returned `Error: Unknown skill: definitely-not-installed`; agent reported no skill content loaded.

## Codex CLI — reported observations

- **A / discovery:** Native `Available skills` catalog listed project `code-review` under `.agents/skills/code-review/SKILL.md`, without manual file reading.
- **B / native invocation:** Initial request led to a **manual SKILL.md read** and is **not** counted as native invocation. On a second explicit `$code-review` turn, Codex reported a structured `<skill>` attachment with instructions and did not reopen SKILL.md; review proposed `return a + b`.
- **C / direct read:** Shell tool explicitly read `.agents/skills/code-review/SKILL.md`; agent reported success (exit code 0).
- **D / missing file:** Shell existence check reported `File does not exist: .../definitely-not-present.py`; agent declined to invent review findings.
- **E / unknown skill:** Agent checked session's native catalog and found no `definitely-not-installed`; explicitly reported **no native selection/invocation attempted**. This is **discovery-level rejection only**, unlike the Claude/OpenCode invocation errors.

## OpenCode — reported observations

- **A / discovery:** Session exposed project `code-review` metadata; agent cited native watcher for project `.opencode/skills`. **Original discovery transcript included an unrelated configuration credential; it is intentionally excluded in full.** Agent also manually read SKILL.md later in that discovery session.
- **B / native invocation:** After an empty-argument attempt, tool trace `Skill("code-review")` succeeded; agent reported receiving `<skill_content name="code-review">` and applied instructions to `sample.py`. Proposed `return a + b`, without executing or editing the file.
- **C / direct read:** `Explored — 1 read` opened `.opencode/skills/code-review/SKILL.md`; agent reported 21 lines, frontmatter, steps, output and guardrails.
- **D / missing file:** `test -e` returned `ABSENT`; `find` returned no match for `definitely-not-present.py`; agent declined to fabricate findings.
- **E / unknown skill:** Native `Skill("definitely-not-installed")` returned `{"error":{"type":"tool.execution","message":"Unable to load skill definitely-not-installed"},"content":[]}`; no instructions loaded.

## Reviewer assessment / remaining gaps

- **Observed functional coverage:** 15 operator-reported passing scenario outcomes, with the Codex E distinction above.
- **Sanitization of this file:** no credential values, home usernames, machine names, private service config or raw logs reproduced. **This does not establish that original traces have been fully redacted or independently reviewed.**
- **Credential response:** Operator stated on 2026-10-16 that remediation was completed. Rotation/revocation has **not been independently verified**; do not record it as independently verified.
- **Models:** OpenCode — **LL Alpha Free** (operator-reported); Claude Code — **unknown**; Codex CLI — **unknown**. Model identities have not been independently verified.
- **Missing:** independently verified original evidence provenance; permission settings; Ubuntu release; precise test timestamps; independent reviewer sign-off.
- **Fixture:** leave `tests/fixtures/agent_compatibility_evidence.json` unchanged until reviewer approval of source traces and redaction; `redacted: true` cannot truthfully be asserted merely because this summary is sanitized.

See [review checklist](XAH-205-REVIEW-CHECKLIST.md) and [operator observations](XAH-205-2026-10-16-operator-observations.md).
