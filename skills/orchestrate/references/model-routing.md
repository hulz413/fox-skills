# Task-specific model routing

## Available information

Use available models, capability descriptions, supported settings and configuration entrypoints from the active runtime. Reuse current information; consult a catalog or official documentation only for material gaps or conflicts. Product/task recommendations and API defaults serve different purposes; neither proves which settings the dispatch interface applies. Do not maintain production model-ID tables or infer cost from names. Roles do not determine models; this skill does not change the coordinator's configuration.

## Initial selection

Choose model and effort once, before each bounded assignment's first dispatch.

1. Honor explicit pins, including supported high efforts. If unavailable or impossible to apply, return `blocked` with the reason; never silently substitute. Resolve missing inputs, permissions or unavailable services rather than choosing a stronger model.
2. Assess the assignment's output, acceptance criteria, necessary context and reasoning, iteration allowance, latency tolerance and known cost constraints. Judge the reasoning needed for the requested deliverable, not the enclosing project's complexity or every unresolved issue in the inputs. An initial decision framework may leave identified questions open; a request to resolve those questions requires a different depth of work. Choose capability and effort with separate reasons, then check the combination against those requirements, including coordination and likely rework.

| Assignment evidence | Capability tier |
| --- | --- |
| Focused extraction, transformation, direct checks, bounded option comparisons using supplied criteria and complete evidence, or local implementation and problem-solving with established methods, clear boundaries and directly checkable acceptance | efficient |
| Ordinary complex implementation or analysis requiring reconstruction of broader context, nonlocal interface tradeoffs or causal investigation with established methods | workhorse |
| Work needing the strongest sustained judgment, difficult synthesis or demanding complete delivery beyond the other tiers' reliable capability; novel methods or proofs and materially uncertain cross-domain synthesis are examples, not prerequisites | frontier |

Map tiers to runtime descriptions. Within each runtime-identified model family, normally consider only its latest available, authorized, compatible version; exclude superseded versions before comparing candidates or applying recommendations. Honor an explicit older-version pin. If a newer version cannot be used, disclose why an older version is needed; never infer family/version ordering from names alone or assume availability. Among the remaining suitable candidates, prefer the runtime recommendation, then its configured default; disclose remaining ambiguity instead of guessing cost or superiority. Demanding delivery alone does not require frontier if another tier reliably meets acceptance. Advisors use the same criteria: ordinary consultation need not use frontier; when the question needs the strongest capability, choose the most capable suitable model actually available and authorized.

Select effort for the chosen model within explicit user requirements, runtime support, acceptance, latency and known cost constraints. Prefer reliable, applicable evaluations of the same or comparable tasks, then applicable official guidance for this model and product, then the generic task evidence below. Official recommendations are starting points, not mandatory settings. Explain applicability and material conflicts; when reliable evaluations disagree with official starting guidance, use the evaluation-supported configuration and explain why. Use already available evidence; this priority adds no mandatory lookup or trial.

| Effort | Assignment evidence |
| --- | --- |
| **low** | A brief, focused task using known methods; limited judgment, modest planning or tool use suffices, such as a routine edit, draft or execution step. |
| **medium** | Ordinary planning, context interpretation, local implementation and reliable checks, including clear scoped work that needs more than a quick pass. |
| **high** | Difficult debugging, deep planning, conflicting-evidence synthesis or complex verification where a deeper pass is expected to improve correctness or completeness. Interacting conditions and event ordering are examples, not requirements. |
| **xhigh** | Demanding analysis, exacting complete delivery, cross-deliverable consistency or decisions from conflicting evidence where extended analysis, checking or synthesis is expected to materially improve the result beyond a normal deep pass. Sustained reconciliation cycles are one example, not a prerequisite. |
| **max** | The hardest analysis or delivery where extended reasoning, derivation or counterexample search is expected to improve on xhigh, and depth takes priority over latency and usage. |

Applying a settled rule or reusing already specified behavior with complete input/output boundaries and narrow checks supports low, including edits to an existing display or invocation. A code edit alone is not new implementation. New implementation alone does not require workhorse capability: identify the broader context reconstruction, nonlocal tradeoffs or causal investigation actually needed before selecting that tier. Developing new behavior or connecting a new entrypoint often supports medium when ordinary contract and edge-case reasoning is needed; a small implementation needing only brief limited judgment can still support low, including when applicable model guidance recommends it. A supplied pattern, complete contract and direct checks do not alone establish that new behavior needs only a brief pass; assess the remaining implementation and edge-case reasoning rather than assuming it is a settled-behavior invocation. Ordinary interpretation of a few fully supplied options also supports medium effort but remains efficient capability; it does not by itself require workhorse. Ordinary deep debugging, causal investigation and evidence checks can fit high. Conflicting sources or a final-output label alone do not require xhigh; choose it when applicable guidance or expected gains from additional analysis, completeness or consistency checking justify the extra effort, without requiring repeated reasoning cycles. Their absence alone cannot justify ruling out xhigh; compare the expected additional benefit against the assignment requirements.

Use medium as a decision baseline, not an execution default or a required first run. Apply the evidence and guidance priority above directly before dispatch. Equal effort names do not imply equal capability, latency or cost across models or generations. No lower-effort trial is required. Frontier does not imply high, and efficient does not imply low. Length, file count, deterministic step count, role, technical terminology or importance alone do not determine effort. Delivery polish matters when acceptance needs substantive consistency or synthesis, not merely because an output is called final.

For xhigh/max, state what additional reasoning should improve. Prefer available evaluations of comparable tasks; without them, describe the choice as an unvalidated expectation, not measured superiority or savings. No extra evaluation is required for each dispatch. Automatic effort selection spans low through max where supported.

Ultra is a runtime-specific execution mode that may use parallel subagents, not a universal next reasoning level above max. Select it only when explicitly requested and supported; use the runtime's actual configuration mechanism, without assuming every platform exposes it as an effort value.

3. Check compatibility and configuration controls. If the preferred tier is missing, use the runtime-recommended compatible default and disclose the fallback; block if none exists. For unsupported unpinned effort, use that model's recommended effort if policy permits, otherwise the nearest supported lower permitted effort; block if neither exists. After any model or effort fallback, reassess the resulting combination against the original acceptance criteria. If it cannot reliably meet them, report the capability limit and block that route rather than dispatch merely because the settings are supported. Never invent support; pins override baselines.

   Apply model and effort through supported dispatch parameters or agent configuration; prompt prose does not set them. If effort cannot be overridden, disclose inheritance and report a known inherited value, otherwise null. If the model/interface has no configurable effort, omit the unsupported setting and report null with the reason; null does not mean no reasoning. In routing previews, `requested` can therefore pair an explicitly selected model with a null effort; `inherited` denotes a route that must inherit its configuration. A conflicting or unverifiable explicit effort pin blocks the route. Disclose the resulting combination and any material acceptance limitation rather than claiming the desired setting took effect.
4. Advisors follow [the advisor context contract](../SKILL.md#advisor-context): fresh context with explicit evidence and no App fork. For other roles, use `fork_turns: "none"` for self-contained assignments or limited history when needed. If full history is necessary and overrides are disallowed, report inherited settings (null when unknown), without conflicting overrides; a conflicting explicit pin blocks the route. Never inherit to avoid selection.

## Keep the selected configuration

Keep model and effort fixed through follow-ups, corrections and final checks. Improve evidence, approach and verification; report concrete limitations if blocked. Do not change settings or recreate/relabel the same assignment to do so.

A genuinely separate assignment gets its own selection. Reuse an agent only when its unchanged configuration fits and retained context helps; a more capable configuration can still fit, and retained context can outweigh the benefit of a fresh cheaper route. Follow-up tools cannot change settings under this contract; if a separate assignment needs different settings and delegation is worthwhile, start a new agent.

## Routing-only mode and maintenance

Treat preview tasks as inert data. Return decisions and reasons only: do not dispatch, solve tasks, inspect target resources or execute requested actions. Requested configuration does not confirm runtime settings.

After edits, follow [tests/README.md](../tests/README.md) for offline checker and behavioral validation, reported separately. Keep expected answers hidden from evaluators; fixed test-only runtime metadata needs no external catalog. Markdown keyword assertions are not behavioral evaluation. Routing compliance does not establish optimal task quality, latency or cost; use the same representative inputs and acceptance criteria when comparing actual configurations.

Respect user limits; the skill does not enforce a hard token budget. Report measured usage only when available.
