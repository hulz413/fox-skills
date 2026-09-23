# Routing regression

Run the checker tests without model calls:

```sh
python3 -m unittest discover -s skills/orchestrate/tests -p 'test_*.py' -v
```

After changing routing instructions, also run this behavioral smoke test in a fresh orchestrator context with the current skill path substituted. Give it the request below without explaining the routing bug or expected parameters:

> Use $orchestrate at <absolute skill path>. Delegate two independent worker tasks: (A) count `pear, apple, pear, plum, apple, pear`; (B) sum `12, 7, 19, 4, 8`. Keep cost and context small. While workers run, independently determine the number of distinct fruit names. Integrate the results and verify consistency. Use only these inputs; do not modify project files. Workers should execute directly.

Use a capable coordinator and record its actual `spawn_agent` calls from its own rollout (exclude ancestor history). Run:

```sh
python3 skills/orchestrate/tests/check_dispatch.py /path/to/orchestrator-rollout.jsonl --efficient-model MODEL_FROM_CURRENT_RUNTIME
```

Repeat the option for multiple acceptable efficient models. Select these from current runtime capability descriptions before evaluating results, not from the model IDs the run happened to choose. Also inspect that at creation time the coordinator presents a Markdown table with one row per worker and columns for subagent/role, assignment, requested model, effort, and task-specific selection reason (one table may cover the batch). Any later model/effort summary must also use a table; a single-agent dispatch still uses one row. Check that each effort is supported for its model and that no dispatch was rejected. The automatic checker targets this self-contained scenario only: production tasks may legitimately require inherited context or a stronger model.

Acceptance: two real worker dispatches pass the checker; workers actually finish; combined results are pear=3, apple=2, plum=1, distinct=3, sum=50. Check runtime-confirmed settings when exposed; requested parameters alone do not prove the effective model. Report unavailable delegation as blocked, not passed.

Unit tests validate the checker, not the Skill's behavior. A behavioral pass is one observation, not a compliance guarantee or a token/cost benchmark. Test files are maintenance-only and need not enter normal skill context.
