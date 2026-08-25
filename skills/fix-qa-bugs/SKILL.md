---
name: fix-qa-bugs
description: Select one unowned, development-ready QA Bug from the feelinsonice Yunxiao Projex queue, create a Chinese-language dedicated Codex task in the current checkout, mark the Bug In Progress, and have that task assess, fix, validate, and commit it. Also handles the internal dedicated-worker mode. Do not use for batch dispatch, PRs, deployment, or other Yunxiao updates.
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

Neither mode may push, create a PR, merge, or deploy. After successfully creating the dedicated task, dispatcher mode performs exactly one permitted Yunxiao write: transition the selected Bug's status to `In Progress`. Treat the user's instruction to dispatch the Bug, including approval of any displayed checkout conflicts, as authorization for this status transition; do not ask for a separate confirmation after task creation. Dedicated-worker mode remains read-only in Yunxiao.

## Dispatcher session reuse

A fixed dispatcher task may handle repeated user requests such as `继续下一个 Bug`. Reuse conclusions already established in that same dispatcher conversation instead of restarting the workflow from zero.

- Cache the verified local repository root, Codex project ID and path, Projex project and organization identity, previously dispatched Bug ownership, and relevant task identifiers in conversation state. Do not create a repository cache file.
- Reuse stable identity conclusions while the dispatcher task, cwd, Codex project, and observed Projex context remain unchanged. Another invocation or the passage of time alone does not invalidate them.
- Refresh volatile state before selecting or creating each new task: the development-ready Bug queue, the chosen Bug's live status, unfinished task ownership, same-checkout conflicts, branch, `HEAD`, and dirty paths.
- Repeat only the affected identity check when evidence indicates a change or contradiction, such as a different cwd or repository, a different Codex project, navigation to another Projex project or organization, ambiguous browser context, or a user-requested full refresh.
- Report reused conclusions and newly refreshed facts concisely; do not narrate a full identity check again when it was reused.

## Dispatcher mode

1. Read [project and Projex selection rules](references/projex.md).
2. Read [Codex task ownership and dispatch rules](references/task-coordination.md).
3. Establish the local Git, Codex project, and Projex project identity on the first invocation, or reuse the verified session identity when the session-reuse conditions still hold. Stop on any mismatch.
4. Refresh all development-ready Bug candidates and all relevant unfinished Codex tasks. Reuse earlier conclusions only as context, not as proof that volatile state is still current.
5. Exclude Bugs owned by unfinished dedicated repair tasks, then select the first remaining candidate by priority and current page order.
6. Detect unfinished tasks that may write to the same checkout. If any exist, show their clickable task links and the selected Bug link in the response body, explain the overlap risk, and ask the user whether to continue. Never navigate to a conflicting task automatically. Continue only after explicit approval for the displayed conflict set.
7. Recheck Bug ownership and same-checkout conflicts immediately before creation to reduce duplicate dispatch and write races. Ask again if a new conflict appears.
8. Create one dedicated Codex task in the current project using the existing local checkout, pass only the minimal routing context, and confirm that the task was accepted or queued. Use a Chinese task title, initial prompt, and response requirement. Near the beginning of the initial message, include the selected Bug as a clickable `[FISN-000: Full Bug title](<detail URL>)` link followed by a synthesized one- or two-sentence `TL;DR`. Do not paste the Bug fields, description, checkout path list, or dispatch analysis into the visible message.
9. Follow the post-dispatch status transition in [project and Projex selection rules](references/projex.md): re-read the selected Bug and set only its status to `In Progress` immediately after the dedicated task is confirmed. Do not add a second user-confirmation gate for this transition.
10. Report the exclusions, selected Bug, conflicts and decision, created task, and Yunxiao status-transition result with clickable links, then stop. Do not wait for completion unless the user separately asks to monitor it.

Dispatcher mode may read Yunxiao, Codex task state, and local Git state, and may perform only the post-creation `In Progress` transition. It must not inspect product code for the selected Bug, run repair tests, edit files, create backup tasks, or change any other Yunxiao field.

## Dedicated-worker mode

1. Read [project and Projex selection rules](references/projex.md) and [current checkout and Git rules](references/worktree-and-git.md).
2. Handle only the Bug named in the worker context. Do not read the queue, select another Bug, or create or message another task.
3. Re-read the live Bug and verify that it still belongs to the current local project and still needs development work.
4. Inspect the current checkout and preserve all pre-existing changes.
5. Assess whether the Bug is valid and worth fixing, then choose the direct-fix, plan, or OpenSpec path.
6. Implement the smallest root-cause fix, add focused regression coverage, run local acceptance, and create exactly one scoped local commit.

If the Bug has already been fixed, resolved, sent to QA, closed, or archived, stop without selecting another Bug.

## Worker opening response

At the start of the dedicated task, read the live Bug details and available evidence before inspecting or changing product code. Then give the user a compact Chinese opening response rather than a field-by-field recap:

- Put the clickable Bug link first.
- Follow it with one `TL;DR` paragraph of one or two natural-language sentences that synthesizes the trigger, faulty behavior, expected behavior, and practical impact. Do not copy the title or description verbatim, enumerate the source fields, or restate the same fact under separate labels.
- Default to at most three short paragraphs: Bug link, `TL;DR`, and one optional `待确认` or `初步思路` sentence. Do not use a table or a long bullet list.
- Add `待确认` only when an uncertainty affects expected behavior, reproduction, scope, or acceptance, then wait for the user's answer.
- When the information is sufficient, add one short `初步思路` sentence describing the likely investigation and validation direction without presenting an unverified root cause as fact.

If clarification is required, provide the preliminary repair direction only after the user answers. This opening direction is provisional: refine it after code inspection and root-cause analysis, then give the separate pre-implementation repair brief before the first code edit.

## Necessity assessment

Stay read-only until this assessment is complete:

1. Use the description, reproduction steps, attachments, comments, activity history, and observed runtime evidence. Do not treat the title as proof.
2. Compare the behavior with current code, tests, OpenSpec, product contracts, and the deployed-version evidence available in the Bug.
3. Distinguish a real defect from intended behavior, a requirement change, an environment or data issue, a duplicate, a stale report, or a problem already fixed elsewhere.
4. State impact, repair benefit, regression risk, and the consequence of not fixing it. Conclude with `needs fix`, `no fix needed`, or `user decision required`.
5. For `no fix needed`, report the evidence and stop without editing or committing.
6. If expected behavior, reproduction conditions, product trade-offs, or scope remain ambiguous or contradictory, ask the user before implementation.

When a required decision has two or three mutually exclusive choices, prefer `request_user_input` with the recommended option first. Do not enter implementation before the user answers.

## Pre-implementation repair brief

After concluding `needs fix` and locating the root cause, but before the first code edit, give the user a concise Chinese repair brief. State:

- the selected route and why;
- the intended change and affected scope;
- the focused validation approach.

Keep this to one short paragraph or a few bullets. For a direct fix, this is an informational checkpoint and does not add another approval gate. For Plan or OpenSpec/spec-driven development, it may serve as the compact introduction to the route's required plan or proposal, and the existing approval gate still applies.

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
- Dedicated-worker Yunxiao access is read-only. Dispatcher mode may change only the selected Bug's status to `In Progress`, and only after the dedicated task is confirmed. Do not post comments or change assignment, verifier, priority, severity, or any other field.

## Dedicated repair sequence

1. Re-read the Bug number, title, URL, priority, severity, assignee, verifier, status, full description, attachments, comments, activity, and related items, then provide the required worker opening response.
2. Record the current repository root, branch, `HEAD`, staged changes, unstaged changes, and untracked files.
3. Complete the necessity assessment. Stop on `no fix needed`; ask the user on `user decision required`.
4. Reproduce and locate the root cause. Follow the root and relevant nested `CLAUDE.md` files. Do not add demo data, silent fallbacks, unrelated compatibility code, or opportunistic cleanup.
5. Select the appropriate complexity route and give the pre-implementation repair brief before any code edit, then follow that route and its approval rules.
6. Prefer a regression test that fails before the fix and passes afterward. If automation is not practical, explain why and record exact manual reproduction and acceptance steps.
7. Re-read live Bug status immediately before the first code edit. Stop if it no longer needs development work.
8. Run focused regression tests plus affected lint, type checks, and integration checks. Do not substitute unrelated passing tests for Bug evidence.
9. Stage only exact Bug paths or patches and create one local Conventional Commit that references the Bug number.
10. Report results and stop.

## Stop conditions

Stop and report instead of bypassing any of these conditions:

- The local Git project, current Codex project, and selected Projex project do not match exactly.
- Dispatcher mode cannot list or inspect relevant Codex tasks, so ownership cannot be established.
- Same-checkout write conflicts exist and the user declines or has not explicitly approved continuing after seeing the exact conflict task links and risk.
- The current project cannot be uniquely resolved for local task creation.
- The dedicated task cannot be created in the existing local checkout.
- The Bug involves destructive database migration, permissions, security, secrets, billing, or irreversible data changes.
- The expected behavior conflicts with OpenSpec, product contracts, or another Bug.
- Existing checkout changes overlap the Bug and cannot be safely separated or precisely staged.
- Required read-only external evidence or authentication is unavailable.
- The expected behavior or repair boundary remains ambiguous.

## Reporting

The dispatcher reports the project identity check, excluded Bugs and their exact owning task titles, the selected Bug number/title/priority/assignee/status, any same-checkout conflict tasks and the user's decision, the new task title and creation result, and whether Yunxiao now shows `In Progress`.

Use clickable Markdown links in ordinary response text:

- Bug: `[FISN-343: Full Bug title](https://devops.aliyun.com/projex/bug/<workitem_id>)`
- Codex task: `[Task title](codex://threads/<thread_id>)`

Keep structured confirmation headers and questions as plain text without Markdown links, for example `是否仍要创建 FISN-343 修复任务？`. Put all clickable links in the response body immediately before the confirmation. Never open or navigate to a task on the user's behalf merely to present a conflict.

The worker communicates and reports in Chinese. It reports the Bug number/title/priority/assignee/status, necessity conclusion and evidence, complexity route, root cause, changed scope, branch, local commit SHA, tests actually run, and any blocker. Claim `fixed locally` only after local acceptance and commit. Never claim deployment or online acceptance.
