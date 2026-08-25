---
name: fix-qa-bugs
description: Select one unowned, development-ready QA Bug from the feelinsonice Yunxiao Projex queue, create a dedicated Codex task in the current checkout, and have that task assess, fix, validate, and commit the Bug. Also handles the internal dedicated-worker mode. Do not use for batch dispatch, PRs, deployment, or Yunxiao updates.
---

# Fix QA Bugs

## Outcome

Handle at most one QA Bug per invocation.

The default dispatcher mode reads the current Bug queue, checks unfinished Codex tasks, excludes Bugs already being repaired, selects the next eligible Bug, and creates one dedicated Codex task. The dedicated task owns all Bug assessment, implementation, local acceptance, and the scoped local commit. The dispatcher must not modify product code.

The same skill also supports dedicated-worker mode. Enter worker mode only when the initial prompt contains all of the following:

- the exact marker `FIX_QA_BUGS_WORKER_CONTEXT`;
- one unique Projex Bug identifier;
- an explicit instruction not to create or contact another task.

A normal user invocation, a Bug URL, or a Bug ID alone always means dispatcher mode. This distinction prevents recursive task creation.

Neither mode may push, create a PR, merge, deploy, or write back to Yunxiao.

## Dispatcher mode

1. Read [project and Projex selection rules](references/projex.md).
2. Read [Codex task ownership and dispatch rules](references/task-coordination.md).
3. Verify the local Git project, current Codex project, and currently selected Projex project before reading the Bug queue. Stop on any mismatch.
4. Read all development-ready Bug candidates and all relevant unfinished Codex tasks.
5. Exclude Bugs owned by unfinished dedicated repair tasks, then select the first remaining candidate by priority and current page order.
6. Recheck task ownership immediately before creation to reduce duplicate dispatch races.
7. Create one dedicated Codex task in the current project using the existing local checkout, pass the required context, and confirm that the task was accepted or queued.
8. Report the exclusions, selected Bug, and created task, then stop. Do not wait for completion unless the user separately asks to monitor it.

Dispatcher mode may read Yunxiao, Codex task state, and local Git state. It must not inspect product code for the selected Bug, run repair tests, edit files, or create backup tasks.

## Dedicated-worker mode

1. Read [project and Projex selection rules](references/projex.md) and [current checkout and Git rules](references/worktree-and-git.md).
2. Handle only the Bug named in the worker context. Do not read the queue, select another Bug, or create or message another task.
3. Re-read the live Bug and verify that it still belongs to the current local project and still needs development work.
4. Inspect the current checkout and preserve all pre-existing changes.
5. Assess whether the Bug is valid and worth fixing, then choose the direct-fix, plan, or OpenSpec path.
6. Implement the smallest root-cause fix, add focused regression coverage, run local acceptance, and create exactly one scoped local commit.

If the Bug has already been fixed, resolved, sent to QA, closed, or archived, stop without selecting another Bug.

## Necessity assessment

Stay read-only until this assessment is complete:

1. Use the description, reproduction steps, attachments, comments, activity history, and observed runtime evidence. Do not treat the title as proof.
2. Compare the behavior with current code, tests, OpenSpec, product contracts, and the deployed-version evidence available in the Bug.
3. Distinguish a real defect from intended behavior, a requirement change, an environment or data issue, a duplicate, a stale report, or a problem already fixed elsewhere.
4. State impact, repair benefit, regression risk, and the consequence of not fixing it. Conclude with `needs fix`, `no fix needed`, or `user decision required`.
5. For `no fix needed`, report the evidence and stop without editing or committing.
6. If expected behavior, reproduction conditions, product trade-offs, or scope remain ambiguous or contradictory, ask the user before implementation.

When a required decision has two or three mutually exclusive choices, prefer `request_user_input` with the recommended option first. Do not enter implementation before the user answers.

## Complexity routing

Choose the route from business semantics, risk, and coordination cost rather than file count. Tell the user which route was selected and why.

### Direct fix

Use for a clear, local, reversible defect that does not change a product contract, persistence model, or cross-service interface and can be covered by focused tests. Reproduce, fix, test, validate, and commit without another implementation approval.

### Plan

Use for a medium-sized defect spanning several files or modules with multiple implementation steps or a meaningful regression surface, but no durable specification change.

1. Produce a read-only implementation plan covering root cause, edit points, tests, risks, and rollback.
2. Ask the user to approve, adjust, or stop before editing.
3. After approval, implement, validate, and commit without separate test or commit confirmations.

### OpenSpec

Use when the fix must define or change product behavior, a cross-service or public contract, HTTP or Temporal events, data models or migrations, authorization or security boundaries, key metric definitions, or several durable acceptance rules.

1. Use `$openspec-explore` and then `$openspec-propose` on the current branch. Include the Bug number in the change context and acceptance criteria.
2. Stop after proposal and ask the user to approve apply, request changes, or stop.
3. After approval, use `$openspec-apply-change` and complete local acceptance.
4. Use `$openspec-sync-specs` and `$openspec-archive-change`, verify the synced main specs and archive, then create one commit containing implementation and OpenSpec artifacts.
5. If evidence contradicts the proposal, return to explore/propose and obtain approval again.

## Browser boundary

- Use Chrome with the `brandpal.ai Work Profile` for Alibaba Cloud and Yunxiao.
- Do not use a personal Chrome profile or the in-app browser as an authentication workaround.
- Reuse normal signed-in state without reading or exporting cookies, Local Storage, passwords, verification codes, or access tokens.
- Hand authentication, OTP, and CAPTCHA steps to the user.
- Yunxiao access is read-only. Do not post comments or change status, assignment, verification, priority, severity, or other fields.

## Dedicated repair sequence

1. Re-read the Bug number, title, URL, priority, severity, assignee, verifier, status, full description, attachments, comments, activity, and related items.
2. Record the current repository root, branch, `HEAD`, staged changes, unstaged changes, and untracked files.
3. Complete the necessity assessment. Stop on `no fix needed`; ask the user on `user decision required`.
4. Select and follow the appropriate complexity route.
5. Reproduce and locate the root cause. Follow the root and relevant nested `CLAUDE.md` files. Do not add demo data, silent fallbacks, unrelated compatibility code, or opportunistic cleanup.
6. Prefer a regression test that fails before the fix and passes afterward. If automation is not practical, explain why and record exact manual reproduction and acceptance steps.
7. Re-read live Bug status immediately before the first code edit. Stop if it no longer needs development work.
8. Run focused regression tests plus affected lint, type checks, and integration checks. Do not substitute unrelated passing tests for Bug evidence.
9. Stage only exact Bug paths or patches and create one local Conventional Commit that references the Bug number.
10. Report results and stop.

## Stop conditions

Stop and report instead of bypassing any of these conditions:

- The local Git project, current Codex project, and selected Projex project do not match exactly.
- Dispatcher mode cannot list or inspect relevant Codex tasks, so ownership cannot be established.
- The current local checkout already has an unfinished dedicated QA repair task that may write to it.
- The current project cannot be uniquely resolved for local task creation.
- The dedicated task cannot be created in the existing local checkout.
- The Bug involves destructive database migration, permissions, security, secrets, billing, or irreversible data changes.
- The expected behavior conflicts with OpenSpec, product contracts, or another Bug.
- Existing checkout changes overlap the Bug and cannot be safely separated or precisely staged.
- Required read-only external evidence or authentication is unavailable.
- The expected behavior or repair boundary remains ambiguous.

## Reporting

The dispatcher reports the project identity check, excluded Bugs and their exact owning task titles, the selected Bug number/title/priority/assignee/status, and the new task title and creation result.

The worker reports the Bug number/title/priority/assignee/status, necessity conclusion and evidence, complexity route, root cause, changed scope, branch, local commit SHA, tests actually run, and any blocker. Claim `fixed locally` only after local acceptance and commit. Never claim deployment or online acceptance.
