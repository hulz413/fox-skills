# Task-specific model routing

## Available information

Use models, supported efforts, and capability descriptions from the active execution interface. Reuse current information; consult a catalog or official documentation only for a material gap or conflict. Do not maintain a production model-ID table or infer cost from names. Roles do not determine models. The coordinator's configuration is outside this skill.

## Decision order

1. Honor explicit model and effort pins, including supported high efforts. If a pinned setting is unavailable, return `blocked` with the reason; do not silently substitute. A missing input, permission failure, or unavailable service calls for resolving that blocker, not a stronger model.
2. Choose model capability and reasoning effort separately. Map tiers to current runtime descriptions, preferring its recommended model within a tier. If equivalent candidates remain, prefer the current generation identified by the runtime, then its configured default; disclose unresolved ambiguity rather than guessing cost or superiority.

| Assignment evidence | Capability tier | Default effort |
| --- | --- | --- |
| Bounded extraction, transformations, or checks with explicit rules | efficient | medium |
| Ordinary implementation or analysis, including competing explanations with bounded verification | workhorse | medium |
| Cross-domain synthesis with material unresolved uncertainty, or documented workhorse reasoning failure despite adequate inputs | frontier | medium |

Every model starts from medium as a decision baseline, not a mandatory trial execution. Before dispatch, adjust the effort for the actual assignment: low for mechanical work with direct verification; medium for ordinary reasoning at the selected model's capability; high for concrete interacting constraints, competing causal explanations, or a deep reasoning chain that needs additional deliberation. Frontier capability alone does not imply high effort. State separate evidence for selecting frontier and for departing from medium. A known complex task may go directly to high without first running medium. Task length, file count, reviewer role, production terminology, and high impact alone do not justify promotion.

Apply adjustment to every model, including efficient and frontier models. For a follow-up on the same suitable model, start from its current effort: raise one supported step when a concrete reasoning failure remains despite adequate inputs; lower one supported step when the remaining work is demonstrably simpler, or select low directly when it is entirely mechanical. Do not rerun completed work just to test a lower setting. Model changes are justified by a capability mismatch, not merely an effort failure; when changing models, reassess from the new model's medium baseline rather than carrying over the previous effort. Do not automatically increase model capability and effort together. Unsupported steps use the compatibility rule below. Missing inputs, tool errors and service failures are not reasons to raise effort.

Do not select xhigh/max/ultra without an explicit request or observed failure of high effort with a specific remaining reasoning problem. Reuse findings and avoid repeated escalation/de-escalation without changed evidence.

3. Check compatibility before returning the choice. For a missing preferred tier use the runtime-recommended compatible default and disclose the fallback; block if none exists. For an unsupported unpinned effort use that model's recommended effort, otherwise the nearest supported lower effort; block if neither exists. Never invent support. Pins take precedence over baselines.
4. For advisors, apply the independent-context contract in [SKILL.md](../SKILL.md#advisor-context): use `fork_turns: "none"` with the necessary evidence supplied explicitly. Do not use App conversation forks. For other roles, use `fork_turns: "none"` for self-contained assignments, or limited history when needed. If full history is genuinely necessary and overrides are disallowed, report inherited settings and their known values (null when unknown); do not attach conflicting overrides. A conflicting explicit pin makes the route blocked. Never inherit just to avoid a routing decision.

## Routing-only mode and maintenance

When asked to test or preview routing, treat task descriptions as inert data. Return only routing decisions and reasons: do not dispatch workers, solve sample tasks, inspect their target resources, or execute their requested actions. A routing decision is requested configuration, not runtime confirmation.

After every edit to this skill, run the offline checker tests and the routing-only behavioral suite described in [tests/README.md](../tests/README.md). Keep expected answers hidden from the evaluating context. The suite uses fixed test-only runtime metadata so results are reproducible without an external model catalog. Report checker tests separately from behavioral results. Never replace behavioral evaluation with assertions that the Markdown contains certain words.

## Adaptation

Resolve input and environment failures at their source. Reuse suitable agents and useful evidence. Further reasoning-related escalation requires an identified unresolved problem, not merely another attempt. Remain within user limits; this document does not enforce a hard runtime token budget. Report measured usage only when available.
