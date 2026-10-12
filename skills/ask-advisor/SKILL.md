---
name: ask-advisor
description: Get an independent second opinion from one analysis-only advisor using the current runtime's subagent tools. Use when the user asks for an advisor, an outside take, or a recommendation before deciding. Supports provider, model, and reasoning-effort overrides.
---

# Ask Advisor

Launch one independent advisor, collect its reasoning, and synthesize a recommendation. The initiating agent retains ownership of the work and the final judgment.

## Input

Accept a question or the current task, with optional `--provider <id>`, `--model <id>`, and `--effort <id>`. Equivalent preferences in natural language also count. Each override replaces only its corresponding default. Ask only when conflicting preferences or missing information prevent a valid launch.

```text
$ask-advisor Evaluate the current approach.
$ask-advisor --provider claude Evaluate the current approach.
$ask-advisor --provider codex --model MODEL_ID --effort medium Review this decision.
```

## Execution and configuration

Use the current runtime's native subagent tools and their documented capabilities. This skill has no dependency on another skill, external agent manager, or additional CLI. If the runtime cannot launch an independent advisor with the required configuration, explain the blocker without claiming an advisor ran.

Resolve configuration directly from user preferences and runtime capabilities. Do not require named profiles, pick a different provider for contrast, or let a profile overwrite the resolved configuration.

Resolve in this order:

1. **Provider:** the user's override, otherwise the initiating agent's current provider. Use verified session metadata and provider identifiers understood by the runtime. Do not infer the provider from an unrelated default or model-name guess. Ask if the current provider cannot be established.
2. **Model:** the user's override, otherwise the selected provider's best model for general reasoning and analysis, with its next-best model as the sole automatic fallback.
3. **Effort:** the user's override, otherwise `high`.

Use the runtime's exposed tool documentation, session metadata, or model catalog to establish available providers, models, capability descriptions, and supported effort settings. Reuse information already supplied; do not invent discovery commands. If the runtime only supports one provider, honor a different provider override by reporting that limitation rather than silently using its sole provider.

Rank models using current runtime capability descriptions and applicable official provider guidance. Treat "flagship" and "frontier" as descriptive terms, not model IDs or guaranteed ordering. Do not infer capability from model names, version numbers, cost, or list order. Do not maintain hardcoded model-ID rankings. Establish the next-best candidate only if fallback is needed. If available evidence cannot establish a required ranking, resolve it from official documentation or ask a focused question. A valid explicit model needs no ranking.

Validate the provider/model/effort combination and the ability to apply it before launch. An advertised model is not proof of access. Effort names are provider-specific: use a documented equivalent only when the runtime establishes the mapping. Never treat an unknown inherited setting as confirmed `high`.

### Fallback and explicit choices

- For an automatically selected model, attempt the best candidate first. If preflight or startup establishes that it is unavailable, inaccessible, or incompatible with the required effort, try the verified next-best candidate once. Revalidate that candidate against the same question and effort requirement before launching.
- Keep the selected provider and effort fixed during fallback. Do not continue to a third model, switch providers, or lower effort automatically. If the next-best candidate also cannot be used, explain the blocker and ask for a supported choice.
- An explicitly requested model is pinned. If it cannot be used with the resolved provider and effort, explain why and ask before substituting it. Explicit provider and effort choices are also pinned.
- Model fallback addresses model-specific availability or compatibility. Missing provider authentication, unavailable services, permission requests, shared rate limits, missing evidence, and poor advisor reasoning require their own resolution; do not route around them by changing models.
- Fall back only before substantive analysis begins. If an attempt created an agent before failing, stop that failed attempt through the supported lifecycle tools before creating its replacement; never run the two concurrently.

Apply the resolved provider, model, and effort through supported dispatch parameters, not prompt prose. For an interface exposing `model`, `reasoning_effort`, and `fork_turns`, pass the resolved model and effort and use `fork_turns: "none"` for fresh context. Other runtimes may use different parameter names. If provider selection is implicit, verify that the selected model belongs to the resolved provider. If the interface cannot apply or confirm the required settings, report the limitation instead of claiming success. The input flags are skill conventions, not assumed runtime tool parameters.

## Independent briefing

Use fresh context rather than forking the conversation. Give the advisor a self-contained briefing containing:

- The precise question and decision to support.
- Relevant constraints, original evidence, and unresolved uncertainties.
- Options already considered and why any were ruled out; distinguish observations from the initiating agent's hypotheses.
- Relevant file paths and the requested review scope, including the base revision for a diff review. Confirm that the advisor can access the referenced resources; otherwise supply the necessary excerpts.
- An explicit request for a recommendation, reasoning, and material verification gaps.

When the user forwards another skill, such as `$ask-advisor /unslop-risk`, instruct the advisor to load that skill through its available skill-loading mechanism and pass the remaining arguments as its input. The advisor executes the forwarded skill. If that skill requires edits or other actions outside analysis, report the conflict rather than expanding permission.

End the briefing with:

```text
This is analysis only. Do NOT edit, create, or delete any files. Do NOT write code.
```

Use a verified read-only execution mode when the provider offers one. A prompt restriction alone is not a sandbox guarantee. Do not select a mode that silently broadens permissions.

## Launch, synthesize, and clean up

Launch the advisor with the briefing as its initial prompt, using an advisor task name or `[Advisor] <topic>` title if supported. Reuse the current workspace when accessible; do not create a worktree for an analysis-only consultation. Use the runtime's supported completion events or bounded waits, then retrieve the complete response. Keep completion notifications enabled when configurable; avoid repeated status polling.

Read the complete response before synthesizing it. Distinguish the advisor's recommendation from your own assessment, state material disagreements and uncertainty, and do not imply that the advice was implemented or independently verified. Briefly report the actual provider, model, and effort, including any fallback and its reason. On an error or permission request, report the actual state rather than presenting a completed consultation.

After a one-off consultation, read and retain the response, then release the advisor using a documented close or archive operation if one exists. If the runtime provides no cleanup operation, leave the completed advisor idle rather than inventing one. If the user requests ongoing advice, retain its ID and resolved configuration for follow-ups; recheck that the retained configuration satisfies any new explicit preferences. Start a fresh advisor when the topic or required configuration changes, and release the old advisor when it is no longer needed. Never stop unrelated agents or delete the user's workspace.
