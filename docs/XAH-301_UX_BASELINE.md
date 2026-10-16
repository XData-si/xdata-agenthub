# XAH-301 — CLI usability baseline

The first v0.3.0 iteration freezes the observable v0.2.0 CLI behavior before UX changes.

| Task | Command | Acceptance |
|---|---|---|
| Discover | `python3 cli/xah.py list` | Success and discoverable `code-review` |
| Filter | `python3 cli/xah.py search review --kind skill --json` | Valid, deterministic JSON array of skills |
| Inspect | `python3 cli/xah.py inspect code-review --json` | Structured provenance including computed SHA-256 |
| Preview | `python3 cli/xah.py init --agent claude --profile developer --target <empty-dir> --dry-run` | Prints proposed writes, leaves target unchanged |
| Diagnose | `python3 cli/xah.py doctor` | Catalog validation succeeds |

Negative cases: unknown item fails with useful error; invalid command reports usage.

## Execute

```bash
python3 -m unittest tests/test_ux_baseline.py -v
python3 -m unittest discover -s tests -v
```

These tests do **not** establish user-research results or native agent runtime compatibility. They are a reproducible behavioral baseline for future UX changes. They use only the Python standard library and no network access.
