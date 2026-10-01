# Orchestrate

A general-purpose skill for planning and coordinating useful subagent work. Invoke `$orchestrate` with a goal and relevant constraints. The coordinator chooses the approach, delegation, model settings, and verification depth, then integrates the results.

Four reusable role definitions cover investigation (**Explorer**), execution (**Worker**), independent assessment (**Reviewer**), and direction or decision advice (**Advisor**). Use any useful mix; choose local work or delegation based on required quality and overall cost, including coordination and verification. Advisors receive selected necessary context in a fresh subagent, without forking an App conversation. Subject expertise and project workflows are supplied with each assignment, while overall planning remains with the coordinator.

## Files

- [SKILL.md](SKILL.md): role definitions and essential coordination guidance.
- [Model routing](references/model-routing.md): task-based selection using current runtime information, selected once before each assignment.
- [agents/openai.yaml](agents/openai.yaml): the skill's interface metadata.

## Runtime behavior

Role definitions are instructions passed to subagents; they do not register native agent types or install persistent agents. Actual permissions, concurrency, and supported initial settings come from the host runtime.

Model routing reuses information already in context. Additional lookup is reserved for material gaps or unreliable information. Within a model family, routing normally uses the latest available compatible version identified by the runtime; explicit version pins and disclosed availability/compatibility exceptions remain supported. There is no maintained model list, third-party routing skill, background updater, or persistent cache. The coordinator's own configuration is set by the caller or session.

Role responsibilities are predefined; models and efforts are selected per assignment rather than bound to roles. Medium is a decision baseline, not a mandatory execution setting or trial. Selection considers the assignment's capability needs, acceptance, iteration, latency and known costs, using applicable task evaluations and model-specific official guidance before generic effort heuristics. Xhigh can support exacting analysis or delivery without repeated reasoning cycles when extra effort has an expected benefit. The coordinator applies each selection through supported runtime controls, discloses inheritance or unavailable effort controls, and keeps the configuration fixed for follow-ups. Corrections change evidence or approach, not configuration. Instructions guide decisions; hard budgets require runtime support. Interface changes may still require maintaining the skill.

Install this folder as `orchestrate` in your discoverable skills directory.

## Regression tests

See [tests/README.md](tests/README.md) for the routing-only behavioral suite and offline checker tests. Run them after every skill edit; sample tasks are never executed. These are maintenance checks, not runtime skill dependencies.

## Design references

Conceptual references, not runtime dependencies:

- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection): task and delivery tradeoffs; recommendations are starting points to evaluate.
- [OpenAI model catalog](https://developers.openai.com/api/docs/models): current model capabilities and supported settings.
- [Practical model selection cookbook](https://developers.openai.com/cookbook/examples/partners/model_selection_guide/model_selection_guide): stage-specific selection and evaluation methods; its 2025 model and pricing examples are historical.
- [donvito/codex-astra-luna-orchestrator](https://github.com/donvito/codex-astra-luna-orchestrator): bounded assignments, resource ownership, concise evidence, and coordinator acceptance.
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents): separate contexts and explicit handoffs.
- [OpenCode agents](https://opencode.ai/v2/docs/agents): general roles and permission boundaries.
