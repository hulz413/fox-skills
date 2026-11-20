# Host capabilities

SKILL.md names actions, not tools. Use the current host's own tool for each action; the session's actual tool list takes precedence over this table. If an action has no supported tool, report the limitation and continue the work that does not depend on it. Never fake an action, such as claiming a rename that did not happen.

| Action | Codex | Claude Code | T3 Code |
|---|---|---|---|
| Rename the current task/chat | `set_thread_title`, omitting `threadId` | No agent-side rename tool; report the limitation (the user can run `/rename`) | `t3_thread_update` with `action: "rename"`, omitting `threadId` |
| Show a clickable link | Markdown link in the message | Markdown link in the message | Markdown link in the message |
| Drive the built-in browser for acceptance | The host's browser tool, if enabled | Browser tools from a connected browser MCP or plugin, if any | `preview_open`, `preview_navigate`, `preview_act`, `preview_snapshot`, then `t3_preview_close` for tabs you opened |
| Ask the coordinator (dispatched mode) | End the turn with the question; the coordinator answers in a follow-up message | Return the question as the result; the coordinator resumes this agent with the answer | End the turn with the question; the coordinator is woken and answers in this thread |

When asking the coordinator, start the message with `QUESTION FOR COORDINATOR:` and include the issue keys, what was checked, the evidence, and the options, so the coordinator can answer without rereading the whole task. The coordinator is the task that dispatched you (in T3 Code, the parent of your thread), and ending the turn as above is how the question reaches it.
