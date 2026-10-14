# Claude Code CLI backend validation

Date: 2026-10-14. CLI: Claude Code 2.1.299. Coordinator: Codex App.

## Artifact and scope

Policy SHA-256:

- `SKILL.md`: `cce66475c8fe337a14b71479313f659e785f94d8ed54cb7d6c3743ee1b32dd64`
- `references/model-routing.md`: `46c3c8f1a827d977799b27887dbbcd424b351aec548709062a4f3818b2e5884b`
- `references/claude-code-cli.md`: `c05f489e4e6b293f6f5ad88d436d08834daf6b15c3c951820517e3c7bab65bbf`

Native dispatch remains the default. The added adapter covers explicitly requested or already-authorized CC CLI dispatch, CC-specific selection, stdin/argv handoff, scoped permissions, structured result inspection, effective-setting evidence and exact-session continuation. Existing tiers, effort criteria, pins, resource ownership, fresh advisor context, independent review, fixed assignment configuration and acceptance rules were retained. Test fixtures and expected answers were not changed.

## Actual CLI execution

The coordinator used its command tool to launch CC in an isolated temporary directory. The assignment was a read-only worker task: read three name/email records, deduplicate email case-insensitively while retaining the first name, lowercase and sort emails, and report input/output counts. Only `Read` was exposed and allowed, with `dontAsk`; hooks were disabled for that invocation and MCP servers excluded. No permission-bypass flags or shared configuration edits were used.

| Check | Result |
| --- | --- |
| Initial CC launch with `--model sonnet --effort low` | Exit 0; successful result; alias resolved to `claude-sonnet-5-5`; records and 3-to-2 count correct. |
| Initial resume under the sandbox | Exit 1; `No conversation found with session ID`. A returned session ID had not established persistence. |
| Launch after approved execution allowing CC session persistence | Exit 0; explicit `--model claude-sonnet-5-5 --effort low`; same correct records. |
| Observable configuration in the assigned persisted transcript | Every assistant entry records `effort: low` and `perTurnEffort: low`; initialization and final model usage identify `claude-sonnet-5-5`. |
| Exact-ID resume with the same model, effort, cwd and tool restrictions | Exit 0; same session ID; returned the initial task marker `fox-cc-retained-7c19` and count 2 without any new tool call or file read. |
| Failure collection | Missing-session error retained; the coordinator treated it as a failure and resolved persistence conditions before another attempt. |

The initial sandboxed run did not persist a transcript; the approved run did. This establishes the observed permission-boundary behavior, without claiming a more specific internal storage root cause. The assigned transcript is under CC's normal user session directory. Only configuration fields from that session were extracted; other conversations, credentials and account details are not included in the evidence.

[Sanitized live evidence](claude-code-cli-live-evidence.json) records observed models, transcript effort fields, results, session IDs, exit codes, failure diagnostics and the CLI-reported costs. Assertions independently checked exact output records, all task model-usage keys, same-session identity, retained marker, absence of follow-up tool calls, effort metadata and the missing-session failure. The measured total across the three successful invocations was USD 0.0356058 as reported by CC; this is not a subscription billing estimate or a Codex cost comparison.

## Offline and behavioral checks

- Offline suite: 59 tests passed.
- Skill structure: `quick_validate.py` passed with isolated PyYAML/uv cache; no shared dependency changes.
- Local links/anchors, Python launch-example syntax and focused `git diff --check`: passed.
- Fresh native evaluator: gpt-6-luna / medium. Both prediction structures passed on the first attempt, zero format repairs. It read policy and blind prompts only, without expected answers, fixture sources or checker implementation. No fixture task was executed.
- Routing rule expectations: 43/45 matched. Autonomous routing expectations: 9/12 matched. Runtime legality: 53/53 selected configurations passed; four blocked cases had no selected configuration and their reasons were reviewed.
- Cooperation first sample: 18/20 matched; 5/5 selected configurations were runtime-legal. Proportionate-work c15-c17 and boundary c18-c20 each matched 3/3.
- A final clarification distinguished fresh subagents/authorized CLI processes from creating an additional App chat, preserving separate restrictions on each. The same independent reviewer rechecked only affected c07/c11 against the clarification, retaining the first answers. The combined retained-plus-rechecked sample matches 19/20, with 6/6 selected configurations runtime-legal. This is an affected-scope recheck, not a second fresh full-suite sample.
- The coordinator reviewed every supplied task and prediction reason. The reviewer independently found no material introduced policy defect. Additional backend cases correctly blocked unverifiable pins/model mismatch, rejected missing required output despite a nominal success result, handled lost sessions, used stdin for shell-sensitive task text, blocked missing auth/CLI and selected from CC rather than Codex model information.

## Retained preview differences

| Case | Expected effort | First prediction | Review |
| --- | --- | --- | --- |
| case_016 | high | xhigh | Long cross-domain causal reasoning was treated as beyond a normal deep pass without enough task-specific justification. |
| case_025 | low | medium | Deterministic deduplication/sort with complete rules was treated as ordinary planning. |
| case_029 | medium | low | A new import entrypoint was treated as a routine reuse, without establishing that remaining implementation judgment was brief. |
| case_031 | xhigh | high | The sample did not fully account for the coupled backfill/cutover/rollback consistency requirement. |
| case_033 | medium | low | Supplied formatter patterns and boundaries alone did not establish brief remaining implementation judgment. |
| case_c03 | medium | low | The same underestimation affected a new export feature. This remains the one cooperation mismatch after the affected-scope recheck. |

First-sample c07 incorrectly treated a prohibition on additional App chats as preventing fresh native consultation. The clarification and affected recheck resolved that interpretation. First-sample c11 chose the expected evidence-exchange action but omitted the recommendation's recipient in its reason; the affected recheck explicitly returned recommendations to the coordinator. Other unaffected reason reviews found no material contradictions. [Preview evidence](claude-code-cli-preview-evidence.json) retains the original scores, mismatching answers and separate recheck answers; no fixed expectations were relaxed.

The remaining effort differences are calibration gaps in this sample, not runtime-invalid dispatches. No same-input before-change comparison was run, so this evidence does not establish whether sample differences were caused by the adapter change.

## Limits

The live task verifies actual CLI invocation, a completed read-only assignment, observed model/effort configuration, persistence failure and recovery, and retained-context continuation. It does not establish mutating-task permissions, every Claude model/effort combination, parallel writers, nested CC delegation, remote providers, provider-side effort guarantees, or hard budget enforcement. Other combinations still require current runtime support and observable configuration evidence. Preview compliance does not establish task quality, repeatability, latency or cost savings.

The live task and actual configuration/resume evidence were unaffected by the final App-chat clarification. Unaffected checks were reused; the final policy artifact was checked through offline validation and the targeted independent recheck.
