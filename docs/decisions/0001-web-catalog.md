# Decision 0001: static catalog site instead of a localhost web server (XAH-307)

- Status: accepted (2026-10-28)
- Context: XAH-307 asked whether a read-only localhost UI adds enough value to justify a server in the CLI.

## Options
1. **Local web server in `xah`** (for example `xah serve`): interactive, but adds a listening socket, request handling
   and a larger attack surface to a dependency-free CLI meant for offline, inspectable use.
2. **Static site generated from the catalog** (`scripts/build_site.py`): one HTML file plus `catalog.json`, no server,
   no dependencies; published on GitHub Pages and buildable locally.
3. No UI: CLI only (`xah list`, `search`, `browse --json`).

## Decision
Option 2. The same generator serves both uses:

```bash
python3 scripts/build_site.py /tmp/agenthub-site   # offline copy
open /tmp/agenthub-site/index.html                 # or xdg-open; works from file://, no server
```

The public site is https://xdata-si.github.io/xdata-agenthub/, deployed by `.github/workflows/pages.yml`.

## UX specification (implemented)
- Header with project name, skill count and install commands.
- Client-side text filter across skill IDs and descriptions; empty sections hide while filtering.
- Cards grouped by the sections of `docs/CATALOG.md`, each with description, source link, install command and seals.
- Light and dark themes from the operating system preference.

## Security constraints
- No external scripts, styles, fonts or images; no network requests from the page.
- All catalog text is HTML-escaped (tested); only the inline filter script runs.
- Read-only: the page cannot install or modify anything.
- The CLI remains dependency-free and has no listening socket.

## Consequences
- No server code to maintain or secure. Interactive actions (install, verify) stay in the CLI where they are explicit.
- Revisit if users need features a static page cannot provide (for example comparing installed state), and then prefer
  extending `xah browse --json` over adding a server.
