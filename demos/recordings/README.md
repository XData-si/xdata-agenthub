# Terminal recordings

[VHS](https://github.com/charmbracelet/vhs) tapes for the launch videos. Every recording runs real commands; nothing
is mocked or edited.

| Tape | Shows | Format |
|---|---|---|
| `install.tape` | clone, `xah search`, install one skill for Claude Code, `xah verify` | 16:9 MP4 + GIF |
| `verify-release.tape` | download v0.3.0, Sigstore signature, checksums, SLSA attestation | 16:9 MP4 + GIF |
| `compare.tape` | replays the published answers in `demos/results/2026-10-29` (no live model call): ShellCheck statement, residual risks, approval step, and the post-hoc table | 16:9 MP4 + GIF |
| `mcp.tape` | `xah mcp list` and `xah mcp inspect sentry` (L0 = listed only) | 16:9 MP4 + GIF |
| `short.tape` | search, install, verify, measured differences | 9:16 MP4 (YouTube Short) |

Render them with the manual **Recordings** workflow (Actions → Recordings → Run workflow) and download the
`recordings` artifact. Locally, run `vhs demos/recordings/<tape>.tape` from the repository root. You need `vhs`,
`ffmpeg` and `ttyd`, plus `cosign` and an authenticated `gh` for `verify-release.tape`. Output goes to
`demos/recordings/out/`, which is not committed.

The Claude Code marketplace install (`/plugin marketplace add XData-si/xdata-agenthub`) runs inside the Claude Code
TUI. Record it by hand with your own account.
