---
name: git-commit
description: Create exactly one git commit using Conventional Commits without a scope. Use whenever the user asks to commit the current repository changes.
---

# Git Commit

You are helping the user commit the current repository changes.

If the user provides extra context or a preferred message, factor it into the commit message while still following the rules below.

## Workflow

1. Inspect the repository state before committing:
   - Run `git status --short`.
   - If there are no staged, unstaged, or untracked changes, tell the user there is nothing to commit and stop.
   - Review the staged diff if there are staged changes.
   - If there are no staged changes, review the unstaged diff and relevant untracked files, then stage the intended changes with `git add -A`.
2. Create exactly one commit.
3. Use the Conventional Commits format, but do not include a scope:
   - Correct: `feat: add login flow`
   - Correct: `fix: handle empty config`
   - Incorrect: `feat(auth): add login flow`
4. Choose the most accurate type from: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
5. Keep the subject concise, imperative, and lowercase unless a proper noun is required.
6. Do not add emoji.
7. If the changes are not obvious, include a short commit body explaining why the change was made.
8. Because a request to commit is a request to commit, do not ask for extra confirmation unless the working tree contains unrelated or surprising changes.

After committing, report the commit hash and final subject.
