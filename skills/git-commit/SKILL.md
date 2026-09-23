---
name: git-commit
description: Create exactly one focused Conventional Commit using the lowest available model tier and reasoning effort. Use whenever the user asks to commit the current repository changes.
---

# Git Commit

You are helping the user commit the current repository changes.

If the user provides extra context or a preferred message, factor it into the commit message while still following the rules below.

## Execution model

Use the lowest-tier model currently available to the execution interface, with that model's minimum supported reasoning effort. Reuse current runtime metadata to identify model tiers and effort ordering; do not hardcode model IDs or effort labels, or infer tiers from name spelling. Among equivalent lowest-tier options, prefer the runtime's current recommended model. Look up missing information only when needed to make this choice. Explicit user overrides and higher-priority constraints take precedence.

Select the executor before reviewing diffs or mutating Git state. If the current agent already uses the selected settings, perform the workflow directly. Otherwise, use a supported execution interface or delegate to one commit executor with explicit model and effort parameters and a sufficient fresh or limited-context handoff. This skill authorizes that delegation and those configuration overrides. Loading the skill alone does not change the current agent's model.

Pass the repository path, requested commit scope, relevant constraints, and existing validation results. A delegated commit executor performs the workflow directly without further delegation. Give it sole ownership of staging and committing; the coordinator verifies and reports its resulting commit without creating another one. Distinguish requested configuration from runtime-confirmed configuration when reporting.

If the required configuration cannot be identified or run, report the limitation before staging or committing; do not silently substitute a higher model tier or reasoning effort. Do not change global model settings to execute this skill.

## Workflow

1. Inspect the repository state before committing:
   - Run `git status --short`.
   - If there are no staged, unstaged, or untracked changes, tell the user there is nothing to commit and stop.
   - Review the staged diff if there are staged changes.
   - If there are no staged changes, review the unstaged diff and relevant untracked files, then stage only the reviewed files that belong to the requested commit. Do not use `git add -A` by default.
2. Create exactly one commit.
3. Use the Conventional Commits format. A scope is optional:
   - Correct: `feat: add login flow`
   - Correct: `fix(config): handle empty config`
   - Use a concise lowercase scope only when it clearly identifies the affected component.
4. Choose the most accurate type from: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
5. Keep the subject concise, imperative, and lowercase unless a proper noun is required.
6. Do not add emoji.
7. If the changes are not obvious, include a short commit body explaining why the change was made.
8. A request to commit authorizes one requested commit. Do not ask for extra confirmation unless the working tree contains unrelated or surprising changes, or the intended files cannot be determined safely.

After committing, report the commit hash and final subject.
