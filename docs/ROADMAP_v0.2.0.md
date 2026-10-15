# XData AgentHub v0.2.0 roadmap (proposal)

Status: **planning**. v0.1.0 is released and immutable. This roadmap is not a commitment to ship all items.

## Product goal

Make the local-first catalog practical to maintain and update without losing local user changes, while improving agent compatibility evidence. Preserve Python 3.10+, dependency-free core, offline operation for local workflows, transparent provenance and human-controlled changes.

## P0 — foundation and compatibility

1. **Versioned catalog metadata**: define schema evolution, entry IDs, optional upstream revision/version, source, license, content digest and compatibility declarations. Maintain backwards compatibility with v0.1.0 catalogs. Provide validator tests and migration examples.
2. **Safe upgrade plan and dry-run**: detect locally modified installed files; show proposed add/update/skip/conflict actions. No silent overwrites. Preserve backups and offer documented rollback. Test interrupted updates and symlink/path traversal defenses.
3. **Agent compatibility matrix**: distinguish discovery, native invocation, direct SKILL.md consumption, negative-case behavior; record client versions, platforms, trace links and known limitations. Start with Claude Code, Codex, OpenCode. Avoid unsupported claims of native loading.
4. **Release quality gates**: cross-platform CLI/installer tests, schema fixtures, offline smoke tests, upgrade/rollback cases, and security audit. Native agent tests may require separately collected operator evidence.

## P1 — catalog experience

5. **Search and filtering**: filter by kind, tags, agent compatibility, license and provenance; deterministic text output plus optional JSON for scripting.
6. **Inspect and provenance**: show content hash, source, license, version, compatibility and local modification status when available.
7. **Catalog update workflow**: opt-in update from trusted catalog source, pinned revision/checksum, offline-first fallback and explicit approval for changes. Do not execute downloaded scripts.
8. **Documentation and migration**: examples for v0.1.0 -> v0.2.0, safe upgrades, backups, troubleshooting and security model.

## P2 — future candidates (not automatic v0.2.0 scope)

- Additional agent targets and declarative target adapters.
- Remote community catalogs and trust policy.
- Web catalog or GUI.
- Automated native runtime tests where supported by each client.

## Suggested phases

- Phase 1: schema + backward compatibility + acceptance fixtures
- Phase 2: dry-run, conflict detection, backup/rollback
- Phase 3: CLI filters, provenance and update workflow
- Phase 4: integration evidence, docs and release gates

## Definition of done

- Existing v0.1.0 commands remain functional or have documented migration.
- All writes to project paths are explicit, reversible where feasible, and protected from traversal/symlink attacks.
- Offline local workflows continue to function.
- Tests cover Linux, macOS and Windows; actual agent behavior claims have traceable evidence.
- No publishing or tagging v0.2.0 before final gates pass.

## Related evidence

- [v0.1.0 launch checklist](LAUNCH_CHECKLIST.md)
- [Runtime integration evidence](integration-evidence/2026-10-15-runtime-results.md)
