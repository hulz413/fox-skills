---
name: fox-dispatch-projex-bugs
description: Coordinate a batch of Alibaba Cloud DevOps Projex bugs assigned to the current user. Sync merged fixes to 已修复, list 待确认 bugs by severity, triage and group them, pick a model and effort per task, and dispatch fox-fix-projex-bug workers in parallel with a shared acceptance workspace, answering their questions and integrating results. Manual invocation only ($fox-dispatch-projex-bugs or /fox-dispatch-projex-bugs).
disable-model-invocation: true
---

# Dispatch Projex bugs

The coordinator plans, dispatches, decides, and reports. It never handles a bug itself: no code investigation beyond reading the bug text, no code edits, commits, acceptance runs, or bug comments. Its only bug status write is `开发完成` → `已修复` during the merge sync. Workers run [fox-fix-projex-bug](../fox-fix-projex-bug/SKILL.md) in dispatched mode and own each bug end to end.

Invoking this skill authorizes, for this run: the merge sync status writes, creating and cleaning the worktrees and branches described below, dispatching workers with the settings chosen here, and answering their in-scope questions. It does not authorize pushing, merging, opening MRs, or touching the user's main checkout, main branch, or running main instance.

Host-specific tools are listed in [host capabilities](references/hosts.md); the steps name actions. Use the Projex client from the fix skill: `"$PY" <fix-skill-dir>/scripts/projex.py`, following its [API guide](../fox-fix-projex-bug/references/projex.md) for credentials and the Python 3.10+ interpreter.

## Defaults

The user can override any of these in the request; their values win.

| Setting | Default |
|---|---|
| Project | The fix skill's default project |
| Bug filter | Assigned to the token's user (`projex.py me`), status exactly `待确认` |
| Concurrency | 5 worker tasks at once |
| Model provider | OpenAI (GPT); the user may name another provider or model |
| Worktree root | `~/Developer/worktrees/<repo-dir-name>/` |
| Base branch | The main checkout's current branch, so workers see fixes that are not yet in master |
| Acceptance workspace | `<root>/bugfix/` on branch `bugfix/projex-daniel`, created from the base branch |
| Fix workspaces | `<root>/<lowercase-key>/`, for example `fisn-1322/`, on branch `bugfix/<lowercase-key>` |
| Local slot | `LOCAL_SLOT=1` for the acceptance workspace |
| Acceptance lock | `<git-common-dir>/fox-bugfix-accept.lock` |

## 1. Prepare

1. Confirm the repository is the main checkout of the intended project and record its path. Run `git fetch origin master`.
2. Run `projex.py me` and record `body.id`. A 403 means the token lacks the organization user read permission: report it and stop, do not guess the user.
3. Refresh the model inventory for every enabled provider (see [model routing](references/model-routing.md)). Do this on every run; never reuse a list from an earlier run.
4. Ensure the acceptance workspace exists. If missing, create it with `git worktree add <root>/bugfix -b bugfix/projex-daniel <base>`, copy (never symlink) the main checkout's untracked `.env` files into it, and install dependencies as the repository documents. If it exists, bring it up to `<base>` only when that is safe: it is clean and no acceptance lock is held. Then fast-forward with `git merge --ff-only <base>` when possible; when `git cherry <base> HEAD` shows only `-` (every acceptance commit is already in the base), `git reset --hard <base>`. Otherwise leave it and report which acceptance commits are not yet in the base, so the user can bring them over.
5. Check whether the acceptance workspace's start scripts support `LOCAL_SLOT`. If not, workers can fix and unit-test but cannot pass acceptance; say so in the plan so nobody expects `开发完成` this run.

## 2. Sync merged fixes

List bugs assigned to the user with status exactly `开发完成` (map the name to its ID through a bug's workflow). Decide each with the fix skill's [merged rule](../fox-fix-projex-bug/SKILL.md#mark-fixed-after-merge): every repair commit for the bug, on the base and acceptance branches, must already be in `origin/master`. A bug often has an earlier fix in master and a later follow-up that is not, so one match in master is not enough. When merged, set `已修复` through the fix skill's status procedure and read back. Otherwise leave the status and list the bug with its unmerged commits.

## 3. Build the list

1. Search with `--status-id <待确认 id> --assigned-to <user id>` page by page until `X-Total` items are read.
2. Skip bugs already being handled: status no longer `待确认`, or an existing task titled with the key. List `已选择` bugs with no visible task in the report; never take them over.
3. Sort by the `严重程度` custom field, P0 first through P3. Map legacy values `1-致命`=P0, `2-严重`=P1, `3-一般`=P2, `4-轻微`=P3; missing values go last. Ties go by creation time, oldest first.

## 4. Triage

Read each bug's title, description, and comment text. Do not open attachments or read code; workers do that. Decide:

- **Group**: bugs that share context, a root cause, or a fix approach go into one task. Prefer grouping when it saves rediscovery or lets one acceptance cover several bugs.
- **Skip**: not this repository's code, a data or configuration problem rather than a code defect, or behavior that exists only on another unmerged branch. Record the reason; do not dispatch.
- **Flags**: a likely database migration (needs the user's approval before acceptance), or frontend dependency changes.
- **Complexity**: the evidence for the capability tier and effort in [model routing](references/model-routing.md).

## 5. Show the plan and dispatch

Show the plan as a table, then dispatch immediately without waiting for confirmation; the user interrupts if something is wrong. Columns: order, keys with links, severity, group reason, complexity, provider/model/effort with a short reason, flags. Below it, list skipped bugs with reasons and any merge sync results.

For each task, in plan order and up to the concurrency limit:

1. Create its fix workspace: `git worktree add <root>/<key> -b bugfix/<key> bugfix/projex-daniel`, where `<key>` is the lowercase first key of the group. Symlink `frontend/node_modules` to the acceptance workspace's copy when that exists.
2. Start a worker task titled with the issue keys (for example `FISN-1322 FISN-1325`) using the chosen model and effort, with fresh context. The brief must contain: the instruction to run the fix-projex-bug skill at its absolute path in dispatched mode; the keys and their Projex links; the fix workspace, acceptance workspace, acceptance branch, slot, and lock path; flags from triage; that questions go to the coordinator; whether one model escalation is allowed; and the expected final report. Pass pointers, not copies of the bug text.
3. When a worker finishes, ends blocked, or ends waiting on the user, its slot frees and the next task starts. A worker waiting on the user does not hold a slot.

## 6. Answer workers

Answer directly, citing the evidence used, when the question is about: the implementation approach, a modest scope adjustment, coordination between bugs or tasks (merging tasks, ordering acceptance), local test data, or a model escalation. Base answers on the bug text, repository docs and conventions, and other bugs in the batch. Record each decision for the final report.

Forward to the user, grouped and with the worker task links: disputed or undocumented expected product behavior, anything beyond the authorization above, approval to apply a migration during acceptance, and cherry-pick conflicts in the acceptance workspace the coordinator cannot settle by reordering or merging tasks. Do not guess product decisions.

For an escalation, start a new attempt at one stronger configuration with the prior evidence handed off; allow at most one per task.

## 7. Finish

When a worker reports its commits landed on the acceptance branch, confirm with `git cherry bugfix/projex-daniel bugfix/<key>` that nothing remains unlanded, then remove its worktree (`git worktree remove`) and delete its branch. Keep the worktree and branch of any blocked or unfinished task and list them.

Report once all tasks have finished or are waiting on the user:

- A table per task: keys with links, conclusion, commits on the acceptance branch, status changes, acceptance result, open questions or blockers, model and effort used.
- Merge sync results and skipped bugs.
- Counts of blocked tasks by cause (for example missing local data, acceptance environment unavailable, waiting on product), so recurring causes are visible.
- Decisions the coordinator made on workers' behalf.
- What the user needs to do next, such as bringing `bugfix/projex-daniel` into the base branch and on to master. `已修复` still requires the fix to reach `origin/master`.
