# Validation revision history

Historical notes preserved from the former test README. These record fixture revisions and earlier validation boundaries, not current execution instructions or proof of current test results. Follow [README.md](README.md) for the maintained procedure.

### Adjacent-effort coverage

All routing case IDs are neutral numeric labels in both fixtures and emitted prompts. Existing rule cases were renamed without changing their expected decisions; historical reports retain their original IDs and results. Rule task wording remains deliberately cued and is scored separately from natural requests.

The workhorse fixture now supports `xhigh` and `max` as well as lower efforts, so these efforts no longer force the frontier model by availability. Per-case fallback patches remain unchanged. This is test runtime metadata, not a claim about production models.

Current expectations are fixed before fresh-context evaluation; the assignment-based revision below changes the first route in the cancellation pair:

| Cases | Expected route | Evidence to inspect in the evaluator's reason |
| --- | --- | --- |
| `case_029` / `case_030` | efficient medium / workhorse high | The first follows a settled cancellation contract; the second must reconstruct cancellation/payment interleavings that individual tests miss. The shared domain must not determine effort. |
| `case_031` | workhorse xhigh | Backfill, read switching, retention and rollback invalidate each other's assumptions; the choice should depend on those feedbacks, not merely on migration terminology. |
| `case_032` | frontier max | Frontier reflects the need to establish a new proof where existing arguments do not apply, despite a single technical domain. Max reflects the unbounded derivation and counterexample search beyond finite checks. |

Review corrected the initial `case_032` expectation from workhorse to frontier before any behavioral evaluation: a specified technical model does not make a new unbounded proof routine. Its task and max effort remain unchanged.

These are routing hypotheses, not measured optimal settings. Do not relax them after seeing answers to obtain a pass. The new unit checks validate neutral IDs and supported fixture settings only; adding cases and passing checker tests does not establish behavioral success. Fresh-context behavioral evaluation of this revision has not yet been run.

## Cooperation previews

Use the maintained [preview generation](README.md#generate-blind-previews), [validation/scoring](README.md#validate-then-score) and [reporting procedure](README.md#report-evidence-and-limits).

Cases cover local small and tightly coupled work, explicit independent delegation, direction advice, repair and independent recheck, missing advisor evidence, and fresh advisor context for a history-dependent question. Inspect reasons to confirm raw evidence is supplied, missing evidence causes no escalation, and repair is followed by independent recheck; exact field scores alone do not prove these explanations. These are previews, not actual advisor, worker, App fork, or scenario executions.

Communication previews also cover reviewer-to-worker evidence questions, advisor-to-explorer evidence requests, and coordinator ownership of scope/approach/resource changes. Inspect that recommendations return to the coordinator and peer explanations do not substitute for independent review. Direct communication requires supported, authorized messaging and does not create a mandatory pipeline.

Fixed-configuration previews cover continuing an existing worker after a reasoning omission and retaining its original effort for a simple remainder. Inspect reasons for evidence/method corrections without automatic model or effort changes. The former escalation/de-escalation and replacement fixtures were retired because the user changed the requirement to initial selection only; historical evaluation reports remain unchanged. Contract revision 2 clarifies action meanings in the generated prompt before evaluation: local includes main-session continuation and delivery; continue means retained-agent work; repair_recheck names the repair owner as role, with independent recheck described in reason. case_c05 now explicitly assigns repairs to the original Worker, so its expected role changes from reviewer to worker. Other pre-existing expected answers are unchanged. Historical reports, including c05/c15/c16 label failures, remain unchanged and must not be rescored as if they used this contract.

Proportionate-work previews (case_c15–case_c17) cover finishing after acceptance, reusing sufficient unchanged validation evidence, and supplying raw counterevidence omitted from an advisor summary. Report this group separately from pre-existing cooperation cases. In addition to field scores, inspect reasons: the first two should avoid unnecessary investigation/retesting; the third must preserve the material counterevidence rather than trusting the summary to save context.

Boundary previews (case_c18–case_c20) cover coordinator control of further delegation and existing-agent reuse with compatible versus incompatible configurations for genuinely separate assignments. Report these separately; neither a new task nor a free slot automatically requires dispatch.

case_c14 explicitly states that the Worker has already received the counterexample and has the required evidence. This distinguishes continuation from supplying missing context without changing its expected answer. The earlier ambiguous wording and first-run label failure remain in the validation report. repair_recheck denotes an independent-review loop; an agent correcting its own reasoning is not automatically that loop.

Both generated prompts embed the same routing output contract from routing_eval.py; a cooperation-only evaluation must not rely on a separately supplied routing prompt for field names or status values.

Automatic-effort policy update: xhigh and max may now be selected from task evidence before first dispatch; ultra remains explicit-request only. Added rule cases cover direct xhigh, direct max and a supported recommended-max fallback. The reserved-effort fixture now uses ultra to preserve its original policy-limit check. Other expected routes and historical reports remain unchanged; these fixtures do not establish behavioral success until evaluated in a fresh context.


## Assignment-based routing revision

Expected decisions for this revision are fixed before fresh-context evaluation. Update existing local-pattern/direct-acceptance implementation and supplied bounded-comparison cases (`case_003`, `case_004`, `case_026`, `case_028`, `case_029`) to efficient/medium. The analogous new-agent cooperation cases (`case_c03`, `case_c08`) also use efficient/medium. Keep `case_c19` on its existing workhorse agent: its configuration is sufficient and retained context helps, so a cheaper hypothetical new route does not require replacement. Other existing expectations and historical reports remain unchanged.

New rules (`case_033`–`case_048`) cover different assignments under the same role, the most capable available suitable Advisor, ordinary consultation, demanding synthesis with established methods, draft versus connected polished delivery, deep debugging without event ordering, low-effort planning/tool use, model-specific guidance, unavailable or inherited effort controls, and explicit pins. New natural requests (`case_049`–`case_052`) cover a local edit, an internal technical draft, conflicting-log debugging and architecture advice. Cooperation `case_c21` covers fresh frontier consultation during implementation. All runtime models and control metadata remain synthetic fixtures; production routing names no vendor or model.

Runtime patches with `effort_control: unavailable` have no configurable effort; an explicitly selected model uses `requested` with null effort and an explanation. With `effort_control: inherited`, report the known `inherited_effort` and disclose inheritance without claiming it was overridden. A conflicting or unverifiable explicit effort pin blocks. Null never asserts that reasoning is disabled. Output fields are unchanged.

Review reasons for capability/effort separation, combined acceptance, task-specific additional reasoning benefits, and disclosed unavailable/inherited controls. For xhigh/max, reasons must distinguish comparable-task evidence from unvalidated expected gains; do not require an extra evaluation per dispatch. Medium is a decision baseline, not a mandatory trial or execution value. The Ultra boundary is a runtime execution-mode restriction, not a universal next effort level.

For checks and reporting, use the [current validation procedure](README.md#choose-the-checks). Fixed answers test compliance with these routing hypotheses, not optimal configurations, effective dispatch settings, actual task quality or cost savings. Actual configuration comparisons would need the same representative inputs and acceptance criteria and are outside this routing-only suite.


### Latest version within a family

User-requested follow-up: normally filter superseded versions out within each runtime-identified family before applying runtime recommendations. `case_053` prefers a newer available compatible version despite a stale recommendation. `case_054` honors an explicit older-version pin. `case_055` and `case_056` use an older version only because the newer one is unavailable or incompatible; reasons must disclose the exception. Family and version-order metadata are synthetic test inputs, not a production model catalog or model-name parser. Expectations are fixed before evaluation of these added cases; unaffected predictions can be reused.

## Effort guidance calibration

Expectations are fixed before fresh-context evaluation. Keep every pre-existing task and expectation unchanged. New rule cases cover applicable official xhigh guidance for an efficient model without repeated cycles (`case_057`), exacting delivery benefiting from extended checks without those cycles (`case_058`), reliable comparable-task evaluations taking precedence over official starting guidance (`case_059`), and applicable low guidance for a small new implementation (`case_060`). Existing `case_040` and natural `case_051` retain high for ordinary deep conflicting-log investigation; broadening xhigh does not automatically raise them.

Inspect reasons separately: capability and effort must remain distinct; guidance must apply to the chosen model and task; evaluation evidence must be reliable and comparable; explain conflicts and extra-effort benefits. Generic defaults are not model-specific official recommendations. Retain explicit pins, unsupported/inherited controls, latest-family versions and fixed-assignment cooperation regressions. No output field or checker interface changes are required.

## Execution and recording evidence

Historical reports retain their original test counts, artifact hashes and coverage limits; they do not establish validation of the current revision.

- [Batch fan-out](batch-fan-out-validation.md) and [sanitized receipt](batch-fan-out-live-evidence.json): two tasks, three CC invocations.
- [Failure classification](failure-classification-validation.md): offline checks, one induced live turn-limit failure and retained-record compatibility.
- [Task summaries](task-summary-validation.md): local replay of retained CLI records; no new worker calls.
- [Acceptance publication](acceptance-publication-validation.md): concurrent publishers/readers and injected failures; visibility is distinct from crash durability.
- [Evidence binding](evidence-binding-validation.md): legacy records, integrity states and isolated local replay; no new worker calls.
