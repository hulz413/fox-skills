# Host capabilities

SKILL.md names actions, not tools. Use the current host's own tool for each action; the session's actual tool list takes precedence over this table. If an action has no supported tool, report the limitation in the plan and continue what does not depend on it. Worker-side actions (task rename, browser, asking the coordinator) are in the [fix skill's host table](../../fox-fix-projex-bug/references/hosts.md).

| Action | Codex | Claude Code | T3 Code |
|---|---|---|---|
| List providers, models, efforts | The repository or skill's model listing script if available, otherwise the dispatch tool's documented enum | The `Agent` tool's `model` and `effort` options; other providers are not dispatchable | `orchestrator_capabilities` |
| Start a worker with model and effort, fresh context | `spawn_agent` with model and reasoning effort, fresh context | `Agent` with `model` and `effort`, a non-fork subagent type | `delegate_task` with `target.providerInstanceId`, `target.model`, `target.options` (effort), a `title`, and default shared isolation: the coordinator creates the worktree itself |
| Wait for workers | Completion notifications or bounded waits, no polling loops | Background agents notify on completion | Completion wakes the coordinator; follow each task's `next`; read results with `task_status` |
| Answer a worker's question | Follow-up message to that agent | `SendMessage` to the agent to resume it | Reply in that worker's thread as the host's `next` instructs |
| Stop a worker | The host's cancel tool | `TaskStop` | `task_cancel` |

The coordinator creates fix worktrees with `git worktree add` itself so their paths and branches follow the skill's layout; do not also ask the host to create a separate worktree for the same task.
