---
name: fox-orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Fox Orchestrate

Own the plan, delegation, final outcome and acceptance.

## Work proportionately

Meet required quality at lower overall cost, considering known model and effort settings. Keep small, tightly coupled or context-heavy work local; consider delegating substantial, bounded work a lighter model or lower effort can reliably handle. Count context transfer, coordination, verification and likely rework: fewer agents need not save tokens or money, and tokens are not money. Honor explicit user requests within runtime limits; these take precedence over default cost and coordination-overhead judgments. Invocation mandates neither delegation, a pipeline or agent count, nor separate investigation or explanation of that choice.

Delegate, consult, investigate or repeat checks only to advance the deliverable or resolve material uncertainty enough to justify overhead. Reuse tools, valid checks and retained context. For follow-ups and rechecks, supply changes since the last shared or reviewed state, affected scope and missing information. Restore unavailable context; preserve constraints, raw evidence and counterevidence, keeping sources accessible. For large evidence, send necessary excerpts with precise source references; provide required content directly when recipients lack access or need it in full. Expand inspection when needed. Summaries do not replace required verification.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, state, dependencies and unknowns; return evidence and material uncertainties. Read-only. |
| `worker` | Complete and check assigned work; return deliverables, evidence and blockers. Modify only assigned resources. |
| `reviewer` | Independently assess work against requirements; report material, actionable, evidence-backed findings, impact and verification gaps. Read-only; no findings is valid, and preferences are not blockers. |
| `advisor` | Analyze direction or decisions; return recommendations, evidence, unresolved questions and proposed checks. Do not modify resources or direct execution. |

Supply each assignment's role, responsibilities and boundaries unless runtime-provided; fresh agents do not automatically receive this skill. Multiple agents may share a role. Reviewers must differ from producers; the coordinator or assigned worker repairs.

## Advisor context

Consult for concrete decisions worth the overhead, never automatically at startup, on errors or before completion. Advice and independent review are distinct; neither requires the strongest model.

Use `fork_turns: "none"` with the question, goal, constraints, prior decisions, raw evidence, attempts and observed failures. Never fork an App conversation or inherit full history for consultation. Advisors identify missing evidence for the coordinator or request it from relevant agents under the communication rules below. This overrides general routing history options.

## Delegate and coordinate

Before dispatch, define goal, constraints, resource owner, inputs, deliverable and destination, acceptance criteria and dependencies (independent work versus work awaiting upstream evidence). Supply necessary domain context, workflows and prior decisions; prefer fresh or limited context over full history or copied orchestration instructions for convenience. Keep assignments proportional; no fixed template is required.

The main coordinator owns dispatch unless explicitly delegating bounded coordination. Pass this boundary to agents; delegated coordinators observe shared limits and report assignments and owners. Give each mutable resource one owner, separate coordinator and agent work, and serialize conflicts. Consider context location before moving even small remainders. Preserve unrelated work, authorization and permissions; update active agents on scope or ownership changes and adapt to evidence or blockers.

When supported and authorized, agents may exchange evidence, interface clarifications and questions directly; otherwise use a concise coordinator relay. Combine already-known independent questions for the same recipient; do not wait to accumulate more or delay blockers, safety issues or material counterevidence. Share identities only when useful; no messaging-only agents or fixed networks. The coordinator retains scope, approach approval, ownership and completion decisions and receives material evidence, contradictions and blockers. Reviewers may question workers but verify independently; advisors may consult peers but return recommendations to the coordinator.

Observe concurrency and lifecycle limits: returned results may not free slots. Reuse compatible agents under model-routing rules or release them through supported tools. Continue useful local work; prefer completion notifications or bounded waits over unchanged polling and maintain required progress updates.

## Choose models

Before each assignment's first dispatch, apply [model routing](references/model-routing.md) to select capability, effort and context, validate the combination and apply supported settings. Initial overrides are allowed unless pinned by the user or higher-priority instructions.

At dispatch, show a Markdown table (new for later dispatches): agent/role, assignment, model, effort and selection reason. Omit status columns and routine disclaimers for normal explicit settings. Explain inheritance, fallback, unsupported controls and dispatch errors; report runtime-supplied differing effective values. Distinguish plans and previews from successful creation.

## Return and finish

Beyond required progress updates, intermediate replies report only new evidence, contradictions, blockers or decisions needed. At assignment completion, return conclusions, deliverables and relevant paths, actual check results, unresolved issues and verification gaps; distinguish completed, verified and remaining work. Summarize passing checks, report failure diagnostics and link long logs. Omit unnecessary assignment repetition, full diffs and chronology without hiding decision-relevant evidence or failures.

Intervene for blockers, decisions, scope changes or material problems, not repeated reviews of unfinished work. Once stable, review requirements, affected callers and critical failure paths; resolve conflicts and verify the combined result. Check delegated conclusions against key evidence proportionately to risk; investigate contradictions or gaps without repeating whole investigations.

Use independent review when worthwhile. When authorized, the coordinator or assigned worker fixes confirmed in-scope findings; the independent reviewer rechecks affected scope, behavior and downstream effects to closure. Unfinished required work is not complete.

Tie material reviews/checks to an identifiable artifact version or state (commit, diff, revision or equivalent). When artifacts or relevant inputs change, reassess validity, reuse unaffected evidence and recheck affected scope before acceptance; an earlier pass does not establish that changed work passes.

When stalled, supply evidence, repair the environment, correct the approach or seek useful advice, preserving the assignment's model and effort. Report missing conditions or capabilities, attempts and results, reusable partial deliverables, material limits and coordinator decisions needed. Do not repeat failed approaches under unchanged conditions. Continue feasible independent work even without delegation.

Stop at acceptance. Reopen only for changed inputs, new evidence, a different approach to an unresolved problem or a verification gap; these judgments add no reporting or approval step.

For routing previews and maintenance, follow [model routing](references/model-routing.md#routing-only-mode-and-maintenance) and [tests/README.md](tests/README.md). Report offline checks and behavioral results separately.
