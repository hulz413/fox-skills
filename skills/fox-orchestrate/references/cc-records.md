# Optional Claude Code records and reports

Read this when persistent acceptance decisions, invocation/task summaries, token accounting or structured failure codes are needed. [CLI execution and actual artifact verification](claude-code-cli.md) remain required; these reporting commands are optional unless the assignment requests them. The runner records execution state and raw logs independently of this choice.

## Invocation records and acceptance

Each invocation records local `elapsed_seconds`, reported `num_turns`, and `token_usage` in its compact state. Token fields are `input_tokens`, `output_tokens`, `cache_read_input_tokens`, and `cache_creation_input_tokens`; `total_tokens` adds those four disjoint categories only when all are reported. Missing or invalid counts are null, never assumed zero. Thinking tokens are not added again to output tokens. No monetary estimate is extracted.

`token_usage_scope: main_loop_invocation` means the final result's `usage` for this invocation's main agent loop. It excludes nested agents and coordinator usage. Do not add cumulative `modelUsage` across resumed calls: it includes earlier session activity and can double-count it. Failed calls retain reported usage; a call without final usage remains unknown. The [official usage guide](https://code.claude.com/docs/en/agent-sdk/cost-tracking) explains these scopes. Elapsed time is local invocation time, not a batch's wall-clock time.

`phase: completed` means execution completed without a reported process/result/permission failure; it does **not** mean the task passed acceptance. After checking the assigned artifact and acceptance criteria, the coordinator may explicitly record the decision against a commit, diff hash or other identifiable artifact snapshot and an existing local evidence file:

```sh
python3 /absolute/path/to/fox-orchestrate/scripts/cc_progress.py record-acceptance \
  --run-dir /absolute/path/to/assignment/turn-1 \
  --outcome passed --artifact-ref COMMIT_OR_SNAPSHOT \
  --evidence-file /absolute/path/to/assignment/verification.json
```

Use `--outcome failed` for a checked rejection. This command records the coordinator's decision; it does not run or independently validate checks. It requires finished execution, and an unsuccessful execution cannot be marked passed. `acceptance.json` preserves the original decision without changing process state or overwriting an existing decision. Repairs use a new turn directory. The decision is valid only for the recorded artifact version; changed artifacts require new checks and a new record. Missing acceptance remains `pending`.

New decisions also store `evidence_sha256`, the SHA-256 of the evidence file's raw bytes, read in blocks without text/JSON normalization. Finalize the evidence and stop writing it before recording acceptance. Evidence must be a readable regular file; hashing failures publish no new decision. The hash binds the bytes read during recording, not the correctness of checks or the current artifact/inputs. It is not an authentication mechanism or an atomic snapshot with the evidence file.

Acceptance is written to a unique same-directory temporary file, closed, then atomically published with a [hard link](https://pubs.opengroup.org/onlinepubs/9699919799/functions/link.html). Readers see either no decision or the complete record; competing/repeated writers cannot replace an existing destination. Temporary files are removed on ordinary success/error exits; abrupt termination can leave them. The filesystem must support hard links; publication errors are reported without an overwrite fallback. This guarantees publication visibility, not power-loss durability or atomic snapshots across multiple files.

Read a summary for explicitly selected invocation directories, without invoking CC or reading raw message bodies:

```sh
python3 /absolute/path/to/fox-orchestrate/scripts/cc_progress.py summarize \
  --run-dir /absolute/path/to/assignment/turn-1 \
  --run-dir /absolute/path/to/another-assignment/turn-1
```

The JSON report separates `process_phase`, `acceptance` and `evidence_integrity` for each invocation. Repeated directory paths count once. `token_totals` reports each category's known subtotal as `reported` and the number of unknown invocations as `unknown_runs`; a subtotal with unknown runs is not a complete total. Older records without token fields stay unknown. The report does not count invocations as unique tasks, infer acceptance from model prose, or scan unrelated directories.

For recorded decisions, summaries compare bound evidence bytes using the same digest rule. They expose only an integrity status, never evidence contents:

| `evidence_integrity` | Meaning |
| --- | --- |
| `null` | No acceptance decision; not applicable |
| `unbound` | Legacy decision without `evidence_sha256`; evidence is not read or backfilled |
| `matched` | Bytes read for this summary match the recorded digest |
| `mismatch` | Readable evidence has different bytes |
| `missing` | Bound evidence file is absent |
| `unreadable` | Bound evidence cannot be read or is not a regular file |

Only an absent digest field is legacy-compatible. A present digest must be exactly 64 lowercase hexadecimal characters; malformed values, including null, fail the command without partial JSON. Integrity problems (`mismatch`, `missing`, `unreadable`) are reported successfully and do not rewrite historical decisions, change acceptance/failure counts, select another artifact or exclude token usage. A historical `passed` can coexist with `mismatch`; `matched` does not establish current artifact/input applicability. Summaries do not rerun checks or modify files. Files may change after or during a read; this is not a concurrent evidence snapshot guarantee.

## Task summaries

For CC task-level collection, the coordinator can supply an optional JSON index:

```json
{"tasks": [
  {"task_id": "A", "run_dirs": ["A/turn-1"], "current_acceptance_run": "A/turn-1"},
  {"task_id": "B", "run_dirs": ["B/turn-1", "B/turn-2"], "current_acceptance_run": "B/turn-2"}
]}
```

```sh
python3 /absolute/path/to/fox-orchestrate/scripts/cc_progress.py summarize-tasks \
  --manifest /absolute/path/to/batch.json
```

Each task requires a unique nonempty `task_id`, a `run_dirs` list and an explicit `current_acceptance_run` path or `null`. Relative run/selection paths resolve against the manifest's directory, including symlink resolution. Repeated paths within one task count once; assigning one canonical directory to multiple tasks is an error. Sessions and directory names do not infer task identity. Keep every attempt, including repairs, in the mapping; unlisted calls are outside the report. Empty `run_dirs` is allowed only with a null selection. Missing/malformed records are errors, not skipped calls.

The selection must belong to that task and contain a valid existing `acceptance.json`, whose passed/failed decision, `artifact_ref` and `evidence_file` become `current_acceptance`, together with the invocation's already computed `evidence_integrity`. Null means no currently selected artifact and counts as pending even if historical decisions passed. Never select by ordering, timestamps, process success or any historical pass. The coordinator confirms that the chosen artifact/version applies to the current assignment and inputs; changed artifacts/inputs require clearing or reassessing that selection under the existing acceptance rules. The reader does not verify current working-tree contents or rerun evidence checks. Historical decisions remain unchanged.

The report contains `tasks` with invocation `runs`, `invocation_count`, `active_invocation_count`, `current_acceptance`, `token_totals`, `execution_reason_counts` and `invocation_acceptance_counts`. Batch totals additionally separate `task_acceptance_counts` from invocation counts. An accepted selected snapshot may coexist with active or later rejected calls; it does not establish that all execution ended or combined acceptance passed.

Task and batch token totals reuse the invocation rules above and include every mapped attempt regardless of selection or acceptance. Per-field unknown counts and per-invocation complete totals remain separate; partial categories across different calls are not combined into a complete total. Empty tasks report `reported: null, unknown_runs: 0`, with zero invocations. Shared calls cannot be double-assigned or automatically apportioned; coordinator/nested/native usage remains outside the existing CC scope. Elapsed times stay per invocation, not summed into batch wall time. The command reads the index, compact execution/acceptance files and any bound evidence; it adds no worker calls, dispatch, retry or record mutation. Existing invocation-summary fields retain their meanings; `evidence_integrity` is an additive field in invocation rows and selected task acceptance metadata. Task selection and all token rules are unchanged.

## Failure reasons

`status.json`, `summary.json` and each `summarize` row include `failure_reasons`: `null` while starting/running, `[]` for completed execution, or a list of fixed reason codes for unsuccessful execution. These codes describe observed evidence, not necessarily the underlying root cause. Independent evidence can produce multiple codes; a known cause suppresses generic missing-result/exit symptoms.

| Code | Evidence |
| --- | --- |
| `launch_error` | The runner could not start the CC subprocess. |
| `permission_denied` | A system denial event or nonempty final denial list. |
| `limit_reached` | An error result with subtype `error_max_turns`, `error_max_budget_usd` or `error_max_structured_output_retries`. |
| `invalid_output` | Malformed event JSON, invalid required result/denial fields, or a missing final result without a more specific explanation. |
| `execution_error` | A failed result not covered above, or a nonzero CC exit without a more specific explanation. |
| `interrupted` | The runner received and forwarded an interruption signal; this alone does not establish timeout or user intent. |
| `runner_error` | The runner encountered an error while processing or recording execution. |
| `unknown` | Unsuccessful execution without classification evidence, including older records without this field. |

The summary adds `execution_reason_counts` and separate `acceptance_counts` (`pending`, `passed`, `failed`). Counts cover deduplicated invocation directories, not unique tasks; reason counts can overlap. A completed execution rejected by the coordinator keeps `failure_reasons: []` and `acceptance: failed`; its check evidence explains the artifact failure. Pending acceptance and unknown token usage are not execution failures. Older completed records summarize with `[]`, active records with `null`, and unsuccessful records with `["unknown"]`; original files are not rewritten. Malformed new reason fields are rejected rather than silently reclassified.

Recovered tool errors and `system/api_retry` events do not themselves establish terminal failure. Do not infer authentication, rate-limit, network or model causes from free-text errors or retry history; inspect retained diagnostics and confirm evidence before treating a problem as shared. Classification adds no retry, dispatch, cancellation or model/effort changes. Preflight errors can occur before a new execution directory exists; they produce a CLI diagnostic rather than a synthetic invocation record. If storage itself fails, a complete failure record may also be unavailable.
