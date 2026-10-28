# XData AgentHub seal of approval

A seal is a maintainer's signed-off statement about **one exact version** of a skill. It is stored in
[`registry/seals.json`](../registry/seals.json) together with the skill's package digest. When the skill changes,
the digest changes, the seal becomes **stale** and CI fails until a maintainer reviews the new version and grants
the seal again. Seals ship inside signed releases (see [VERIFYING.md](VERIFYING.md)), so a seal can be checked
offline against the files you installed.

| Seal | Badge | Requirements |
|---|---|---|
| **XData Reviewed** | `reviewed` | 1. Passes the deterministic [skill security gate](../scripts/skill_security_check.py) (no executable content, hidden Unicode or comments, piped downloads, encoded blobs, shortened links, prompt-injection or exfiltration phrasing; a Safety section). 2. AI review verdict `pass`, or every finding resolved by a maintainer ([AI review](../scripts/ai_skill_review.py), advisory). 3. Maintainer review in a pull request. |
| **XData Verified** | `verified` | Reviewed, plus recorded runtime evidence for this version in at least one agent client (native skill loading, positive and negative scenario) under [`integration-evidence/`](integration-evidence/). |
| **EU Ready** | `eu-ready` | Reviewed, plus the EU checklist below. |

## EU Ready checklist
A skill is EU Ready when a maintainer confirms that:
1. It can be followed entirely with EU-hosted or self-hosted infrastructure — no step requires a non-EU service without
   an alternative.
2. Where it touches personal data, it applies GDPR principles (minimisation, purpose, retention, transfers) and does not
   ask to move personal data to third parties without a legal basis.
3. Where it touches AI systems, security obligations or software sold in the EU, it references the applicable EU law
   (AI Act, NIS2, Cyber Resilience Act, GDPR, DORA, Data Act) accurately, with dates, and tells readers to verify them.
4. It contains no telemetry, tracking or data collection, and works offline once installed.
5. The AI review reported `eu_ready: true` or a maintainer recorded why it is EU Ready anyway.

## Granting and checking

```bash
python3 scripts/seal.py check                                   # CI: every seal matches the current package digest
python3 scripts/seal.py list
python3 scripts/seal.py grant threat-modeling verified --by "XData maintainers" \
  --evidence docs/integration-evidence/2026-10-28-runtime-results.md
```

Only maintainers grant seals, in a pull request that shows the evidence. A seal is not a certification by any public
authority and does not guarantee that a skill is correct for your environment.
