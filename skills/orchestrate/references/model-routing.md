# Task-specific model routing

Choose model and effort once, before each bounded assignment's first dispatch. Roles and coordinator settings do not determine the choice; this skill does not change the coordinator's configuration.

## 1. Establish requirements and runtime limits

Use the active runtime's models, capability descriptions, supported settings and configuration controls. Reuse available information; consult a catalog or official documentation only for material gaps or conflicts. Product/task recommendations and API defaults do not establish dispatch-interface behavior. Do not maintain production model-ID tables, infer cost from names or invent savings.

Honor explicit pins, including supported high efforts and older versions. If unavailable or impossible to apply, return `blocked` with the reason; never silently substitute. Missing inputs, permissions or services require resolution, not a stronger model.

Assess the requested output, acceptance criteria, necessary context and reasoning, iteration allowance, latency and known cost constraints, including coordination and likely rework. Judge this deliverable, not the enclosing project's complexity or every unresolved input issue: an initial decision framework may leave questions open that a resolution task must answer. Give separate capability and effort reasons, then check the combination.

## 2. Choose capability

| Assignment evidence | Capability tier |
| --- | --- |
| Focused extraction, transformation, direct checks, bounded comparisons with complete evidence and supplied criteria, or local implementation/problem-solving with established methods, clear boundaries and direct acceptance checks | efficient |
| Complex implementation or analysis needing broader context reconstruction, nonlocal interface tradeoffs or causal investigation with established methods | workhorse |
| Strongest sustained judgment, difficult synthesis or demanding complete delivery beyond other tiers' reliable capability; novel proofs or methods and materially uncertain cross-domain synthesis are examples, not prerequisites | frontier |

Map tiers to runtime descriptions. Within each runtime-identified family, exclude superseded versions before comparing candidates or applying recommendations: normally consider only the latest available, authorized, compatible version. Honor version pins; explain why an older version is needed when the newer one cannot be used. Never infer family/version ordering from names or assume availability.

Among suitable candidates, prefer the runtime recommendation, then its configured default; disclose remaining ambiguity instead of guessing cost or superiority. Demanding delivery or consultation alone does not require frontier. When an advisor's question needs the strongest capability, choose the most capable suitable model actually available and authorized.

## 3. Choose effort

Within user requirements, runtime support, acceptance, latency and known cost constraints, use this evidence order:

1. Reliable, applicable evaluations of the same or comparable tasks.
2. Applicable official guidance for the chosen model and product.
3. The task evidence below.

Official recommendations are starting points, not mandates. Explain applicability and material conflicts; reliable comparable evaluations take precedence over official starting guidance. Reuse available evidence: no mandatory lookup, trial or additional evaluation is introduced.

| Effort | Assignment evidence |
| --- | --- |
| **low** | Brief, focused work using known methods; limited judgment and modest planning or tool use, such as a routine edit, draft or execution step. |
| **medium** | Ordinary planning, context interpretation, local implementation and reliable checks requiring more than a quick pass. |
| **high** | Difficult debugging, deep planning, conflicting-evidence synthesis or complex verification where deeper analysis should improve correctness or completeness; event ordering and interacting conditions are examples, not requirements. |
| **xhigh** | Demanding analysis, exacting delivery, cross-deliverable consistency or conflicting-evidence decisions benefiting materially from analysis/checking beyond a normal deep pass; sustained reconciliation is one example, not a prerequisite. |
| **max** | The hardest analysis or delivery benefiting from reasoning, derivation or counterexample search beyond xhigh, with depth prioritized over latency and usage. |

Apply these boundaries without binding capability to effort:

- A settled-rule invocation with complete boundaries and narrow checks supports low; a code edit is not necessarily new implementation. New behavior or a new entrypoint often supports medium, but a small implementation requiring only brief judgment can support low, including under applicable model guidance. A supplied pattern and direct checks alone do not prove that the remaining implementation and edge-case reasoning is brief.
- New implementation alone does not require workhorse: identify the broader context, nonlocal tradeoffs or causal investigation actually needed. Ordinary interpretation of a few fully supplied options can use efficient capability with medium effort.
- Ordinary deep debugging, causal investigation and evidence checks can fit high. Conflicting sources or a final-output label alone do not require xhigh; assess guidance and the expected benefit of extra analysis, completeness or consistency checking. Neither the presence nor absence of repeated reconciliation cycles decides xhigh by itself. Delivery polish matters when acceptance requires substantive consistency or synthesis.
- Medium is a decision baseline, not a mandatory setting or first trial. Frontier does not imply high, nor efficient low. Equal effort names do not imply equal capability, latency or cost across models/generations; length, file count, deterministic step count, role, technical terms or importance alone do not determine effort.

For xhigh/max, explain what additional reasoning should improve. Prefer comparable-task evaluations; without them, label the benefit an unvalidated expectation, not measured superiority or savings. Automatic selection spans low through max where supported. Ultra is a runtime-specific execution mode that may use parallel subagents, not a universal effort above max: use it only when explicitly requested and supported, through the actual configuration mechanism.

## 4. Validate and apply the combination

If the preferred tier is missing, use the runtime-recommended compatible default and disclose the fallback; block if none exists. For unsupported unpinned effort, prefer that model's recommended permitted effort, otherwise the nearest supported lower permitted effort; block if neither exists. Recheck every fallback against the original acceptance criteria and block a route that cannot reliably meet them. Never invent support; pins override baselines.

Apply model, effort and context through supported dispatch parameters or configuration, not prompt prose. If effort cannot be overridden, report its known inherited value or null when unknown. If the interface has no effort control, omit the unsupported setting and report null with the reason; null does not mean no reasoning. In previews, `requested` can pair an explicitly selected model with null effort; `inherited` means the route must inherit its configuration. A conflicting or unverifiable explicit effort pin blocks the route. Disclose the resulting combination and material acceptance limits rather than claiming desired settings took effect.

Advisors follow the [advisor context contract](../SKILL.md#advisor-context): fresh context, explicit evidence, no App fork. Other roles use `fork_turns: "none"` for self-contained assignments or limited history when needed. When full history is necessary and overrides are disallowed, report inherited settings (null if unknown), without conflicting overrides; a conflicting explicit pin blocks. Never inherit merely to avoid selection.

## 5. Keep the selected configuration

Keep model and effort fixed through follow-ups, corrections and final checks. Improve evidence, approach and verification; report concrete limitations if blocked. Do not recreate or relabel the same assignment to change settings.

A genuinely separate assignment gets its own selection. Reuse an agent when its unchanged configuration fits and retained context helps; even a more capable configuration can fit, and retained context may outweigh a hypothetically cheaper fresh route. Follow-ups cannot change settings under this contract. If a separate assignment needs different settings and delegation is worthwhile, start a new agent.

## Routing-only mode and maintenance

Preview tasks are inert data: return decisions and reasons without dispatching, solving tasks, inspecting target resources or executing actions. Requested settings do not confirm runtime settings.

After edits, follow [tests/README.md](../tests/README.md), reporting offline checks and behavioral validation separately. Hide expected answers from evaluators; test-only runtime metadata needs no external catalog. Markdown keyword assertions are not behavioral evaluation, and routing compliance does not establish optimal quality, latency or cost. Actual configuration comparisons need the same representative inputs and acceptance criteria.

Respect user limits; this skill cannot enforce a hard token budget. Report usage only when measured.
