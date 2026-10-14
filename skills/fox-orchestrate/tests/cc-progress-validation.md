# Local CC terminal progress validation

Historical record: this display implementation has been removed. Use [background validation](cc-background-validation.md) for the current behavior. Server/terminal lifecycle descriptions below apply only to the earlier validation.

Validated on 2026-10-14 with Claude Code 2.1.299 from Codex App on macOS.

Final artifact SHA-256:

- `scripts/cc_progress.py`: `9c95c35c1a6e1f001d739ef68bec3390220b819391fe2890ebb47c4b770abc35`
- `tests/test_cc_progress.py`: `d646101a67971b2199315745251710d678ae5d98fcac0016d268ba15a7c2b2af`
- `references/claude-code-cli.md`: `ee8fc1736e0802ec7701c398c257e324d2ef0904af40a8d803a1d32f51c869ee`

## Actual CC execution

An isolated read-only worker read three name/email records, deduplicated by case-insensitive email while preserving the first name, normalized/sorted emails and returned the result. The task included a private canary in the final answer to test display separation. The coordinator verified exact output records with local assertions, without forwarding raw logs to its model context.

Both turns used `claude-sonnet-5-5` / `low`, with only Read exposed/allowed, `dontAsk`, invocation-only hooks disabled and MCP excluded. The second turn resumed the exact first session and reverified the input. No configuration change, permission-bypass option or additional progress-report prompt was used. The same-session transcript recorded `effort: low` and `perTurnEffort: low` on all four assistant entries; the runner itself reports effective effort as unknown, leaving evidence verification to the coordinator.

| Evidence | Initial turn | Final-version resume |
| --- | --- | --- |
| CC / runner exit code | 0 / 0 | 0 / 0 |
| Observed model | claude-sonnet-5-5 | claude-sonnet-5-5 |
| Raw stdout kept locally | 9,984 bytes | 10,104 bytes |
| Caller status output | 408 bytes | 428 bytes |
| Filtered local progress | 6 lines | 6 lines |
| Canary present in raw/final result and absent from viewer | Passed | Passed |
| Actual records, tool events and same-session checks | Passed | Passed |
| Separate Terminal launch | osascript acknowledged opening | Not reopened |

The actual worker call returned only compact status JSON to Codex. The full stdout, stderr, result, progress and status artifacts remain under `/private/tmp/fox-cc-progress-live/turn-1` and `turn-2`; sanitized local assertions are in `/private/tmp/fox-cc-progress-live/sanitized-validation.json`. These are validation deliverables, not runtime dependencies. Viewing logs later in Codex would add context; this check did not send their bodies to the model.

The first live turn preceded cancellation-only hardening; unchanged event filtering and terminal-launch evidence were reused. The second live turn executed the final script. Both actual progress logs were rendered with the final viewer in a locally captured verification process; only assertion outcomes and byte counts were returned to Codex.

## Tests and independent review

- 68 offline tests passed, including nine progress-runner tests.
- Incremental test observed `Read started` while a controlled worker was still running, before completion; raw prompt/body/arguments/results were absent from the viewer and caller output. Raw evidence remained available locally.
- Failure checks covered malformed JSON, malformed denial metadata, nonzero CC exit, permission denials, missing result and refusing to overwrite existing turn evidence. Prompt shell metacharacters stayed literal through stdin.
- Cancellation checks covered an active leader, descendants holding stdout after their leader exits, and a descendant ignoring SIGTERM. Cancellation is marked `cancelled`/`incomplete`, forwarded to the assigned process group and escalated after five seconds; the leader is reaped. The viewer alone does not control the worker.
- Terminal-opening timeout is bounded and reports a viewer-unavailable state; the worker remains independently executable.
- Skill structure validation, local links/anchors, Python compilation and focused diff whitespace checks passed.
- Independent reviewer gpt-6-luna / medium found two cancellation defects during review. Both were fixed; the same reviewer rechecked affected process/cleanup paths and nine focused tests and found no remaining material issue.
- Model routing and cooperation selection policies/fixtures were unchanged. Prior preview evidence was not rerun or rescored; the existing calibration gaps in `claude-code-cli-validation.md` remain disclosed. This change was checked with operational tests and live execution rather than claiming new routing accuracy.

## Limits

The computer-use tool refused access to Terminal, so no GUI screenshot or accessibility-text observation was obtained. Terminal automation acknowledged the separate-window launch; filtered rendering, real event collection and live CC execution were checked separately. A launch acknowledgement is not claimed as a screenshot check.

The runner supports POSIX hosts; automatic Terminal opening is macOS-specific. Existing event display uses only standard-library local parsing/file operations and no model/API call. This establishes no extra inference for display itself, not zero overall task/coordinator tokens or measured total cost savings. The display contains tool-state events rather than model body text, command arguments/output or invented percentages; unknown event types remain in raw logs but are omitted from display. Effective configuration pins and task acceptance remain coordinator responsibilities.
