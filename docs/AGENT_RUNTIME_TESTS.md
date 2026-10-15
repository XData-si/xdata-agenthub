# Agent runtime integration test protocol

The CLI unit tests confirm file placement, **not** that Claude Code, Codex or OpenCode discovers or follows a skill. Do not claim runtime compatibility without recorded evidence.

## Preparation

Use a disposable, non-sensitive directory per client. Record OS, client version, model, command line, current working directory, and date. Keep network and shell permissions minimal. Do not grant write access to production repositories.

```bash
mkdir -p /tmp/xah-runtime-claude /tmp/xah-runtime-codex /tmp/xah-runtime-opencode
python3 cli/xah.py init --agent claude --profile developer --target /tmp/xah-runtime-claude
python3 cli/xah.py init --agent codex --profile developer --target /tmp/xah-runtime-codex
python3 cli/xah.py init --agent opencode --profile developer --target /tmp/xah-runtime-opencode
```

Run each client **from its corresponding directory** using its documented CLI launch command. Avoid relying on a globally installed skill.

## Test A: discovery

Ask the agent: "List the project skills you can discover. Identify the path and name of code-review without performing a review." Record the exact response and whether the client provides a native skill listing or only infers a name from files.

## Test B: invocation

Create a disposable `sample.py` with a deliberately obvious bug, e.g. `def add(a, b): return a - b`. Ask: "Use the code-review skill to review sample.py. Identify the defect and propose a minimal fix. Do not modify files." Record whether the client explicitly loaded the skill, the observed behavior and any tool call evidence.

## Test C: negative case

Ask the agent to review a nonexistent file without fabricating its contents. The correct result acknowledges that the file is absent. Do not score an invented review as success.

## Evidence record

| Field | Value |
|---|---|
| Agent/client and version | |
| OS / Python | |
| Model | |
| Project directory | |
| Installed skill path | |
| Discovery evidence | |
| Invocation evidence | |
| Negative-case result | |
| Permissions granted | |
| Overall decision | PASS / FAIL / INCONCLUSIVE |

A **PASS** requires observable discovery, actual skill use (not merely generic task completion), and safe negative-case behavior. Mark **INCONCLUSIVE** if the client does not expose evidence of skill loading.

## Reporting

Store redacted transcripts and version details under `docs/integration-evidence/` via a pull request. Never commit API keys, user directories, access tokens, private prompts or confidential documents. Keep a separate result for each client/version. Re-run after significant client updates.
