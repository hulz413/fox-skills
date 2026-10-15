# Failure classification validation

Date: 2026-10-15. Result: scoped validation passed. The offline suite passed 79 tests, including 20 runner tests; one real CC invocation deliberately ended at its turn limit and was classified correctly. The expected execution failure was not a failed validation. Documenting these results made no additional worker calls or execution-policy changes.

## Tested artifact and evidence

- Implementation commit: `1c988727772d2ec55a3a4e5c67be27bbae73e7d1`.
- Runner SHA-256, identical for the live run and committed implementation: `31d20a9ecf86da4c5e325bb2eda3eac40f682bbaaea8bd3602e1887089187279`.
- Classification and recording contract: [CLI failure reasons](../references/claude-code-cli.md#failure-reasons). Executable offline checks: [test_cc_progress.py](test_cc_progress.py).
- Retained live evidence in the originating chat's local `work/failure-classification-live/` directory: frozen manifest, prompt/input, one-off harness, raw events/stderr, result/status/summary and controller receipt. These local files are not repository dependencies or a portable replay fixture; raw session identifiers and local paths are not copied here.
- Saved live `result.json` SHA-256: `a07c5a5952b282ce9902ee482c91eaf2d1e93b5d02a6c0cf6dc53809b5ac1726`; raw `stdout.jsonl` SHA-256: `01a396b53f2c95043c0b4426e4e1e2c9599d14989137a768dbb036d8d4786485`. Hashes identify retained artifacts; they do not replace their contents or independently attest to provider behavior.

## Offline coverage

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s skills/fox-orchestrate/tests -p 'test_*.py' -v
```

The reviewed implementation passed 79 tests: the previous 73-test suite plus six new runner test methods and strengthened existing assertions. The 20 runner tests contain subcases; these numbers are test-method counts, not numbers of live failures or classification categories. Offline checks use synthetic records, fake CLI processes and fault injection, without model/service calls.

| Area | Offline evidence |
| --- | --- |
| Launch versus preflight | Missing executable produces `launch_error`, exit 127 and an execution record. Missing prompt fails before a new directory exists. |
| Permission evidence | Final denials and a system denial surviving an empty final list produce `permission_denied`. A nonzero CC exit of 2 alone does not imply denial. |
| Limit results | Explicit `error_max_turns`, `error_max_budget_usd` and `error_max_structured_output_retries` fixtures map to `limit_reached`. |
| Output and execution errors | Malformed JSON, invalid result/denial fields and unexplained missing results map to `invalid_output`; unexplained nonzero exits and well-formed failed results (including an unrecognized error subtype) map to `execution_error`. Error prose is not used to infer authentication or HTTP causes. |
| Multiple reasons | Independent permission/output or permission/execution evidence is retained together. Generic missing-result/exit symptoms do not replace a more specific explanation. |
| Recovery versus terminal failure | A tool-error block and API-retry event followed by a successful final result leave `failure_reasons: []`. This tests classification, not the backend's recovery algorithm. |
| Interruption | Synthetic process-group termination is classified as `interrupted`, not timeout. Existing descendant forwarding/escalation checks remain passing. |
| Runner failure and cleanup | A one-shot recording-error injection after permission evidence produces both `permission_denied` and `runner_error`. Implementation review fixed an unclosed stdout pipe; regression assertions check subprocess termination and pipe closure. |
| Record validation and legacy data | Malformed reason lists are rejected without echoing arbitrary values. Legacy unsuccessful records become `unknown` in summaries without rewriting the source; running records remain unclassified and completed records have no execution reasons. |
| Summaries and acceptance | Invocation directories are deduplicated; overlapping reason counts remain separate from acceptance counts. Completed execution can have failed artifact acceptance and zero execution reasons. Unfinished/unsuccessful execution cannot pass acceptance; decisions require evidence and cannot overwrite earlier decisions. |
| Token and compact-output boundaries | Failed usage is retained, session-cumulative model usage is not summed, missing/invalid usage remains unknown, and private bodies/arguments/diagnostics stay outside compact output. |

## Real CLI coverage

Preflight reported Claude Code 2.1.299, logged-in `claude.ai` authentication and `firstParty` provider configuration. The requested and initialized model was `claude-haiku-5-5`; requested effort was `low`. The runner's `effective_effort` remained `null`; effective effort and the provider route were not independently attested for this invocation.

A single invocation read a synthetic JSON file containing values `[13, 29, 47]` and a marker, with a prompt requiring an actual Read before returning the sum and marker. Only the Read tool was exposed/allowed. Options included `restricted`, `dontAsk`, `permission-prompts none`, disabled hooks/bundled skills and empty strict MCP configuration. The harness froze one invocation, `--max-turns 1` and a 120-second host timeout; it issued no retry or continuation.

| Observation | Recorded value |
| --- | --- |
| Tool activity | One Read tool call and a non-error tool result; fixture input hash unchanged |
| Final result | `subtype: error_max_turns`, `is_error: true`, `terminal_reason: max_turns` |
| Execution state | `phase: failed`, `incomplete: true`, `failure_reasons: ["limit_reached"]` |
| Exit codes | CC 1; runner 1; controller observed runner exit 1, as expected for this induced failure |
| Summary counts | `limit_reached: 1`, all other execution reasons 0; acceptance pending 1, passed 0, failed 0 |
| Acceptance guard | Coordinator-side `check_acceptance(state, "passed")` rejected the actual state; no `acceptance.json` was written |
| Other evidence | No permission denial or invalid event; stderr empty; host timeout not reached |
| Timing | Runner 7.071 seconds; controller 7.158 seconds |
| Turn fields | Requested `max-turns: 1`; CLI-reported `num_turns: 2`, retained unchanged |

The result's turn count is reported metadata, not a claim that it equals the configured limit or counts model requests. The stream also contained a `rate_limit_event` with status `allowed`; this was not an induced throttling failure. This run verifies an explicit terminal limit result and its recording/summary path, not general limit-accounting semantics.

Reported tokens: input 2, output 108, cache read 1,556, cache creation 2,247; total 3,913, with no unknown categories. Scope is this failed invocation's `main_loop_invocation`; coordinator usage, nested agents, hidden service activity and monetary billing are outside the measurement. The failed invocation's tokens remained included.

## Retained-record compatibility

A local summary check reused the three pre-classification records from the [earlier fan-out run](batch-fan-out-validation.md), without rerunning workers. All three completed executions received empty execution reasons; their existing acceptance outcomes remained passed, failed, passed. Reported token total remained 43,989 with zero unknown invocations, and hashes of their status/summary/acceptance files remained unchanged. This is compatibility evidence, not three new live classification trials or consumption from the turn-limit run.

## Not verified

- Live launch/preflight failures, permission denial, malformed/missing output, generic execution error, signal cancellation or runner/storage failure. Those paths have the offline coverage above; actual persistent disk failure may prevent any complete record.
- Live budget exhaustion or structured-output retry exhaustion. Their subtype mappings were tested only with fixtures.
- Authentication, network, rate-limit/overload or model-availability faults; retry exhaustion, shared-blocker diagnosis, batch pause/resume or recovery after a failure. No retry or scheduling logic was added; automatic recovery was not evaluated.
- A successful fresh invocation, artifact acceptance decision or same-session repair in this live check. Earlier evidence and offline checks cover different scenarios and must not be relabeled as coverage from this invocation. The live rejection used the acceptance helper, not the `record-acceptance` CLI command.
- Native subagent records, concurrency/fan-out behavior, other CLI versions/models/providers, independent effective-effort verification, general task quality, repeatability, performance or token savings.
- New routing/cooperation model previews or an independent reviewer/worker repair loop. Routing and coordination policy did not change.

The validation entrypoint remains [tests/README.md](README.md). Historical CLI/background/fan-out reports retain their original artifacts and scopes.
