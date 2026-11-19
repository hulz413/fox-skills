# Fox Fix Projex Bug

Fixes Projex (Alibaba Cloud DevOps) bugs end to end from a bug URL or issue key such as `FISN-1134`, one bug or a group of related bugs per task:

1. Confirms the bug, shows its link, renames the task to the issue keys, and moves the bug to `已选择`.
2. Reads the description, comments, and attachments, and restates the problem in plain Chinese.
3. Investigates and either fixes it, asks material questions, or posts a conclusion comment when no change is needed.
4. Validates with focused tests and local end-to-end acceptance in the host's built-in browser, then creates one local commit per bug with a `Bug: <key>` trailer.
5. Posts a repair comment and sets `开发完成`; sets `已修复` only once every repair commit for the bug is in `origin/master`.

It never pushes, merges, deploys, or uses shared environments.

## Modes

- **Standalone**: invoke it on a bug; it works in the current repository and branch.
- **Dispatched**: [`fox-dispatch-projex-bugs`](../fox-dispatch-projex-bugs/README.md) starts it as a worker with a fix worktree, a shared acceptance worktree, a local slot, and an acceptance lock; questions go to the coordinator.

## Requirements

- `ALIYUN_YUNXIAO_TOKEN` with Projex work item, comment, and workflow permissions (organization user read permission too, for `projex.py me`).
- Python 3.10+ for `scripts/projex.py` (standard library only).

## Files

- [SKILL.md](SKILL.md): the procedure.
- [references/projex.md](references/projex.md): Projex API usage and the bundled client.
- [references/hosts.md](references/hosts.md): Codex, Claude Code, and T3 Code tool mapping.
- [scripts/projex.py](scripts/projex.py): narrow Projex OpenAPI client.
- [tests/test_projex.py](tests/test_projex.py): offline contract tests; run `python3 -m unittest tests.test_projex` from this folder.
