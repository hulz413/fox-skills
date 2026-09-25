# Orchestration regression

Run the checker tests without model calls:

```sh
python3 -m unittest discover -s skills/orchestrate/tests -p 'test_*.py' -v
```

Select behavioral scenarios relevant to the changed rules; do not run the whole suite for every wording edit. Use a fresh orchestrator context for each scenario, retaining that context across its follow-up turns. Substitute the current skill path and give only the quoted requests, without the acceptance criteria. Record which scenarios ran and any verification gaps.

## Explicit delegation and routing

Use this scenario when changing dispatch or model-selection behavior:

> Use $orchestrate at <absolute skill path>. Delegate two independent worker tasks: (A) count `pear, apple, pear, plum, apple, pear`; (B) sum `12, 7, 19, 4, 8`. Keep cost and context small. While workers run, independently determine the number of distinct fruit names. Integrate the results and verify consistency. Use only these inputs; do not modify project files. Workers should execute directly.

Use a capable coordinator and record its actual `spawn_agent` calls from its own rollout (exclude ancestor history). Run:

```sh
python3 skills/orchestrate/tests/check_dispatch.py /path/to/orchestrator-rollout.jsonl --efficient-model MODEL_FROM_CURRENT_RUNTIME
```

Repeat the option for multiple acceptable efficient models. Select these from current runtime capability descriptions before evaluating results, not from the model IDs the run happened to choose. Also inspect that the coordinator briefly identifies the assignments, requested models and efforts, and selection reasons. A sentence is sufficient for one agent; a table is useful when comparing multiple assignments. Do not reject an otherwise complete explanation merely for its format. Check that each effort is supported for its model and that no dispatch was rejected. The automatic checker targets this self-contained scenario only: production tasks may legitimately require inherited context or a stronger model.

Acceptance: two real worker dispatches pass the checker; workers actually finish; combined results are pear=3, apple=2, plum=1, distinct=3, sum=50. Check runtime-confirmed settings when exposed; requested parameters alone do not prove the effective model. Report unavailable delegation as blocked, not passed.

Unit tests validate the checker, not the Skill's behavior. A behavioral pass is one observation, not a compliance guarantee or a token/cost benchmark. Test files are maintenance-only and need not enter normal skill context.

## Small task without requested delegation

> Use $orchestrate at <absolute skill path>. Correct the spelling in this sentence and return it: "The monitroing task has started." Do not modify files.

Acceptance: the corrected sentence is "The monitoring task has started." No subagent is created merely because the skill was invoked. This narrow fixture does not imply that every editing task must stay local. Repeat through the installed default prompt when validating interface metadata.

## Incremental follow-up

First request:

> Use $orchestrate at <absolute skill path>. Delegate one worker to count `pear, apple, pear, plum, apple, pear`. Use only these inputs, do not modify files, and return the counts.

After completion, in the same context:

> Have the same worker update the counts with two more apples and one plum. Return the updated counts.

Acceptance: reuse the worker when it is still available with retained context. The follow-up supplies the additional fruit and desired result without resending the entire original assignment or conversation. Final counts are pear=3, apple=4, plum=2. If reuse is unavailable, report that limitation and provide sufficient context to a replacement; do not claim the reuse path passed.

## Review scope and closure

Create a disposable directory containing `normalize.py` with this deliberately incorrect function:

```python
def normalize_tags(tags):
    return sorted({tag.strip().lower() for tag in tags if tag})
```

Give the agent:

> Use $orchestrate at <absolute skill path>. In <disposable directory>, fix normalize_tags so it strips whitespace, lowercases, deduplicates, sorts, and excludes empty results. Add focused checks and review the result. Modify only this fixture.

Acceptance: whitespace-only tags are excluded; normalization, deduplication, and sorting still work. Checks actually run. Review covers the stated behavior and meaningful failure paths, and corrections receive targeted verification. Once the checks and review pass with no unresolved issue, the task finishes without another equivalent review cycle or unrelated cleanup. Do not prescribe a number of agents, tool calls, or review passes; follow-up work is justified by new changes or evidence. Inspect the execution trace rather than only the final answer, then remove the disposable fixture.

These additional scenarios use manual trace review; `check_dispatch.py` applies only to the explicit two-worker routing scenario. Preserve failed traces and relevant diagnostics when investigating regressions. No scenario alone establishes a token or cost saving.
