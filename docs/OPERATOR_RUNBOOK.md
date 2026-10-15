# Operator runbook (v0.2.0 development)

## Routine checks

Run from the repository root:

```sh
python3 cli/xah.py doctor
python3 -m unittest discover -s tests -v
python3 cli/xah.py status --target ./project
python3 cli/xah.py audit --target ./project
```

`doctor` checks catalog references and local package paths. `audit` is heuristic and not a security certification. `status` reports only manifest-tracked files.

## Backup / restore rehearsal (non-destructive example)

```sh
mkdir -p /tmp/xah-operator-demo
python3 cli/xah.py add code-review --target /tmp/xah-operator-demo
```

Create a complete backup of `/tmp/xah-operator-demo` using your approved backup tool, including hidden files. To test recovery, restore the backup **to a new empty directory** and compare the installed file and `.xah-installed.json` byte-for-byte with the backup; run `status` against the restored directory. Do not use this demo command against an existing project containing the same skill: `add` refuses existing destinations.

## Common failure modes

| Symptom | Cause to investigate | Safe response |
|---|---|---|
| `update --dry-run` exits 2 | Unmanaged, modified, missing, symlinked or differently owned file | Review diff and ownership; back up before manual resolution |
| `update --apply` exits 1 | Invalid path, manifest, I/O failure or interrupted transaction | Inspect error and backup; verify both files and manifest |
| `ROLLBACK INCOMPLETE` | Recovery write failed | Stop; restore entire project from independent backup |
| `status` says modified | Recorded SHA-256 differs from current bytes | Preserve user changes; do not overwrite blindly |
| `inspect` has no installed files | Item not tracked by this manifest | Check target and manifest; untracked copies are not detected |
| `catalog-refresh` refuses URL | Not HTTPS, redirect, missing revision or checksum mismatch | Verify full immutable revision and digest out of band |
| `doctor` fails after catalog refresh | Catalog references files absent from checkout | Restore previous catalog from backup or matching reviewed checkout |
| Native agent does not discover skill | Adapter path alone is not proof of runtime compatibility | Follow client-specific instructions and collect actual runtime evidence |

## Release operator checklist

- Freeze an immutable candidate commit SHA and record it; never use a moving branch name as evidence.
- Re-run required release validation on that exact candidate; save workflow URLs and platform matrix results.
- Review catalog changes, security findings, install/update rollback behavior and documentation.
- Collect real native-client evidence before making native compatibility claims. The compatibility framework alone does not meet that condition.
- Record approver and sign-off in release evidence; only then consider a new tag. Never rewrite `v0.1.0`.

## Related guides

[Migration](MIGRATION_v0.2.0.md) · [Update and rollback](UPDATE_DRY_RUN.md) · [Catalog refresh](TRUSTED_CATALOG_REFRESH.md) · [Compatibility evidence](AGENT_COMPATIBILITY_EVIDENCE.md) · [Release gates](RELEASE_GATES_v0.2.0.md)
