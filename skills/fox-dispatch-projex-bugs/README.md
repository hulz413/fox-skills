# Fox Dispatch Projex Bugs

Coordinates a batch of Projex (Alibaba Cloud DevOps) bugs assigned to you. Each run:

1. Marks `开发完成` bugs whose fix is already in `origin/master` as `已修复`.
2. Lists your `待确认` bugs, sorted by severity (P0 first) and then age.
3. Triages them from the bug text, groups related bugs into one task, and picks a model and effort per task (the coordinator's own provider by default).
4. Shows the plan and dispatches up to 5 workers in parallel without waiting. Each worker runs [`fox-fix-projex-bug`](../fox-fix-projex-bug/SKILL.md) in its own worktree, then lands and accepts its fix one at a time in a shared acceptance worktree (`bugfix/projex-daniel`, created from `origin/master` by default) on a separate local slot.
5. Answers workers' implementation questions and forwards product questions to you.
6. Owns every Projex write: sets dispatched bugs to `已选择`, and after a worker's fix lands posts the worker's drafted comment and sets `开发完成`. Then it cleans up finished worktrees and reports.

The coordinator never fixes bugs itself. Invoke it manually with `$fox-dispatch-projex-bugs` (Codex) or `/fox-dispatch-projex-bugs` (Claude Code); `allow_implicit_invocation: false` and `disable-model-invocation: true` keep it manual-only.

## Requirements

- `ALIYUN_YUNXIAO_TOKEN` with Projex work item, comment, and workflow permissions plus organization user read permission (for `projex.py me`).
- The `fox-fix-projex-bug` skill next to this one.
- For parallel acceptance, the target repository's start scripts must support `LOCAL_SLOT=<n>` on the acceptance branch.

## Files

- [SKILL.md](SKILL.md): the coordination procedure.
- [references/model-routing.md](references/model-routing.md): per-task model and effort selection.
- [references/hosts.md](references/hosts.md): Codex, Claude Code, and T3 Code tool mapping.
- [scripts/finish_bug.py](scripts/finish_bug.py): checks that a fix landed on the acceptance branch, then posts the worker's comment and sets `开发完成`; `--dry-run` writes nothing.
