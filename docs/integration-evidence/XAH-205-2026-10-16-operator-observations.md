# XAH-205 — Native client observations (operator-reported, 2026-10-16)

**Status: review pending.** This document summarizes manual, operator-provided client transcripts. It is **not** an independently verified execution log. Raw transcripts are deliberately excluded because one OpenCode discovery transcript exposed a credential in an unrelated local configuration file. **Rotate that credential** and re-check all source traces before publishing any excerpts.

## Environment and scope

- OS: Ubuntu Linux, kernel `7.0.0-31-generic`, x86_64 (operator-reported `uname -a`; Ubuntu release number not collected).
- Python: 3.14.7 (not a claim about the clients' embedded runtimes).
- Client versions: Claude Code **2.1.301**, Codex CLI **0.162.1**, OpenCode **2.0.11**.
- Date: **2026-10-16**; session transcript times supplied by operator. Precise UTC timestamps per scenario **not independently captured**.
- Client model names, permission settings, installation commands, independent reviewer sign-off: **not recorded**.
- Disposable workspaces: `/tmp/xah-client-tests/{claude,codex,opencode}`; each contained a `code-review` skill and `sample.py` with `def add(a, b): return a - b`.
- Skill locations: `.claude/skills/code-review/SKILL.md`, `.agents/skills/code-review/SKILL.md`, `.opencode/skills/code-review/SKILL.md`, respectively.

## Observed results

| Scenario | Claude Code | Codex CLI | OpenCode |
|---|---|---|---|
| A — native discovery | PASS: skill surfaced in startup project-skill catalog | PASS: skill in session's Available skills catalog | PASS: skill metadata surfaced natively; project skills directory watched |
| B — native invocation | PASS: `Skill(code-review)` loaded skill and applied review | PASS: explicit `$code-review` produced structured skill attachment; initial plain-language request had only read file | PASS: `Skill("code-review")` returned skill content; initial empty-argument call was retried |
| C — direct read | PASS: file tool read full SKILL.md | PASS: explicit shell read of SKILL.md | PASS: file tool read full 21-line SKILL.md |
| D — missing file | PASS: missing target acknowledged, no invented review | PASS: `test -e` confirmed absent | PASS: `test -e` and `find` confirmed absent |
| E — unknown skill | PASS: native `Skill` returned unknown-skill error | PASS **discovery-level only**: absent from catalog; no native invocation attempted | PASS: native `Skill` returned unable-to-load error with empty content |

**15/15 operator-reported scenario outcomes met their respective test expectations.** This is not 15 identical native-invocation checks: Codex E was verified through discovery only.

## Reproduction prompts and observations (redacted summaries)

1. **A / discovery** — Ask client to list discoverable project skills without opening files; identify `code-review` and discovery mechanism. Claude and Codex reported startup catalogs. OpenCode reported native metadata and project directory watcher, **but subsequently inspected unrelated configuration and exposed a credential in its original transcript**. Do not reuse that transcript.
2. **B / invocation** — Request `code-review` through client-native skill selection and review `sample.py` without edits/execution. Claude invoked `Skill(code-review)`. Codex's first attempt only read SKILL.md; a second explicit `$code-review` turn received a structured skill attachment. OpenCode invoked `Skill("code-review")` after an empty-argument attempt. All three proposed `return a + b`; no test execution was claimed.
3. **C / direct read** — Explicitly read the project SKILL.md from disk and report absolute path, frontmatter, sections and success. All three reported success, independently of native invocation.
4. **D / negative missing file** — Request review of `definitely-not-present.py`, first checking existence, without creating content or fabricating findings. All three reported absence and declined to invent a review.
5. **E / negative unknown skill** — Ask whether `definitely-not-installed` is available without creating or reading skills. Claude reported `Unknown skill` from native invocation. Codex checked only the catalog and stated no callable native selection tool was available for the negative attempt. OpenCode reported `Unable to load skill definitely-not-installed`, with empty content.

These are **paraphrased evidence summaries**, not verbatim command transcripts. They omit local usernames, hostnames, credentials, account identifiers and unrelated file contents. They cannot substitute for separately reviewed trace artifacts.

## Outstanding acceptance criteria / security gate

- [x] Operator provided real client versions and Linux kernel/architecture.
- [x] Five manual functional scenarios per client were reported.
- [ ] Record exact model, permissions, Ubuntu release, and UTC timestamps or explicitly approve gaps.
- [ ] Rotate credential exposed by the original OpenCode discovery trace.
- [ ] Independently inspect and redact source traces; verify they contain no secrets or personal data.
- [ ] Reviewer signs off on trace provenance and test-method distinctions, especially Codex E.
- [ ] Add schema-valid entries to `tests/fixtures/agent_compatibility_evidence.json` with `redacted: true` **only after** reviewed evidence excerpts exist; update baseline statuses only then.
- [ ] Run evidence validator and repository tests after fixture updates.

Keep issue #5 open until these are completed. Do not change the immutable v0.1.0 tag or publish v0.2.0 based on this draft.
