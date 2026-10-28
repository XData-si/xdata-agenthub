# Runtime skill integration results (2026-10-28)

Scope: five skills from this release candidate — `agenthub-router`, `shell-script-review`, `threat-modeling`, `database-migrations` (reached via the router) and `code-review` (installed, discovery only). Each client used a disposable project directory with skills installed by `xah add --agent <client>` (project scope). Fixtures: `build.sh` and `design.md` exactly as in the skills' example fixtures. Traces were **captured by the maintainers' harness** in machine-readable form (`claude -p --output-format stream-json`, `opencode run --format json`); raw logs are not committed because they contain host-specific session metadata.

| Client | Version | Model | OS |
|---|---|---|---|
| Claude Code | 2.1.308 | claude-sonnet-5.5 (via an OpenAI-compatible gateway) | Linux x86_64 (container), Python 3.11 |
| OpenCode | 1.19.4 | claude-sonnet-5.5 (via the same gateway) | Linux x86_64 (container), Python 3.11 |

Claude Code ran with `--allowedTools Read,Glob,Grep,Skill` and Bash/Write/Edit/web tools disallowed. OpenCode ran with its default permissions in the disposable directory; it used read-only shell commands (`command -v shellcheck`, `ls`, `find`) and modified no files (directory listing compared before and after).

## Results

| Scenario | Prompt (abridged) | Claude Code 2.1.308 | OpenCode 1.19.4 |
|---|---|---|---|
| A discovery | "List the project skills you can discover…" | PASS — listed all 5 with paths; `init` event lists them as skills | PASS — listed all 5 with paths, separated one built-in skill |
| B1 `shell-script-review` | "Use the shell-script-review skill to review build.sh…" | PASS — native `Skill(shell-script-review)` call, then `Read build.sh`; found unguarded `rm -rf $BUILD_DIR/*`, `eval` injection, parsing `ls`, missing error handling, with line numbers; stated ShellCheck NOT RUN | PASS — native `skill(shell-script-review)` call; same four findings; ShellCheck absent, reported as manual review |
| B2 `threat-modeling` | "Use the threat-modeling skill to produce a threat model for design.md…" | PASS — native `Skill(threat-modeling)`; read `references/stride.md`; produced assumptions, Mermaid data-flow diagram, trust boundaries, STRIDE table | PASS — native `skill(threat-modeling)`; read `references/stride.md`; assumptions, boundaries, STRIDE table |
| B3 `agenthub-router` | "Rename users.fullname in production PostgreSQL… which skills, in which order? Do not perform the change." | PASS — `Skill(agenthub-router)` then `Skill(database-migrations)`; expand–contract over three releases, batched backfill, `lock_timeout`, backup before drop; reported `sql-review` as NOT RUN because it was not installed | PASS — `skill(agenthub-router)` then `skill(database-migrations)`; same plan |
| C negative | "Use shell-script-review to review deploy.sh" (file does not exist) | PASS — searched, reported the file is absent, did not invent a review, offered options | PASS — searched, reported the file is absent, did not invent a review |

**Status: Verified for the tested scenarios** on both clients: native skill loading is visible in the captured tool-call traces, behaviour followed the skills' procedures, and negative cases were handled safely. This upgrades the Claude Code status from "Provisional" in the [2026-10-15 results](2026-10-15-runtime-results.md), which lacked an independent native trace.

## Observations and limitations

- Both agents answered some scenarios in Slovenian because the host has a user-level instruction file with a language preference; this does not affect skill behaviour.
- The test tarball was created on macOS and contained `._*` AppleDouble files; Claude Code noticed and ignored them. Create archives with `COPYFILE_DISABLE=1`.
- OpenCode initially failed on every request because an unrelated, separately configured MCP server on the host exposed a tool schema with a top-level `oneOf`, which the model providers reject. The tests were re-run with that host-level MCP configuration disabled for the test process only. This is an environment issue, not a skill issue, but it is a useful warning: one invalid MCP tool schema can disable an entire agent.
- Codex CLI was not re-tested in this round.
- Verified means only these scenarios with these versions; it does not certify every skill, model or client version, nor production safety.
