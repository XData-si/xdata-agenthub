# CLI search filters and JSON (XAH-207)

`xah search [query] [--kind KIND] [--tag TAG] [--agent CLIENT] [--license LICENSE] [--provenance TEXT] [--json]`

Examples:

```sh
python cli/xah.py search review --kind skill
python cli/xah.py search --agent codex --license MIT --json
python cli/xah.py search --provenance "XData" --json
python cli/xah.py search no-match --json
```

All filters are combined with AND. Kind, tag, agent and license match case-insensitively and exactly; provenance is a case-insensitive substring of the catalog's `source` field. Free-text search uses a case-insensitive substring of the serialized item metadata (preserves previous broad search behavior). Results are sorted by stable item ID; empty JSON results are `[]`. No network calls or new dependencies.

**Important:** `--agent` filters catalog-declared `targets`, not observed runtime compatibility. `--provenance` filters catalog source descriptions; it does not establish supply-chain trust. In schema-v1 catalogs without tags, `--tag` correctly yields no matches.

The existing `xah list` and plain `xah search review` commands continue to work.
