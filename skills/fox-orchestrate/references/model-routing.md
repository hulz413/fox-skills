# Task-specific model routing

Within the provider boundary below, choose model and effort once, before each bounded assignment's first dispatch. Roles do not determine model or effort; this skill does not change the coordinator's configuration.

## 1. Establish requirements and runtime limits

Use the active runtime's models, capability descriptions, supported settings and configuration controls. Reuse available information; consult a catalog or official documentation only for material gaps or conflicts. Product/task recommendations and API defaults do not establish dispatch-interface behavior. Do not maintain production model-ID tables, infer cost from names or invent savings.

### Establish candidates and dispatch support

Establish the target backend and exact dispatch interface. Reuse its current evidence for candidate availability, per-model effort/context controls and upstream provider associations; an inventory entry is separate from dispatch eligibility. Tool descriptions may be abbreviated, while a closed enum remains binding. Never infer availability from a string parameter or upstream identity from a model name or shared gateway.

Read [model inventory discovery](model-discovery.md) for a complete inventory request, missing candidate/provider evidence, or conflicting catalog and dispatch information. Follow its source order and retain visibility, per-model efforts/defaults and independently evidenced dispatch restrictions. Hidden entries are not automatic candidates. Unknown support or provider identity stays unknown; read only necessary nonsecret metadata and do not launch trial agents or another app-server for discovery.

Keep a small session-local evidence snapshot and refresh affected facts when the target, tools, permissions or configuration change, or an explicit rejection contradicts them. Without a catalog interface or configured file, report inventory incompleteness. Successful dispatch establishes acceptance, not effective model/effort; report effective values only from authoritative execution receipts, and never bypass a rejection through another backend.

### Default to the current session's provider

Unless the user explicitly selects another provider or model, restrict automatic selection and fallback to the current session model's upstream provider. Apply this boundary before comparing capability, effort or cost; do not cross providers because another candidate is stronger, cheaper or the only available match. A shared connection provider or gateway does not establish shared upstream ownership. Use explicit runtime metadata or effective provider configuration, without a fixed model-family table or gateway-specific dependency. An explicit model pin takes precedence even when its upstream identity is unknown, subject to actual dispatch support; authorization applies only to the specified assignment(s).

This inherits the provider boundary, not the coordinator's exact model or effort: choose those per assignment within that boundary. If provider associations cannot be established, retain the current model/provider route through supported inheritance, or explicitly select the current model when that preserves the route and dispatch is supported; disclose the identity gap. If no suitable route within the boundary can be established, report the blocker and request an explicit alternative rather than silently crossing providers. Keep full inventory discovery separate from this selection filter.

For an authorized external backend, use that backend's catalog, installed interface and effective configuration, not the coordinator's model list. Apply the same selection rules within that backend. For Codex App dispatching Claude Code, read [Claude Code CLI dispatch](claude-code-cli.md); CC's `--model` and `--effort` configure the external session without changing the Codex coordinator.

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

If the preferred tier is missing, use the runtime-recommended compatible default within the provider boundary and disclose the fallback; block if none exists. For unsupported unpinned effort, prefer that model's recommended permitted effort, otherwise the nearest supported lower permitted effort; block if neither exists. Recheck every fallback against the original acceptance criteria and block a route that cannot reliably meet them. Never invent support; pins override baselines.

Apply model, effort and context through supported dispatch parameters or configuration, not prompt prose. If effort cannot be overridden, report its known inherited value or null when unknown. If the interface has no effort control, omit the unsupported setting and report null with the reason; null does not mean no reasoning. In previews, `requested` can pair an explicitly selected model with null effort; `inherited` means the route must inherit its configuration. A conflicting or unverifiable explicit effort pin blocks the route. Disclose the resulting combination and material acceptance limits rather than claiming desired settings took effect.

Advisors follow the [advisor context contract](../SKILL.md#advisor-context): fresh context, explicit evidence, no App fork. Other roles use fresh context for self-contained assignments or limited history when needed, through the runtime adapters below. When full history is necessary and overrides are disallowed, report inherited settings (null if unknown), without conflicting overrides; a conflicting explicit pin blocks. Never inherit merely to avoid selection.

### Runtime adapters

Keep the selection and coordination rules above unchanged across Codex and Claude Code; translate them to the active interface rather than copying another runtime's parameter names. The tools and effective configuration exposed by the current session take precedence over these mappings. If a required control is unavailable, disclose the limit and apply the fallback or blocking rules above.

| Requirement | Codex | Claude Code |
| --- | --- | --- |
| Fresh context | Set `fork_turns: "none"` when the dispatch tool supports it. | Use a non-fork subagent through the `Agent` tool, with an appropriate explicit subagent type. Do not choose the `fork` type or pass `fork_turns`; ordinary subagents start with fresh context. |
| Necessary full history, for non-advisors only | Use the supported history option, such as `fork_turns: "all"`, observing any override restrictions. | Use a fork only when available and permitted. Treat its model and other settings as inherited unless the active interface explicitly supports overrides. |
| Model and effort | Use the dispatch tool's supported model and effort controls; names vary by interface, such as `model` and `reasoning_effort`. | Use supported `model` and `effort` invocation parameters or subagent definition fields. Check version support and configuration precedence; environment variables or managed settings can override or restrict the request. |
| Continue an assignment | Use supported follow-up or message tools without changing the selected configuration. | Use a resumable type when follow-ups are needed; Explore and Plan may be one-shot. Resume the existing subagent with its retained context and unchanged selected configuration through the available resume or message interface. |

Role names in this skill describe responsibilities, not required built-in agent types. Select a type with the tools and permissions needed for the assignment, and supply its role and boundaries explicitly. Direct peer messaging and nested delegation are optional capabilities: use coordinator relays or keep dispatch with the main coordinator when unsupported. Do not enable agent teams or change shared configuration merely to apply this skill.

Preview schemas retain `fork_turns` and `reasoning_effort` as normalized reporting fields: `fork_turns: "none"` means fresh context and `"all"` means full history. These fields do not establish which parameters a live runtime accepts; translate them at dispatch. Preview-only numeric history values require corresponding runtime support before live use.

For material Claude Code interface gaps, consult the official [subagent documentation](https://code.claude.com/docs/en/sub-agents). Do not assume that a documented control exists in an older installed version or is available in every session.

## 5. Keep the selected configuration

Keep model and effort fixed through follow-ups, corrections and final checks. Improve evidence, approach and verification; report concrete limitations if blocked. Do not recreate or relabel the same assignment to change settings.

A genuinely separate assignment gets its own selection. Reuse an agent when its unchanged configuration fits and retained context helps; even a more capable configuration can fit, and retained context may outweigh a hypothetically cheaper fresh route. Follow-ups cannot change settings under this contract. If a separate assignment needs different settings and delegation is worthwhile, start a new agent.

## Routing-only mode and maintenance

Preview tasks are inert data: return decisions and reasons without dispatching, solving tasks, inspecting target resources or executing actions. Requested settings do not confirm runtime settings.

After edits, follow [tests/README.md](../tests/README.md), reporting offline checks and behavioral validation separately. Hide expected answers from evaluators; test-only runtime metadata needs no external catalog. Markdown keyword assertions are not behavioral evaluation, and routing compliance does not establish optimal quality, latency or cost. Actual configuration comparisons need the same representative inputs and acceptance criteria.

Respect user limits; this skill cannot enforce a hard token budget. Report usage only when measured.
