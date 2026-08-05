---
name: pick-vertical-slice
description: Select either one implementation-ready vertical slice or one set of pairwise parallel OpenSpec changes from a user-provided coding-plan Markdown document. Use when choosing the next OpenSpec change from a coding plan, or selecting multiple changes that can safely be developed concurrently in separate worktrees.
---

# Pick Vertical Slice

Select the next actionable OpenSpec change, or one set of changes that can all start concurrently, from a coding plan. Do not implement code or invent missing requirements.

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

## Selection rule

Return exactly one non-empty selection:

- Select a single change when it is the next unblocked slice, when it owns a shared prerequisite, or when no other candidate is pairwise safe to run with it.
- Select multiple changes only when every pair is safe to start and merge independently under the parallelization assessment. They form one parallel set, not successive batches.
- Do not include a change that depends on another selected change. Put it under deferred items and explain which selected change unlocks it.
- Do not describe future execution batches. Run this skill again after the selected change or parallel set has merged to choose the next selection.

## Output

Present the selected change or parallel set first, followed by its details. State whether it is a single change or a parallel set. Every selected change must be understandable and verifiable by one developer.

Use this format:

```markdown
## Selected change(s)

| OpenSpec change | Goal | Owns | Prerequisites |
| --- | --- | --- | --- |
| `verb-object` | Verifiable capability | Paths or shared boundary | None / specific condition |

Selection: Single change / parallel set. Explain why every selected change is safe to start now.

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

- `plan item`: Why it was not selected now, or the specific selected change or decision that unlocks it.
```

Use lowercase English kebab-case names, preferably `verb-object`, such as `add-report-export`. Name the capability, not the implementation layer.

Only after user confirmation, use `openspec-propose` to create artifacts for the selected change. If the user has already explicitly asked to create them, start proposing immediately and keep every change's boundary and dependencies consistent with this selection.
