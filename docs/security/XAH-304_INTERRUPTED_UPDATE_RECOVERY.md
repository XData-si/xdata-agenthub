# XAH-304 — interrupted update recovery runbook

**Status:** operational guidance; not proof of crash consistency.

## Scope and limitations

`cli/update_apply.py` uses staged file replacement and rolls back on ordinary Python exceptions. A killed process, host power loss, concurrent writer or filesystem failure can leave a partial update. The installed manifest may not reflect the on-disk files after an interrupted operation. No automatic crash-recovery journal or multi-process lock is currently guaranteed.

## Recovery procedure (operator-controlled)

1. **Stop further writes** from XAH and other automation against the affected target. Avoid re-running `update --apply` blindly.
2. **Preserve evidence**: copy the affected project and `.xah-installed.json` to a separate, access-controlled backup. Do not upload secrets or raw agent traces to public issues.
3. **Inspect states** with `python3 cli/xah.py status --target /path/to/project`. Treat `modified` and `missing` as indicators for manual review, not permission to overwrite.
4. **Compare expected files** with a trusted pre-update backup, the manifest SHA-256 records, and the local curated catalog. The manifest itself may be stale or compromised.
5. **Restore only from a verified backup** after confirming the intended owner and expected content. Do not automatically replace user-edited files.
6. **Run read-only checks**: `python3 cli/xah.py doctor`, `python3 cli/xah.py audit --target /path/to/project`, and `python3 cli/xah.py update ITEM_ID --target /path/to/project --agent generic --dry-run` (adjust agent to the original installation).
7. **Resume writes only after** a human reviews the differences, verifies no unexpected symlinks, and confirms the target is not being modified concurrently.

## Risk register

| Risk | Current status | Required follow-up |
|---|---|---|
| Process killed after one file replacement | Open | Fault-injection subprocess test and recovery evidence |
| Power loss / fsync directory durability | Open | Platform-specific durability design and test |
| Concurrent writers / TOCTOU | Open | Cross-process locking or descriptor-relative safe operations |
| Manifest and file set atomicity | Open | Transaction journal or recovery protocol |
| Backups contain credentials | Open | Private storage, redaction and retention policy |

## Release claim

The updater offers **best-effort exception rollback**, not a crash-safe transaction. Do not describe it as concurrency-safe or crash-consistent until independently verified and approved.
