---
name: git-workflow
description: Prepare clean branches, atomic commits and reviewable pull or merge requests without rewriting shared history or leaking secrets. Use when committing, branching, rebasing, resolving conflicts or preparing a change for review.
license: MIT
---

# Git Workflow Hygiene

## Goal
A history that reviewers can follow and that can be bisected and reverted safely.

## Inputs
- Repository branching model (trunk-based, GitFlow, release branches) from `CONTRIBUTING.md`.
- Commit message convention (for example Conventional Commits) and protected branch rules.

## Procedure
1. **Start from an updated base.** `git fetch` and branch from the current target (`main`). Name branches by intent (`fix/invoice-rounding`, `123-export-csv`).
2. **Stage deliberately.** Review `git diff` and `git status`; stage by file or hunk (`git add -p`). Never commit generated artefacts, local configuration, `.env` files or credentials.
3. **Atomic commits.** One logical change per commit, and the tests pass at every commit when practical. Subject in the imperative, ≤ 72 characters; the body explains *why* and references the issue.
4. **Keep up to date.** Rebase your own unpublished branch on the target or merge the target in, per project convention. After a branch is shared, prefer merge or new commits over rewriting.
5. **Resolve conflicts carefully.** Understand both sides; rerun tests after resolution; never pick "ours" or "theirs" for whole files without reading them.
6. **Open the review.** Description: what, why, how to verify, risks, screenshots or logs. Keep it small (guideline: under ~400 changed lines) or split it.
7. **Respond to review** with follow-up commits so reviewers see what changed; squash only if the project wants it, at merge time.

## Hard rules
- No force push to shared or protected branches. On your own unmerged branch, use `--force-with-lease` only when the project allows it.
- If a secret was committed: treat it as leaked. Rotate it first; rewriting history does not undo exposure.
- Do not bypass hooks (`--no-verify`) or protections without explicit authorization.

## Decision points
- History needs fixing after push → add a corrective commit, or open a new branch and pull request, instead of rewriting.
- Large binary or generated files → Git LFS or build artefacts, not the repository.

## Example fixture
```text
fix: round invoice totals half-up per line item

Totals were rounded once at the end, which differed from the printed lines
by up to 1 cent. Refs #123
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| Force-pushing is fine, nobody uses this branch. | Reviewers, CI and other agents may have fetched it. Use new commits or a new branch unless the branch is provably yours alone. |
| I'll clean up the history later. | Later rarely comes, and history rewrites after review lose discussion context. Commit cleanly now. |
| Skipping the hook just this once. | Hooks encode checks the project decided on. Bypassing them needs explicit authorization. |
| The secret was only in one commit, I'll remove it. | Assume it is leaked the moment it was pushed. Rotate first; rewriting history does not revoke it. |

## Acceptance checks
- `git diff --staged` reviewed; no secrets, debug output or unrelated files.
- Each commit message explains the reason for the change.
- Branch is current with the target and CI is green, or failures are explained.
- No history rewrite on shared branches.

## Output
Branch, commits and a review request with a verification section.

## Safety
Destructive commands (`reset --hard`, `clean -fdx`, `push --force`, branch deletion) require checking what will be lost and explicit approval when others may be affected.
