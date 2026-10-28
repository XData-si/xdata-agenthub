---
name: rust-review
description: Review Rust code for soundness and robustness — unsafe blocks, panics and unwrap, error types, ownership in async code, Send/Sync, dependency and feature hygiene. Use when reviewing Rust crates, services or FFI code, or before publishing a crate.
license: MIT
---

# Rust Review

## Goal
Safe Rust stays safe: every `unsafe` block is justified and minimal, errors are typed and propagated, and the code does not panic on input it should reject.

## Inputs
- Crate type (library, binary, `no_std`), MSRV, edition, async runtime, feature flags, CI configuration.

## Review checklist
1. **`unsafe`**: each block has a `// SAFETY:` comment stating the invariants; the block is as small as possible; safe wrappers enforce invariants; consider `#![forbid(unsafe_code)]` where no unsafe is needed. Run Miri on tests that exercise unsafe code.
2. **Panics**: no `unwrap()`/`expect()` on fallible input in libraries or request paths; indexing and slicing on untrusted lengths use `get()`; integer overflow considered (`checked_*`, `saturating_*`).
3. **Errors**: libraries expose typed errors (`thiserror` or hand-written enums); binaries may use `anyhow` with context; no `Box<dyn Error>` leaking across stable APIs without reason.
4. **Async**: no blocking calls (file system, CPU-heavy work, `std::thread::sleep`) on the async executor — use `spawn_blocking`; locks are not held across `.await` (or use async-aware locks deliberately); cancellation safety of `select!` branches.
5. **Concurrency**: `Send`/`Sync` bounds make sense; `Arc<Mutex<_>>` contention considered; no `static mut`.
6. **API design**: borrowing over cloning in signatures, `impl Trait` vs generics chosen deliberately, semver impact of public changes (`cargo semver-checks`).
7. **Dependencies**: `cargo audit` or `cargo deny` for advisories and licences; minimal features; no git dependencies in published crates.
8. **Tooling**: `cargo clippy -- -D warnings`, `cargo fmt --check`, tests including property tests (`proptest`) for parsers.

## Example fixture
```rust
pub fn parse_len(buf: &[u8]) -> usize {
    let n = u32::from_be_bytes(buf[0..4].try_into().unwrap()) as usize;
    unsafe { *buf.as_ptr().add(4 + n) as usize }
}
```
Expected findings: panics on short input, unchecked arithmetic, out-of-bounds read in `unsafe` with no SAFETY reasoning; should return `Result` and use `get()`.

## Acceptance checks
- Clippy, fmt and tests pass; Miri run for code with `unsafe`, or marked NOT RUN with reason.
- Every `unsafe` block has a SAFETY comment that a reviewer can verify.
- Negative case: malformed or truncated input returns an error instead of panicking (test included).

## Output
Findings by severity, suggested diffs, tool results.

## Safety
Do not publish crates or yank versions without maintainer approval. Treat FFI and `unsafe` changes as security-sensitive and require a second reviewer.
