# Inspect metadata and provenance (XAH-208)

```sh
python cli/xah.py inspect code-review
python cli/xah.py inspect code-review --json
python cli/xah.py inspect code-review --target ./my-project --json
```

The existing human-readable inspect command still includes the source file's full text. New metadata distinguishes:

- **Computed locally:** SHA-256 of the catalog entry's referenced file. This proves only which local bytes were read.
- **Compared locally:** `digest_matches` compares those bytes against an optional catalog-declared digest. A match does **not** authenticate the catalog or upstream publisher.
- **Declared only:** source, license, version, upstream, targets and compatibility. These values are unverified metadata, not independent security or native agent runtime attestations.
- **Installed state:** optional `--target` checks manifest-tracked files belonging to the selected item, with `untouched`, `modified` or `missing`. An empty array means no matching tracked files, not proof that no untracked copy exists.

JSON is deterministic and suitable for scripts. The command is offline and read-only; it does not validate remote source identity or download content.
