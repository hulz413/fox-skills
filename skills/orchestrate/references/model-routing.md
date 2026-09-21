# Task-specific model routing

Choose the model and reasoning effort for each assignment. Roles do not pin configurations, and no external model-selection skill or static model catalog is needed.

## Use available information

Start with the supported models, efforts, and capability descriptions already exposed by the active execution tools. Reuse still-valid information; sufficient context needs no extra query, including when this skill is invoked again.

Use an exposed catalog or current official provider documentation only when missing or unreliable information materially affects the choice. Refresh the relevant information when the runtime changes, sources conflict, or a configuration is rejected. Public documentation can inform capability judgments; availability and accepted parameters come from the actual execution interface.

Honor explicit user settings. When overrides or comparison information are unavailable, use a compatible configured or runtime-recommended default and disclose material limitations. Report an unavailable pinned setting rather than silently replacing it. Use the metadata supplied in a fresh context; this skill does not provide a persistent cache or discovery service.

## Match the assignment

Consider ambiguity, interacting constraints, consequences of error, difficulty of verification, required tools or modalities, and the user's quality, latency, and usage preferences. Focused, checkable work often suits an efficient model; difficult synthesis or reasoning may justify stronger capabilities and deeper effort. Treat these as judgment calls, not a fixed classification table.

Interpret effort levels using that model's supported values and descriptions. Base capability, speed, and cost comparisons on available descriptions or observed evidence. Choose an execution mode compatible with the assignment's delegation boundaries and shared concurrency.

## Apply the choice

Set real model and effort parameters on the supported execution tool. Some runtimes prohibit overrides with full-history forks: use a sufficient fresh or limited-context handoff when appropriate, or preserve necessary context and report inherited settings. Keep relevant constraints and prior decisions in the handoff.

Retain enough task state to explain the choice and assess the result. Distinguish requested settings from runtime-confirmed settings. The coordinator's own model and effort are set by its caller or session, outside this skill.

## Adapt from results

Use observed outcomes to adjust context, approach, model, or effort. Missing inputs, permissions, and service failures need remedies appropriate to their causes. Reuse an agent when its configuration fits; when replacement is needed, hand off useful results and settle resource ownership before the replacement proceeds.

There is no fixed retry or escalation count. Continue when progress or new evidence justifies the expected benefit, within user-provided limits. Re-plan or surface the blocker when attempts stop producing useful progress. Report measured usage only when available; these instructions do not enforce a hard runtime budget.
