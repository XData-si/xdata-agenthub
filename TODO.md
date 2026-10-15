# TODO — What remains before a public launch

## P0 — must do
- [x] Move this scaffold into a dedicated **public** GitHub repository; confirm ownership and visibility.
- [ ] Review name and branding with XData; create original logo and social preview (1280×640).
- [ ] Run smoke tests on Linux, macOS and Windows (WSL); test Python 3.10–3.13.
- [ ] Perform security review of installer, path handling and untrusted Markdown content.
- [ ] Choose licensing and obtain clearance for every third-party item before importing it.
- [ ] Establish automated CI lint/test, releases, tags and checksums.
- [ ] Validate that CLI installs into an isolated target and does not overwrite existing files.
- [ ] Create GitHub issue templates, Discussions, repository topics and homepage.

## P1 — compelling product
- [ ] Add 25+ original, useful skills with tested examples and acceptance checks.
- [ ] Build adapters for Claude Code, Codex and OpenCode with explicit compatibility tests.
- [x] Add basic `xah init` starter profiles and dry-run mode.
- [ ] Add interactive stack builder, richer profiles and agent-specific adapters.
- [ ] Add provenance manifests, license metadata and version pinning.
- [ ] Implement meaningful security scanning (the current audit is only a simple heuristic).
- [ ] Build a browsable searchable website and documentation.
- [ ] Add offline fixture-based tests, schema validation and JSON output.

## P2 — growth
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
