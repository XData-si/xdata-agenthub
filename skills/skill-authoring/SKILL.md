---
name: skill-authoring
description: Write or improve an agent skill (SKILL.md) so that agents load it at the right time and follow it reliably — trigger-focused description, scoped procedure, examples, acceptance checks and safety boundaries. Use when creating a new skill for this hub or a private catalog, or when a skill is ignored or misapplied.
license: MIT
---

# Skill Authoring

## Goal
A skill that an agent selects when — and only when — it is relevant, and that turns into consistent, verifiable work.

## Inputs
- The recurring task the skill should cover, examples of good and bad results, and the target clients (Claude Code, Codex, OpenCode or generic).
- Existing skills, to avoid overlap (`xah search <keyword>`).

## Procedure
1. **Scope one job.** A skill covers one kind of task (for example "review OAuth integrations"), not a whole domain. Split when the procedure branches into unrelated paths.
2. **Frontmatter.** `name` in lowercase-hyphen form that matches the directory; `description` states **what the skill does and when to use it**, with the words a user would actually type (technologies, symptoms, artefacts). Agents decide from the description alone whether to load the skill.
3. **Body structure** (see [`docs/SKILL_QUALITY_STANDARD.md`](https://github.com/XData-si/xdata-agenthub/blob/main/docs/SKILL_QUALITY_STANDARD.md)): Goal; When to use (optional); Inputs; Procedure with numbered, imperative steps and decision points; Example fixture; Acceptance checks including negative cases; Output; Safety.
4. **Be concrete.** Commands, thresholds, file names and formats instead of adjectives ("TLS 1.2+", "batch of 10 000 rows", "p95 latency"). Explain the why when a step is non-obvious, so the agent can adapt rather than follow blindly.
5. **Keep the main file short** (roughly under 150 lines); move long checklists, tables or templates into `references/` or `assets/` and link them, so they load only when needed.
6. **Make it verifiable.** Acceptance checks are observable (a test, a command output, a file) and include at least one negative case; ask the agent to report NOT RUN rather than guessing.
7. **Set boundaries.** What the skill must never do (production changes without approval, exposing secrets, running untrusted code), and when to stop and ask.
8. **Stay portable.** Plain Markdown; no client-specific syntax unless the skill targets one client; no hidden instructions, remote includes or scripts that run automatically.
9. **Test it** with the scenario in the fixture on at least one real client; record the client and version, observed behaviour and fixes (see `docs/AGENT_RUNTIME_TESTS.md`).

## Example fixture
```yaml
# Weak
description: Helps with databases.
# Strong
description: Plan and review schema and data migrations that deploy without downtime or data loss, using expand-contract, batching and tested rollback. Use when adding, renaming or removing columns, tables, indexes or constraints, or backfilling data.
```

## Acceptance checks
- The description names concrete triggers; a reviewer can predict three prompts that should and one that should not load the skill.
- Every procedure step is actionable; no step depends on unstated context.
- At least one negative acceptance check and an explicit safety section exist.
- `xah doctor` passes and the catalog entry matches the directory and frontmatter name.

## Output
`skills/<id>/SKILL.md` (plus optional `references/`), a catalog entry, and a short test record.

## Safety
Do not copy third-party skills without a compatible licence and attribution; do not embed credentials, internal hostnames or personal data in public skills.
