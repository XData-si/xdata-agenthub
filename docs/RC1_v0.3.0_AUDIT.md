# v0.3.0 RC1 — release audit findings

**Audit scope:** repository documentation and source inspection on development `main` after merged PRs #67 and #68. This is **not** a production certification, runtime test, release approval or claim that the candidate is ready to publish.

## Confirmed

- Integration PR #67 merged as `929242dbc27663fcf1c9c5ad8a2e50c39e5ed785`; documentation PR #68 merged as `82f44780bce93dcbce685f611a4b66428d8950fc`.
- CI `Tests` and `Release validation` succeeded on the reviewed **PR head** `53e5591cbccc7beef6c4dfe4794a9a952469fd5f` before #68 merge.
- `cli/release_gates.py` requires six self-declared gate records with `passed`, `reference` and `reviewer`; it **does not authenticate** any of them.
- `cli/recovery_execute.py` uses cooperative locking, hash checks, and journal state transitions. It is **not** atomic across multiple files, and external writers can still race with checks.
- Existing agent evidence in `docs/integration-evidence/2026-10-15-runtime-results.md` is limited to documented client versions/scenarios and operator-provided transcripts. Do not generalize to all skills or production.
- README and CHANGELOG were stale with respect to integrated v0.3.0 features; updated in this audit branch.

## Outstanding blockers before any tag or release

1. **Freeze candidate SHA** after this audit PR is reviewed and merged. CI results for the #68 squash merge commit `82f44780bce93dcbce685f611a4b66428d8950fc` were not returned by the workflow-run lookup at audit time. Do not reuse PR-head CI as final-SHA evidence.
2. **Operator rehearsal:** run commands in `docs/RC1_v0.3.0_READINESS.md` on a fresh checkout at frozen SHA; record logs and verify backup restoration in a disposable workspace.
3. **Security sign-off:** manually review rollback, symlink handling, external writer race, backup integrity, and crash interruption. Explicitly accept residual risks.
4. **Native compatibility:** record current versions and actual skill invocation evidence, or restrict RC1 claims to path-level adapters.
5. **Release gate evidence:** collect authentic CI links, named approvers and references; `release-check` alone cannot establish truth.
6. **Release-owner approval:** explicit approval for tag/publication is required separately.

**Decision:** HOLD — documentation improved; RC1 publication is not yet authorized or fully evidenced. No tag or GitHub Release should be created by this PR.
