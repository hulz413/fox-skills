# Current checkout and Git rules

## Shared working location

- The dedicated task reuses the current saved project's local checkout. It does not create or switch worktrees or branches.
- Do not fetch, pull, rebase, merge, or force-push.
- Do not stash, clean, reset, or revert pre-existing work.
- The dispatcher remains read-only in the local repository and product code. Its only external write is the selected Bug's post-creation `In Progress` transition defined in [project and Projex selection rules](projex.md). Only the dedicated worker may edit Bug-scoped files.

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
