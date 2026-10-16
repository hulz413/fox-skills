# Task summary validation

Date: 2026-10-15. Result: scoped validation passed: 84 offline tests and a local summary replay of three retained real CLI records. Replay means reading saved compact execution and acceptance records through summary commands; it does not rerun CC/model calls or feed raw event streams through the runner. Documenting these results made no new worker calls or execution-policy changes.

## Tested artifact and evidence

- Implementation commit: `7da5bb53903708e705f2fcaa4769064386f9e0d5`.
- Runner SHA-256, matching the replay receipt and committed implementation: `a3eeee2dc7a7d5f3d3771755cb479062e688dfd5c4120d9c214053415f88242b`.
- Contract and usage: [CLI task summaries](../references/cc-records.md#task-summaries). Task-specific offline checks: [test_task_summary.py](test_task_summary.py); existing invocation checks: [test_cc_progress.py](test_cc_progress.py).
- Replay source: the A/turn-1, B/turn-1 and B/turn-2 records from the [earlier fan-out run](batch-fan-out-validation.md). Its [sanitized receipt](batch-fan-out-live-evidence.json) records the original live evidence and configuration; replay did not revalidate model, effort, authentication or provider routing.
- The originating chat retains `work/task-summary-validation/` with the explicit task index, captured summary and replay receipt; source records remain in `work/fan-out-live-20261015/`. These local files are not repository dependencies or a portable replay fixture. Raw session identifiers and absolute local paths are not copied here.

## Offline coverage

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s skills/fox-orchestrate/tests -p 'test_*.py' -v
```

The complete suite passed 84 tests: the previous 79 tests plus five task-summary test methods with subcases. These are test-method counts, not live-call or scenario counts. The new tests use synthetic records and local command invocations without model/service calls; existing runner tests also use fake CLI processes and fault injection.

| Area | Offline coverage |
| --- | --- |
| Task ownership | Explicit grouping preserves all attempts; records sharing a session are not collapsed. Relative/absolute/symlink aliases deduplicate within a task; cross-task ownership and duplicate/invalid task IDs are rejected. |
| Current artifact selection | Null selection remains pending despite a historical pass. Explicit selection can retain an older passed snapshot or a rejected snapshot while another call is active. Ordering does not determine selection. Missing selectors, nonmember selections, absent decisions and an invalid pass on failed execution are rejected. |
| Token accounting | Rejected and failed attempts remain included. Complete per-invocation totals sum normally; partial fields retain known subtotals, unknown counts and known zero values. Partial categories across separate calls do not create a complete total. Empty tasks report zero invocations with `reported: null, unknown_runs: 0`; an empty task list is accepted. |
| Legacy records and validation | Older failed records retain the `unknown` execution reason. Missing execution records, malformed execution/acceptance records and selected calls without acceptance fail the CLI without partial JSON output or raw broken-content diagnostics. An unselected call without acceptance remains pending. |
| Read-only behavior and compatibility | A patched process launcher rejects any subprocess dispatch during the task-summary function; file bytes remain unchanged in the synthetic fixture. Unused private acceptance fields are excluded. The CLI works from a different cwd. Existing invocation-summary output keys and token totals remain compatible. |

The unchanged existing suite also checks execution/acceptance separation, acceptance guards, token normalization, compact diagnostics and failure classification. See the [failure classification report](failure-classification-validation.md) for its separate artifact and live coverage; those live checks are not new task-summary trials.

## Retained real-record replay

The coordinator supplied an index mapping A to one invocation and B to its initial and repair invocations. `current_acceptance_run` explicitly selected A/turn-1 and B/turn-2. The task-summary CLI ran from a different cwd using manifest-relative paths; selections' `artifact_ref` values matched the corresponding saved acceptance records.

| Task | Invocation count | Explicit current selection | Selected acceptance | Tokens across all mapped attempts |
| --- | ---: | --- | --- | ---: |
| A | 1 | A/turn-1 | passed | 15,712 |
| B | 2 | B/turn-2 | passed | 28,277 |
| Batch | 3 | Two selected snapshots | Two tasks passed | 43,989 |

B's first candidate was a seeded artifact rejection, not a runtime failure. B/turn-1 remained completed/acceptance-failed and contributed 16,064 tokens; B/turn-2 contributed 12,213. Invocation acceptance counts remained pending 0, passed 2, failed 1; task acceptance counts were pending 0, passed 2, failed 0. All three executions were completed, active invocation count was zero, and execution-reason counts were zero. The original records predate classification fields; completed legacy records summarize with empty execution reasons.

Batch token subtotals were input 16, output 1,305, cache read 34,654 and cache creation 8,014, totaling 43,989, with zero unknown invocations for every category. Scope remains `main_loop_invocation`, including the rejected candidate and repair. Coordinator/nested/native usage and monetary billing are outside this measurement; selection does not filter consumption.

Two additional checks passed:

- The pre-change invocation-level `summarize` from base commit `2e389086c17d9a0cfd2aec12de5df685eace1976` and the new implementation produced equal parsed JSON for the same three directories. This comparison covers the retained sample, not every possible input.
- SHA-256 hashes of all nine source `status.json`, `summary.json` and `acceptance.json` files remained unchanged across replay. Source record preservation does not establish integrity of every referenced artifact/evidence file.

## Not verified

- Fresh worker execution, new artifact acceptance decisions or same-session repair through the new implementation. Only summary commands were run against retained records; original live behavior retains its earlier validation scope.
- Retained-record replay with active invocations, null/older/failed current selections, duplicate ownership, missing/partial tokens, invalid records or empty tasks. Those branches have the offline coverage above; the retained sample had two explicit passed selections and complete usage.
- Concurrent record/index mutation, crash-consistent cross-file snapshots, large batches, throughput or token savings. Read-only summaries do not establish scheduler, retry, queue, cancellation or recovery behavior.
- Automatic verification that selected artifacts still match the working tree or current task inputs, evidence-file contents/hashes, or completeness of the coordinator's index. The coordinator owns applicability; unlisted calls are outside the report, and selected snapshot acceptance does not establish combined batch acceptance.
- Native subagent recording/accounting or portability across other environments/CLI versions. The feature remains a CC record reader; the offline alias test exercised the local filesystem's symlink behavior.
- New routing/cooperation model previews or an independent reviewer/worker repair loop. Execution, routing and coordination policy were unchanged.

The validation entrypoint remains [tests/README.md](README.md). Earlier reports retain their original test counts, artifacts and limits.
