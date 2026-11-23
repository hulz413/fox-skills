---
name: fox-coordinate-issues
description: Coordinate a batch of issues from Projex bugs, QA test cases, or user feedback. Sync merged Projex fixes, triage, and dispatch parallel fox-fix-issue workers that share one acceptance workspace, answering their questions and owning every external write. Manual invocation only ($fox-coordinate-issues or /fox-coordinate-issues).
disable-model-invocation: true
---

# Coordinate issues

The coordinator plans, dispatches, decides, and reports. It never handles an issue itself: no code investigation beyond reading the reports, no code edits, commits, case runs, or acceptance runs; the one time it starts the acceptance environment is the smoke test in [Prepare](#1-prepare). It owns every external write for dispatched issues; workers never write outside git. Workers run [fox-fix-issue](../fox-fix-issue/SKILL.md) in dispatched mode and own each issue end to end.

Each issue comes from a source, and the fix skill's source guides say how it is read and written back: [Projex](../fox-fix-issue/sources/projex.md) for Projex bugs, [general](../fox-fix-issue/sources/general.md) for everything else, including QA test cases. One run may mix sources.

Invoking this skill authorizes, for this run: for Projex bugs, setting dispatched bugs to `已选择`, posting the comments workers draft and setting `开发完成` (then `已修复` for a fix already in `origin/master`) as described in [Finish](#8-finish), and the merge sync `已修复` writes; creating and cleaning the worktrees and branches described below; dispatching workers and case runners with the settings chosen here; and answering their in-scope questions. It authorizes no write to any other source by itself: when the user explicitly specifies a write-back target and scope, write within that scope and read it back; otherwise present drafts and ask. Do not overwrite unrelated content. It does not authorize pushing, merging, opening MRs, or touching the user's main checkout, main branch, or running main instance.

Host-specific tools are listed in [host capabilities](references/hosts.md); the steps name actions. For Projex, use the client from the fix skill: `"$PY" <fix-skill-dir>/scripts/projex.py`, following its [API guide](../fox-fix-issue/sources/projex.md#api-guide) for credentials and the Python 3.10+ interpreter.

## Defaults

The user can override any of these in the request; their values win.

| Setting | Default |
|---|---|
| Source | What the user names: Projex bugs, QA test cases, or issues they describe or link. With nothing named, Projex with the filter below |
| Projex project | The fix skill's default project |
| Projex filter | Assigned to the token's user (`projex.py me`), status exactly `待确认` or `再次打开`. The user states any other condition in words, such as only `待确认`, or several other statuses. A stated condition replaces only its own part: naming statuses keeps the assignee default. Never try to read a Projex saved view or the filter behind a view link: the API does not expose it. If the user gives only a view link, ask once for its conditions in words. Only status and assignee filter on the server; say so if the user asks for more |
| Concurrency | 5 worker tasks at once |
| Model provider | The provider the coordinator itself runs on; the user may name another provider or model |
| Worktree root | `~/Developer/worktrees/<repo-dir-name>/` |
| Base branch | `origin/master`, independent of the main checkout; the user may name another branch for a run, for example when related fixes are still unmerged on a feature branch |
| Acceptance workspace | `<root>/verification/` on branch `bugfix/verification`, created from the base branch |
| Fix workspaces | `<root>/<lowercase-key>/`, for example `fisn-1322/`, on branch `bugfix/<lowercase-key>` |
| Local slot | `LOCAL_SLOT=1` for the acceptance workspace |
| Acceptance lock | `<git-common-dir>/fox-verification.lock`, taken and released only with `../fox-fix-issue/scripts/accept-lock.sh`, with owner `coordinator` for the coordinator's own holds; its `acquire` can wait 45 minutes, so run it in the background when the host limits foreground commands |
| Acceptance login | macOS Keychain generic password, service `fox-local-login`, account = the email that owns the local test data. If it is missing, ask the user once through a secret card and store it with `security add-generic-password -U`; never keep it in a file. |

## 1. Prepare

1. Confirm the repository is the main checkout of the intended project and record its path. Run `git fetch origin master`, and fetch the base branch too when the user named another.
2. The Projex steps apply when the run involves Projex, or when `bugfix/verification` exists and has commits with a `Bug:` trailer that are not in the base (`git log <base>..bugfix/verification --grep '^Bug: '`), because step 5 may reset them away. Then run `projex.py me` and record `body.id`. A 403 means the token lacks the organization user read permission: report it and do not guess the user; stop when the run involves Projex, otherwise skip step 4 and do not reset in step 5.
3. Refresh the model inventory for every enabled provider (see [model routing](references/model-routing.md)). Do this on every run; never reuse a list from an earlier run.
4. When the Projex steps apply, run the [merge sync](#2-sync-merged-projex-fixes) now. It reads repair commits from the acceptance branch, and the next step can reset that branch and drop the only commits that carry a bug's trailer.
5. Ensure the acceptance workspace exists. If missing, create it with `git worktree add <root>/verification -b bugfix/verification <base>`, copy (never symlink) the main checkout's untracked `.env` files into it, and install dependencies as the repository documents. If it exists and is clean with no acceptance lock held, bring it up to `<base>` as in [update to the base](references/acceptance-env.md#update-to-the-base); otherwise leave it and report why.
6. Smoke-test acceptance before dispatching, so environment problems surface once instead of once per worker: follow [smoke test](references/acceptance-env.md#smoke-test). It also says how to start shared local middleware that is down.

## 2. Sync merged Projex fixes

Only when the Projex steps apply (Prepare step 2); run it from Prepare step 4, before the acceptance workspace is brought up to the base. List bugs assigned to the user with status exactly `开发完成` (map the name to its ID through a bug's workflow). Decide each with the [merged rule](../fox-fix-issue/sources/projex.md#mark-fixed-after-merge). When merged, set `已修复` through the fix skill's status procedure and read back, without asking. Otherwise leave the status and list the bug with its unmerged commits, or as undecided when no repair commit was found. The workflow may refuse to move `已修复` back, so apply the rule strictly.

## 3. Build the list

**Projex.** Search with `--status-id <id of each requested status> --assigned-to <user id>` page by page until `X-Total` items are read, and state the resolved filter (status names, assignee) in the plan. Skip bugs already being handled: status no longer one of the requested statuses, or an existing task titled with the key. Also search `已选择` with the same assignee and list those with no visible task in the report; never take them over. Sort by the `严重程度` custom field, P0 first through P3. Map legacy values `1-致命`=P0, `2-严重`=P1, `3-一般`=P2, `4-轻微`=P3; missing values go last. Ties go by creation time, oldest first.

**Issues the user describes or links.** Read each from where it lives, without changing it (see the [general source guide](../fox-fix-issue/sources/general.md)). Keep the user's order unless they ask for another.

**QA test cases.** The failures are the issues, so run the cases first (section 4).

Give every issue without a source key a short lowercase key, such as `qa-login-03` or `fb-export-csv`, unique within the run and among existing worktrees and branches. Use it for the task title, workspace, branch, lock owner, and test data.

## 4. Run QA cases

Only when the run includes QA test cases: dispatch one case runner and sort its failures as in [references/qa-cases.md](references/qa-cases.md). It holds the lock while running, so start fix workers only after it reports.

## 5. Triage

Read each issue's report: for Projex, the title, description, and comment text; for other sources, what the user supplied or the runner reported. Do not open attachments or read code; workers do that. Decide:

- **Group**: issues that share context, a root cause, or a fix approach go into one task. Prefer grouping when it saves rediscovery or lets one acceptance cover several issues.
- **Skip**: not this repository's code, a data or configuration problem rather than a code defect, or behavior that exists only on another unmerged branch. Record the reason; do not dispatch.
- **Flags**: a likely database migration (needs the user's approval before acceptance), frontend dependency changes, or additions to a shared numbered registry such as error codes, which parallel workers can claim twice; tell those workers to recheck the number before landing.
- **Complexity**: the evidence for the capability tier and effort in [model routing](references/model-routing.md).

## 6. Show the plan and dispatch

Show the plan as a table, then dispatch immediately without waiting for confirmation; the user interrupts if something is wrong. Columns: order, keys (with links when the source has them), source, severity when known, group reason, complexity, provider/model/effort with a short reason, flags. Below it, list skipped issues and non-defect case failures with reasons, and any merge sync results.

For each task, in plan order and up to the concurrency limit:

1. For Projex bugs, set each bug in the group to `已选择`, mapping the exact name to its ID through the workflow, and read back. Skip a bug already there; do not move a later status back. Other sources get no write.
2. Create its fix workspace while holding the acceptance lock, so the base never includes another worker's temporary cherry-picks: `git worktree add <root>/<key> -b bugfix/<key> bugfix/verification`, where `<key>` is the lowercase first key of the group. Symlink `frontend/node_modules` to the acceptance workspace's copy when that exists, and make sure `/frontend/node_modules` is in the shared exclude file (`git rev-parse --git-path info/exclude`), because a directory-only ignore pattern leaves the symlink untracked and blocks `git worktree remove`.
3. Start a worker task titled with the issue keys (for example `FISN-1322 FISN-1325`) using the chosen model and effort, with fresh context, and a brief built from the checklist in [references/worker-brief.md](references/worker-brief.md).
4. When a worker finishes, ends blocked, or ends waiting on the user, its slot frees and the next task starts. A worker waiting on the user does not hold a slot. Each time a task is dispatched, finishes, ends blocked, or starts waiting on the user, tell the user in one line right away: the keys, the state, and what happens next (for example `FISN-1322 验收通过，等待写回` or `FISN-1325 阻塞：缺本地数据，已转给你`). Do not wait for the final report, and do not repeat what the plan already said.

## 7. Answer workers

Answer directly, citing the evidence used, when the question is about: the implementation approach, a modest scope adjustment, coordination between issues or tasks (merging tasks, ordering acceptance), local test data, or a model escalation (see [model routing](references/model-routing.md#6-escalate-at-most-once)). When a cherry-pick conflicts because the acceptance branch moved after the fix workspace was created, [move the fix branch](references/acceptance-env.md#move-a-fix-branch) yourself. Base answers on the reports, repository docs and conventions, and other issues in the batch. Record each decision for the final report.

Before forwarding a factual question (which session or record a report refers to, whether data exists, which version an environment ran), check it yourself against the issue source and the read-only data sources the user has authorized; forward it only if those cannot settle it, and say what you checked.

Forward to the user, grouped and with the worker task links: disputed or undocumented expected product behavior, anything beyond the authorization above, approval to apply a migration during acceptance, and cherry-pick conflicts in the acceptance workspace the coordinator cannot settle by reordering or merging tasks. Do not guess product decisions. When a forwarded question involves the PRD or another product document, include the relevant excerpt and its section number, so the user can decide without looking it up.

### Acceptance lock problems

Before stopping or replacing a worker, and whenever a worker ends unexpectedly or reports that `acquire` timed out, follow [lock recovery](references/acceptance-env.md#lock-recovery). Never release a lock whose owner is still running.

## 8. Finish

When a worker reports that acceptance passed and its commits landed on the acceptance branch, or reports a settled no-fix conclusion:

1. Write each issue's draft to a UTF-8 file. Do not edit its substance; return it to the worker if it contradicts its own report.
2. For Projex bugs, run [`scripts/finish_bug.py`](scripts/finish_bug.py) per bug from the target repository through a login shell: `--fix-branch <the task's fix branch>` for a repair (every bug of a group uses the group's one branch, named after its first key), `--mode already-fixed --fix-commit <sha>` for a fix already in `origin/master`, and `--mode conclusion` for a no-fix conclusion once any product question it depends on is settled. The script checks the landing and, for a repair, the `Bug: <key>` trailer before writing, skips a comment that already exists, sets the statuses, and exits nonzero when the read-back does not match (its header has the details). A fix branch without commits fails the check: the issue then needs one of the other two modes, not a repair. When the landing or trailer check fails, write nothing to Projex for that bug; ask the worker about a landing failure and the user about a missing trailer.
3. For other sources, check a repair's landing with `finish_bug.py --mode landing --fix-branch <the task's fix branch>`, which writes nothing. Keep the draft for the report as the ready-to-paste conclusion. If the user explicitly authorized a write-back target and scope, write within that scope and read it back, preserving unrelated content. Otherwise present grouped drafts and ask before writing.
4. Remove the worktree (`git worktree remove`) and delete the fix branch and any backup branch with `git branch -D`. The branch was cherry-picked, not merged, so `-d` refuses it; the landing check above is what makes the deletion safe.

If a write fails or its outcome is uncertain, check its effect with read-only calls before retrying, and report what is still pending. Keep the worktree and branch of any blocked or unfinished task and list them.

Report once all tasks have finished or are waiting on the user:

- A table per task: keys with links, source, conclusion, commits on the acceptance branch, write-backs made (or the ready-to-paste conclusion), acceptance result, open questions or blockers, model and effort used.
- Merge sync results, skipped issues, and QA case failures that were not code defects, with their class and evidence.
- Counts of blocked tasks by cause (for example missing local data, acceptance environment unavailable, waiting on product), so recurring causes are visible.
- Decisions the coordinator made on workers' behalf.
- Test data that workers could not remove, with where it lives. Before reporting, remove what you can yourself, scoped by the issue key, the run's time window and the project, and list only what is still left.
- What the user needs to do next, such as pushing `bugfix/verification` and opening an MR to master. Projex `已修复` requires the fix to reach `origin/master`.
