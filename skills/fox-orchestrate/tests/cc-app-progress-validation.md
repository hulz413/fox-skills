# CC progress inside Codex App

Historical record: this display implementation has been removed. Use [background validation](cc-background-validation.md) for the current behavior. Server/terminal lifecycle descriptions below apply only to the earlier validation.

Validated on 2026-10-14, macOS, Claude Code 2.1.299, coordinator in Codex App.

## Confirmed display path

Codex's available `open_in_codex` tool accepts browser targets. In this session it returned `queued`, which did not establish a visible panel. The supported `cua.createBrowserTab("iab", url, {visible: true})` path successfully opened the local page in the **Codex In-app Browser**. A disposable capability probe changed its visible counter from 1 to 16 between two observations, establishing autonomous page updates without model polling as the refresh mechanism. The probe listener was stopped after verification.

The actual progress panel was then opened before CC started. Its observed state changed from “等待启动” / “等待执行事件…” to “执行完成，待验收”, displaying six filtered event lines, including Read start/completion and process completion. The same tab was marked as a deliverable. The actual screenshot is `/private/tmp/fox-cc-app-live/app-progress.png`; the tab is inside Codex App, not system Terminal or an external browser.

## Actual worker and isolation checks

The runner launched one read-only CC assignment with explicit `claude-sonnet-5-5` / `low`, Read-only tools, `dontAsk`, invocation-only hooks disabled and MCP excluded. CC read three records and correctly produced two deduplicated, normalized/sorted name/email records. The coordinator checked the exact records locally. No progress-report prompts were sent to CC.

- CC and runner exit codes: both 0.
- Observed model in initialization/final usage: `claude-sonnet-5-5`.
- Both assistant entries in the assigned persisted transcript record `effort: low` and `perTurnEffort: low`.
- Raw stdout: **9,958 bytes**, retained only in the local run directory.
- Model-facing caller output: **427 bytes** of compact status, without raw CC output.
- HTTP response contains six filtered progress lines and a small state projection. It excludes raw result text, prompt, arguments, stderr, session transcript and the private canary present in CC's actual final answer.
- The runner still reports effective effort as unknown until the coordinator independently checks appropriate metadata; the App labels low as the requested effort rather than claiming server-side proof.

Local raw/result/status/progress artifacts and sanitized assertions remain under `/private/tmp/fox-cc-app-live/`. The panel server is tracked as its own command session and intentionally remains available for the user, with a 30-minute idle shutdown. Closing the panel does not control the worker. The screenshot and local assertions are verification artifacts, not runtime dependencies.

## Final artifact checks

SHA-256:

- `scripts/cc_progress.py`: `ecee78d4453f974692180f074dffc26a9322fe7d728c9ef0dfa1a37b6fc45f01`
- `scripts/cc_progress_panel.py`: `8ec35a855fd3d4600f994b1d6dfc0c0b96b7afb305658d87bf2ffadec34ef687`
- `tests/test_cc_progress.py`: `bfefa395b40b942b9a537189003243f2473d48994258e145ae93a07e461e32fb`
- `tests/test_cc_progress_panel.py`: `273a1cf2c1d7d93b627720dec3c6dda8ceee644b18898b09d9c535bcb1a3d0ee`
- `references/claude-code-cli.md`: `8eb8b42bf1f7ee83d6e383152c3c714652344f0fbdf267e82a937a4120e8fc73`

All **72 offline tests passed**, including 13 runner/panel tests. Panel tests cover incremental delivery, bounded backlog, filtering of malformed/control/private content, forbidden raw/result paths, token path, Host and Origin validation. Existing process failure, permission-denial, literal prompt, evidence preservation and cancellation tests remain passing. Skill structure validation, local links/anchors, Python syntax and focused diff whitespace checks passed.

Independent reviewer gpt-6-luna / medium identified the obsolete terminal `view` route during review. The function, CLI registration and dispatch branch were removed; automatic Terminal-opening code and its flag were also removed. The same reviewer rechecked the affected paths and 13 focused tests and found no remaining material issue. The final cleanup removed only unused terminal display code/test usage; the live App server/rendering/worker paths were unchanged, so their actual execution evidence was reused.

Model selection, roles, permissions, ownership, advisor context, fixed follow-up configuration, acceptance and existing fixture expectations were not changed. Routing/cooperation previews were not rerun or silently rescored; earlier calibration gaps remain disclosed in `claude-code-cli-validation.md`. Older `cc-progress-validation.md` describes the historical Terminal implementation, not the current display procedure.

## Token and verification boundary

The page performs local HTTP fetches every 250 ms, renders with `textContent`, bounds displayed history to 300 lines and stops fetching after completion/backlog delivery. The local server/filter/browser code makes **no model or provider API call**, and no progress data is injected into Codex turns. Thus ongoing progress display adds zero model inference/token usage; it does not ask CC to produce extra narration.

This is a causal implementation check, not an A/B billing benchmark. Initial dispatch/open-panel tool calls, task execution, necessary verification and final acceptance still incur their normal model usage. DOM observations and a screenshot were taken for this validation only; the shipped refresh mechanism does not use model-facing browser reads or screenshots. No claim of zero total orchestration tokens, reduced task tokens, or provider-side billing equivalence is made.

The supported result is an App **browser panel**, not chat-by-chat progress messages or a native embedded terminal session. If this App surface is unavailable, the skill reports the display gap and does not fall back to system Terminal or model-mediated updates under a zero-extra-inference requirement. The server binds only loopback, uses a capability URL, serves no directory/raw files, and expires when idle; no tunnel, remote upload, shared configuration change or permission bypass was introduced.
