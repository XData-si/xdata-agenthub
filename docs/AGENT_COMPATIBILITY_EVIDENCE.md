# Agent compatibility evidence matrix (XAH-205)

**Status: operator-accepted manual testing completed on 2026-10-16.** The fixture contains nine sanitized positive-method records (discovery, native invocation and direct read) for Claude Code 2.1.301, Codex CLI 0.162.1 and OpenCode 2.0.11; all three are marked `tested`. Generic remains `not_tested`. The operator reported 15/15 passing scenarios, including negative checks. This is **operator-accepted evidence, not an independently audited runtime certification**. The recorded UTC timestamp is operator acceptance time, not original test execution time. See [acceptance decision](integration-evidence/XAH-205-ACCEPTANCE.md), [sanitized scenarios](integration-evidence/XAH-205-SANITIZED-SCENARIOS.md) and [client test kit](CLIENT_TEST_KIT.md).

For each client, capture the exact client version, operating system and version, date, and installation mode (`xah add code-review --agent claude|codex|opencode|generic --target <temporary-project>`). Run these three separate checks:

| Method | Reproducible test | Pass criterion |
|---|---|---|
| discovery | Ask the client to list available project skills without naming the skill | Client independently identifies the installed skill |
| native_invocation | Invoke the installed skill using that client's documented native syntax | Client recognizes and executes the installed skill as a skill |
| direct_read | Explicitly ask the client to open the installed `SKILL.md` path | Client reads the file, regardless of skill discovery support |

Also test negative cases: absent skill, malformed frontmatter, unrelated skill, and a renamed/unrecognized skill path. Record the exact prompt and reproduction steps. Mark each outcome `pass`, `fail` or `blocked`. Do **not** infer native support from a successful direct file read.

Store redacted excerpts only, without tokens, account identifiers, private prompts or user data. Add actual test records to `tests/fixtures/agent_compatibility_evidence.json`; set a client's baseline to `tested` only after recording its observations. Run:

```sh
python cli/compat_evidence.py tests/fixtures/agent_compatibility_evidence.json
python -m unittest discover -s tests -v
```

The evidence validator checks structure and explicit redaction acknowledgement; it cannot independently authenticate client observations. XAH-205 was closed on operator acceptance with documented limitations. Independent review of original traces was not completed; a passing validator does not authenticate runtime execution.
