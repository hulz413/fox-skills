# Claude Code CLI dispatch from Codex App

Read this when Claude Code CLI is requested or already authorized as an execution backend. Use Codex's command tool to run the installed `claude` executable. Do not pass Claude model IDs to Codex's native subagent dispatcher. This reference adds a backend adapter; it does not relax the [coordination rules](../SKILL.md) or [model-routing rules](model-routing.md).

## Prepare one bounded assignment

- Keep the coordinator in Codex App. Record backend `claude-code-cli`, role, resource owner, working directory, inputs, deliverable, acceptance, dependencies and selected model/effort. Supply role boundaries explicitly; CC does not inherit the Codex conversation or its invoked skills.
- Check the installed `claude --version`, supported CLI flags and existing authentication. For auth checks, retain only the needed logged-in/provider fields; do not print credentials or unrelated account details. Missing CLI, authentication or permissions is a blocker, not permission to install, log in interactively, change shared settings or substitute a backend.
- Select model and effort using CC's available models, current documentation and account restrictions. Honor exact pins. Aliases can resolve through user/provider configuration; record the resolved model and use it on subsequent turns to avoid alias drift. Never infer CC availability from the Codex model catalog.
- Check effort support, environment overrides and managed/account caps before accepting a pin. CC can clamp unsupported or capped effort, including silently in JSON output. A successful process or model self-report does not establish the effective effort. If a pin cannot be verified, block the route rather than claim it applied. An unpinned unknown effective effort must be reported as unknown with its requested value and acceptance limits.
- Select tools, permissions, hooks and MCP access for the role and assignment. Preserve required project instructions and existing safeguards. CC is a separate process: Codex's tool permissions are not automatically a CC permission policy. Do not add permission-bypass flags or broaden access to overcome a denial. In unattended runs, use supported non-interactive denial behavior and narrowly allow only authorized operations. Keep dispatch with the coordinator unless bounded coordination was explicitly delegated.

## Start and collect

Start a new session for a new assignment, without `--resume`, `--continue` or `--fork-session`. Advisors receive fresh supplied context, never an App fork. Save the prompt as a UTF-8 file containing the task, constraints, necessary raw evidence and acceptance criteria; do not embed untrusted task text in shell code.

Use explicit `--model`, `--effort` and structured output. Run the local [progress runner](../scripts/cc_progress.py) to save full stdout/stderr while exposing only a small status record to Codex. The following read-only example is not a model recommendation or a permission template for writing tasks. Use absolute paths and a new run directory for each turn:

```sh
python3 /absolute/path/to/fox-orchestrate/scripts/cc_progress.py run \
  --run-dir /absolute/path/to/assignment/turn-1 \
  --cwd /absolute/path/to/workspace \
  --prompt-file /absolute/path/to/assignment/prompt.txt \
  --model SELECTED_CC_MODEL --effort SELECTED_CC_EFFORT \
  -- --tools Read --allowedTools Read --permission-mode dontAsk \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --settings '{"disableAllHooks":true}'
```

The runner currently supports POSIX hosts (macOS/Linux). It passes the prompt through stdin and launches CC through an argv array, never shell interpolation. It fixes `-p --output-format stream-json --verbose`; parameters after `--` are authorized CC options, not a shell command. Retain required hooks/MCP tools when the assignment needs them. These invocation-only restrictions do not edit shared settings. The runner does not select models, grant permissions, verify effort or replace coordinator acceptance.

### Background execution and on-demand status

Run CC through the host's asynchronous command/process-session interface. Track the host session and each assignment's run directory separately. Do not start an HTTP server, open a progress UI or external terminal, stream events into chat, or ask CC for progress narration. Continue useful coordinator work and prefer native completion notifications when available. Do not cancel another assignment's process or start overlapping writers on the same resource.

Query status only when it affects a concrete decision: a dependency blocks the next step, the user asks for status, evidence suggests failure or timeout, or completion must be checked for acceptance. Read the local compact record with:

```sh
python3 /absolute/path/to/fox-orchestrate/scripts/cc_progress.py status \
  --run-dir /absolute/path/to/assignment/turn-1
```

This command reads a file; it does not invoke CC. Query once for the decision at hand. An unchanged status is not a reason to query again. Avoid fixed-interval polling, repeated log reads and synthetic progress updates. When completion is required and no independent work remains, use the host's bounded process wait/completion mechanism; do not implement a model-driven refresh loop. Keep required user-facing updates focused on new evidence, decisions or blockers.

Full events remain in `stdout.jsonl`, stderr in `stderr.log`, and the final result in `result.json`. Only brief state is stored in `status.json` and `summary.json`; the runner prints one compact final status. Model text, thinking, tool arguments and tool output are excluded from that state. Unknown events stay in raw logs. After completion inspect only the required result, artifact checks and targeted diagnostics; never `tee` or dump full logs into model-facing tool output.

### Lightweight records and summaries

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

Acceptance is written to a unique same-directory temporary file, closed, then atomically published with a [hard link](https://pubs.opengroup.org/onlinepubs/9699919799/functions/link.html). Readers see either no decision or the complete record; competing/repeated writers cannot replace an existing destination. Temporary files are removed on ordinary success/error exits; abrupt termination can leave them. The filesystem must support hard links; publication errors are reported without an overwrite fallback. This guarantees publication visibility, not power-loss durability or atomic snapshots across multiple files.

Read a summary for explicitly selected invocation directories, without invoking CC or reading raw message bodies:

```sh
python3 /absolute/path/to/fox-orchestrate/scripts/cc_progress.py summarize \
  --run-dir /absolute/path/to/assignment/turn-1 \
  --run-dir /absolute/path/to/another-assignment/turn-1
```

The JSON report separates `process_phase` and `acceptance` for each invocation. Repeated directory paths count once. `token_totals` reports each category's known subtotal as `reported` and the number of unknown invocations as `unknown_runs`; a subtotal with unknown runs is not a complete total. Older records without token fields stay unknown. The report does not count invocations as unique tasks, infer acceptance from model prose, or scan unrelated directories.

### Task summaries

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

The selection must belong to that task and contain a valid existing `acceptance.json`, whose passed/failed decision, `artifact_ref` and `evidence_file` become `current_acceptance`. Null means no currently selected artifact and counts as pending even if historical decisions passed. Never select by ordering, timestamps, process success or any historical pass. The coordinator confirms that the chosen artifact/version applies to the current assignment and inputs; changed artifacts/inputs require clearing or reassessing that selection under the existing acceptance rules. The reader does not verify current working-tree contents or rerun evidence checks. Historical decisions remain unchanged.

The report contains `tasks` with invocation `runs`, `invocation_count`, `active_invocation_count`, `current_acceptance`, `token_totals`, `execution_reason_counts` and `invocation_acceptance_counts`. Batch totals additionally separate `task_acceptance_counts` from invocation counts. An accepted selected snapshot may coexist with active or later rejected calls; it does not establish that all execution ended or combined acceptance passed.

Task and batch token totals reuse the invocation rules above and include every mapped attempt regardless of selection or acceptance. Per-field unknown counts and per-invocation complete totals remain separate; partial categories across different calls are not combined into a complete total. Empty tasks report `reported: null, unknown_runs: 0`, with zero invocations. Shared calls cannot be double-assigned or automatically apportioned; coordinator/nested/native usage remains outside the existing CC scope. Elapsed times stay per invocation, not summed into batch wall time. The command only reads the index and compact execution/acceptance files; it adds no worker calls, dispatch, retry or record mutation. The invocation-level `summarize` interface/output remains unchanged.

### Execution failure handling

Malformed JSON, missing/failed results and process errors cannot report success; permission denials reported by either a system event or the final denial list require attention, even when the other source is empty. `permission_denial_seen` preserves the event evidence separately from the final list count. Preserve the distinct CC and runner exit codes. Cancellation remains incomplete and is forwarded/escalated to the assigned process group without changing model/configuration. The runner does not automatically retry a failed turn.

### Failure reasons

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

**Token boundary:** local execution, log recording and state updates make no extra model calls. There is no continuous display or monitoring token overhead. Necessary orchestrator queries, interpreting their compact results, dispatch and acceptance still consume normal tokens; do not promise zero total token consumption.

Inspect structured events after completion, not just the last output line or claimed task success:

- Retain the session ID from initialization/result events, CLI version, requested configuration, observable effective configuration, exit status and diagnostics in the assignment record. Use reported fields only when actually present; output schemas vary by version. `system/init.model`, assistant message models and final `modelUsage` provide model evidence. Inspect all relevant model usage for substitutions or fallback, accounting separately for auxiliary models rather than equating every usage key with the worker model.
- Require a successful process exit and a successful final `result` (`is_error: false`, successful subtype), then check permission denials, incomplete work and the actual acceptance criteria. A final response alone does not prove files changed correctly or tests passed. Empty/malformed output, missing result, authentication/model errors, cancellation and denied required operations are failures or incomplete work; preserve their diagnostics.
- Verify effort through runtime configuration evidence, such as the session's local `/effort` report or sanitized configuration metadata, where supported. Some CC versions record `effort` and `perTurnEffort` on assistant entries in that session's persisted transcript; inspect only the assigned session and extract only needed fields. CLI acceptance, `per_turn_effort_active` and thinking-token counts do not establish a particular effort level. Do not collect raw API bodies or credentials merely for proof. Record unavailable evidence honestly; never use model prose as configuration evidence.
- If a pin differs from observed settings, stop accepting work under that route and report the mismatch. Do not silently retry with another backend/model/effort. For unpinned substitutions, apply the existing fallback and acceptance rules before further work.

## Resume without changing configuration

Save the exact session ID and verify that persistence actually worked before promising continuation. Do not use `--no-session-persistence` for resumable work. A returned session ID alone does not prove that a transcript was saved; sandbox permissions or local persistence policy may prevent it.

For a follow-up, give the runner a new turn directory and resume the recorded ID in the same working directory using its `--resume SESSION_ID` option, the same resolved model and selected effort, and the same required permission/tool configuration. Save each turn's stdout, stderr and exit status separately without overwriting earlier evidence. Supply the delta, missing evidence and affected checks. Never use `--continue` to guess which session to resume, or `--fork-session` to replace the existing assignment. Do not change configurations during corrections, repairs or final checks.

If the session is missing, report the persistence failure. Restore necessary context only through an authorized fresh-context handoff with the unchanged assignment configuration; disclose the loss of retained context rather than presenting the new process as a successful resume. Resolve permission or persistence conditions before repeating a failed call. Independent reviewers use a separate fresh session from the producer and receive the artifact/version and necessary evidence.

## Finish

The coordinator checks outputs, affected callers and critical failure paths, and owns repairs/rechecks and final acceptance. Distinguish requested settings, observable effective settings, CC task completion and coordinator verification. Retain useful failure evidence and requested deliverables, remove unneeded task-created temporary data, and do not delete unrelated CC sessions or shared configuration. Actual provider/tool usage belongs to the external backend; report costs only when measured, without inferring equivalence to Codex usage.

Current interface references: [CLI flags](https://code.claude.com/docs/en/cli-reference), [programmatic execution and resume](https://code.claude.com/docs/en/headless), [model and effort configuration](https://code.claude.com/docs/en/model-config). Consult them for material interface gaps; use the installed interface and observed behavior for execution.
