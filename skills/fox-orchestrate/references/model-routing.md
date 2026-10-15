# Task-specific model routing

Within the provider boundary below, choose model and effort once, before each bounded assignment's first dispatch. Roles do not determine model or effort; this skill does not change the coordinator's configuration.

## 1. Establish requirements and runtime limits

Use the active runtime's models, capability descriptions, supported settings and configuration controls. Reuse available information; consult a catalog or official documentation only for material gaps or conflicts. Product/task recommendations and API defaults do not establish dispatch-interface behavior. Do not maintain production model-ID tables, infer cost from names or invent savings.

### Discover candidates and dispatch capabilities

Keep the observed model inventory separate from dispatch eligibility. Establish the execution backend and exact dispatch tool first; do not combine the coordinator's catalog with an external backend's capabilities. For Codex, use this source order, reusing current evidence already supplied by that same runtime:

1. Query the target running Codex runtime's read-only `model/list` through an available supported client/interface. For a complete inventory, follow every pagination cursor until exhausted; request hidden entries too when the interface supports it, retaining visibility separately. Do not equate the first page or picker-visible subset with all known models. Do not start another app-server and present its list as the current App's list.
2. If that interface is unavailable or leaves a material gap, read the model catalog referenced by the target's **effective** `model_catalog_json` configuration. Resolve the active config layers/profile and target home through available runtime evidence; never assume the default home, hard-code a catalog filename or require a particular gateway. If the effective path cannot be established, report that gap. Read only necessary model metadata, not credentials. Read all entries for a complete inventory, retaining hidden entries separately from visible candidates. An on-disk catalog may be older or newer than the running App's cached/filtered menu; label it as file evidence, not an exact UI inventory.
3. Check candidates against the current dispatch tool's schema and authoritative runtime validation rules, including model-specific backend, effort and context restrictions. Distinguish a closed enum or explicit exclusive allowlist from an abbreviated description. Codex may advertise only the first five overrides in `spawn_agent` while validating exact IDs against the full runtime catalog; absence from that description alone is not rejection evidence. When the target's validation contract confirms full-catalog lookup and a candidate meets its restrictions, retain it as eligible even if unadvertised. A generic string parameter alone proves only that an ID can be submitted, not availability. Catalog entries cannot widen a closed enum, and separate model/effort enums do not establish every Cartesian combination. If applicable validation rules cannot be confirmed, mark eligibility unconfirmed rather than unsupported.

Retain exact model IDs separately from display names and preserve each model's own effort list and default (`supportedReasoningEfforts` / `defaultReasoningEffort` in `model/list`, or `supported_reasoning_levels` / `default_reasoning_level` in a configured catalog). Missing effort metadata means unknown, not an empty list or permission to use another model's efforts. Keep catalog-declared efforts separate from narrower dispatch restrictions and actual execution receipts.

For provider discovery, distinguish the Codex connection provider from an upstream execution provider or route. Use explicit runtime metadata or the target's effective provider configuration, reading only nonsecret identifiers and necessary endpoint metadata. A configured provider is not proof of account access, and a gateway connection does not enumerate its upstream providers. A name, endpoint or ID prefix does not prove upstream provider, OAuth/API-key route, account or billing source. Record explicit model-provider associations only; otherwise keep the upstream unknown. Report configured providers separately from associations confirmed for discovered models, and state when a complete upstream provider inventory is unavailable. Do not require a gateway-specific API to fill that gap.

### Default to the current session's provider

Unless the user explicitly selects another provider or model, restrict automatic selection and fallback to the current session model's upstream provider. Apply this boundary before comparing capability, effort or cost; do not cross providers because another candidate is stronger, cheaper or the only available match. A shared connection provider or gateway does not establish shared upstream ownership. Use the provider evidence above, without a fixed model-family table or gateway-specific dependency. An explicit model pin takes precedence even when its upstream identity is unknown, subject to actual dispatch support; authorization applies only to the specified assignment(s).

This inherits the provider boundary, not the coordinator's exact model or effort: choose those per assignment within that boundary. If provider associations cannot be established, retain the current model/provider route through supported inheritance, or explicitly select the current model when that preserves the route and dispatch is supported; disclose the identity gap. If no suitable route within the boundary can be established, report the blocker and request an explicit alternative rather than silently crossing providers. Keep full inventory discovery separate from this selection filter.

For each inventory entry, retain source, exact ID, display name, visibility, known provider associations, per-model efforts/default, and independent dispatch facts: advertised in tool description, eligible/ineligible/unconfirmed under the validation contract (with evidence), and execution verified or not. Inventory requests include all discovered entries; selection still honors visibility, authorization, eligibility, inheritance, fallback and pins. Hidden entries must not silently become automatic selection candidates. Do not remove or block a model solely because an abbreviated tool description omits it.

Keep a small session-local evidence snapshot including backend/target, dispatch interface, inventory completeness and source, provider evidence, model/effort/context restrictions, and unresolved conflicts. Reuse it for the same unchanged target; refresh affected evidence when tools, target, permissions or configuration change, or an explicit dispatch rejection contradicts it. Do not create a persistent model registry, background updater or trial-agent discovery loop. With no catalog interface or configured file, dispatch declarations establish only their explicitly evidenced candidates; disclose inventory incompleteness. A skill cannot supply a runtime interface the host does not expose.

A successful dispatch establishes acceptance, not necessarily the effective model or effort. Report effective values only when supplied by an authoritative execution receipt; otherwise distinguish requested settings from unknown effective settings. Never reinterpret a rejection as permission to bypass the tool through another backend.

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
