# Update dry-run (XAH-203)

Preview a tracked resource against the current local catalog:

```sh
xah update code-review --target ./my-project --dry-run
```

This command **never writes files**, and requires the explicit `--dry-run` flag. It prints one deterministic, path-sorted action per source file:

- `add`: destination is absent and not tracked.
- `skip`: tracked file is unchanged and matches the bundled source.
- `update`: tracked file matches its recorded SHA-256, but bundled source differs.
- `conflict`: unmanaged destination, modified tracked file, missing tracked file, symlink, or different owner.

Exit code `2` means at least one conflict. Exit code `1` means invalid arguments, unsafe paths or malformed manifest. No automatic overwrite or update is implemented in XAH-203; apply and rollback belong to later milestones.

The plan uses the currently bundled local source, so it is offline and deterministic for a fixed catalog and target. It does not contact upstream registries.
