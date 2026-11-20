---
name: fox-dispatch-projex-bugs
description: Coordinate a batch of Alibaba Cloud DevOps Projex bugs assigned to the current user. Sync merged fixes to 已修复, list 待确认 bugs by severity, triage and group them, pick a model and effort per task, and dispatch fox-fix-projex-bug workers in parallel with a shared acceptance workspace, answering their questions and integrating results. Manual invocation only ($fox-dispatch-projex-bugs or /fox-dispatch-projex-bugs).
disable-model-invocation: true
---

# Dispatch Projex bugs

The coordinator plans, dispatches, decides, and reports. It never handles a bug itself: no code investigation beyond reading the bug text, no code edits, commits, or acceptance runs. It owns every Projex write for dispatched bugs: status changes, and the repair or conclusion comments that workers draft. Workers never write to Projex, which keeps every write in one place that can check it against git and against the user's decisions. Workers run [fox-fix-projex-bug](../fox-fix-projex-bug/SKILL.md) in dispatched mode and own each bug end to end.

Invoking this skill authorizes, for this run: setting dispatched bugs to `已选择`, posting the comments workers draft and setting `开发完成` as described in [Finish](#7-finish), the merge sync `已修复` writes, creating and cleaning the worktrees and branches described below, dispatching workers with the settings chosen here, and answering their in-scope questions. It does not authorize pushing, merging, opening MRs, or touching the user's main checkout, main branch, or running main instance.

Host-specific tools are listed in [host capabilities](references/hosts.md); the steps name actions. Use the Projex client from the fix skill: `"$PY" <fix-skill-dir>/scripts/projex.py`, following its [API guide](../fox-fix-projex-bug/references/projex.md) for credentials and the Python 3.10+ interpreter.

## Defaults

The user can override any of these in the request; their values win.

| Setting | Default |
|---|---|
| Project | The fix skill's default project |
| Bug filter | Assigned to the token's user (`projex.py me`), status exactly `待确认` |
| Concurrency | 5 worker tasks at once |
| Model provider | The provider the coordinator itself runs on; the user may name another provider or model |
| Worktree root | `~/Developer/worktrees/<repo-dir-name>/` |
| Base branch | `origin/master`, independent of the main checkout; the user may name another branch for a run, for example when related fixes are still unmerged on a feature branch |
| Acceptance workspace | `<root>/bugfix/` on branch `bugfix/projex`, created from the base branch |
| Fix workspaces | `<root>/<lowercase-key>/`, for example `fisn-1322/`, on branch `bugfix/<lowercase-key>` |
| Local slot | `LOCAL_SLOT=1` for the acceptance workspace |
| Acceptance lock | `<git-common-dir>/fox-bugfix-accept.lock`, taken and released only with `../fox-fix-projex-bug/scripts/accept-lock.sh` |
| Acceptance login | macOS Keychain generic password, service `fox-local-login`, account = the email that owns the local test data. If it is missing, ask the user once through a secret card and store it with `security add-generic-password -U`; never keep it in a file. |

## 1. Prepare

1. Confirm the repository is the main checkout of the intended project and record its path. Run `git fetch origin master`.
2. Run `projex.py me` and record `body.id`. A 403 means the token lacks the organization user read permission: report it and stop, do not guess the user.
3. Refresh the model inventory for every enabled provider (see [model routing](references/model-routing.md)). Do this on every run; never reuse a list from an earlier run.
4. Ensure the acceptance workspace exists. If missing, create it with `git worktree add <root>/bugfix -b bugfix/projex <base>`, copy (never symlink) the main checkout's untracked `.env` files into it, and install dependencies as the repository documents. If it exists, bring it up to `<base>` only when that is safe: it is clean and no acceptance lock is held. Then fast-forward with `git merge --ff-only <base>` when possible; when every acceptance commit is already in the base, `git reset --hard <base>`. Count them as in the base when `git cherry <base> HEAD` shows only `-`, or when merging HEAD into the base changes nothing (`git merge-tree --write-tree <base> HEAD` prints the same tree as `git rev-parse <base>^{tree}`), which covers squash merges. Otherwise leave it and report which acceptance commits are not yet in the base, so the user can bring them over.
5. Smoke-test acceptance before dispatching, so environment problems surface once instead of once per worker. Take the acceptance lock with `../fox-fix-projex-bug/scripts/accept-lock.sh` (owner `coordinator`), start the slot from a login shell exactly as workers will (`LOCAL_SLOT=<slot> scripts/restart.sh`, no `--with-console`), confirm the frontend answers, log in once with the acceptance login below (through `playwright-cli` or the app's login API), then stop the slot and release the lock. If the start scripts lack `LOCAL_SLOT` support or any step fails, fix it or record it in the plan before dispatching, so nobody expects `开发完成` while the environment is broken.

## 2. Sync merged fixes

List bugs assigned to the user with status exactly `开发完成` (map the name to its ID through a bug's workflow). Decide each with the fix skill's [merged rule](../fox-fix-projex-bug/SKILL.md#mark-fixed-after-merge): every repair commit for the bug, on the base and acceptance branches, must already be in `origin/master`. A bug often has an earlier fix in master and a later follow-up that is not, so one match in master is not enough. When merged, set `已修复` through the fix skill's status procedure and read back, without asking. Otherwise leave the status and list the bug with its unmerged commits. The workflow may refuse to move `已修复` back, so apply the rule strictly.

## 3. Build the list

1. Search with `--status-id <待确认 id> --assigned-to <user id>` page by page until `X-Total` items are read.
2. Skip bugs already being handled: status no longer `待确认`, or an existing task titled with the key. List `已选择` bugs with no visible task in the report; never take them over.
3. Sort by the `严重程度` custom field, P0 first through P3. Map legacy values `1-致命`=P0, `2-严重`=P1, `3-一般`=P2, `4-轻微`=P3; missing values go last. Ties go by creation time, oldest first.

## 4. Triage

Read each bug's title, description, and comment text. Do not open attachments or read code; workers do that. Decide:

- **Group**: bugs that share context, a root cause, or a fix approach go into one task. Prefer grouping when it saves rediscovery or lets one acceptance cover several bugs.
- **Skip**: not this repository's code, a data or configuration problem rather than a code defect, or behavior that exists only on another unmerged branch. Record the reason; do not dispatch.
- **Flags**: a likely database migration (needs the user's approval before acceptance), frontend dependency changes, or additions to a shared numbered registry such as error codes, which parallel workers can claim twice; tell those workers to recheck the number before landing.
- **Complexity**: the evidence for the capability tier and effort in [model routing](references/model-routing.md).

## 5. Show the plan and dispatch

Show the plan as a table, then dispatch immediately without waiting for confirmation; the user interrupts if something is wrong. Columns: order, keys with links, severity, group reason, complexity, provider/model/effort with a short reason, flags. Below it, list skipped bugs with reasons and any merge sync results.

For each task, in plan order and up to the concurrency limit:

1. Set each bug in the group to `已选择`, mapping the exact name to its ID through the workflow, and read back. Skip a bug already there; do not move a later status back.
2. Create its fix workspace while holding the acceptance lock, so the base never includes another worker's temporary cherry-picks: `git worktree add <root>/<key> -b bugfix/<key> bugfix/projex`, where `<key>` is the lowercase first key of the group. Symlink `frontend/node_modules` to the acceptance workspace's copy when that exists.
3. Start a worker task titled with the issue keys (for example `FISN-1322 FISN-1325`) using the chosen model and effort, with fresh context. The brief must contain: the instruction to run the fix-projex-bug skill at its absolute path in dispatched mode; the keys and their Projex links; the fix workspace, acceptance workspace, acceptance branch, slot, and lock path; flags from triage; that the coordinator is this dispatching task and questions reach it by ending the turn as the fix skill's host table describes; whether one model escalation is allowed; that the worker makes no Projex writes and returns comment drafts instead; and the expected final report. Pass pointers, not copies of the bug text.
4. When a worker finishes, ends blocked, or ends waiting on the user, its slot frees and the next task starts. A worker waiting on the user does not hold a slot.

## 6. Answer workers

Answer directly, citing the evidence used, when the question is about: the implementation approach, a modest scope adjustment, coordination between bugs or tasks (merging tasks, ordering acceptance), local test data, or a model escalation. When a cherry-pick conflicts because the acceptance branch moved after the fix workspace was created, move the fix branch yourself: keep its commits on a backup branch, reset the fix branch to the acceptance `HEAD` when its worktree is clean, and have the worker re-apply and resolve the commits in the fix workspace. Base answers on the bug text, repository docs and conventions, and other bugs in the batch. Record each decision for the final report.

Forward to the user, grouped and with the worker task links: disputed or undocumented expected product behavior, anything beyond the authorization above, approval to apply a migration during acceptance, and cherry-pick conflicts in the acceptance workspace the coordinator cannot settle by reordering or merging tasks. Do not guess product decisions. When a forwarded question involves the PRD or another product document, include the relevant excerpt and its section number, so the user can decide without looking it up.

For an escalation, start a new attempt at one stronger configuration with the prior evidence handed off; allow at most one per task.

## 7. Finish

When a worker reports that acceptance passed and its commits landed on the acceptance branch:

1. Write each bug's draft to a UTF-8 file. Do not edit its substance; return it to the worker if it contradicts its own report.
2. Run [`scripts/finish_bug.py`](scripts/finish_bug.py) per bug from the target repository through a login shell: `--fix-branch bugfix/<key>` for a repair, `--mode already-fixed --fix-commit <sha>` for a fix already in `origin/master`, and `--mode conclusion` for a no-fix conclusion once any product question it depends on is settled. The script checks the landing first (patch equivalence, or the same subject and changed lines when a cherry-pick was merged automatically), skips a comment that already exists, posts the draft, sets `开发完成` unless the mode is conclusion, and reads both back. Never write to Projex for a bug whose landing check fails; ask the worker instead.
3. Remove the worktree (`git worktree remove`) and delete the branch.

If a write fails or its outcome is uncertain, check its effect with read-only calls before retrying, and report what is still pending. Keep the worktree and branch of any blocked or unfinished task and list them.

Report once all tasks have finished or are waiting on the user:

- A table per task: keys with links, conclusion, commits on the acceptance branch, status changes, acceptance result, open questions or blockers, model and effort used.
- Merge sync results and skipped bugs.
- Counts of blocked tasks by cause (for example missing local data, acceptance environment unavailable, waiting on product), so recurring causes are visible.
- Decisions the coordinator made on workers' behalf.
- Test data that workers could not remove, with where it lives. Before reporting, remove what you can yourself, scoped by the bug key, the run's time window and the project, and list only what is still left.
- What the user needs to do next, such as pushing `bugfix/projex` and opening an MR to master. `已修复` requires the fix to reach `origin/master`.
