# Before/after demos

Do AgentHub skills change what an agent actually does? These demos run the same task with and without a skill and
compare the answers against a rubric that is fixed in advance. Cases where the skill does not help are reported too.

| Demo | Skill | Fixture | What is planted |
|---|---|---|---|
| `shell` | `shell-script-review` | [`fixtures/shell/deploy.sh`](fixtures/shell/deploy.sh) | 7 issues: unguarded `rm -rf` on an empty variable, no `set -e`, predictable temp file, word splitting, `curl -k`, ignored health check, remote command injection |
| `migration` | `database-migrations` | [`fixtures/migration/context.md`](fixtures/migration/context.md) | rename a column on a 40M-row table during rolling deploys; 6 expected practices |
| `review` | `code-review` | [`fixtures/review/invoices.py`](fixtures/review/invoices.py) | 7 issues: SQL injection, two tenant-isolation breaks, credential logging, off-by-one pagination, missing 404, unvalidated input |

**Latest results:** [results/2026-10-29/RESULTS.md](results/2026-10-29/RESULTS.md). In short, a frontier model found
every planted issue with and without the skills. The skills changed how the work was reported (it said which tools
were not run, listed residual risks, asked for approval), not how much was found.

## Reproduce

Requirements: Claude Code on `PATH` with model access through the environment, and Python 3.10+.

```sh
demos/run.sh /tmp/demo-out 3                    # 3 demos x 2 conditions x 3 runs, read-only tools
python3 demos/extract.py /tmp/demo-out/raw demos/results/$(date +%F)
python3 demos/score.py demos/results/$(date +%F) --markdown
```

The harness:
- copies each fixture into a disposable directory;
- installs the skill only in the *skill* condition;
- gives every run an empty `CLAUDE_CONFIG_DIR`, so host instructions, memory and MCP servers cannot leak in.

Before you publish results, read the answers and record every scoring correction in `overrides.json`, with the
quoted evidence.

Answers are stored as plain `.txt`, verbatim. They are recorded agent output, not instructions, so they must not
look like Markdown documentation that an agent might load. They quote dangerous commands from the fixtures.

## Rules for honest demos

- Fix the rubric before the first run. Never change it after seeing the answers; label later observations as post-hoc.
- Use identical prompts in both conditions, and never name the skill in the prompt.
- Publish every run, including those where the skill made no difference or made things worse.
