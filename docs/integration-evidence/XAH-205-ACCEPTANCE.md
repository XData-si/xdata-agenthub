# XAH-205 — Operator-accepted validation decision

**Decision date:** 2026-10-16. **Disposition:** accepted by the test operator with documented limitations.

The operator explicitly reconfirmed reviewing the original test outcomes and authorized validation and issue closure on 2026-10-16 at **16:16:37 UTC**. This is an **operator acceptance**, not independent third-party verification of source traces.

## Formal evidence

- `tests/fixtures/agent_compatibility_evidence.json` contains nine sanitized, operator-reviewed records: discovery, native invocation and direct read for each of Claude Code 2.1.301, Codex CLI 0.162.1 and OpenCode 2.0.11.
- The evidence field `timestamp_utc: 2026-10-16T16:16:37Z` is the **operator's final acceptance timestamp**, **not the execution timestamp**. Execution timestamps were not recorded.
- Client baseline status is `tested` for the three tested clients and `not_tested` for `generic`.
- Negative scenarios D and E are summarized in [sanitized scenario excerpts](XAH-205-SANITIZED-SCENARIOS.md). Codex E was discovery-only and must not be represented as a native tool invocation failure.
- Models: OpenCode **LL Alpha Free** (operator-reported); Claude Code and Codex CLI **not recorded**. OS distribution release and permission settings **not recorded**.
- Operator reported credential remediation completed. No secret or raw transcript was committed.

## Limitations

The fixture validator checks structural completeness and `redacted: true` acknowledgement, not independent provenance or test runtime authenticity. No independent source-trace audit was completed. The operator explicitly accepted this limitation to close the current functional-compatibility task; any future audit should obtain sanitized source traces and independently validate them.

## Validation commands

```sh
python3 cli/compat_evidence.py tests/fixtures/agent_compatibility_evidence.json
python3 -m unittest discover -s tests -v
```

CI/test outcomes must be inspected separately; writing this decision document does not assert they have run.
