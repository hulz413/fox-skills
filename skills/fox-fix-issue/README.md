# Fox Fix Issue

Fixes one issue or a group of related issues end to end, wherever they come from: a Projex (Alibaba Cloud DevOps) bug URL or key such as `FISN-1134`, a QA test case, or feedback passed on from a chat, a document, or a screenshot.

1. Identifies the issue and its key, shows its link, and renames the task to the keys.
2. Reads the whole report and restates the problem in plain Chinese.
3. Investigates and either fixes it, asks material questions, or concludes that no fix is needed.
4. Validates with focused tests, creates one local commit per issue, then runs local end-to-end acceptance in the host's built-in browser.
5. Writes back by source. Projex: `已选择`, a repair comment and `开发完成`, a conclusion comment, and `已修复` only once every repair commit (found by its `Bug: <key>` trailer) is in `origin/master`. Other sources: nothing is written without the user's confirmation; the report carries a ready-to-paste conclusion.

It never pushes, merges, deploys, or uses shared environments. Invoke it manually with `$fox-fix-issue` (Codex) or `/fox-fix-issue` (Claude Code); `allow_implicit_invocation: false` and `disable-model-invocation: true` keep it manual-only.

## Modes

- **Standalone**: invoke it on an issue; it works in the current repository and branch.
- **Dispatched**: [`fox-coordinate-issues`](../fox-coordinate-issues/README.md) starts it as a worker with a fix worktree, a shared acceptance worktree, a local slot, and an acceptance lock; questions go to the coordinator, and the worker returns write-back drafts instead of writing. The coordinator can also start a case runner that only runs QA cases.

## Requirements

- For Projex: `ALIYUN_YUNXIAO_TOKEN` with Projex work item, comment, and workflow permissions (organization user read permission too, for `projex.py me`), and Python 3.10+ for `scripts/projex.py` (standard library only).

## Files

- [SKILL.md](SKILL.md): the procedure shared by every source.
- [sources/projex.md](sources/projex.md): Projex identification, comments, statuses, the merged rule, and the API guide.
- [sources/general.md](sources/general.md): every other source, QA test cases and the case runner included.
- [references/dispatched-mode.md](references/dispatched-mode.md): where a dispatched worker edits, tests, lands, and accepts, and how it uses the acceptance lock.
- [references/hosts.md](references/hosts.md): Codex, Claude Code, and T3 Code tool mapping.
- [scripts/projex.py](scripts/projex.py): narrow Projex OpenAPI client.
- [scripts/in_master.py](scripts/in_master.py): decides whether a fix commit's change is in `origin/master`, squash merges included.
- [scripts/accept-lock.sh](scripts/accept-lock.sh): bounded acquire and owner-checked release of the shared acceptance lock in dispatched mode.
- [scripts/run-vitest.sh](scripts/run-vitest.sh): `vitest run` with workers capped at 50% of the cores (`RUN_VITEST_MAX_WORKERS` overrides), so parallel worktrees do not exhaust memory. The percentage was checked on vitest 3.2.7 and 4.1. A project's own `poolOptions` or `VITEST_MAX_FORKS` / `VITEST_MAX_THREADS` take precedence over the cap. It fails instead of downloading vitest when none is installed.
- [tests/](tests/): offline tests of the Projex client, the acceptance lock, the merged check, and the vitest wrapper; run `python3 -m unittest tests.test_projex tests.test_accept_lock tests.test_in_master tests.test_run_vitest` from this folder.

## Official references

Projex OpenAPI documentation used by `scripts/projex.py` and `sources/projex.md`, checked on 2026-10-30.

- [ListWorkitemAttachments: request syntax and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemattachments)
- [GetWorkitemFile: request parameters and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemfile)
- [Service endpoint: endpoint domain](https://help.aliyun.com/zh/yunxiao/developer-reference/service-access-point-domain)
- [Personal access tokens: creation and permissions](https://help.aliyun.com/zh/yunxiao/user-guide/personal-access-token)
- [GetProject: request syntax and authorization](https://help.aliyun.com/zh/yunxiao/developer-reference/getproject)
- [GetWorkitem: request syntax and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitem)
- [SearchWorkitems: request parameters and pagination window](https://help.aliyun.com/zh/yunxiao/developer-reference/searchworkitems)
- [ListWorkitemComments: request syntax and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemcomments)
- [GetWorkitemWorkflowInfo: response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemworkflowinfo-get-work-item-workflow-information)
- [UpdateWorkitem: request syntax and status update format](https://help.aliyun.com/zh/yunxiao/developer-reference/updateworkitem)
- [CreateWorkitemComment: request parameters and formatType](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitemcomment)
