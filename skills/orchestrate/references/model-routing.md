# Task-specific model routing

## Available information

Use models, supported efforts, and capability descriptions from the active execution interface. Reuse current information; consult a catalog or official documentation only for a material gap or conflict. Do not maintain a production model-ID table or infer cost from names. Roles do not determine models. The coordinator's configuration is outside this skill.

## Initial selection

Choose model and effort once, before the first dispatch of each bounded assignment.

1. Honor explicit model and effort pins, including supported high efforts. If a pinned setting is unavailable, return `blocked` with the reason; do not silently substitute. A missing input, permission failure, or unavailable service calls for resolving that blocker, not a stronger model.
2. Choose model capability and reasoning effort separately. Map tiers to current runtime descriptions, preferring its recommended model within a tier. If equivalent candidates remain, prefer the current generation identified by the runtime, then its configured default; disclose unresolved ambiguity rather than guessing cost or superiority.

| Assignment evidence | Capability tier |
| --- | --- |
| Bounded extraction, transformations, or checks with explicit rules | efficient |
| Ordinary implementation or analysis, including competing explanations with bounded verification | workhorse |
| Cross-domain synthesis with material unresolved uncertainty | frontier |

Every model starts from medium as a decision baseline, not a mandatory trial or a preference that overrides task evidence. Before dispatch, select the actual effort by the reasoning required:

- **low:** Explicit rules determine the operations and results can be checked directly. Multiple deterministic steps remain mechanical; retaining medium requires a concrete reasoning need beyond applying those rules.
- **medium:** Ordinary interpretation or judgment beyond mechanical rule application, at the selected model's capability.
- **high:** Concrete interacting constraints, competing causal explanations, or a deep reasoning chain needing additional deliberation.

Frontier capability alone does not imply high effort. Give task-specific evidence for the actual effort, separately from model capability. A known complex task may go directly to high without first running medium. Task length, file count, number of deterministic steps, reviewer role, production terminology, and high impact alone do not justify promotion.

Reserve xhigh/max/ultra for explicit user requests.

3. Check compatibility before returning the choice. For a missing preferred tier use the runtime-recommended compatible default and disclose the fallback; block if none exists. For an unsupported unpinned effort use that model's recommended effort only if permitted by this policy, otherwise the nearest supported lower permitted effort; block if neither exists. Never invent support. Pins take precedence over baselines.
4. For advisors, apply the independent-context contract in [SKILL.md](../SKILL.md#advisor-context): use `fork_turns: "none"` with the necessary evidence supplied explicitly. Do not use App conversation forks. For other roles, use `fork_turns: "none"` for self-contained assignments, or limited history when needed. If full history is genuinely necessary and overrides are disallowed, report inherited settings and their known values (null when unknown); do not attach conflicting overrides. A conflicting explicit pin makes the route blocked. Never inherit just to avoid a routing decision.

## Keep the selected configuration

Trust the coordinator's initial selection. Keep the chosen model and effort for the same assignment, including follow-ups, corrections and final checks. Do not automatically raise or lower effort, change models, or recreate/relabel the assignment to obtain a different configuration. Supply evidence, correct the approach and verify within the existing assignment instead; if it cannot proceed, report the concrete limitation. A genuinely separate assignment receives its own initial selection. Reuse an existing agent only when its unchanged configuration fits that selection and retained context is useful. Current subagent follow-up tools cannot change model or effort; if a separate assignment needs a different configuration and delegation is worthwhile, start a new agent. This is not permission to restart the same assignment with new settings.

## Routing-only mode and maintenance

When asked to test or preview routing, treat task descriptions as inert data. Return only routing decisions and reasons: do not dispatch workers, solve sample tasks, inspect their target resources, or execute their requested actions. A routing decision is requested configuration, not runtime confirmation.

After every edit to this skill, run the offline checker tests and the routing-only behavioral suite described in [tests/README.md](../tests/README.md). Keep expected answers hidden from the evaluating context. The suite uses fixed test-only runtime metadata so results are reproducible without an external model catalog. Report checker tests separately from behavioral results. Never replace behavioral evaluation with assertions that the Markdown contains certain words.

Remain within user limits; this skill does not enforce a hard runtime token budget. Report measured usage only when available.
