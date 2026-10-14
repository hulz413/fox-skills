# CC background execution validation

Validated on 2026-10-14. This is the current execution mode; prior Terminal and App panel reports describe removed implementations.

## Artifact and checks

- Actual live-run runner SHA-256: `27a65244a66c7b2442201293ae81d77bc9623c4ead6039a6f74fa9b1855b9ce0`.
- Offline suite after review: 68 tests passed, including compact-state isolation, status queries without another CC invocation, literal stdin/argv, exclusive evidence directories, failure/permission denial handling and process-group cancellation/escalation.
- Skill format validation passed. Final diff/content review preserved roles, routing, configuration pins, resume, permissions and acceptance rules.
- Removed panel server and its tests; removed filtered `progress.log` display output. No UI or HTTP server is launched by the runner. Previous task listener on port 57011 was stopped and absence checked.

## Actual CC task

- CLI: 2.1.299; model: `claude-sonnet-5-5`; effort: `low`.
- Host command returned a running process session; coordinator ran independent checks before collection. Exactly one explicit `status` query was made for acceptance, with no periodic polling.
- Three input records were deduplicated case-insensitively, preserving the first record, lowercasing and sorting emails. The two expected output records were checked locally.
- Session: `a1df64f7-411a-4cda-9c69-c2c7ecf4706a`. Process and runner exits were 0; no permission denials or malformed events occurred.
- Assigned session transcript recorded both `effort` and `perTurnEffort` as `low` on both assistant entries; model initialization and final model usage matched the selected model. The runner leaves `effective_effort` unknown until the coordinator checks this separate evidence.
- Raw stdout: 10207 bytes; compact status: 419 bytes. A private final-result canary remained in local logs/results and was absent from model-facing status. Full logs were never printed to the coordinator.
- Retained evidence: `/private/tmp/fox-cc-background-validation/` (`turn-1/`, inputs, prompt and `verification.json`).

## Limits

Local recording and state queries do not invoke CC or another model. Necessary orchestration queries, dispatch and final acceptance still consume normal model tokens. Same-session continuation was verified in prior CLI validation; it was not rerun because its implementation/configuration contract is unchanged. Routing selection policy is unchanged; no new blind model-routing/cooperation preview was run for this display removal. This small read-only run does not establish performance or cost savings on larger tasks.

## Pre-commit review

Independent reviewer found that a system permission-denied event could be lost when the final result's denial list was empty. The runner now preserves `permission_denial_seen` independently of that list count, and returns needs-attention/incomplete for either source. A regression test covers the exact event sequence. The successful live run above preceded this fix; its recorded event stream was replayed through the final runner with identical final result and no body leakage. No extra CC model call was required for this replay.

Final runner SHA-256: `fdea2763b29179c370a3eae8651cbda99bb313feb3cc11daa6643fffeac1ff90`. Replay assertions are in `/private/tmp/fox-cc-background-validation/review-verification.json`.

Independent reviewer rechecked the fix and found no remaining material issue; all 9 focused runner tests passed. The complete offline suite passed 68/68.
