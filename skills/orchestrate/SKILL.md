---
name: orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Orchestrate

Own the plan, delegation and final outcome. Supply each agent with the domain context and workflows its assignment needs.

## Work proportionately

Choose local work or delegation to meet required quality at lower overall cost, considering the current model and effort when known. Keep small, tightly coupled or context-heavy work local; consider delegating substantial, bounded work a lighter model or lower effort can reliably handle. Count context transfer, coordination, verification and likely rework; fewer agents need not use fewer tokens or cost less; tokens are not money. Honor explicit requests within runtime limits. Invoking this skill mandates neither delegation, a pipeline or agent count, nor a separate investigation or explanation of that choice.

Delegation, consultation, investigation and repeated checks must advance the deliverable or resolve material uncertainty, with gains justifying overhead. Reuse tools, valid checks and retained context. Follow-ups supply changes or missing information; restore unavailable context and preserve constraints, raw evidence and counterevidence. Summaries do not replace required verification.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, state, dependencies and unknowns; return evidence and material uncertainties. Read-only. |
| `worker` | Complete and check assigned work; return deliverables, evidence and blockers. Modify only assigned resources. |
| `reviewer` | Independently assess work against requirements; report material, actionable, evidence-backed findings, impact and verification gaps. Read-only; no findings is valid, and preferences are not blockers. |
| `advisor` | Analyze direction or decisions; return recommendations, evidence, unresolved questions and proposed checks. Do not modify resources or direct execution. |

Include the role, responsibilities and boundaries in each assignment unless the runtime supplies them; fresh agents do not automatically receive this skill. Multiple agents may share a role. A reviewer must be someone other than the producer; the coordinator or assigned worker owns repairs.

## Advisor context

Consult an advisor for a concrete decision worth the overhead, not automatically at startup, on errors or before completion. Advice and independent review are distinct assignments; neither mandates the strongest model.

Use `fork_turns: "none"`, supplying the question, goal, constraints, prior decisions, raw evidence, attempted approaches and observed failures. Never fork an App conversation or inherit full history for consultation. The advisor identifies missing evidence for the coordinator to supply, or requests it from a relevant agent under the communication rules below. This overrides general history options in model routing.

## Delegate and coordinate

Before dispatch, define the goal, constraints, resource owner, necessary inputs, deliverable and destination, and acceptance criteria. Identify dependencies: what can proceed independently and what must await upstream evidence. Supply necessary context and prior decisions, preferring fresh or limited context over full history or copied orchestration instructions for convenience. Keep assignments proportional; no fixed template is required.

The main coordinator owns dispatch unless it explicitly delegates bounded coordination. Pass this boundary to agents; delegated coordinators observe shared limits and report assignments and resource owners. Give each mutable resource one owner, separate coordinator and agent work, and serialize conflicts. Consider where necessary context resides before moving even a small remainder. Preserve unrelated work, authorization and permissions; update active agents when scope or ownership changes and adapt to new evidence or blockers.

When supported and authorized, agents may exchange evidence, interface clarifications and questions directly; otherwise use a concise coordinator relay. Share identities only when useful, without extra agents for messaging or fixed networks. Scope, approach approval, ownership and completion decisions stay with the coordinator, who receives material evidence, contradictions and blockers. Reviewers may question workers but verify findings independently; advisors may consult peers but return recommendations to the coordinator.

Observe runtime concurrency and lifecycle limits; returned results may not free slots. Reuse compatible agents under model-routing rules or release them through supported tools. Continue useful local work while agents run; prefer completion notifications or bounded waits over unchanged polling and maintain required progress updates.

## Choose models

Before each assignment's first dispatch, apply [model routing](references/model-routing.md) to select capability, effort and context, check their combined suitability and apply supported settings. Initial overrides are allowed unless pinned by the user or higher-priority instructions.

At dispatch, show a Markdown table with agent/role, assignment, model, effort and selection reason; use a new table for later dispatches. For normal explicit settings, omit status columns and routine configuration disclaimers. Explain inheritance, fallback, unsupported controls and dispatch errors; report different effective values when supplied by the runtime. Distinguish plans and previews from successful creation.

## Return and finish

Return conclusions, deliverables and relevant paths, checks and results, unresolved issues and verification gaps. Distinguish completed, verified and remaining work. Summarize passing checks, give failure diagnostics and link long logs; omit unnecessary assignment repetition, full diffs and chronology without hiding decision-relevant evidence or failures through truncation.

Intervene for blockers, decisions, scope changes or material problems rather than repeatedly reviewing unfinished work. Once stable, review requirements, affected callers and critical failure paths; resolve conflicts and verify the combined result. Check delegated conclusions against key evidence proportionately to risk, investigating contradictions or gaps without repeating whole investigations.

Own final acceptance and use independent review when worthwhile. When authorized, the coordinator or assigned worker fixes confirmed in-scope findings; the independent reviewer then rechecks affected scope, behavior and downstream effects to closure. Report actual results and material gaps; unfinished required work is not complete.

When stalled, supply evidence, fix environment issues, correct the approach or seek useful advice while preserving the assignment's model and effort. Report missing conditions or capabilities, attempted approaches and results, reusable partial deliverables and decisions needed from the coordinator. Do not repeat a failed approach under unchanged conditions. Continue feasible independent work, including when delegation is unavailable, and explain material limits.

Stop at acceptance. Reopen work only for changed inputs, new evidence, a different approach to an unresolved problem or a verification gap; these judgments add no reporting or approval step.

For routing previews and skill maintenance, follow [model routing](references/model-routing.md#routing-only-mode-and-maintenance) and [tests/README.md](tests/README.md). Report offline checks and behavioral results separately.
