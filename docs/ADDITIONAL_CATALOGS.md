# Additional local catalogs

Organisations often need private skills next to the public catalog (internal runbooks, deployment procedures).
Instead of forking AgentHub, point the CLI at one or more additional **local** catalog files:

```bash
python3 cli/xah.py --catalog ~/org-skills/catalog.json list
XAH_CATALOGS=~/org-skills/catalog.json:~/team/catalog.json python3 cli/xah.py doctor
python3 cli/xah.py --catalog ~/org-skills/catalog.json add org-deploy --agent claude --scope user
```

## Rules

- `--catalog PATH` is a global option and can be repeated; `XAH_CATALOGS` holds paths separated by the OS path
  separator (`:` on Linux/macOS, `;` on Windows). Both are combined; the built-in catalog is always loaded first.
- An additional catalog uses the same schema as `registry/catalog.json` (v1 or v2) and is validated the same way.
- Item `path` values are relative to **the directory that contains the catalog file**, and must stay inside it
  (symlinks that escape it are refused).
- Item IDs must be unique across all catalogs. A duplicate is an error; private catalogs cannot shadow public entries.
  Use an organisation prefix (for example `acme-deploy`).
- A missing catalog file is an error, not a silent skip.
- Nothing is downloaded: additional catalogs are local files. Distribute them with your own version control.
- `catalog-refresh` only updates the built-in catalog.

## Minimal example

```text
org-skills/
  catalog.json
  skills/org-deploy/SKILL.md
```

```json
{"schema_version": 1, "items": [{"id": "org-deploy", "type": "skill", "name": "Org Deploy",
  "description": "Internal deployment procedure", "path": "skills/org-deploy/SKILL.md",
  "license": "Proprietary", "source": "Acme internal", "targets": ["claude", "codex", "opencode"]}]}
```

Declared `license` and `source` remain metadata only; `xah trust` does not verify them.
