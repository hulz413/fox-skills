---
name: handoff
description: Create a resumable checkpoint for the current task. Use when the user asks to hand off work, preserve the current state, continue across sessions, or generate a recovery point for pickup.
---

# Handoff

Create a factually complete checkpoint that can restore the current task in a new session. Invoking this skill authorizes writing the checkpoint only. It does not authorize project changes, commits, pushes, or execution of the recorded next steps.

## Derive the checkpoint title

Do not copy the task display title. Automatically summarize the actual task from:

- the current active objective;
- the user's latest request that changed or narrowed the scope;
- the work actually completed or in progress.

Convert that summary into a short, recognizable English action-object phrase, then normalize it to lowercase kebab-case:

- use only `a-z`, `0-9`, and single hyphens;
- prefer a concrete action and object, such as `implement-user-auth`;
- avoid generic titles such as `handoff`, `checkpoint`, or `current-task`;
- make the filename recognizable without opening the file.

## Gather the current state

Prefer reliable facts already present in the current session. Perform read-only workspace checks when needed. Record only confirmed information, never guess, and never describe planned work as completed.

When a Git repository is relevant, record the workspace path, branch, HEAD, staged changes, unstaged changes, untracked files, and the relevant files. Record validation commands that were actually run and their results. Mark unavailable or unchecked information as unverified instead of inventing placeholders.

Do not include passwords, tokens, private keys, complete environment variable values, or other secrets. Record only variable names or redacted facts when needed.

## Create the checkpoint

Use this fixed root directory:

```text
/tmp/agents/checkpoints/
```

Use this exact filename format:

```text
checkpoint-{title}-{date}-{time}.md
```

Where:

- `title` is the automatically derived English kebab-case summary;
- `date` is the system-local date in `YYYYMMDD` format;
- `time` is the system-local time in `HHmmss` format.

Example:

```text
/tmp/agents/checkpoints/checkpoint-implement-user-auth-20260819-183000.md
```

Create the directory and verify that the target path does not exist before writing. Never overwrite an existing checkpoint. If a same-second collision occurs, obtain a new current timestamp and generate another unused path that still follows the exact format.

The checkpoint identifier is the filename basename without `.md`. Write the checkpoint headings and narrative in Chinese. Preserve code, commands, paths, symbol names, and error messages in their original form.

Include this logical structure, rendering the headings in Chinese in the actual checkpoint:

```markdown
---
checkpoint_id: "checkpoint-{title}-{date}-{time}"
created_at: "ISO 8601 local timestamp"
task_slug: "{title}"
workspace: "absolute workspace path or unverified"
---

# Task Checkpoint

## Task Goal and Scope

## Current State

## Completed Work

## Key Decisions and Constraints

## Files and Git State

## Validation Results

## Risks and Blockers

## Next Steps
```

Order the next steps for execution and make the first item concrete enough to start immediately after restoration. Use the Chinese equivalent of "None" or "Unverified" for an empty or unchecked section; do not remove fixed sections.

## Report completion

After a successful write, report the absolute checkpoint path and checkpoint identifier. Immediately before the command block, convey the following instruction in the user's current language:

Start a new task in the same project, then copy and send the command below to restore the context.

End with a standalone code block containing only the following line, replacing the placeholders with the actual absolute path:

```text
$pickup /tmp/agents/checkpoints/checkpoint-{title}-{date}-{time}.md
```

Do not add a shell prompt before the command or explanatory text inside the code block. The user must be able to copy the entire line into a new session and invoke pickup directly.
