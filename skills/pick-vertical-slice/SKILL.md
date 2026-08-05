---
name: pick-vertical-slice
description: Select implementation-ready vertical slices from a user-provided coding-plan Markdown document for OpenSpec, including multiple changes that can be safely developed in parallel across separate worktrees. Use when evaluating, splitting, prioritizing, or selecting OpenSpec changes from a coding plan, or deciding which implementation work can run in parallel.
---

# Pick Vertical Slice

Produce a small set of actionable OpenSpec change candidates from a coding plan. Do not implement code or invent missing requirements.

## Inputs and boundaries

1. Obtain the coding-plan Markdown. If the user does not provide its path or contents, ask for it.
2. In the plan's repository, read `AGENTS.md`, `CLAUDE.md`, existing `openspec/` artifacts, and relevant code to establish naming, specification, and test conventions. Treat the plan as intent, not proof of the current implementation.
3. Mark unresolved product decisions, external permissions, data migrations, interface contracts, or designs as prerequisites. Never represent assumptions as decided work.

## Slice criteria

Each change must be an independently verifiable user or system capability with its smallest necessary end-to-end path. Do not split by layer into "database only", "API only", or "component only" work. Keep the schema, service, UI, and tests required for one capability in the same slice.

Prefer candidates that:

- deliver and validate independently, with a clear entry point, observable outcome, and acceptance criteria;
- have a focused change surface, few dependencies, and reuse established models, contracts, and patterns;
- remove a real blocker for later slices or deliver user value early.

Do not select candidates that:

- are plan items with technical labels but no behavior or acceptance outcome;
- depend on undecided protocols, fields, or product rules;
- only work when another change simultaneously edits the same file, shared contract, or migration chain;
- are over-split solely to increase apparent parallelism.

## Parallelization assessment

For each candidate, list `owns`, `reads`, and `depends_on`. Mark it safe for parallel development in a separate worktree only when all conditions hold:

1. It does not write overlapping files, directories, shared contracts, database migrations, or lockfiles.
2. It does not rely on interfaces, types, configuration keys, or data structures from another candidate that have not merged.
3. Its tests and acceptance checks can run independently.

Shared read-only directories are safe. If a conflict could be coordinated, make the work sequential or propose a smaller prerequisite change that establishes the shared boundary. Never recommend parallel changes that modify the same infrastructure or public model.

## Output

Present recommended execution batches first, followed by candidate details. Recommend only one to three of the most valuable changes by default. Add more only when the plan is large enough and each batch remains understandable and verifiable by one developer.

Use this format:

```markdown
## Recommended batches

| Batch | OpenSpec change | Goal | Parallelism | Prerequisites |
| --- | --- | --- | --- | --- |
| 1 | `verb-object` | Verifiable capability | Parallel with ... / sequential | None / specific condition |

## Change details

### `verb-object`

- Scope: Included user path, code boundary, and acceptance outcome.
- Excludes: Explicitly adjacent work that is out of scope.
- Evidence: Relevant plan sections and current repository evidence.
- Owns: Paths, contracts, or migrations it will write.
- Reads: Read-only dependencies.
- Dependencies: Changes that must complete first or decisions that must be confirmed.
- Acceptance: Runnable tests, checks, or manual verification.

## Deferred items and blockers

- `plan item`: Why it was not selected, or the specific decision/prerequisite change that unlocks it.
```

Use lowercase English kebab-case names, preferably `verb-object`, such as `add-report-export`. Name the capability, not the implementation layer.

Only after user confirmation, use `openspec-propose` to create artifacts for the selected change. If the user has already explicitly asked to create them, start proposing immediately and keep every change's boundary and dependencies consistent with this selection.
