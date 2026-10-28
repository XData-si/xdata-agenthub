# European digital sovereignty and legislation

AgentHub is maintained by [XData](https://xdata.si) in Slovenia (EU). This page states what the project itself does for
sovereignty, and which skills help European organisations meet their obligations.

## How AgentHub is built
- **No telemetry, no accounts, no hosted service.** The `xah` CLI is dependency-free Python that works offline; nothing is
  sent anywhere when you browse, install or verify skills.
- **Instructions only.** Skills are plain Markdown; they never ship code that runs on your machine.
- **Works with EU and self-hosted models.** Skills are model-agnostic Agent Skills; nothing requires a specific US AI
  provider. See `local-llm-serving` and `llm-gateway-routing` for running agents on EU-hosted or on-premise models with
  data-retention controls and masking of secrets and personal data.
- **Verifiable supply chain.** Package digests, Sigstore-signed releases and SLSA provenance ([VERIFYING.md](VERIFYING.md))
  let you mirror releases into your own EU infrastructure and prove they were not modified.
- **Mirror-friendly.** The repository is plain git; you can mirror it to an EU-hosted Git server and install from there
  (`xah --catalog` also supports private catalogs next to the public one, see [ADDITIONAL_CATALOGS.md](ADDITIONAL_CATALOGS.md)).
- **Honest limits.** The public repository and CI run on GitHub (a US provider), and signing uses the public Sigstore
  infrastructure. Organisations that need EU-only tooling should mirror signed releases internally and verify them there.

## Skills for EU obligations

| Topic | Skill |
|---|---|
| Data residency, jurisdiction, GDPR transfers, keys, exit plans | `eu-data-sovereignty` |
| Personal data handling (GDPR) | `data-privacy` |
| AI systems offered in the EU (Regulation (EU) 2024/1689) | `eu-ai-act-readiness` |
| Cybersecurity obligations of essential and important entities (Directive (EU) 2022/2555) | `nis2-readiness` |
| Software and connected products sold in the EU (Regulation (EU) 2024/2847) | `cyber-resilience-act` |
| Supply-chain evidence that NIS2 and CRA ask for | `supply-chain-provenance`, `dependency-audit` |
| Incident handling for 24 h / 72 h reporting | `incident-response`, `postmortem`, `runbook-authoring` |

Skills that meet the [EU Ready checklist](SEAL.md#eu-ready-checklist) carry the **EU Ready** seal.

These skills help prepare engineering evidence. They are **not legal advice**; obligations come from the official texts
and national transpositions, and dates can change through amendments.
