# XAH-205: Native client test kit

This kit **does not run** Claude Code, Codex or OpenCode. It prepares disposable workspaces and observation templates for an operator who has those clients installed. A successful preparation or CI job is **not evidence of native compatibility**.

## 1. Prepare offline workspaces

From the repository root:

```sh
python3 scripts/prepare_client_tests.py --output ./local-client-tests
```

Choose a fresh empty output directory outside production repositories. The script refuses nonempty destinations and uses the local catalog only. It creates one project each for `claude`, `codex` and `opencode`, with `code-review`, a deliberately defective `sample.py` and an `observations.template.json`. Keep these generated observations **local** until reviewed for secrets and privacy.

## 2. Run each native client yourself

Open a terminal in `local-client-tests/claude`, `local-client-tests/codex` and `local-client-tests/opencode`, respectively. Record the actual executable version, model and OS. Launch the installed client using its currently documented command and supported authentication. Do not use production credentials or allow autonomous writes.

For each client, follow the prompts in its observation template, in this order:

1. **Discovery:** client identifies `code-review` without being pointed at its path. Inspect actual skill-discovery evidence, not generic claims.
2. **Native invocation:** use the client's documented skill invocation mechanism. Observe skill loading, not merely a plausible review of `sample.py`.
3. **Direct read:** explicitly open the installed `SKILL.md`. This checks file access only.
4. **Negative missing file:** ask about `definitely-not-present.py`. The client must acknowledge its absence.
5. **Negative unrelated skill:** request `definitely-not-installed` without inventing it.

Capture exact commands/prompts, client version, model, OS, permission settings, timestamps, observed outputs and trace links where available. Mark results `pass`, `fail` or `blocked` only after observation. If no native skill-load trace exists, report `blocked` or inconclusive rather than claiming native support.

## 3. Submit evidence, not claims

Redact transcripts and remove usernames, home directories, tokens, API keys, project secrets and sensitive prompts. Convert observations to the schema in `tests/fixtures/agent_compatibility_evidence.json` (methods: `discovery`, `native_invocation`, `direct_read`). Record negative-case results in redacted supporting trace documents under `docs/integration-evidence/`, linked from the evidence entries. Only set a client's status to `tested` after its full test suite is actually run and reviewed.

```sh
python3 cli/compat_evidence.py tests/fixtures/agent_compatibility_evidence.json
python3 -m unittest discover -s tests -v
```

The evidence validator checks schema and redaction acknowledgement, not whether a client actually performed the claimed actions. Independent review is required. **Keep issue #5 open until real client/version/OS results, negative cases and redacted traces have been submitted and reviewed.** Do not alter the `v0.1.0` tag or claim a v0.2.0 release from test-kit CI.
