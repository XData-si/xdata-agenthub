# XAH-304 explicit recovery operator guide

Recovery is intentionally **manual and fail-closed**. It is not a power-loss-proof
database transaction and does not protect against non-cooperating writers or
adversarial filesystem races.

1. Stop all processes that could modify the target project. Preserve a copy of
   the project, installed manifest and `.xah-transactions` directory.
2. Inspect with `xah recovery --target PROJECT --json` and
   `xah recovery --target PROJECT --lock-status --json`.
3. If `.xah-update.lock` exists, **do not run rollback**. Verify ownership
   independently, including host and process identity. This CLI never removes
   the lock automatically. Do not remove a lock merely because a PID is absent.
4. Review the read-only `xah recovery --rollback-plan TXID --target PROJECT`.
   For a journal already fully rolled back, also run
   `xah recovery --resolution-check TXID --target PROJECT`.
5. Only after independent confirmation that no other writer is running, use
   `xah recovery --rollback TXID --target PROJECT`. The command acquires the
   cooperative writer lock and checks the transaction, backup hashes, current
   file hashes and manifest records before writes. It restores verified
   original bytes, removes only files matching the intended add digest, and
   reconciles tracked manifest entries. It then marks the journal `resolved`.
6. Inspect again and run `xah status --target PROJECT`.

**Important limitations:** the original installed manifest is not snapshotted.
The executor accepts only original/intended digest records for the same item.
A crash during rollback can leave a partially restored state; rerun only after
inspection. A failure after partial writes may require manual repair. The
cooperative lock does not protect against external writers or symlink races.
Journal backups may contain sensitive data; protect and retain them under
your organization's policy. Never delete journals or force-unlock blindly.

This workflow requires passing CI and an independent security review before
production use.
