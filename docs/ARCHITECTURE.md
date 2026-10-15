# Architecture

```text
registry/catalog.json -> CLI search/inspect -> local template file -> target project
                                               \-> audit (heuristic)
```

## Current architecture
- No backend, database, hosted service or network dependency.
- Registry contains vetted relative paths to checked-in templates.
- CLI resolves template paths under repository root, refuses missing or out-of-root paths and avoids overwrites.
- The installer copies the CLI and the catalog assets to a private user prefix; no sudo.

## Future architecture
Add a signed versioned registry, adapter interfaces and a static website. Avoid arbitrary remote execution; isolate any optional validators. Maintain SBOM, checksums and source metadata.

## Compatibility
Current markdown templates are generic and are not automatically converted into proprietary agent formats. The AGENTS.md example is suitable for projects that honor that convention; support must be verified per client/version.
