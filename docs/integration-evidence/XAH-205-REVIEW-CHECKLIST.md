# XAH-205 — Evidence review and security sign-off

This checklist supplements [operator observations](XAH-205-2026-10-16-operator-observations.md). The operator reported 15/15 successful functional scenarios on 2026-10-16. These are **not yet independently reviewed or authenticated compatibility evidence**.

## Immediate security action (outside GitHub)

The original OpenCode discovery transcript included a credential from a local `service.json`. Treat it as compromised: rotate/revoke it using the owning service's supported procedure, inspect relevant access logs if available, and confirm the replacement is not exposed. Do not paste the old or new value into an issue, PR, terminal transcript or chat. **Credential rotation cannot be performed from this repository.**

## Evidence reviewer checklist

- [ ] Confirm credential rotation/revocation, without disclosing the value.
- [ ] Review source transcripts privately; remove secrets, usernames, hostnames, home paths, account IDs and unrelated configuration.
- [ ] Confirm actual CLI versions: Claude Code 2.1.301, Codex CLI 0.162.1, OpenCode 2.0.11.
- [ ] Confirm OS release (e.g. `cat /etc/os-release`) and document kernel 7.0.0-31-generic, x86_64.
- [ ] Record model names and permission modes for each client; if unavailable, explicitly note the gap.
- [ ] Record per-scenario UTC timestamps from trustworthy local logs where available; do not invent timestamps from narrative descriptions.
- [ ] Preserve three distinct evidence methods: discovery, native invocation, direct read. Do not treat a file read as native invocation.
- [ ] Preserve Codex E caveat: nonexistent skill was rejected by catalog discovery; no native invocation failure was observed.
- [ ] Verify negative scenarios D and E from sanitized excerpts.
- [ ] Record reviewer identity/role, date and explicit approval, without sensitive identifiers.
- [ ] Only after reviewed excerpts are available, add the required entries to `tests/fixtures/agent_compatibility_evidence.json` with `redacted: true`, and mark the corresponding client `tested`.
- [ ] Run `python3 cli/compat_evidence.py tests/fixtures/agent_compatibility_evidence.json` and `python3 -m unittest discover -s tests -v`.
- [ ] Review the final PR and close #5 only after acceptance criteria are met.

## Evidence format

The fixture schema requires, for each of the three positive methods per client: `client`, `client_version`, `os`, `os_version`, `method`, `result`, `prompt`, `steps`, `evidence`, `redacted` and `timestamp_utc`. The `redacted` flag is an assertion that review **already happened**, not an instruction to redact later. Negative scenarios are documented separately with sanitized excerpts.

**Current fixture remains unchanged**: all client baselines `not_tested`, evidence array empty. This avoids falsely asserting redaction or reviewer approval.

## Local collection commands (safe metadata only)

Run outside client chat sessions; review output before sharing:

```sh
claude --version
codex --version
opencode --version
uname -srm
grep -E '^(NAME|VERSION_ID)=' /etc/os-release
date -u +%Y-%m-%dT%H:%M:%SZ
```

The current time command captures a **new** collection time; it does not retroactively establish test timestamps. Obtain model/permission information from client interfaces or locally reviewed session metadata, without exposing authentication data.

## Release gate

No change to immutable `v0.1.0`; do not claim a v0.2.0 release or close #5 on the basis of this checklist alone.
