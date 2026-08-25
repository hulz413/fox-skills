# fix-qa-bugs

Selects one development-ready QA Bug from the feelinsonice Yunxiao Projex queue, excludes Bugs already owned by unfinished Codex tasks, and creates one dedicated repair task in the current local checkout.

The dedicated task re-verifies the Bug, decides whether a code change is necessary, selects a direct-fix, plan, or OpenSpec route, implements the smallest valid repair, runs local acceptance, and creates one scoped local commit.

## Safety properties

- Verifies that the local Git repository, current Codex project, and currently selected Yunxiao project all identify feelinsonice before reading the queue.
- Uses Chrome's `brandpal.ai Work Profile` for read-only Yunxiao access.
- Reuses the existing checkout, lists clickable links for tasks that may conflict, and requires an explicit user decision before accepting same-checkout write risk.
- Creates at most one task per invocation and prevents worker recursion with an internal context marker.
- Creates the dedicated task with a Chinese title and initial prompt, and requires the worker to communicate and report in Chinese.
- Never pushes, creates a PR, deploys, or updates Yunxiao.

## Installation

The canonical skill lives in this repository. Install it by linking the skill directory into the shared agent skill directory:

```bash
ln -s /Users/hulz/Developer/side-projects/fox-skills/skills/fix-qa-bugs /Users/hulz/.agents/skills/fix-qa-bugs
```

## Usage

Invoke `$fix-qa-bugs` from the feelinsonice project. You may optionally supply one Projex Bug URL or `FISN-<number>` target. A normal invocation always dispatches a dedicated task; only the generated internal worker prompt enters repair mode.
