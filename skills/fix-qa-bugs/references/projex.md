# Project identity and Projex selection rules

## Fixed feelinsonice identity

- Local repository root: `/Users/hulz/Developer/brandpal/projects/feelinsonice`
- Local project name: `feelinsonice`
- Yunxiao project name: `feelinsonice`
- Yunxiao Bug list: `https://devops.aliyun.com/projex/project/ab491d6f94800aaeb9ef68e915/bug#viewIdentifier=1dedc5afd44979211cad516f`
- Yunxiao project ID: `ab491d6f94800aaeb9ef68e915`
- Yunxiao organization ID: `659b8196e29648ed55c8f571`

These Yunxiao identifiers were observed on 2026-08-21 and must be verified at runtime.

## Mandatory identity check

Perform this check before opening or refreshing the Bug list:

1. Resolve the current Git repository root and project name. Stop unless the root is the fixed feelinsonice repository above.
2. Use the Codex project list to resolve the current task's saved project. Stop unless its local path resolves to the same repository root.
3. In Chrome's `brandpal.ai Work Profile`, inspect the currently selected Projex project context without changing projects. Use the selected or most recently active Projex project tab and read the visible project name, project ID, and organization ID.
4. Stop if no current Projex project context can be determined, if multiple active project contexts are ambiguous, or if any cloud value differs from the fixed feelinsonice identity.
5. Only after all three identities match may the dispatcher navigate within that project and read the Bug queue.

Do not switch the cloud project to manufacture a match. Report the local repository, Codex project, and observed cloud project values when stopping.

The dedicated worker repeats the local-versus-cloud check before relying on live Bug data.

## Candidate selection

1. If the user provides a Bug URL or serial number, place only that Bug in the candidate set. A serial number has the form `FISN-338`; a URL must resolve uniquely.
2. If URL and serial number are both supplied, they must identify the same work item.
3. Without a target, read every currently development-ready Bug candidate. Do not stop at the first visible row.
4. Exclude fixed, resolved, pending-verification, closed, archived, or otherwise terminal items, including items with clear repair evidence even if the status name is not terminal.
5. Order the remaining candidates by `Urgent`, `High`, `Medium`, and `Low`. Preserve the current page order within a priority.
6. Apply the active-task ownership exclusions from [task coordination](task-coordination.md), then select the first remaining candidate.
7. If a status is unclear, inspect resolution, activity, comments, and related PR evidence before keeping the candidate.
8. If no candidate remains, report why and do not create a task.

If a user-specified Bug is already owned by another dedicated task, report that task and stop. Do not select a different Bug.

## Current field notes

The `priority` field values observed on 2026-08-21 were:

| Order | Value | ID |
| --- | --- | --- |
| 1 | `Urgent` | `70001c3bff679c238a27a6d070` |
| 2 | `High` | `931655bbb1c3cec743d26a7135` |
| 3 | `Medium` | `a25b99cbcb3e36da5c692a63b6` |
| 4 | `Low` | `de62fd282a0b7b86d8b8404ade` |

`New` was status ID `28` and `Closed` was `100085` on that date. Status workflows can change. Read current metadata and decide whether development work is still required rather than hard-coding `New` as the only eligible state or treating every non-closed item as eligible.

## Required Bug detail

The dispatcher reads and passes:

- serial number, unique work-item identifier, title, detail URL, status, priority, and severity;
- preconditions, reproduction steps, expected result, and actual result;
- attachment names and relevant visible evidence;
- comment and activity summaries plus related work items;
- assignee and verifier.

The worker must re-read all of these fields live. Missing expected behavior requires product or QA clarification; do not silently turn a Bug into a product requirement.

## Read-only boundary

Use an existing least-privilege `x-yunxiao-token` with the official search API only when one is already available. Otherwise use Chrome's signed-in state. Never create a long-lived token or extract browser credentials.

Do not post comments or change any Yunxiao field.
