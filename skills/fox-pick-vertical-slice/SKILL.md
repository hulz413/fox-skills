---
name: fox-pick-vertical-slice
description: Reconcile a coding plan's slice statuses with the current repository implementation, then select either one implementation-ready vertical slice or one set of pairwise parallel OpenSpec changes. Use when choosing the next OpenSpec change from a coding-plan Markdown document, or selecting multiple changes that can safely be developed concurrently in separate worktrees.
---

# Fox Pick Vertical Slice

Audit and, when necessary, update the coding plan's implementation statuses before selecting the next actionable OpenSpec change or one set of changes that can all start concurrently. Do not implement code or invent missing requirements.

## Inputs and boundaries

1. Obtain the coding-plan Markdown. If the user does not provide its path or contents, ask for it. Resolve a writable source document before starting when status reconciliation may need to persist changes.
2. In the plan's repository, read `AGENTS.md`, `CLAUDE.md`, existing and archived `openspec/` artifacts, relevant code, tests, migrations, and recent history to establish conventions and implementation evidence. Treat the plan and task checkboxes as claims, not proof of the current implementation.
3. Mark unresolved product decisions, external permissions, data migrations, interface contracts, or designs as prerequisites. Never represent assumptions as decided work.

## Status reconciliation

Complete this audit before assessing candidates:

1. Enumerate every plan slice and its recorded implementation status.
2. Trace each slice to its active or archived OpenSpec change, implementation, tests, migrations, and other acceptance evidence. Run the smallest relevant checks when practical. Use history only to locate or explain evidence; do not treat a commit message, an archived change, or checked tasks alone as proof of completion.
3. Mark a slice `completed` only when its end-to-end outcome and required acceptance checks are present and passing in the current repository. Keep reverted or unverifiable work non-completed. Preserve the plan's existing status vocabulary. If it defines an active status, use it for confirmed partial or active work; when it only defines `pending` and `completed`, represent every non-completed state as `pending`.
4. Compare the evidence-based status with every recorded status. If they differ, update only the affected status cells in the source coding-plan file before selection. Preserve row order, priorities, dependencies, descriptions, and unrelated content. Re-read the file and inspect the diff to verify the update.
5. If a required update cannot be persisted, stop before selection and report the exact blocker. If evidence is insufficient, leave the status unchanged, state the uncertainty, and prevent that slice or any dependent candidate from being treated as unblocked.

Use the reconciled plan as the sole status baseline for the remaining workflow. Exclude completed slices from candidate selection. Do not create or update OpenSpec artifacts during this audit.

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

After reconciliation, report that the plan is complete and return no selection when every slice is completed. Report the blocking prerequisites and return no selection when incomplete slices exist but none can start. Otherwise, return exactly one non-empty selection:

- Select a single change when it is the next unblocked slice, when it owns a shared prerequisite, or when no other candidate is pairwise safe to run with it.
- Select multiple changes only when every pair is safe to start and merge independently under the parallelization assessment. They form one parallel set, not successive batches.
- Do not include a change that depends on another selected change.
- Do not select a completed slice or a slice whose implementation status could not be verified enough to establish that its prerequisites are complete.
- Do not describe future execution batches. Run this skill again after the selected change or parallel set has merged to choose the next selection.

## Output

Present the selected change or parallel set first, followed by its details. State whether it is a single change or a parallel set. Every selected change must be understandable and verifiable by one developer. If status cells changed, add one concise note after the selection explanation naming the updated slices and their old and new statuses; do not add an audit report when no statuses changed.

Write every user-facing heading, table header, label, explanation, and acceptance criterion in the primary language of the user's most recent message. Translate the template headings and labels below; they are semantic placeholders, not fixed English text. Keep only code identifiers, paths, commands, and OpenSpec change names in English.

Use this format:

```markdown
## <localized selected change(s) heading>

| <localized OpenSpec change> | <localized goal> | <localized owns> | <localized prerequisites> |
| --- | --- | --- | --- |
| `verb-object` | <localized verifiable capability> | <localized paths or shared boundary> | <localized none or specific condition> |

<localized selection label>: <localized single change / parallel set>. <localized explanation of why every selected change is safe to start now>.

## <localized change details heading>

### `verb-object`

- <localized scope>: <localized included user path, code boundary, and acceptance outcome>.
- <localized excludes>: <localized adjacent work that is out of scope>.
- <localized evidence>: <localized relevant plan sections and current repository evidence>.
- <localized owns>: <localized paths, contracts, or migrations it will write>.
- <localized reads>: <localized read-only dependencies>.
- <localized dependencies>: <localized changes that must complete first or decisions that must be confirmed>.
- <localized acceptance>: <localized runnable tests, checks, or manual verification>.

```

Use lowercase English kebab-case names, preferably `verb-object`, such as `add-report-export`. Name the capability, not the implementation layer.

Only after user confirmation, use `openspec-propose` to create artifacts for the selected change. If the user has already explicitly asked to create them, start proposing immediately and keep every change's boundary and dependencies consistent with this selection.
