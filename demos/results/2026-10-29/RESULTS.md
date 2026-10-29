# Before/after results (2026-10-29)

**Setup.** Claude Code 2.1.308, model `claude-sonnet-5.5` through an OpenAI-compatible gateway, Linux container. Three
runs per condition. Tools were limited to `Read, Glob, Grep, Skill`. Each run had an empty `CLAUDE_CONFIG_DIR`, so it had
no user instructions, memory, plugins or MCP servers (`mcp_servers: 0` in every trace). The prompts were identical in
both conditions and never named the skill. In the *skill* condition the skill was installed in the project with
`xah add <skill> --agent claude`. All 9 skill runs loaded it natively from the project directory (`skill_sources:
project`), not a built-in skill with the same name.

**Scoring.** We fixed the [rubric](../../rubric.json) before the first run and scored it with `score.py`. A maintainer
read every answer. Four pattern misses were corrected in [overrides.json](overrides.json), each with the quoted
evidence. All four were false negatives, two in each condition.

```
python3 demos/score.py demos/results/2026-10-29 --overrides demos/results/2026-10-29/overrides.json --markdown
```

| Demo | Condition | Runs | Items found (mean, min–max) | Skill loaded | Mean time | Mean cost |
|---|---|---|---|---|---|---|
| shell | baseline | 3 | 7/7 (7–7) | 0/3 | 22.7 s | $0.0682 |
| shell | skill | 3 | 7/7 (7–7) | 3/3 | 24.5 s | $0.072 |
| migration | baseline | 3 | 6/6 (6–6) | 0/3 | 21.5 s | $0.0652 |
| migration | skill | 3 | 6/6 (6–6) | 3/3 | 27.6 s | $0.0789 |
| review | baseline | 3 | 7/7 (7–7) | 0/3 | 15.4 s | $0.061 |
| review | skill | 3 | 7/7 (7–7) | 3/3 | 17.7 s | $0.0625 |

**shell** — runs that found each item (baseline / skill):

- S1 empty APP_NAME makes rm -rf wipe /var/www: 3 / 3
- S2 no set -e / unchecked cd: 3 / 3
- S3 predictable /tmp/release.tgz: 3 / 3
- S4 unquoted variables / word splitting in find loop: 3 / 3
- S5 curl -k disables TLS verification: 3 / 3
- S6 health check result ignored: 3 / 3
- S7 remote command built from local unquoted variables: 3 / 3

**migration** — runs that found each item (baseline / skill):

- M1 no in-place RENAME while old app versions run (expand-contract): 3 / 3
- M2 batched backfill: 3 / 3
- M3 lock_timeout or statement_timeout: 3 / 3
- M4 rollback plan: 3 / 3
- M5 backup or restore point before the destructive step: 3 / 3
- M6 verification before dropping the old column: 3 / 3

**review** — runs that found each item (baseline / skill):

- R1 SQL injection via f-string: 3 / 3
- R2 missing tenant check on single invoice (IDOR): 3 / 3
- R3 export returns all tenants: 3 / 3
- R4 Authorization header logged: 3 / 3
- R5 off-by-one: page 1 skips the first 100 rows: 3 / 3
- R6 missing row crashes instead of 404: 3 / 3
- R7 no input validation on page (negative, huge, non-integer): 3 / 3

Mean output tokens and tool calls per run: shell 2,498 / 2.0 without the skill and 2,720 / 2.7 with it; migration
2,739 / 1.0 and 3,735 / 2.0; review 1,691 / 3.0 and 2,087 / 3.3.

## What this shows

- **No difference in what was found.** The model found every planted issue in all 18 runs, with or without the skill.
  These fixtures are textbook problems, and a current frontier model already knows them, so we hit a ceiling. On tasks
  like these, a skill does not make this model find more bugs.
- **The skill costs a little more.** Runs with the skill took 8–28 % longer and cost 3–21 % more (about $0.002–0.014
  per run), mostly from loading and following the procedure.

## What differed (post-hoc; not part of the pre-registered rubric)

We noticed these differences only after reading the answers, so they are hypotheses for the next round, not results:

| Signal | Without skill | With skill |
|---|---|---|
| Shell review states that ShellCheck was **not** run (honest evidence) | 0/3 | 3/3 |
| Code review ends with an explicit "Residual risks" section | 0/3 | 3/3 |
| Migration plan requires approval before the production change | 0/3 | 2/3 |

Each one follows a step that the respective skill asks for: report which tools were and were not run, separate facts
from hypotheses, and get approval for production changes. If this holds, a skill buys **consistent process and
honest reporting**, not recall. That is still useful in CI and audits, but it is a smaller claim.

## Limitations

- One client, one model, three runs per condition, three seeded fixtures. Small models, local models and harder or
  ambiguous tasks may behave differently. That is the next round.
- Pattern scoring is a first pass. It produced 4 false negatives in 126 checks; a maintainer spot-check of the matched
  passages found no false positives, but we cannot rule them out.
- Raw stream-json traces are not committed because they contain host-specific session metadata. The committed
  [answers](answers/) (`.txt`) are the agents' final answers, verbatim, and [metrics.json](metrics.json) is extracted from the
  traces by `extract.py`.
