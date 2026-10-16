# Agent compatibility evidence matrix (XAH-205)

**Status: awaiting real client testing.** For reproducible isolated setup and observation templates, see [Client test kit](CLIENT_TEST_KIT.md). The fixture currently records `not_tested` for Claude Code, Codex, OpenCode and generic consumers. This is not a compatibility claim.

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

The evidence validator checks structure and explicit redaction acknowledgement; it cannot independently authenticate client observations. Real client execution and independent review are required before closing XAH-205.
