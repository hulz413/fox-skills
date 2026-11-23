# Acceptance environment

Procedures for the shared acceptance workspace that [SKILL.md](../SKILL.md) points to. `accept-lock.sh` is `../fox-fix-issue/scripts/accept-lock.sh`.

## Update to the base

Prepare step 5, when the acceptance workspace exists, is clean, and no acceptance lock is held:

1. Fast-forward with `git merge --ff-only <base>` when possible.
2. Otherwise, when every acceptance commit is already in the base, `git reset --hard <base>`. Count them as in the base when `git cherry <base> HEAD` shows only `-`, or when merging HEAD into the base changes nothing (`git merge-tree --write-tree <base> HEAD` prints the same tree as `git rev-parse <base>^{tree}`), which covers squash merges.
3. Before such a reset, record the old `HEAD`. After it, in each clean worktree of a fix branch kept from an earlier run, run `git rebase --onto bugfix/verification <old HEAD>`, or the branch keeps the old acceptance commits and its landing check fails. Abort a conflicting rebase and handle it as in [move a fix branch](#move-a-fix-branch); list a dirty worktree.
4. Otherwise leave it and report which acceptance commits are not yet in the base, so the user can bring them over.

## Smoke test

Prepare step 6, before dispatching:

1. Take the acceptance lock. Start the slot from a login shell exactly as workers will (`LOCAL_SLOT=<slot> scripts/restart.sh`, no `--with-console`), confirm the frontend answers, and log in once with the acceptance login (through `playwright-cli` or the app's login API). Then stop the slot and release the lock.
2. If a step fails on local setup (a missing `.env` file, uninstalled dependencies, a stale process on the slot's ports), fix it.
3. If the shared local middleware the slot needs (for example PostgreSQL, Redis, Temporal) is not running, start it with the repository's own start script or documented command (the start script's error message normally prints it), the same way the user's main environment does (same data directory or database file), never with an improvised alternative that would run a different configuration. Start it detached from the session (for example in its own process session), because interrupting the coordinator's thread kills processes started from its shell, and record the exact command. Slot mode only checks that middleware; it does not start it. The same applies when a worker later reports it down.
4. If it needs a change to the target repository, such as start scripts without `LOCAL_SLOT` support, do not edit the code: record the blocker in the plan before dispatching, so nobody expects a completion while the environment is broken.

## Move a fix branch

When a worker's cherry-pick conflicts because the acceptance branch moved after its fix workspace was created:

1. Take the acceptance lock first, for the same reason as when creating a fix workspace.
2. Keep the commits with `git branch bugfix/<key>-backup bugfix/<key>`.
3. When the fix worktree is clean, run `git reset --hard bugfix/verification` inside it (the branch is checked out there, so it cannot be moved from elsewhere).
4. Release the lock and have the worker re-apply the commits from the backup branch and resolve them in the fix workspace.

## Lock recovery

Run `accept-lock.sh status <lock>` first.

- **The owner's task is still running.** The lock is only busy. Tell the worker that timed out to acquire again; do not touch the lock.
- **The owner's task has ended** (finished, failed, or stopped) while the lock is still held. Nobody else can release it, so recover it yourself:
  1. Stop the slot environment, then look at the acceptance workspace.
  2. Commits above the last commit a finished worker reported as landed are the dead owner's unaccepted cherry-picks; reset to that commit (to the base when nothing has landed yet) and discard uncommitted changes. If any commit above it is not the dead owner's, stop and ask the user.
  3. Release with the dead owner's name, `accept-lock.sh release <lock> "<owner>"`, or remove the lock directory when it has no owner file.
  4. Resume or re-dispatch the task.

Never release a lock whose owner is still running, and record each recovery for the final report.
