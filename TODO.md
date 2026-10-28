# TODO — What remains before a public launch

## P0 — must do
- [x] Move this scaffold into a dedicated **public** GitHub repository; confirm ownership and visibility.
- [ ] Review name and branding with XData; create original logo and social preview (1280×640).
- [ ] Run smoke tests on Linux, macOS and Windows (WSL); test Python 3.10–3.13.
- [ ] Perform security review of installer, path handling and untrusted Markdown content.
- [ ] Choose licensing and obtain clearance for every third-party item before importing it.
- [x] Establish automated CI unit-test workflow.
- [ ] Add release automation, tags and checksums.
- [ ] Validate that CLI installs into an isolated target and does not overwrite existing files.
- [x] Create GitHub issue templates.
- [ ] Enable Discussions, set repository topics and homepage in GitHub settings.

## P1 — compelling product
- [x] Add 25+ original skills (61 currently).
- [ ] Complete editorial review of every skill for domain-specific examples, fixtures and acceptance checks (substantial first pass committed).
- [x] Add path-based skill installers for Claude Code, Codex and OpenCode with unit tests.
- [ ] Verify actual client discovery in supported versions; implement semantic adapters where needed.
- [x] Add basic `xah init` starter profiles and dry-run mode.
- [ ] Add interactive stack builder, richer profiles and agent-specific adapters.
- [ ] Add provenance manifests, license metadata and version pinning.
- [ ] Implement meaningful security scanning (the current audit is only a simple heuristic).
- [x] Publish categorized Markdown catalog and documentation.
- [ ] Build a browsable searchable website.
- [ ] Add offline fixture-based tests, schema validation and JSON output.

## P2 — growth
- [x] Claude Code plugin marketplace (`.claude-plugin/marketplace.json`) with topic bundles; `agenthub-router` meta-skill.
- [ ] Verify `npx skills add XData-si/xdata-agenthub` and record evidence; appear on the skills.sh directory.
- [ ] Submit the marketplace to Anthropic's plugin directory and to curated awesome lists (follow each list's rules).
- [ ] Mark the first skills **Verified** with recorded runtime evidence (Claude Code, Codex, OpenCode).
- [ ] Add "common rationalizations" sections to workflow skills (reasons agents skip steps, and the rebuttal).
- [ ] Publish a static catalog site (GitHub Pages) generated from `registry/catalog.json`.
- [ ] Tag a release with checksums and release notes; publish a social preview image.
- [ ] Publish demo video/GIF, benchmark reproducibility notes and honest comparison matrix.
- [ ] Prepare Show HN, Dev.to, Reddit and LinkedIn launch posts; follow community rules.
- [ ] Publish starter kits for Python, TypeScript, Kubernetes and AI/RAG projects.
- [ ] Recruit external maintainers; document governance and moderation.
- [ ] Measure opt-in usage and community engagement without collecting personal data by default.

## Explicit non-goals for alpha
- No arbitrary GitHub repository execution.
- No claims of full cross-agent interoperability.
- No auto-execution of downloaded MCP servers or skills.
- No remote registry sync until supply-chain controls exist.
