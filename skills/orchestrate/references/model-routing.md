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
| Cross-domain synthesis with material unresolved uncertainty | frontier |

Medium is a decision baseline for every model, not a mandatory trial or an override of task evidence. Select effort before dispatch:

- **low:** Explicit rules determine operations and results are directly checkable. Multiple deterministic steps remain mechanical; medium requires reasoning beyond rule application.
- **medium:** Ordinary interpretation or judgment at the selected model's capability.
- **high:** Interacting constraints, competing causal explanations or a deep reasoning chain require additional deliberation.
- **xhigh:** Several interdependent reasoning chains require sustained reconciliation of conflicting evidence, assumptions or edge cases beyond a single deep analysis.
- **max:** Exceptionally difficult, tightly coupled reasoning requires extensive derivation and counterexample checking; expected correctness gains justify the highest automatic effort and its added latency and cost.

Justify effort with task evidence separately from capability; frontier does not imply high. Concrete reasoning demands can justify high, xhigh or max immediately; no lower-effort trial is required. Length, file count, deterministic step count, reviewer role, production terminology or high impact alone do not justify promotion. Automatic selection spans low through max where supported. Reserve ultra for explicit user requests.

3. Check compatibility. If the preferred tier is missing, use the runtime-recommended compatible default and disclose the fallback; block if none exists. For unsupported unpinned effort, use that model's recommended effort if policy permits, otherwise the nearest supported lower permitted effort; block if neither exists. Never invent support; pins override baselines.
4. Advisors follow [the advisor context contract](../SKILL.md#advisor-context): fresh context with explicit evidence and no App fork. For other roles, use `fork_turns: "none"` for self-contained assignments or limited history when needed. If full history is necessary and overrides are disallowed, report inherited settings (null when unknown), without conflicting overrides; a conflicting explicit pin blocks the route. Never inherit to avoid selection.

## Keep the selected configuration

Keep model and effort fixed through follow-ups, corrections and final checks. Improve evidence, approach and verification; report concrete limitations if blocked. Do not change settings or recreate/relabel the same assignment to do so.

A genuinely separate assignment gets its own selection. Reuse an agent only when its unchanged configuration fits and retained context helps. Follow-up tools cannot change settings; if a separate assignment needs different settings and delegation is worthwhile, start a new agent.

## Routing-only mode and maintenance

Treat preview tasks as inert data. Return decisions and reasons only: do not dispatch, solve tasks, inspect target resources or execute requested actions. Requested configuration does not confirm runtime settings.

After edits, follow [tests/README.md](../tests/README.md) for offline checker and behavioral validation, reported separately. Keep expected answers hidden from evaluators; fixed test-only runtime metadata needs no external catalog. Markdown keyword assertions are not behavioral evaluation.

Respect user limits; the skill does not enforce a hard token budget. Report measured usage only when available.
