# Orchestrate

A general-purpose skill for planning and coordinating useful subagent work. Invoke `$orchestrate` with a goal and relevant constraints. The coordinator chooses the approach, delegation, model settings, and verification depth, then integrates the results.

Four reusable role definitions cover investigation (**Explorer**), execution (**Worker**), independent assessment (**Reviewer**), and direction or decision advice (**Advisor**). They can be instantiated in any useful mix; work stays with the coordinator by default unless delegation is worthwhile. Advisors receive selected necessary context in a fresh subagent, without forking an App conversation. Subject expertise and project workflows are supplied with each assignment, while overall planning remains with the coordinator.

## Files

- [SKILL.md](SKILL.md): role definitions and essential coordination guidance.
- [Model routing](references/model-routing.md): task-based selection using current runtime information, plus adaptation from results.
- [agents/openai.yaml](agents/openai.yaml): the skill's interface metadata.

## Runtime behavior

Role definitions are instructions passed to subagents; they do not register native agent types or install persistent agents. Actual permissions, concurrency, and supported configuration changes come from the host runtime.

Model routing reuses information already in context. Additional lookup is reserved for material gaps or unreliable information. There is no maintained model list, third-party routing skill, background updater, or persistent cache. The coordinator's own configuration is set by the caller or session.

Retries and upgrades depend on observed progress and user constraints, with no skill-imposed numeric limit. Instructions guide decisions; hard budgets require runtime support. Interface changes may still require maintaining the skill.

Install this folder as `orchestrate` in your discoverable skills directory.

## Regression tests

See [tests/README.md](tests/README.md) for the routing-only behavioral suite and offline checker tests. Run them after every skill edit; sample tasks are never executed. These are maintenance checks, not runtime skill dependencies.

## Design references

Conceptual references, not runtime dependencies:

- [donvito/codex-astra-luna-orchestrator](https://github.com/donvito/codex-astra-luna-orchestrator): bounded assignments, resource ownership, concise evidence, and coordinator acceptance.
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents): separate contexts and explicit handoffs.
- [OpenCode agents](https://opencode.ai/v2/docs/agents): general roles and permission boundaries.
