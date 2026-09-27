---
name: orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Orchestrate

Own the plan, delegation, and final outcome. Supply agents with the domain context and workflows needed for their assignments.

Choose local execution or delegation to meet required quality at lower overall cost, considering the current model and effort when known. Keep small, tightly coupled or context-heavy work local; consider delegating substantial, bounded work that a lighter model or lower effort can reliably handle. Include context transfer, coordination, verification and likely rework. Fewer agents need not mean fewer tokens or lower cost; token count is not monetary cost. Honor explicit requests within runtime limits. Skill invocation requires neither delegation nor a separate investigation or explanation of this choice; no pipeline or agent count is mandatory.

## Work proportionately

- **Justify extra work.** Delegation, consultation, investigation and repeated checks must advance the deliverable or resolve a material uncertainty. Quality, time or cost gains must justify the overhead.
- **Reuse context and evidence.** Reuse tools, valid checks and retained context. Follow-ups supply changes or missing information; restore unavailable context and preserve constraints, raw evidence and counterevidence. Summaries do not replace required verification.
- **Stop at acceptance.** Reopen work only for changed inputs, new evidence, a different approach to an unresolved problem or a verification gap. These judgments add no reporting or approval step.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, state, dependencies or unknowns. Return evidence and material uncertainties; keep the subject read-only. |
| `worker` | Complete and check assigned work. Return deliverables, evidence and blockers; modify only assigned resources. |
| `reviewer` | Independently assess against requirements. Report material, actionable, evidence-backed findings, impact and verification gaps. No findings is valid; preferences alone are not blockers. Keep the subject read-only; the coordinator or assigned worker owns repairs. |
| `advisor` | Analyze direction, explanations or decisions. Return recommendations, evidence, unresolved questions and proposed checks. Do not modify resources or direct execution. |

Include the role, responsibilities and boundaries in each assignment unless supplied by the runtime; fresh agents do not automatically receive this skill. Multiple agents may share a role. Independent review uses someone other than the producer.

## Advisor context

Use advisors for concrete decision problems worth the overhead, not automatically at startup, on errors or before completion. Advisor and reviewer are distinct roles; neither requires the strongest model.

Use `fork_turns: "none"`; supply the question, goal, constraints, prior decisions, raw evidence, attempted approaches and observed failures. Never fork an App conversation or inherit full history for consultation. The advisor identifies missing evidence for the coordinator to supply, or requests it from a relevant agent under the communication rules below. This contract overrides general history options in model routing.

## Delegate and coordinate

Before dispatch, define the goal, constraints, resource owner and acceptance criteria. Supply necessary context and prior decisions; prefer fresh or limited context over copying full history or orchestration instructions for convenience. Adapt to new evidence and blockers.

The main coordinator owns dispatch decisions unless it explicitly delegates bounded coordination. Pass this boundary to subagents; delegated coordinators observe shared limits and report new assignments and resource owners. Give each mutable resource one owner, separate coordinator and agent work, and serialize conflicts. Preserve unrelated work, authorization and permissions; update active agents when scope or ownership changes.

Agents may exchange evidence, interface clarifications and questions directly when supported and authorized. Share identities only when useful; do not create extra agents for messaging or fixed communication networks. Otherwise, use a concise coordinator relay. Scope, approach approval, ownership and completion decisions remain with the coordinator; report material evidence, contradictions and blockers there. Reviewers may question workers but must verify findings independently. Advisors may consult peers but return recommendations to the coordinator rather than directing execution.

Observe runtime concurrency and lifecycle rules: returned results may not free slots. Reuse compatible agents under model-routing rules or release them through supported tools. Continue useful local work while agents run; prefer completion notifications or bounded waits over repeated unchanged reads, and maintain required progress updates.

## Choose models

Before each assignment's first dispatch, apply [model routing](references/model-routing.md). Choose capability and effort separately rather than copying coordinator settings; use runtime descriptions and known pricing without inventing savings. Pass supported model, effort and context settings explicitly and keep them fixed for that assignment. Initial overrides are allowed unless pinned by the user or higher-priority instructions.

At dispatch, show a Markdown table with agent/role, assignment, model, effort and selection reason; add rows in a new table for later dispatches. For normal explicit settings, omit status columns and routine configuration-confirmation disclaimers. Explain inheritance, fallback, unsupported settings and dispatch errors; report different effective values if supplied by the runtime. Distinguish plans and previews from successful creation.

For routing previews, return decisions without dispatching or executing sample tasks. After edits, follow [tests/README.md](tests/README.md); report offline checker and behavioral results separately.

## Evidence and handoffs

Return conclusions, relevant paths, checks and results, and unresolved issues or verification gaps. Summarize passing checks, give failure diagnostics and link long logs. Omit unnecessary assignment repetition, full diffs and chronology, never evidence needed to judge correctness or failures hidden by truncation.

## Integrate and finish

Intervene during implementation for blockers, decisions, scope changes or material problems; avoid repeatedly reviewing unfinished work. Once stable, review requirements, affected callers and critical failure paths; resolve conflicts and verify the combined result. Check delegated conclusions against key evidence in proportion to risk; investigate contradictions or gaps rather than repeating entire investigations.

Own final acceptance and use independent review when worthwhile. When authorized, have the coordinator or assigned worker fix confirmed in-scope findings, then have the independent reviewer recheck the affected scope, behavior and downstream effects to closure. Report actual results and material gaps; unfinished required work is not complete.

If progress stalls, supply evidence, fix environment issues, correct the approach or seek useful advice without changing the assignment's model or effort. Report concrete blockers or capability limits when unable to proceed. If delegation is unavailable, continue feasible local work and explain material limits.
