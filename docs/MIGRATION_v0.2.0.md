# Migration from v0.1.0 to v0.2.0 development main

**Scope:** This is a tested-command migration procedure for the development branch, **not** a claim that v0.2.0 has been released. Keep the immutable v0.1.0 tag for production rollback. Use Python 3.10+.

## Before changing anything

1. Stop other writers to the target project. Commit outstanding work and record the currently installed AgentHub revision (`git rev-parse HEAD`).
2. Back up the entire target project, **including hidden directories** (`.claude/`, `.agents/`, `.opencode/`) and `.xah-installed.json`. A version-control commit plus a separate filesystem backup is recommended.
3. Run the current `python3 cli/xah.py status --target ./project` and save its output. If the manifest does not exist (older installations), existing files are **unmanaged**; the updater will not adopt or overwrite them.
4. Run `python3 -m unittest discover -s tests -v` and `python3 cli/xah.py doctor` from the AgentHub checkout.

## Read-only preview

```sh
python3 cli/xah.py list
python3 cli/xah.py search --kind skill --agent codex --json
python3 cli/xah.py inspect code-review --target ./project --json
python3 cli/xah.py update code-review --target ./project --dry-run
```

Exit 0 means the plan has no conflicts; exit 2 means conflicts (including modified, missing or unmanaged files); exit 1 means invalid input or another error. **Do not** proceed on a conflict.

## Explicit update

```sh
python3 cli/xah.py update code-review --target ./project --apply
python3 cli/xah.py status --target ./project
python3 cli/xah.py audit --target ./project
```

Only explicitly selected items are updated. Review the diff and run project-specific tests. Catalog `targets` are declarations; they are not evidence that an agent has loaded a skill natively.

## Recovery / rollback

If a command reports an error, do not assume every write was rolled back. For ordinary exceptions, the updater attempts to restore original bytes and the manifest. It is **not crash-safe**, does not support concurrent writers, and may not preserve file metadata. If it reports `ROLLBACK INCOMPLETE`, stop immediately.

Restore the **whole project** from the backup (including `.xah-installed.json`), then rerun `status` and application tests. Do not restore only the manifest while leaving files from a newer update in place. For a Git-tracked project, use your recorded commit or backup with normal review; do not run destructive `git reset --hard` on a workspace with uncommitted changes.

## Catalog refresh is separate

`catalog-refresh` is an opt-in HTTPS JSON refresh requiring an explicit revision, trusted expected SHA-256 and `--approve`. It is not a package downloader. Review the catalog diff and run `doctor` after refresh. In offline environments, continue with the bundled catalog. See [trusted catalog refresh](TRUSTED_CATALOG_REFRESH.md).

## Compatibility and release status

The schema-v1 catalog remains valid; v2 metadata is optional and not evidence of publisher authenticity. Native Claude Code, Codex and OpenCode behavior must be tested and recorded separately. See [compatibility evidence](AGENT_COMPATIBILITY_EVIDENCE.md) and [release gates](RELEASE_GATES_v0.2.0.md). Do not tag v0.2.0 until final release SHA and native-client claims are signed off.
