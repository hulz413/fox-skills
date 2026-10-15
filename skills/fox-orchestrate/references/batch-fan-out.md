# Batch fan-out

Use this recipe for repeated, independently checkable assignments such as module migrations or separate audits. Fan-out distributes a batch across workers; collection brings their results back to the coordinator. It uses the existing host tools, without a scheduler or persistent worker pool.

Apply the [assignment, ownership and acceptance rules](../SKILL.md#delegate-and-coordinate) and [model routing](model-routing.md). Native subagents remain the default; use the [CC CLI adapter](claude-code-cli.md) only when that backend is authorized. This recipe adds no roles, model presets or execution permissions.

## Define the batch

Record the common input version or snapshot, shared change rule and applicable limits once. Extend the existing assignment records with task IDs and links to each task's agent/session and invocation records; no fixed file format is required. Keep coupled changes together, and put work requiring upstream results in a later batch.

For example, a configuration migration can share one reviewed input snapshot and migration rule, with this task list:

| Task | Exclusive scope | Acceptance check | Invocation records |
| --- | --- | --- | --- |
| M01 | Module A and its migration tests | Module A behavior and new configuration contract | `batch/M01/turn-1`, `batch/M01/turn-2` |
| M02 | Module B and its migration tests | Module B behavior and new configuration contract | `batch/M02/turn-1` |

These paths illustrate CC turn directories; native assignments link to their host records. Keep check criteria and necessary context in each assignment under the existing contract. A file is a suitable task boundary only when its change can be completed and checked independently.

## Dispatch and isolate

For an unproven batch rule, check a small representative subset before expanding; reuse applicable prior validation. Set concurrency from supported free capacity and actual resource limits. Refill available capacity using host completion notifications or bounded waits, observing the existing lifecycle rules; do not assume returned results release slots or add periodic model-driven polling.

Read-only tasks may share the specified input snapshot and use separate output locations. Run concurrent code writers in separate worktrees based on the same specified input version, then let the coordinator integrate changes serially. If required inputs include uncommitted changes, establish how those inputs reach the worktrees rather than silently using a committed baseline. Preserve unrelated work. Apply existing resource ownership to shared services and check outputs too; worktrees isolate checkout files, not every external resource.

Use the existing context and continuation rules for each assignment. For CC, keep its prompt and per-turn records through the adapter; do not replace the runner with shell interpolation or batch-level shared logs.

## Collect failures and results

An isolated task failure need not stop independent tasks. When a shared authentication, permission, service or input problem affects the batch, pause further affected dispatches and diagnose it before repeating calls. Do not automatically cancel unrelated active work or set a universal failure-rate threshold. Follow the existing repair and fixed-configuration rules; a new turn directory is still part of the same assignment.

Maintain the mapping from task ID to all its invocations and the artifact/version each acceptance decision covers. Use the CC adapter's `summarize` for selected turn directories and `record-acceptance` after coordinator checks, following its [recording contract](claude-code-cli.md#lightweight-records-and-summaries). Process completion leaves task acceptance pending. Keep failed attempts in the record; include their reported tokens when summarizing batch consumption.

Count tasks by task ID, not invocation count. The example has two tasks and three invocations; M01's repair does not create a third task. Report each task's checked artifact and remaining work separately from invocation totals. Preserve the CC token scope and unknown subtotals; native usage is reported only when available, and the CC summary does not account for native workers or coordinator usage.

## Integrate and accept

The coordinator integrates accepted outputs and checks the combined artifact against the batch goal and relevant cross-task contracts. Individual passes do not establish that the integrated result passes. Apply the existing version-bound review and acceptance rules to the combined result, retaining unresolved tasks and useful failure evidence. Clean up task-created disposable artifacts through the host's supported mechanisms without discarding unintegrated work.
