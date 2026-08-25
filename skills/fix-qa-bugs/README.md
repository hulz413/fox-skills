# fix-qa-bugs

Selects one development-ready QA Bug from the feelinsonice Yunxiao Projex queue, excludes Bugs already owned by unfinished Codex tasks, creates one dedicated repair task in the current local checkout, and then marks that Bug `In Progress`.

The dedicated task re-verifies the Bug, decides whether a code change is necessary, selects a direct-fix, plan, or OpenSpec route, implements the smallest valid repair, runs local acceptance, and creates one scoped local commit.

## Safety properties

- Verifies that the local Git repository, current Codex project, and currently selected Yunxiao project all identify feelinsonice before reading the queue.
- Reuses verified project identity within a fixed dispatcher conversation and refreshes only volatile Bug, task, and checkout state for each next dispatch.
- Uses Chrome's `brandpal.ai Work Profile`; all Yunxiao access is read-only except the selected Bug's post-creation status transition to `In Progress`.
- Reuses the existing checkout, lists clickable links for tasks that may conflict, and requires an explicit user decision before accepting same-checkout write risk.
- Creates at most one task per invocation and prevents worker recursion with an internal context marker.
- Reads each leading candidate's complete Bug details and comment threads before dispatch so stale descriptions or later QA/product decisions can change whether it should be repaired.
- Creates the dedicated task with `gpt-5.6-sol` and `high` reasoning, a Chinese title, a readable Bug link, routing instructions, and a complete Bug/comment snapshot; the worker normally performs only a lightweight freshness check and generates the first TL;DR in its opening response.
- When the user explicitly authorizes isolated batch coordination and names a local final branch, rebases each validated Bug branch onto the latest final-branch tip and integrates it with `git merge --ff-only` before cleaning up its temporary worktree.
- Never pushes, creates a PR, deploys, or updates any Yunxiao field other than the selected Bug's post-creation `In Progress` transition.

## Installation

The canonical skill lives in this repository. Install it by linking the skill directory into the shared agent skill directory:

```bash
ln -s /Users/hulz/Developer/side-projects/fox-skills/skills/fix-qa-bugs /Users/hulz/.agents/skills/fix-qa-bugs
```

## Usage

Invoke `$fix-qa-bugs` from the feelinsonice project. You may optionally supply one Projex Bug URL or `FISN-<number>` target. A normal invocation always dispatches a dedicated task; only the generated internal worker prompt enters repair mode.
