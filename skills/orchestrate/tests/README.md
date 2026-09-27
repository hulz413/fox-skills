# Routing-only regression

After every edit to the skill, from the repository root run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/orchestrate/tests -p 'test_*.py' -v
python3 skills/orchestrate/tests/routing_eval.py
```

The second command emits a blind evaluation prompt; it does not call a model. Give that prompt plus the current `references/model-routing.md` to a fresh evaluation context. Prohibit delegation, execution of sample tasks, and tools other than reading the policy/prompt, writing predictions, and the structure-only validation command below. Request JSON decisions only, using the generated output template and field contract. The reason must be a separate field; fork_turns accepts only a context mode. Structural errors fail validation and must not be silently repaired or counted as successful routes. Do not supply `routing_cases.json`, expected answers, or this checker source to that context. A single evaluation can handle the whole suite; do not launch one agent per case. The evaluator must save its JSON answer to a temporary file and run the structure-only gate before returning:

```sh
python3 skills/orchestrate/tests/routing_eval.py --validate-output /path/to/predictions.json
```

This mode never loads cases or expected answers. If it fails, preserve the first response, allow one format-only repair using the diagnostics, and validate again. Do not change model/effort choices during format repair. If still invalid, report a failed evaluation rather than retrying indefinitely. Report first-pass structure failures separately even if repaired. After the gate passes, the coordinator scores the decisions:

```sh
python3 skills/orchestrate/tests/routing_eval.py /path/to/predictions.json
```

Inspect reasons as well as the score: high effort and frontier routes need task-specific evidence. Do not adjust expectations merely to make a run pass. Fixtures cover bounded, routine, complex and frontier work, non-code work, misleading size/risk/role cues, explicit pins, unavailable settings, effort fallback, inheritance and evidence-based escalation. They also check medium defaults for all three model tiers, upward and downward adjustments on each tier, direct high selection before any execution, and environment failures that must not trigger escalation. Fixed synthetic runtime IDs are fixtures, not a production model catalog.

Unit tests validate the checker. The separately scored fresh-context answers test routing behavior. Neither dispatches the selected models nor proves effective runtime settings, task quality, repeatability across runs, or token savings. If a fresh evaluation is unavailable, report behavioral validation as not run; checker success alone is insufficient. Remove temporary prompts and predictions after inspection, retaining failure evidence only when needed.

`check_dispatch.py` and `test_dispatch.py` retain the older actual-trace checker for compatibility. Its unit tests are offline. Do not perform actual dispatches or execute scenario tasks as part of this routing-only suite.

## Separate scores

The 24 original, deliberately cued scenarios are rule checks (`rules`), not evidence of autonomous model selection. Four natural requests (`autonomous`) omit model/effort instructions and difficulty labels. They cover list processing, a UI feature, a payment-notification investigation and venue comparison; none is a GEO scenario. Groups and expected answers stay hidden from the evaluator. Report the two scores separately and inspect reasons; do not publish a combined routing accuracy. Expectations are fixed before evaluation and must not be relaxed after seeing answers.

The scorer reports final structure validity separately. If structure or case coverage is invalid, both routing scores are unscored (`null`). Also disclose first-pass format failures and repair count from the evaluation trace; a final structural pass does not mean first-pass success. Run this small suite once per relevant change; no extra agents or repeated runs are required without a failure or changed requirement. These four examples are a limited sample, not proof of general real-world routing reliability.

## Cooperation previews

Also run `python3 skills/orchestrate/tests/cooperation_eval.py` to emit the cooperation prompt. Give both generated prompts, SKILL.md and model-routing.md to the same fresh evaluator; keep both fixture files and checker sources hidden. Save routing and cooperation predictions separately. Use `cooperation_eval.py --validate-output /path/to/cooperation.json` for the cooperation structure gate, following the same first-response preservation and one format-only repair procedure above. Score it with `cooperation_eval.py /path/to/cooperation.json`. This structure-only mode does not load fixture expectations.

Report cooperation separately from autonomous routing and rule compliance. Cases cover local small and tightly coupled work, explicit independent delegation, direction advice, repair and independent recheck, missing advisor evidence, and fresh advisor context for a history-dependent question. Inspect reasons to confirm raw evidence is supplied, missing evidence causes no escalation, and repair is followed by independent recheck; exact field scores alone do not prove these explanations. These are previews, not actual advisor, worker, App fork, or scenario executions.

Communication previews also cover reviewer-to-worker evidence questions, advisor-to-explorer evidence requests, and coordinator ownership of scope/approach/resource changes. Inspect that recommendations return to the coordinator and peer explanations do not substitute for independent review. Direct communication requires supported, authorized messaging and does not create a mandatory pipeline.
