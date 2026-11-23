# Fox Coordinate Issues

Coordinates a batch of issues: Projex (Alibaba Cloud DevOps) bugs assigned to you, QA test cases to run, or issues you describe or link from anywhere. One run may mix them. Each run:

1. For Projex, marks `开发完成` bugs whose fix is already in `origin/master` as `已修复`.
2. Builds the list: your `待确认` and `再次打开` Projex bugs (or the statuses you name; saved Projex views are never read, so state conditions in words) sorted by severity (P0 first) and then age, the issues you named, and for QA cases the failures a case runner finds. Case failures that are not code defects (wrong case, environment or data, disputed expectation) are reported, not fixed.
3. Triages them from the reports, groups related issues into one task, and picks a model and effort per task (the coordinator's own provider by default).
4. Shows the plan and dispatches up to 5 workers in parallel without waiting. Each worker runs [`fox-fix-issue`](../fox-fix-issue/SKILL.md) in its own worktree, then lands and accepts its fix one at a time in a shared acceptance worktree (`bugfix/verification`, created from `origin/master` by default) on a separate local slot.
5. Answers workers' implementation questions and forwards product questions to you, and tells you in one line whenever a task is dispatched, finishes, is blocked, or waits on you.
6. Owns every external write. Projex: sets dispatched bugs to `已选择`, and after a worker's fix lands posts the worker's drafted comment and sets `开发完成` (and `已修复` when the fix was already in `origin/master`). Other sources: writes nothing unless you confirm a draft in the task. Then it cleans up finished worktrees and reports, with a ready-to-paste conclusion per non-Projex issue.

The coordinator never fixes issues or runs cases itself. Invoke it manually with `$fox-coordinate-issues` (Codex) or `/fox-coordinate-issues` (Claude Code); `allow_implicit_invocation: false` and `disable-model-invocation: true` keep it manual-only.

## Requirements

- For Projex: `ALIYUN_YUNXIAO_TOKEN` with Projex work item, comment, and workflow permissions plus organization user read permission (for `projex.py me`).
- The `fox-fix-issue` skill next to this one.
- For parallel acceptance, the target repository's start scripts must support `LOCAL_SLOT=<n>` on the acceptance branch.

## Files

- [SKILL.md](SKILL.md): the coordination procedure.
- [references/model-routing.md](references/model-routing.md): per-task model and effort selection.
- [references/hosts.md](references/hosts.md): Codex, Claude Code, and T3 Code tool mapping.
- [references/acceptance-env.md](references/acceptance-env.md): smoke test, moving a fix branch after a conflict, and lock recovery.
- [references/qa-cases.md](references/qa-cases.md): running QA cases and sorting their failures.
- [references/worker-brief.md](references/worker-brief.md): what each worker brief must contain.
- [scripts/finish_bug.py](scripts/finish_bug.py): checks that a fix landed on the acceptance branch, then for Projex posts the worker's comment and sets `开发完成`; `--mode landing` only checks, and `--dry-run` writes nothing.
- [tests/test_finish_bug.py](tests/test_finish_bug.py): offline checks of the landing gate and status decisions; run `python3 -m unittest tests.test_finish_bug` from this folder.
