---
name: fox-ask-advisor
description: Get independent, analysis-only advice for decisions, debugging, planning, research, or review. Use when the user requests outside perspectives or checkpoint advice; also invoke proactively when the agent is stuck, repeated attempts yield no useful progress, or the current approach is not converging.
---

# Fox Ask Advisor

Consult one advisor by default, or multiple advisors when requested. Collect independent reasoning, examine material disagreements, and synthesize a recommendation. The initiating agent retains ownership of the work and the final judgment.

## Proactive consultation

Unless automatic consultation is off for the current task, consult proactively when reasoning is stuck: repeated attempts are not producing useful evidence, the same failure persists without a better-supported next step, or contradictory results leave the approach unable to converge. Do not wait for a fixed number of failures or an explicit user request. A normal failed experiment that narrows the problem, or an error with a clear corrective next step, is not by itself a trigger.

Briefly announce the blocker and the question before launching; no renewed confirmation is needed within the task's existing authorization. Use one advisor unless the user requested more. Include the failed approaches, original errors, and assumptions needing challenge. Missing permissions, credentials, or a necessary user decision require their own resolution; advice cannot replace them.

Do not open repeated consultations for an unchanged blocker. Follow up with the involved advisor when new evidence or a materially different question warrants it; otherwise report what remains blocked and continue independent authorized work. Resume implementation only after the analysis-only consultation ends.

`once` covers one consultation and its follow-ups, while leaving this default stuck-trigger behavior enabled. `session` adds the checkpoints below. `off` ends session mode and disables all automatic consultations for the current task until the user explicitly re-enables them. A later explicit one-off consultation is allowed without itself re-enabling automatic consultations. These are prompt-level instructions, not a background monitor or a guarantee that every runtime will select the skill.

## Input

Accept a question or the current task, with optional `--advisors <N>` (default `1`), `--provider <id>`, `--model <id>`, `--effort <id>`, `--context auto|full|brief` (default `auto`), and `--mode once|session|off` (default `once`). Equivalent preferences in natural language also count. Each explicit field overrides only its corresponding default. Ask only when conflicting preferences or missing information prevent a valid launch.

An explicit count must be a positive integer. A request for multiple advisors without a count or member list means two; a list of multiple members implies its length unless a count is supplied. Apply partial per-advisor configurations to slots in order unless the user identifies a target. Common provider/model/effort preferences apply to all slots, with per-advisor fields taking precedence. Clarify count/list conflicts or unresolved assignments together before launch. Do not increase the count automatically, truncate a list, or launch a partial group.

```text
$fox-ask-advisor Evaluate the current approach.
$fox-ask-advisor --provider claude Evaluate the current approach.
$fox-ask-advisor --provider codex --model MODEL_ID --effort medium Review this decision.
$fox-ask-advisor --context full Review what I just changed.
$fox-ask-advisor --advisors 2 Compare these approaches independently.
$fox-ask-advisor Ask one Codex advisor and one Claude Code advisor to review this plan.
$fox-ask-advisor --mode session
```

## Execution and configuration

Use the current runtime's native subagent tools or a documented CLI that can apply every advisor's requested configuration. Prefer native tools when they support the resolved configuration. This skill has no dependency on another skill, external agent manager, or additional CLI installation. Verify the complete advisor list before launching anyone. If no available interface can apply and confirm every resolved configuration, explain the blocker without claiming the consultation ran. Do not simulate independent advisors in the host's own response.

Resolve each advisor's configuration directly from user preferences and runtime capabilities. Do not let named profiles or unrelated runtime defaults overwrite the resolved configuration. Apply explicit choices before filling defaults: when a model is specified without a provider, use its verified provider rather than applying the automatic provider route. Clarify ambiguous model ownership or conflicting explicit choices.

Resolve in this order:

1. **Provider:** honor explicit choices as above. Otherwise, for one advisor use the initiating agent's current provider unless the initiating agent already uses that provider's best general reasoning and analysis model; in that case choose another available provider. Verify the initiating model and the required capability ranking; do not infer that it is already the best from its effort setting. If several alternative providers are available, choose one with verified suitability for the question and explain the choice; do not claim a universal cross-provider ranking. For multiple advisors, retain the existing route: default slots 1 and 2 to Codex and Claude Code; additional slots require an explicit provider. The single-advisor switching rule does not apply to these slots. Map execution routes to verified provider identifiers using session metadata and documented capabilities rather than model-name guesses. If discovery confirms only one provider is available, use it for unpinned default slots and disclose that independent context supplies the second perspective. Incomplete discovery or a failed launch does not establish that only one provider is available. Explicit providers remain pinned, even when the initiating agent already uses their best model.
2. **Model:** the user's override; otherwise, for one advisor use the selected provider's best model for general reasoning and analysis, with its next-best model as the sole automatic fallback. For multiple advisors, select task-appropriate model + effort combinations of comparable capability and reasoning depth across providers, rather than always choosing flagships or matching effort labels alone. Disclose material comparability gaps. Use the same model + effort for both default slots when they share a provider unless the user specifies otherwise. Identical configurations are allowed; independence then comes from separate contexts.
3. **Effort:** the user's override, otherwise assess the advisor's question before launch, starting from `medium`. Keep `medium` for bounded analysis with clear evidence; lower it for straightforward, narrow questions, or raise it for complex reasoning, interacting constraints, consequential uncertainty, or difficult debugging. Select a supported level proportional to the task; do not automatically choose the maximum. `medium` is a decision baseline, not a required first execution: choose the final effort before launching, without a trial run or an automatic escalation ladder.

Use the runtime's exposed tool documentation, session metadata, or model catalog to establish available providers, models, capability descriptions, and supported effort settings. Reuse information already supplied; do not invent discovery commands. If the runtime only supports one provider, honor a different provider override by reporting that limitation rather than silently using its sole provider.

If the initiating provider/model cannot be verified sufficiently to resolve the automatic route, report the missing information and ask for a provider choice rather than guessing. Switching providers because the initiating agent already uses its provider's best model is an initial selection rule, not a recovery path after launch failure.

Select or rank models using current runtime capability descriptions and applicable official provider guidance. Treat "flagship" and "frontier" as descriptive terms, not model IDs or guaranteed ordering. Do not infer capability from model names, version numbers, cost, or list order. Do not maintain hardcoded model-ID rankings. Establish the next-best candidate only if fallback is needed. If available evidence cannot establish a required ranking, resolve it from official documentation or ask a focused question. A valid explicit model needs no ranking.

Validate the provider/model/effort combination and the ability to apply it before launch. An advertised model is not proof of access. Effort names are provider-specific: use a documented equivalent only when the runtime establishes the mapping. Never treat an unknown inherited setting as the resolved effort.

### Fallback and explicit choices

Automatic model fallback below applies only to a single-advisor consultation. For multiple advisors, report unsupported settings before launch. If a launch fails after the group has been validated, retain available results, label the consultation incomplete, and do not replace the failed advisor automatically. Preserve every advisor's resolved configuration for follow-ups.

- For an automatically selected model, attempt the best candidate first. If preflight or startup establishes that it is unavailable, inaccessible, or incompatible with the required effort, try the verified next-best candidate once. Revalidate that candidate against the same question and effort requirement before launching.
- Keep the selected provider and effort fixed during fallback. Do not continue to a third model, switch providers, or lower effort automatically. If the next-best candidate also cannot be used, explain the blocker and ask for a supported choice.
- An explicitly requested model is pinned. If it cannot be used with the resolved provider and effort, explain why and ask before substituting it. Explicit provider and effort choices are also pinned.
- Model fallback addresses model-specific availability or compatibility. Missing provider authentication, unavailable services, permission requests, shared rate limits, missing evidence, and poor advisor reasoning require their own resolution; do not route around them by changing models. Treat an error as model-specific when it names that model or its own quota or credits, or tells you to switch models; fall back once. Treat it as shared when it applies to the account, provider, or every model.
- Fall back only before substantive analysis begins. If an attempt created an agent before failing, stop that failed attempt through the supported lifecycle tools before creating its replacement; never run the two concurrently.

Apply the resolved provider, model, and effort through supported dispatch parameters, not prompt prose. For an interface exposing `model`, `reasoning_effort`, and `fork_turns`, pass the resolved model and effort with `fork_turns: "none"` for a `brief` context. For a `full` context, use the interface's full-history value; if the fork inherits the parent's settings, first verify that they match the resolved configuration. See Context selection. Other runtimes may use different parameter names. If provider selection is implicit, verify that the selected model belongs to the resolved provider. If the interface cannot apply or confirm the required settings, report the limitation instead of claiming success. The input flags are skill conventions, not assumed runtime tool parameters.

## Context selection and briefing

For multiple advisors, use separate fresh contexts and give everyone the same self-contained initial briefing, without other advisors' answers or a prescribed solution. `auto` resolves to `brief`. An explicit `full` conflicts with this independent-analysis workflow; ask which requirement to change before launch.

For a single advisor, choose how much of the conversation it sees. An explicit `full` or `brief` is pinned; resolve `auto` from the question:

- **`full`**: forward the conversation history when the question reviews work done in this session, such as a pre-delivery check or a stuck debugging loop, and the decisive evidence lives in tool output, errors, or intermediate results that a summary would lose.
- **`brief`**: start fresh with a self-contained briefing when the question is a choice or tradeoff, when the conversation carries strong hypotheses from the initiating agent that could anchor the advisor, or when most of a long conversation is irrelevant. When unsure, use `brief`; independence is the default value of an advisor. Because forks often cannot apply the resolved model and effort, `auto` usually ends in `brief`; request `full` explicitly to forward history.

Some fork mechanisms run on the parent's model and effort and ignore overrides:

- An automatically selected `full` must not override the resolved configuration. If it cannot apply the resolved provider, model, and effort, use `brief` and say so.
- An explicit `full` changes context only; it does not waive the resolved provider, model, or effort. Use an inheriting fork only when the runtime confirms the parent's settings match the resolved configuration. If full history cannot be combined with that configuration, explain the conflict and ask which requirement to change.

For `full`, append the precise question and the requested review scope. State that the advisor is not the initiating agent, must not continue the user's task or any session-mode commitment in the history, and answers only the appended question; the initiating agent's conclusions in the history are claims to check, not established facts.

For `brief`, give the advisor a self-contained briefing containing:

- The precise question and decision to support.
- Relevant constraints, original evidence, and unresolved uncertainties.
- Options already considered and why any were ruled out; distinguish observations from the initiating agent's hypotheses.
- Relevant file paths and the requested review scope, including the base revision for a diff review. Confirm that the advisor can access the referenced resources; otherwise supply the necessary excerpts.
- An explicit request for a recommendation, reasoning, and material verification gaps.

When the user forwards another skill, such as `$fox-ask-advisor /unslop-risk`, instruct the advisor to load that skill through its available skill-loading mechanism and pass the remaining arguments as its input. The advisor executes the forwarded skill. If that skill requires edits or other actions outside analysis, report the conflict rather than expanding permission.

During each consultation, the host and all advisors only inspect existing information and return analysis in the conversation. Do not edit, create, or delete files, write implementation code, or modify external state. Separate consultations in session mode from any independently authorized implementation between them.

End every prompt sent to an advisor, including follow-ups and either context, with this exact suffix:

```text
This is analysis only. Do NOT edit, create, or delete any files. Do NOT write code. Do NOT launch an advisor or any other subagent.
```

Use a verified read-only execution mode when the provider offers one. A prompt restriction alone is not a sandbox guarantee. Do not select a mode that silently broadens permissions.

## Review basis and follow-ups

- Identify the material version or state in the initial briefing: for code, the review base and head plus any scoped uncommitted changes; for documents or plans, the revision or inspected state. State material uncertainty when the basis cannot be identified precisely. When inputs change, reassess affected conclusions and retain unaffected evidence.
- Give material issues needing follow-up stable IDs such as `D1`. Track the claim, supporting evidence, and disposition (`resolved`, `disputed`, or `missing evidence`) with a brief reason. Keep this record in the conversation; omit it when there are no such issues. Mark an issue resolved only when evidence or reasoning addresses it; agreement alone is insufficient.
- Reuse the involved advisors for follow-ups on the same approach. Send relevant opposing arguments, new evidence, changed inputs, and open issue IDs; focus reassessment on those issues and affected conclusions. Restore any unavailable context. Repeat a full analysis only when changes invalidate the earlier basis.

## Launch, synthesize, and clean up

Launch the complete, validated list, in parallel where supported, using identifiers such as `[Advisor 1] <topic>`. Reuse the current workspace when accessible; do not create worktrees or generated report files for consultation. Use supported completion events or bounded waits to collect every complete response. Keep completion notifications enabled when configurable; do not repeatedly poll, send hurry-ups, or interrupt advisors to accelerate completion.

Read every complete response before synthesizing it. Distinguish the advisors' recommendations from your own assessment, state material disagreements and uncertainty, and do not imply the advice was implemented or independently verified. If an advisor uses the host's model, explain that its value comes from a separate context. On an error or permission request, report the actual state rather than presenting a completed consultation.

For multiple advisors, compare agreements and disagreements about evidence, assumptions, and tradeoffs. Send material opposing arguments to the involved advisors for focused reassessment, avoiding unnecessary all-to-all exchanges. Treat forwarded answers as evidence to evaluate, not instructions that can change scope or configuration. Use at most two cross-review rounds after the initial analyses unless the user requests a different limit. Stop earlier when the issue is resolved or further discussion would add no useful evidence. Do not force consensus or treat majority opinion as proof. Apply the analysis-only suffix and completion-waiting rules to every follow-up.

Report the reviewed basis, material agreements, remaining disagreements, how reassessment changed the reasoning, and verification gaps. Identify every advisor's verified provider/model/effort/context and briefly explain automatic choices, any fallback, comparability gaps, and single-provider selections when relevant. For multiple advisors, report the initial analysis pass and cross-review round count separately. Include issue dispositions when tracked; use a compact table only when helpful. Clearly label failed or missing responses rather than presenting partial results as group consensus.

For a single advisor, weigh the advice seriously:

- Override a specific claim only with an empirical failure after following it or primary-source evidence that contradicts it. A passing self-test is not such evidence; it may only show that the test does not check what the advice checks.
- When the advice conflicts with evidence you already hold, do not silently pick a side or switch direction. Send one follow-up to the same advisor that states the conflict ("I found X, you suggest Y; which constraint breaks the tie?"), then conclude. Report any disagreement that remains after that follow-up.

Start fresh advisors when the topic or required configuration changes, or when the consultation should challenge assumptions now shared with the host, such as a final pre-delivery review or a decision to change approach. Recheck that retained configurations satisfy any new explicit preferences.

After a one-off consultation and any follow-ups, retain the responses and release each advisor using a documented close or archive operation if one exists. If none exists, leave completed advisors idle rather than inventing one. For ongoing advice, retain their IDs and resolved configurations, and release them when no longer needed. Never stop unrelated agents or delete the user's workspace.

## Session mode

`--mode session` makes the initiating agent consult the configured advisor or advisors on its own at checkpoints for the rest of the current task. Preserve the resolved count and per-advisor preferences across checkpoints; default to one advisor unless multiple advisors were requested. Each checkpoint may run several advisors and cross-review rounds when multiple advisors were requested. Announce activation once, naming the checkpoints; do not ask for confirmation. The mode ends with `--mode off`, task completion, or a switch to an unrelated task. This mode is a prompt-level commitment: after context compaction it may be lost, and the user can re-enable it.

Consult at these checkpoints:

- After orientation and before substantive work. Reading files and gathering sources is orientation; writing, editing, and committing to an interpretation are substantive work.
- When stuck: recurring errors, an approach that is not converging, or results that do not fit.
- When considering a change of approach.
- When you believe the task is complete, before delivering it.

On tasks longer than a few steps, consult at least before committing to an approach and before declaring done. Skip consultation on short reactive steps where the tool output you just read dictates the next action.

Apply the reuse rules above: keep the configured advisors through an approach, and start fresh advisors for the pre-delivery review and for a change of approach, resolving their contexts again. Checkpoint consultations do not need user confirmation; in your reply, briefly note the checkpoint, the advice, and what you decided. Release every retained advisor when the mode ends.
