# XAH-304 — crash recovery journal design (proposal)

**Status:** design for review. No journal or automatic recovery is implemented by this document.

## Safety invariants

1. Never silently overwrite local edits or untracked files.
2. Recovery must be explicit and must fail closed when ownership, integrity or provenance cannot be established.
3. The lock `.xah-update.lock` is cooperative only. A stale lock must not be deleted automatically based on PID alone.
4. Each transaction must record intended relative paths and hashes before any destination replacement.
5. Journal metadata and backups must stay inside the target's trust boundary; symlinks and path escapes are refused.
6. A journal does not itself guarantee power-loss durability; fsync file *and directory* behavior requires platform-specific validation.

## Proposed transaction states

`prepared` → `applying` → `committed` → `cleaned`

On failure, `recovery_required` is a diagnostic state, not permission to roll back without verification.

## Proposed storage

```text
<target>/
  .xah-update.lock/
    pid
  .xah-transactions/
    <random-id>/
      journal.json
      originals/
      staged/
```

- Journal fields: `schema_version`, transaction ID, catalog item ID, agent, timestamp (diagnostic only), state, ordered file operations, relative paths, original SHA-256 (or null for add), intended SHA-256, backup SHA-256, and per-operation completion marker.
- Restrict permissions on journal directories. Do not place tokens, raw agent traces, or unredacted secrets in JSON metadata.
- Original file bytes may contain secrets: treat backups as sensitive, protect permissions and define retention.
- Write-ahead ordering: persist backup and journal, fsync relevant files and directories, then replace destination; persist progress markers after each operation.
- Validate the existing manifest and every destination immediately before applying; verify again during recovery.

## Proposed recovery CLI

`xah recovery status --target DIR` (read-only)

`xah recovery inspect TRANSACTION_ID --target DIR` (read-only)

`xah recovery rollback TRANSACTION_ID --target DIR --approve` (explicit, with hash checks)

`xah recovery finalize TRANSACTION_ID --target DIR --approve` (explicit, only if every intended file matches)

These commands are **not yet implemented**. No automatic lock removal.

## Recovery decision table

| Observed file | Journal expected | Action |
|---|---|---|
| Matches original digest | Original | Leave unchanged |
| Matches intended digest | Replacement | Eligible for verified rollback/finalization |
| Neither original nor intended | Unknown/local modification | Refuse automatic action; manual investigation |
| Symlink, path escape, missing backup | Unsafe/incomplete | Refuse automatic action |
| Manifest inconsistent with verified files | Partial transaction | Report and require explicit recovery |

## Implementation phases

1. Add schema validator and deterministic tests for malicious journal paths, symlinks, tampered backups and invalid state transitions.
2. Add write-ahead journal creation with safe atomic writes and directory fsync where supported.
3. Instrument `update --apply` to write progress markers and preserve journal on hard exit.
4. Add read-only recovery status/inspect.
5. Add explicit rollback/finalize with strong hash preconditions and backup retention policy.
6. Add subprocess hard-exit tests at every write boundary, then cross-platform CI and independent security review.

## Release gate

Do not claim crash consistency or unattended recovery until all phases are implemented, tested, and independently reviewed. The current `update --apply` still uses best-effort exception rollback.
