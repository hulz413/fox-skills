# Current checkout and Git rules

## Shared working location

- In the default single-Bug workflow, the dedicated task reuses the current saved project's local checkout. It does not create or switch worktrees or branches. An explicitly authorized batch workflow instead isolates each Bug on its own local branch and worktree before using the final-branch integration protocol below.
- Do not fetch, pull, rebase, merge, or force-push during the default single-Bug workflow. The explicitly authorized final-branch integration protocol below is the only rebase/merge exception.
- Do not stash, clean, reset, or revert pre-existing work.
- The dispatcher remains read-only in product code. In the default workflow it is also read-only in Git. An explicitly authorized batch coordinator may create and remove isolated Bug branches and worktrees and perform only the final-branch integration protocol below. Its only non-Git external write is the selected Bug's post-creation `In Progress` transition defined in [project and Projex selection rules](projex.md). Only the dedicated worker may edit Bug-scoped files.

## Before editing

1. Record the repository root, current branch, and `HEAD`.
2. Inspect staged, unstaged, and untracked files and compare them with the dispatch snapshot.
3. Identify which changes predate the worker and which paths the Bug is likely to touch.
4. Continue when existing changes do not overlap the Bug, while reporting that tests run in a dirty checkout.
5. Stop if existing and Bug changes overlap or cannot be safely distinguished. Do not overwrite, stash, or restore them.

Because the checkout is shared, recheck unfinished dedicated QA repair tasks before the first edit. Stop if another worker may be writing to the same checkout.

## Local commit

1. Complete focused Bug regression checks and affected local acceptance.
2. Review the complete diff for unrelated edits, debug code, generated caches, or credentials.
3. Stage exact Bug paths or patches only. Never use `git add -A`, `git add .`, or an equivalent broad command.
4. Create exactly one Conventional Commit and reference the Bug number in the subject or body.
5. For the OpenSpec route, include implementation, synced main specs, and the archived change in the same final commit. Do not commit before sync and archive.
6. Verify `git show --stat --oneline HEAD` and `git status --short` afterward. All unrelated pre-existing changes must remain uncommitted.

Stop after the local commit. Do not push, open a PR, deploy, or alter remote branch state.

## Explicit final-branch integration

Use this protocol only when the user explicitly requests batch coordination, each completed Bug is isolated on its own local branch and worktree, and the user has named the local final branch. It does not authorize a push, PR, deployment, force-push, or unrelated history rewrite.

Run only one final-branch integration transaction at a time, even while Bug repair tasks remain parallel. For each locally committed and validated Bug:

1. Confirm the Bug worktree is clean, the scoped Bug commit exists, and the final branch and its checkout are unambiguous. Preserve the final branch tip as the expected rebase base.
2. In the Bug worktree, rebase the Bug branch onto the current local final branch.
3. Resolve conflicts in the Bug branch before touching the final branch. Reconcile the final branch's already-integrated behavior with the Bug's intended fix; never mechanically choose all of `ours` or `theirs`. Stage only the resolved paths and continue the rebase.
4. When conflict resolution changes code, rerun the focused tests, lint, type checks, or other checks affected by those edits. Always run `git diff --check`, inspect `git status`, and confirm that no conflict markers remain. A conflict-free rebase does not require repeating the worker's full validation.
5. Recheck the final branch tip immediately before integration. If it differs from the expected rebase base, rebase the Bug branch onto the new tip and repeat any conflict-specific validation. Do not fall back to a merge commit.
6. In the final-branch checkout, run `git merge --ff-only <bug-branch>`. Treat an `--ff-only` failure as stale-base or abnormal-state evidence; repair the state or rebase again instead of using a non-fast-forward merge.
7. Verify that the final branch `HEAD` equals the Bug branch `HEAD` and that the final checkout has no new uncommitted changes. A clean fast-forward moves only the ref to the already validated rebased commit, so do not rerun routine post-merge tests unless the integration state is abnormal.
8. Report the post-rebase commit SHA, then remove that Bug's temporary worktree and local Bug branch. Rebase rewrites commit IDs, so never report the pre-rebase SHA as the integrated commit.

The worker concurrency limit and the final-branch integration lock are separate controls: a committed Bug may release a repair slot, while its short rebase and fast-forward integration still waits for exclusive access to the final branch.
