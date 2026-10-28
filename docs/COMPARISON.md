# How AgentHub compares

An honest overview of the agent-skill ecosystem as of **October 2026**, so you can choose the right source. Facts change quickly; corrections are welcome via pull request. Star counts and catalog sizes are deliberately omitted because they change daily.

| Source | Type | Curation | Install | Executable content | Focus |
|---|---|---|---|---|---|
| **XData AgentHub** (this repo) | curated collection + CLI | maintainers review every skill in a PR; original content only | Claude Code plugin marketplace, `npx skills`, `xah` CLI | **none** — instructions only, gated in CI | engineering, security, operations, AI systems, EU compliance |
| [anthropics/skills](https://github.com/anthropics/skills) | official examples | Anthropic | Claude Code plugin marketplace | some skills include scripts | document handling, examples, the reference format |
| [obra/superpowers](https://github.com/obra/superpowers) | methodology framework | maintainer team | plugin installs for many agents | varies (check each skill) | opinionated development workflow (brainstorm → plan → TDD → review) |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | curated collection | maintainer-curated | `npx skills`, Claude Code marketplace, manual | varies (check each skill) | software delivery lifecycle |
| [skills.sh](https://skills.sh) (Vercel) | directory + leaderboard + CLI | open; usage-ranked | `npx skills add <owner/repo>` | depends on each repository | discovery across the ecosystem |
| SkillsMP and similar indexes | crawler of public GitHub skills | automated | manual download | depends on each repository | maximum breadth |
| ClawHub (OpenClaw) | open marketplace | open submissions | OpenClaw | varies | OpenClaw agents; affected by the 2026 "ClawHavoc" poisoning campaign |

## When AgentHub is the right choice
- You want skills you can **read completely in minutes** and that cannot execute code on their own.
- You need **production topics** (threat modeling, OAuth, supply chain, SLOs, incidents, MCP, local LLMs, EU AI Act) rather than prompts or demos.
- You must justify provenance to a security or compliance reviewer: every entry is original, MIT-licensed and listed in `registry/catalog.json`.
- You want to combine public skills with **private organisation skills** without forking ([additional catalogs](ADDITIONAL_CATALOGS.md)).

## When something else fits better
- You want a full opinionated workflow framework with subagents → superpowers.
- You need document-generation skills with scripts (PDF, spreadsheets) → anthropics/skills.
- You want the widest possible choice and will vet each skill yourself → skills.sh or an index.

## Using AgentHub safely alongside other sources
Treat every third-party skill like a dependency: read the full `SKILL.md` and any scripts, pin to a commit, prefer sources without executable content, and never follow a skill that asks you to download and run tools from a link. The `prompt-injection-defense`, `agent-guardrails` and `skill-authoring` skills in this repository describe the controls in detail.
