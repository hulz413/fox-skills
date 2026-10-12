---
name: fox-ask-advisor
description: Get an independent second opinion from one analysis-only advisor using the current runtime's subagent tools. Use when the user asks for an advisor, an outside take, or a recommendation before deciding, or asks to keep consulting an advisor at key checkpoints of the current task. Supports provider, model, reasoning-effort, context, and session-mode overrides.
---

# Fox Ask Advisor

Launch one independent advisor, collect its reasoning, and synthesize a recommendation. The initiating agent retains ownership of the work and the final judgment.

## Input

Accept a question or the current task, with optional `--provider <id>`, `--model <id>`, `--effort <id>`, `--context auto|full|brief` (default `auto`), and `--mode once|session|off` (default `once`). Equivalent preferences in natural language also count. Each override replaces only its corresponding default. Ask only when conflicting preferences or missing information prevent a valid launch.

```text
$fox-ask-advisor Evaluate the current approach.
$fox-ask-advisor --provider claude Evaluate the current approach.
$fox-ask-advisor --provider codex --model MODEL_ID --effort medium Review this decision.
$fox-ask-advisor --context full Review what I just changed.
$fox-ask-advisor --mode session
```

## Execution and configuration

Use the current runtime's native subagent tools and their documented capabilities. This skill has no dependency on another skill, external agent manager, or additional CLI. If the runtime cannot launch an independent advisor with the required configuration, explain the blocker without claiming an advisor ran.

Resolve configuration directly from user preferences and runtime capabilities. Do not require named profiles, pick a different provider for contrast, or let a profile overwrite the resolved configuration.

Resolve in this order:

1. **Provider:** the user's override, otherwise the initiating agent's current provider. Use verified session metadata and provider identifiers understood by the runtime. Do not infer the provider from an unrelated default or model-name guess. Ask if the current provider cannot be established.
2. **Model:** the user's override, otherwise the selected provider's best model for general reasoning and analysis, with its next-best model as the sole automatic fallback. An explicit `full` context without a model or effort override inherits the parent's instead; see Context selection.
3. **Effort:** the user's override, otherwise `high`, with the same `full` exception.

Use the runtime's exposed tool documentation, session metadata, or model catalog to establish available providers, models, capability descriptions, and supported effort settings. Reuse information already supplied; do not invent discovery commands. If the runtime only supports one provider, honor a different provider override by reporting that limitation rather than silently using its sole provider.

Rank models using current runtime capability descriptions and applicable official provider guidance. Treat "flagship" and "frontier" as descriptive terms, not model IDs or guaranteed ordering. Do not infer capability from model names, version numbers, cost, or list order. Do not maintain hardcoded model-ID rankings. Establish the next-best candidate only if fallback is needed. If available evidence cannot establish a required ranking, resolve it from official documentation or ask a focused question. A valid explicit model needs no ranking.

Validate the provider/model/effort combination and the ability to apply it before launch. An advertised model is not proof of access. Effort names are provider-specific: use a documented equivalent only when the runtime establishes the mapping. Never treat an unknown inherited setting as confirmed `high`.

### Fallback and explicit choices

- For an automatically selected model, attempt the best candidate first. If preflight or startup establishes that it is unavailable, inaccessible, or incompatible with the required effort, try the verified next-best candidate once. Revalidate that candidate against the same question and effort requirement before launching.
- Keep the selected provider and effort fixed during fallback. Do not continue to a third model, switch providers, or lower effort automatically. If the next-best candidate also cannot be used, explain the blocker and ask for a supported choice.
- An explicitly requested model is pinned. If it cannot be used with the resolved provider and effort, explain why and ask before substituting it. Explicit provider and effort choices are also pinned.
- Model fallback addresses model-specific availability or compatibility. Missing provider authentication, unavailable services, permission requests, shared rate limits, missing evidence, and poor advisor reasoning require their own resolution; do not route around them by changing models. Treat an error as model-specific when it names that model or its own quota or credits, or tells you to switch models; fall back once. Treat it as shared when it applies to the account, provider, or every model.
- Fall back only before substantive analysis begins. If an attempt created an agent before failing, stop that failed attempt through the supported lifecycle tools before creating its replacement; never run the two concurrently.

Apply the resolved provider, model, and effort through supported dispatch parameters, not prompt prose. For an interface exposing `model`, `reasoning_effort`, and `fork_turns`, pass the resolved model and effort with `fork_turns: "none"` for a `brief` context. For a `full` context, use the interface's full-history value and pass no model or effort override when the fork inherits the parent's; see Context selection. Other runtimes may use different parameter names. If provider selection is implicit, verify that the selected model belongs to the resolved provider. If the interface cannot apply or confirm the required settings, report the limitation instead of claiming success. The input flags are skill conventions, not assumed runtime tool parameters.

## Context selection and briefing

Choose how much of the conversation the advisor sees. An explicit `full` or `brief` is pinned; resolve `auto` from the question:

- **`full`**: forward the conversation history when the question reviews work done in this session, such as a pre-delivery check or a stuck debugging loop, and the decisive evidence lives in tool output, errors, or intermediate results that a summary would lose.
- **`brief`**: start fresh with a self-contained briefing when the question is a choice or tradeoff, when the conversation carries strong hypotheses from the initiating agent that could anchor the advisor, or when most of a long conversation is irrelevant. When unsure, use `brief`; independence is the default value of an advisor. Because forks often cannot apply the resolved model and effort, `auto` usually ends in `brief`; request `full` explicitly to forward history.

Some fork mechanisms run on the parent's model and effort and ignore overrides:

- An automatically selected `full` must not override the resolved configuration. If it cannot apply the resolved provider, model, and effort, use `brief` and say so.
- An explicit `full` without an explicit model or effort means the user accepts the parent's configuration. Fork with it, without asking, and report the model and effort as inherited.
- An explicit `full` with an explicit model or effort requires that the runtime confirms the parent already uses those values. Otherwise, or if the runtime cannot fork full history at all, explain the conflict and ask.

For `full`, append the precise question and the requested review scope. State that the advisor is not the initiating agent, must not continue the user's task or any session-mode commitment in the history, and answers only the appended question; the initiating agent's conclusions in the history are claims to check, not established facts.

For `brief`, give the advisor a self-contained briefing containing:

- The precise question and decision to support.
- Relevant constraints, original evidence, and unresolved uncertainties.
- Options already considered and why any were ruled out; distinguish observations from the initiating agent's hypotheses.
- Relevant file paths and the requested review scope, including the base revision for a diff review. Confirm that the advisor can access the referenced resources; otherwise supply the necessary excerpts.
- An explicit request for a recommendation, reasoning, and material verification gaps.

When the user forwards another skill, such as `$fox-ask-advisor /unslop-risk`, instruct the advisor to load that skill through its available skill-loading mechanism and pass the remaining arguments as its input. The advisor executes the forwarded skill. If that skill requires edits or other actions outside analysis, report the conflict rather than expanding permission.

End the advisor's prompt, in either context, with:

```text
This is analysis only. Do NOT edit, create, or delete any files. Do NOT write code. Do NOT launch an advisor or any other subagent.
```

Use a verified read-only execution mode when the provider offers one. A prompt restriction alone is not a sandbox guarantee. Do not select a mode that silently broadens permissions.

## Launch, synthesize, and clean up

Launch the advisor with the prompt prepared for its context, using an advisor task name or `[Advisor] <topic>` title if supported. Reuse the current workspace when accessible; do not create a worktree for an analysis-only consultation. Use the runtime's supported completion events or bounded waits, then retrieve the complete response. Keep completion notifications enabled when configurable; avoid repeated status polling.

Read the complete response before synthesizing it. Distinguish the advisor's recommendation from your own assessment, state material disagreements and uncertainty, and do not imply that the advice was implemented or independently verified. In the final reply, report the configuration actually used in one line, giving the reason for the context and for any fallback, for example: `Advisor: <provider> / <model> / <effort> / context: brief (full-history fork cannot apply the resolved model)`. If the advisor runs the same model as the initiating agent, note that its value comes from a separate context rather than a stronger model. On an error or permission request, report the actual state rather than presenting a completed consultation.

Weigh the advice seriously:

- Override a specific claim only with an empirical failure after following it or primary-source evidence that contradicts it. A passing self-test is not such evidence; it may only show that the test does not check what the advice checks.
- When the advice conflicts with evidence you already hold, do not silently pick a side or switch direction. Send one follow-up to the same advisor that states the conflict ("I found X, you suggest Y; which constraint breaks the tie?"), then conclude. Report any disagreement that remains after that follow-up.

Reuse an advisor for follow-ups on the same approach: clarifications, the conflict follow-up above, or reporting what happened after acting on its advice. Send only what changed since the last consultation. Start a fresh advisor when the topic or required configuration changes, or when the consultation should challenge assumptions the two of you now share, such as a final pre-delivery review or a decision to change approach. Recheck that a retained configuration satisfies any new explicit preferences.

After a one-off consultation, read and retain the response, then, after any conflict follow-up, release the advisor using a documented close or archive operation if one exists. If the runtime provides no cleanup operation, leave the completed advisor idle rather than inventing one. If the user requests ongoing advice, retain its ID and resolved configuration for follow-ups, and release it when it is no longer needed. Never stop unrelated agents or delete the user's workspace.

## Session mode

`--mode session` makes the initiating agent consult an advisor on its own at checkpoints for the rest of the current task. Announce activation once, naming the checkpoints; do not ask for confirmation. The mode ends with `--mode off`, task completion, or a switch to an unrelated task. This mode is a prompt-level commitment: after context compaction it may be lost, and the user can re-enable it.

Consult at these checkpoints:

- After orientation and before substantive work. Reading files and gathering sources is orientation; writing, editing, and committing to an interpretation are substantive work.
- When stuck: recurring errors, an approach that is not converging, or results that do not fit.
- When considering a change of approach.
- When you believe the task is complete, before delivering it.

On tasks longer than a few steps, consult at least before committing to an approach and before declaring done. Skip consultation on short reactive steps where the tool output you just read dictates the next action.

Apply the reuse rules above: keep one advisor through an approach, and start a fresh one for the pre-delivery review and for a change of approach, resolving its context again. Checkpoint consultations do not need user confirmation; in your reply, briefly note the checkpoint, the advice, and what you decided. Release every retained advisor when the mode ends.
