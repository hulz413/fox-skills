# Codex and Claude Code compatibility validation

Validated on 2026-10-14. Policy artifact SHA-256:

- `SKILL.md`: `80d09749f281118fbc3388dfcb9c3c0b5ed391f7e4998c19ae0f53d658673bab`
- `references/model-routing.md`: `8483d900652d7d188cb84198ed5e7524956f21248cd507d3f73743241a1c360c`

## Scope and evidence

The change translates existing fresh-context and configuration rules to Codex and Claude Code interfaces. Selection tiers, effort criteria, pins, ownership, advisor isolation, independent review, fixed follow-up configuration and acceptance rules remain unchanged. Preview field names remain compatible with the existing checkers.

- Offline suite: 59 tests passed, including the existing local context-filter tests. No context-filter files were changed.
- Skill structure: `quick_validate.py` passed using isolated `uv` with PyYAML. System Python lacked PyYAML; default uv cache access was denied. A temporary cache resolved validation without changing shared configuration.
- Local reference links, anchors and `git diff --check`: passed.
- Fresh-context evaluator: gpt-6-luna / medium, supplied only policy and blind prompts; both structures passed on first attempt, zero repairs. Scenario tasks and selected fixture agents were not executed.
- Routing rules: 43/45 fixed expectations matched. Autonomous routing: 12/12 matched. Runtime legality: 53/53 selected configurations passed; four blocked cases had no selected configuration and their blocking reasons were reviewed.
- Cooperation: 20/20 expectations matched, including proportionate-work cases c15-c17 (3/3) and boundary cases c18-c20 (3/3). All six new-agent configurations passed runtime legality checks.
- Coordinator reviewed every routing and cooperation reason against its supplied task. Two effort calibration differences remain, recorded below; no further material contradictions were identified. Matching fixture fields alone was not treated as reason review.

## Retained routing differences

| Case | Supplied task | Fixed expectation | Evaluator choice and reason |
| --- | --- | --- | --- |
| case_016 | Cross-domain synthesis under material uncertainty; detailed causal reconciliation of conflicting technical and economic constraints, with a long chain of implications. | strong-fixture / high | strong-fixture / xhigh: "Materially uncertain cross-domain synthesis needs frontier capability; xhigh supports the long causal reconciliation across interacting constraints." |
| case_033 | Add one local field formatter with an established pattern, complete contract, file boundary and direct acceptance checks. | light-fixture / medium | light-fixture / low: "A local formatter follows a supplied pattern with complete boundaries and direct checks." |

Both choices are runtime-legal, but fail the fixed effort expectations. The first justification does not establish why checking beyond a normal deep pass is needed; the second relies on supplied patterns and boundaries without establishing that the remaining implementation judgment is brief. These are reported as preview calibration gaps. Neither expected answers nor existing selection rules were changed to make the sample pass. No before-change sample was taken, so this run does not establish whether these differences are a regression.

## Claude Code smoke check and limits

Installed CLI: Claude Code 2.1.299. A non-persistent `claude -p` invocation of `/fox-orchestrate` completed successfully with only Read enabled, hooks disabled for that invocation and no MCP servers. It loaded the current skill and model-routing reference and correctly explained:

- Advisor fresh context through an explicit non-fork subagent type, without passing Codex's `fork_turns` parameter.
- Codex fresh context through supported `fork_turns: "none"`.
- Reporting inherited or unknown effort without claiming an unsupported override succeeded.
- Blocking an unverifiable explicit effort pin.
- Resuming a suitable existing worker with retained context and unchanged configuration.

This is actual Claude Code loading and interpretation evidence, not live Claude Code subagent dispatch, model/effort application, resume or peer-messaging verification. No scenario task was executed in that CLI session. The Codex evaluator used an actual fresh-context subagent with requested gpt-6-luna / medium; the runtime returned no differing effective settings. Neither preview establishes task quality, latency or cost savings.

The final resume-row clarification (choose a resumable type; Explore and Plan may be one-shot) was reviewed against the [official Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents). It changes no fixture selection or cooperation rule; unaffected preview evidence was reused.
