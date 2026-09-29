# Task-specific model routing

## Available information

Use models, supported efforts and capability descriptions from the active interface. Reuse current information; consult a catalog or official documentation only for material gaps or conflicts. Do not maintain production model-ID tables or infer cost from names. Roles do not determine models; this skill does not change the coordinator's configuration.

## Initial selection

Choose model and effort once, before each bounded assignment's first dispatch.

1. Honor explicit pins, including supported high efforts. If unavailable, return `blocked` with the reason; never silently substitute. Resolve missing inputs, permissions or unavailable services rather than choosing a stronger model.
2. Choose capability and effort separately. Map tiers to runtime descriptions and prefer its recommended model within the tier. Break equivalent ties by runtime-identified current generation, then configured default; disclose remaining ambiguity instead of guessing cost or superiority.

| Assignment evidence | Capability tier |
| --- | --- |
| Bounded extraction, transformations, or checks with explicit rules | efficient |
| Ordinary implementation or analysis, including competing explanations with bounded verification | workhorse |
| Tasks requiring new methods, proofs or explanations where established approaches are insufficient for a reliable conclusion, even within one domain; or cross-domain synthesis with material unresolved uncertainty | frontier |

Select effort for the chosen model by the reasoning needed to complete the assignment:

| Effort | Assignment evidence |
| --- | --- |
| **low** | Known rules largely determine the operations: extract, transform, replace or directly verify information, without substantive judgment between alternatives. |
| **medium** | The goal and contract are clear. Understand context, choose a local approach and handle ordinary edge cases; issues can generally be resolved individually and checked separately. |
| **high** | Correctness depends on interactions between conditions or event ordering. Compare competing explanations, trace state changes or construct counterexamples; checking each condition separately is insufficient. |
| **xhigh** | Conclusions from several reasoning chains depend on one another. Resolving one subproblem changes another, requiring repeated reconciliation of assumptions, approaches and counterexamples. |
| **max** | The core problem requires extended derivation or broad counterexample search. Established patterns and local checks are insufficient to establish a conclusion, and additional reasoning is expected to materially improve correctness. |
| **ultra** | Only when explicitly requested by the user and supported by the runtime. |

Use medium as the decision baseline, then select directly from task evidence; no lower-effort trial is required. Justify effort separately from model capability: frontier does not imply high. Length, file count, deterministic step count, reviewer role, technical terminology or importance alone do not determine effort. Automatic selection spans low through max where supported.

3. Check compatibility. If the preferred tier is missing, use the runtime-recommended compatible default and disclose the fallback; block if none exists. For unsupported unpinned effort, use that model's recommended effort if policy permits, otherwise the nearest supported lower permitted effort; block if neither exists. Never invent support; pins override baselines.
4. Advisors follow [the advisor context contract](../SKILL.md#advisor-context): fresh context with explicit evidence and no App fork. For other roles, use `fork_turns: "none"` for self-contained assignments or limited history when needed. If full history is necessary and overrides are disallowed, report inherited settings (null when unknown), without conflicting overrides; a conflicting explicit pin blocks the route. Never inherit to avoid selection.

## Keep the selected configuration

Keep model and effort fixed through follow-ups, corrections and final checks. Improve evidence, approach and verification; report concrete limitations if blocked. Do not change settings or recreate/relabel the same assignment to do so.

A genuinely separate assignment gets its own selection. Reuse an agent only when its unchanged configuration fits and retained context helps. Follow-up tools cannot change settings; if a separate assignment needs different settings and delegation is worthwhile, start a new agent.

## Routing-only mode and maintenance

Treat preview tasks as inert data. Return decisions and reasons only: do not dispatch, solve tasks, inspect target resources or execute requested actions. Requested configuration does not confirm runtime settings.

After edits, follow [tests/README.md](../tests/README.md) for offline checker and behavioral validation, reported separately. Keep expected answers hidden from evaluators; fixed test-only runtime metadata needs no external catalog. Markdown keyword assertions are not behavioral evaluation.

Respect user limits; the skill does not enforce a hard token budget. Report measured usage only when available.
