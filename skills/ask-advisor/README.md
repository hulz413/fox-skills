# Ask Advisor

Get an independent second opinion using the current runtime's native subagent tools while the initiating agent keeps ownership of the task.

## Requirements

Make this folder discoverable by your agent runtime. The runtime must support independent subagents and applying the selected model and reasoning effort. Provider overrides work only when the runtime supports the requested provider. No additional skill, external agent manager, or CLI is required.

## Usage

```text
$ask-advisor Evaluate the current approach.
$ask-advisor --provider claude Evaluate the current approach.
$ask-advisor --provider codex --model MODEL_ID --effort medium Review this decision.
```

Provider, model, and effort preferences can also be written in natural language. Omitted values resolve to the initiating agent's provider, that provider's best reasoning model, and `high`, respectively. Model ranking comes from current capability information rather than a fixed model-name table.

If the automatically selected best model cannot be used, the skill may try the next-best model once, keeping provider and effort fixed. Explicit model choices do not fall back without approval. Unresolvable rankings or unsupported settings require clarification rather than silent substitution.

The advisor analyzes without modifying files. One-off advisors are released after their answers are collected when the runtime supports cleanup; otherwise they remain completed and idle. Ongoing advisors are retained when requested. The response reports the configuration actually used and any fallback.

See [SKILL.md](SKILL.md) for the complete workflow. Input flags are skill conventions; the executor maps them to supported runtime dispatch parameters rather than assuming matching tool argument names.
