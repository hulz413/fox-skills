# Orchestrate validation

## Choose the checks

Run the offline suite after every skill edit, from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/fox-orchestrate/tests -p 'test_*.py' -v
```

For model-routing changes, run one fresh-context routing and cooperation preview. For cooperation-only changes, run a fresh cooperation preview and reuse unaffected routing results when available; identify any result not rerun. Documentation-only rearrangements need link and content review, not another behavioral run. Repeat checks only for changed requirements, failures or unresolved verification gaps.

Use [live-cooperation.md](live-cooperation.md) when changes to handoffs or coordination warrant actual execution evidence. These optional isolated scenarios are separate from previews and are not required on every skill invocation. [validation-history.md](validation-history.md) preserves earlier fixture revisions; it is not the current procedure.

For Claude Code CLI backend changes, use the [CLI dispatch procedure](../references/claude-code-cli.md) with an isolated small task. Check the actual result, observed model and effort, same-session continuation, and failure diagnostics separately from blind previews. Do not silently broaden permissions when persistence or required tools are denied. See [CLI validation evidence](claude-code-cli-validation.md) for the recorded run and its limits.

For background execution, `test_cc_progress.py` checks compact status isolation, literal handoff, evidence preservation, on-demand queries without re-invoking CC, failures and cancellation. Verify a real isolated CC task separately; see [background validation](cc-background-validation.md). The [App progress validation](cc-app-progress-validation.md) and [Terminal validation](cc-progress-validation.md) are historical evidence for removed display implementations; neither describes the current runner.

The [batch fan-out live validation](batch-fan-out-validation.md) records the 2026-10-15 two-task, three-invocation CC smoke test, with a [sanitized receipt](batch-fan-out-live-evidence.json). Its coverage and unverified items are specific to that run; it does not establish general scheduling, isolation or performance guarantees.

The [failure classification validation](failure-classification-validation.md) separates offline classification/acceptance checks, one induced live CLI turn-limit failure and retained-record compatibility checks. It lists unverified failure paths; documentation added no worker calls.

The [task summary validation](task-summary-validation.md) separates 84 offline tests from local summary replay of three retained real CLI records. It records task/artifact selection, token accounting, compatibility and unverified items; no new worker calls were made.

The [acceptance publication validation](acceptance-publication-validation.md) records 90 offline tests, controlled concurrent readers/publishers, duplicate CLI writes, injected-failure cleanup and isolated publication replay. Its limits distinguish atomic visibility from crash durability; no worker calls were added.

## Generate blind previews

```sh
python3 skills/fox-orchestrate/tests/routing_eval.py
python3 skills/fox-orchestrate/tests/cooperation_eval.py
```

These commands emit prompts, not model calls. Give the relevant generated prompt(s), current SKILL.md and references/model-routing.md to one fresh evaluator. Keep routing_cases.json, cooperation_cases.json, expected answers and checker sources hidden. A cooperation-only prompt includes its own routing output contract.

Prohibit delegation, App forks, execution of scenario tasks, and tools other than reading the supplied policy/prompts, writing predictions, and running the structure-only gates below. Request JSON decisions using the embedded contracts; save routing and cooperation answers separately. Reasons belong in their own field, never in fork_turns. Use one evaluator for the suite, not one agent per case.

## Validate, then score

The evaluator runs the applicable structure-only gate before returning:

```sh
python3 skills/fox-orchestrate/tests/routing_eval.py --validate-output /path/to/routing.json
python3 skills/fox-orchestrate/tests/cooperation_eval.py --validate-output /path/to/cooperation.json
```

These modes do not load expected answers. Cooperation validation also enforces route presence: new-agent actions require a route object; local and existing-agent actions require null. An extra configuration report on a follow-up is a contract error, not a new dispatch. A format-only repair may remove that extra report while preserving the selected action, but must not invent a missing routing decision. Preserve the first response if invalid; allow one format-only repair using diagnostics, without changing decisions. If still invalid, report failure instead of retrying indefinitely. Disclose first-pass failures and repair counts even if the final structure passes.

After structure passes, the coordinator scores the saved answers:

```sh
python3 skills/fox-orchestrate/tests/routing_eval.py /path/to/routing.json
python3 skills/fox-orchestrate/tests/cooperation_eval.py /path/to/cooperation.json
```

Inspect reasons as well as fields. Record pass/fail/not reviewed for each case. Contradictory reasons fail behavioral acceptance; unreviewed reasons do not establish a pass. Do not use keyword matching or another evaluator to rubber-stamp scores. Expectations are fixed before evaluation; do not relax them to make predictions pass.

Review capability and effort separately, then their combined suitability. Check task-specific reasons for higher effort, evidence versus unvalidated expected gains, explicit pins, unavailable/inherited controls, latest compatible family versions, and fixed configuration for an existing assignment. For cooperation, check resource ownership, coordinator decisions, fresh advisor evidence, independent repair/recheck, preservation of counterevidence, useful agent reuse, and stopping after sufficient acceptance evidence. Apply the action meanings in the generated prompt rather than guessing from labels.

## Report evidence and limits

Report offline checker results, final structure validity, first-pass format failures, routing rules, autonomous routing, cooperation, and per-case reason review separately. Keep proportionate-work (case_c15–case_c17) and boundary (case_c18–case_c20) results distinct from the other cooperation cases. Do not publish a combined routing accuracy. Invalid structure or case coverage leaves routing scores unscored. If fresh evaluation is unavailable, say behavioral validation was not run.

Unit tests validate the checkers. Fresh-context previews test decisions against fixed routing/cooperation hypotheses; synthetic runtime IDs are fixtures, not a production model catalog. Neither proves effective dispatch settings, actual task quality, repeatability, latency or cost savings. Comparisons of configurations require the same representative inputs and acceptance criteria plus measured results. Live-scenario evidence must be reported separately from preview results.

Discovery cases `case_062`–`case_067` cover catalog-only candidates, catalog/tool effort conflicts, effective configured-file fallback, unknown provider identity, unconfirmed string-parameter models, and invalidated capability snapshots. Review their evidence explanations as well as selected routes. These previews do not establish a live `model/list` connection, effective-profile resolution or an exact match to a running App menu; report those separately if exercised.

check_dispatch.py and test_dispatch.py retain an older actual-trace checker for compatibility; its unit tests are offline. Do not dispatch selected models or execute sample tasks as part of the preview suite. Remove temporary prompts and predictions after inspection, preserving failure evidence when useful. Historical reports remain historical and must not be silently rescored against revised contracts.


## Runtime legality versus selection calibration

Scoring also returns `runtime_validity`, shared by routing and new-agent cooperation routes. It applies the public runtime plus each case's runtime patch and checks model membership, availability, compatibility, supported effort, and unavailable/inherited effort controls. It never chooses a replacement or rewrites predictions. Blocked or unspecified inherited configurations are reported as not checked when there is no selected configuration to validate. Pins, full-history permissions, policy restrictions such as explicit-only ultra, and the truth of blocking/inheritance explanations still require reason review when available only in task prose; this checker does not infer them from language.

To check routing predictions without hidden expected answers, save the emitted routing prompt and run:

```sh
python3 skills/fox-orchestrate/tests/routing_eval.py /path/to/predictions.json --validate-runtime /path/to/routing-prompt.json
```

This command returns nonzero for violations, invalid structure, or incomplete runtime verification. It is not an automatic repair gate: changing model/effort is a decision change, not a format-only repair. Keep the original prediction and record any later decision separately. This offline checker is not a hook into the host's live dispatch API.

The existing `groups.rules` and `groups.autonomous` scores remain exact expectation matches, not task-success or quality scores. `expectation_differences_without_runtime_violation` lists remaining mismatches separately; absence of a detected runtime violation does not prove a choice obeys every instruction or is optimal. Runtime-invalid choices must not be reported as merely calibration differences. Do not merge these categories into one accuracy number.

For checker/report-only changes that leave prompts, selection policy and fixtures unchanged, replay retained predictions and test the checker; a fresh model sample is unnecessary. Label replays with the new checker revision and retain original reports. See [selection-calibration.md](selection-calibration.md) for the reviewed ambiguous cases and evidence needed before changing expectations.

Discovery cases `case_068`–`case_069` cover full-catalog exact-ID acceptance beyond an abbreviated five-model description, pagination, and unknown upstream identity behind a known connection provider. Review complete-inventory behavior separately using a multi-page source and a configured-file snapshot; routing previews alone do not prove that every inventory entry was retained. Preserve hidden entries as inventory without silently selecting them.

See [full-inventory follow-up evidence](runtime-discovery-validation.md#full-inventory-follow-up) for the fresh previews, two-page inventory scenario and actual configured-file discovery, including provider and live-runtime evidence gaps.
