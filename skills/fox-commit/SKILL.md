---
name: fox-commit
description: Create exactly one focused Conventional Commit directly in the current session using its current model. Use whenever the user asks to commit the current repository changes.
---

# Fox Commit

You are helping the user commit the current repository changes.

If the user provides extra context or a preferred message, factor it into the commit message while still following the rules below.

## Execution model

Perform the workflow directly in the current session using its current model. Use that model's lowest supported reasoning effort when the runtime provides a control for this operation, respecting explicit user overrides. Use available runtime metadata to identify supported efforts; do not change the model or global defaults.

Skill instructions alone cannot change the active turn's reasoning setting. If no supported control is available, continue at the actual setting and briefly disclose the limitation rather than claiming a lower effort or blocking the commit. Reuse existing task context and valid verification results; keep commit checks proportionate to the changes.

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
