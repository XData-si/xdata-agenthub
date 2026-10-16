# XData AgentHub v0.3.0 roadmap

**Status:** proposed implementation plan. v0.2.0 alpha is published and immutable. No tag or release for v0.3.0 is authorized.

## Product objective

Make the local-first agent capability catalog easier to discover, safer to extend, and more maintainable without sacrificing offline-first workflows, Python 3.10+ compatibility, dependency-free CLI core, explicit operator approval or honest native-client evidence.

## P0 — required foundation

| Issue | Deliverable | Acceptance |
|---|---|---|
| [XAH-301](https://github.com/XData-si/xdata-agenthub/issues/29) | CLI UX baseline and regression suite | Five operator walkthroughs; consistent help/errors; deterministic JSON; existing commands remain compatible |
| [XAH-302](https://github.com/XData-si/xdata-agenthub/issues/30) | Declarative target adapter contract | Versioned contract; fixtures; traversal and symlink defense; no unsupported semantic conversion |
| [XAH-303](https://github.com/XData-si/xdata-agenthub/issues/31) | Catalog trust and supply-chain hardening | Explicit allowlist, pinned SHA-256, negative security cases, no remote execution |
| [XAH-304](https://github.com/XData-si/xdata-agenthub/issues/32) | Security review and evidence traceability | Threat model, residual risks, reviewer decision, exact SHA CI evidence |
| [XAH-308](https://github.com/XData-si/xdata-agenthub/issues/36) | Migration, release gates and docs | Cross-platform matrix, rollback smoke, compatibility notes and human approval |

## P1 — user-facing experience

| Issue | Deliverable |
|---|---|
| [XAH-305](https://github.com/XData-si/xdata-agenthub/issues/33) | Catalog browsing, guided local discovery and actionable diagnostics |
| [XAH-306](https://github.com/XData-si/xdata-agenthub/issues/34) | Opt-in community catalog specification with trust boundaries |

## P2 — design gate only

[XAH-307](https://github.com/XData-si/xdata-agenthub/issues/35): assess optional localhost read-only web catalog; do not assume a GUI or add mandatory runtime dependencies.

## Delivery sequence

1. **Phase A:** XAH-301 baseline, XAH-304 security gap analysis.
2. **Phase B:** XAH-302 adapter contract and XAH-303 trust policy.
3. **Phase C:** XAH-305 guided discovery and XAH-306 catalog design.
4. **Phase D:** XAH-308 migration, full release validation and human sign-off.
5. **Optional:** XAH-307 decision after evaluating Phase C.

## Release boundaries

- No mutation of v0.2.0 release/tag.
- All writes require explicit approval and safe handling of locally modified files.
- No arbitrary remote code execution; catalog metadata is untrusted.
- Offline workflows remain usable.
- Native-client claims must be grounded in operator evidence and identify untested cases.
- CI success alone is not a substitute for security sign-off.
- No v0.3.0 tag/publication without explicit human authorization.
