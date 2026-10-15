# Fox Ask Advisor

Get an independent second opinion using the current runtime's native subagent tools while the initiating agent keeps ownership of the task.

## Requirements

Make this folder discoverable by your agent runtime. The runtime must support independent subagents and applying the selected model and reasoning effort. Provider overrides work only when the runtime supports the requested provider. No additional skill, external agent manager, or CLI is required.

## Usage

```text
$fox-ask-advisor Evaluate the current approach.
$fox-ask-advisor --provider claude Evaluate the current approach.
$fox-ask-advisor --provider codex --model MODEL_ID --effort medium Review this decision.
$fox-ask-advisor --context full Review what I just changed.
$fox-ask-advisor --mode session
```

Provider, model, effort, context, and mode preferences can also be written in natural language. Omitted values resolve to the initiating agent's provider, that provider's best reasoning model, task-appropriate effort, `auto`, and `once`, respectively. Effort selection starts from `medium` and moves down or up according to the advisor question's complexity before launch; this does not mean running once at `medium` first. Model ranking comes from current capability information rather than a fixed model-name table.

`--context auto` forwards the conversation history (`full`) when the question reviews work done in this session and the evidence lives in the transcript; otherwise it sends a self-contained briefing (`brief`) to keep the advisor independent. If forking cannot apply the resolved model or effort, an automatic `full` falls back to `brief`. An explicit `--context full` preserves the resolved configuration; if an inheriting fork cannot match it, the agent asks which requirement to change. Because forks usually cannot apply a different model or effort, `auto` usually ends in `brief`; request `--context full` explicitly when the advisor needs the history.

`--mode session` lets the agent consult an advisor on its own before substantive work, when stuck, when changing approach, and before delivering, for the rest of the current task. Each consultation runs a subagent, so a task may cost several advisor runs. The mode lives in the conversation and can be lost after context compaction. To enable it by default, add a line such as this to `AGENTS.md` or `CLAUDE.md`:

```text
For multi-step implementation tasks, use $fox-ask-advisor --mode session.
```

If the automatically selected best model cannot be used, the skill may try the next-best model once, keeping provider and effort fixed. Explicit model choices do not fall back without approval. Unresolvable rankings or unsupported settings require clarification rather than silent substitution.

The advisor analyzes without modifying files or launching subagents. When its advice conflicts with evidence the agent holds, the agent asks the same advisor once more to reconcile before concluding. One-off advisors are released after their answers are collected when the runtime supports cleanup; otherwise they remain completed and idle. Ongoing advisors are retained when requested. The response reports the configuration and context actually used and any fallback.

See [SKILL.md](SKILL.md) for the complete workflow. Input flags are skill conventions; the executor maps them to supported runtime dispatch parameters rather than assuming matching tool argument names.
