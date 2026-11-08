---
name: fox-orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Fox Orchestrate

Own the plan, delegation, final outcome and acceptance.

Use the host's native subagents by default. When Claude Code CLI is requested or already authorized as the execution backend, follow [Claude Code CLI dispatch](references/claude-code-cli.md) to coordinate it from Codex App through the available command tool. The same roles, routing, ownership and acceptance rules apply; a CLI worker is an external process, not a Codex native subagent.

## Work proportionately

Meet required quality at lower overall cost, considering known model and effort settings. Keep small, tightly coupled or context-heavy work local; consider delegating substantial, bounded work when a lighter model or lower effort can reliably handle it, or to isolate large temporary logs or exploration results from the main context. Count dispatch, context transfer, coordination, verification and likely rework: fewer agents need not save tokens or money, and tokens are not money. Honor explicit user requests within runtime limits; these take precedence over default cost and coordination-overhead judgments. Invocation mandates neither delegation, a pipeline or agent count, nor separate investigation or explanation of that choice.

Delegate, consult, investigate or repeat checks only to advance the deliverable or resolve material uncertainty enough to justify overhead. Reuse tools, valid checks and retained context. For follow-ups and rechecks, supply changes since the last shared or reviewed state, affected scope and missing information. Restore unavailable context; preserve constraints, raw evidence and counterevidence, keeping sources accessible. When recipients can read a source, pass a precise pointer (path, commit, link or query) instead of restating its content. For large evidence, prefer targeted queries and bounded reads before loading it into context; send necessary excerpts with precise source references and provide required content directly when recipients lack access or need it in full. When limiting tool output, retain the original command's exit status and necessary failure diagnostics. Expand inspection when needed. Summaries do not replace required verification.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, state, dependencies and unknowns; return evidence and material uncertainties. Read-only. |
| `worker` | Complete and check assigned work; return deliverables, evidence and blockers. Modify only assigned resources. |
| `reviewer` | Independently assess work against requirements; report material, actionable, evidence-backed findings, impact and verification gaps. Read-only; no findings is valid, and preferences are not blockers. |
| `advisor` | Analyze direction or decisions; return recommendations, evidence, unresolved questions and proposed checks. Do not modify resources or direct execution. |

Supply each assignment's role, responsibilities and boundaries unless runtime-provided; fresh agents do not automatically receive this skill. Multiple agents may share a role. Reviewers must differ from producers; the coordinator or assigned worker repairs.

## Advisor context

Consult for concrete decisions worth the overhead, never automatically at startup, on errors or before completion. Advice and independent review are distinct; apply the role defaults under Choose models below.

Start advisors with fresh context using the active runtime's [context controls](references/model-routing.md#runtime-adapters), supplying the question, goal, constraints, prior decisions, raw evidence, attempts and observed failures. Never fork an App conversation or inherit full history for consultation. Advisors identify missing evidence for the coordinator or request it from relevant agents under the communication rules below. This overrides general routing history options.

A fresh native subagent or authorized CLI process does not require creating another App chat. A prohibition on additional App chats alone does not prohibit those execution paths; honor any separate restrictions on subagents, external backends or processes.

## Delegate and coordinate

Before dispatch, define goal, constraints, resource owner, inputs, deliverable and destination, acceptance criteria and dependencies (independent work versus work awaiting upstream evidence). Supply necessary domain context, workflows and prior decisions. Keep assignments proportional; no fixed template is required. Label each constraint's source: user requirements bind; coordinator assumptions may be challenged. Preserve authorization boundaries, prohibitions, acceptance conditions and rejected approaches through exact excerpts or accessible source references, not a summary alone. Check rules that change product behavior against their requirement source before dispatch.

Choose context by where essential information lives and how reliably it can be recovered. Continue locally when reconstructing accumulated decisions would outweigh delegation benefits. Use fresh context for self-contained assignments with sufficient source evidence; use supported history inheritance when essential context cannot be reliably reconstructed, subject to the advisor exception above. Inherit only what is needed; full history guarantees neither understanding nor cache reuse.

The main coordinator owns dispatch unless explicitly delegating bounded coordination. Pass this boundary to agents; delegated coordinators observe shared limits and report assignments and owners. Give each mutable resource one owner, separate coordinator and agent work, and serialize conflicts. Preserve unrelated work, authorization and permissions; update active agents on scope or ownership changes and adapt to evidence or blockers.

When supported and authorized, agents may exchange evidence, interface clarifications and questions directly; otherwise use a concise coordinator relay. Combine already-known independent questions for the same recipient; do not wait to accumulate more or delay blockers, safety issues or material counterevidence. Share identities only when useful; no messaging-only agents or fixed networks. The coordinator retains scope, approach approval, ownership and completion decisions and receives material evidence, contradictions and blockers. Reviewers may question workers but verify independently; advisors may consult peers but return recommendations to the coordinator.

Observe concurrency and lifecycle limits: returned results may not free slots. Reuse compatible agents under model-routing rules or release them through supported tools. Continue useful local work; prefer completion notifications or bounded waits over unchanged polling and maintain required progress updates.

For batches of independent assignments, use [batch fan-out](references/batch-fan-out.md) to track tasks, isolate parallel work and collect results through the existing dispatch and acceptance rules.

## Choose models

Keep the main Orchestrator on the current task model. Default advisors to Claude flagship → GPT flagship fallback, and other subagents (including reviewers and delegated coordinators) to task-selected GPT models. Choose effort independently. Apply [user overrides, role defaults and fallback boundaries](references/model-routing.md#role-defaults-and-user-overrides).

Before each assignment's first dispatch, complete the [routing preflight](references/model-routing.md#establish-candidates-and-dispatch-support): establish candidate/provider evidence and actual controls, then select and apply model, effort and context. Complete required discovery before an inheritance fallback; fresh context alone does not select a configuration. Reuse valid runtime evidence and follow the linked discovery rules for inventory requests or gaps.

At dispatch, show a Markdown table (new for later dispatches): agent/role, assignment, model, effort and selection reason; identify the backend when using an external CLI or mixing runtimes. Omit status columns and routine disclaimers for normal explicit settings. Explain inheritance, fallback, unsupported controls and dispatch errors; report runtime-supplied differing effective values. Distinguish plans and previews from successful creation.

## Return and finish

Beyond required progress updates, intermediate replies report only new evidence, contradictions, blockers or decisions needed. At assignment completion, return conclusions, deliverables and relevant paths, actual check results, unresolved issues and verification gaps; distinguish completed, verified and remaining work. Summarize passing checks, report failure diagnostics and link long logs. Omit unnecessary assignment repetition, full diffs and chronology without hiding decision-relevant evidence or failures.

Intervene for blockers, decisions, scope changes or material problems, not repeated reviews of unfinished work. Once stable, review requirements, affected callers and critical failure paths; resolve conflicts and verify the combined result. Check delegated conclusions against key evidence proportionately to risk; investigate contradictions or gaps without repeating whole investigations.

Use independent review when worthwhile. When authorized, the coordinator or assigned worker fixes confirmed in-scope findings; the independent reviewer rechecks affected scope, behavior and downstream effects to closure. Unfinished required work is not complete.

Tie material reviews/checks to an identifiable artifact version or state (commit, diff, revision or equivalent). When artifacts or relevant inputs change, reassess validity, reuse unaffected evidence and recheck affected scope before acceptance; an earlier pass does not establish that changed work passes.

When stalled, supply evidence, repair the environment, correct the approach or seek useful advice, preserving the assignment's model and effort. Report missing conditions or capabilities, attempts and results, reusable partial deliverables, material limits and coordinator decisions needed. Do not repeat failed approaches under unchanged conditions. Continue feasible independent work even without delegation.

Stop at acceptance. Reopen only for changed inputs, new evidence, a different approach to an unresolved problem or a verification gap; these judgments add no reporting or approval step.

When the same kind of failure recurs across assignments, repairs or rechecks, identify its likely structural cause, such as a missing check, constraint, data source or instruction, as an improvement candidate. Report the candidate, its evidence and a proposed fix in the final result. Recommend these improvements only; implementing them requires separate authorization.

For routing previews and maintenance, follow [model routing](references/model-routing.md#routing-only-mode-and-maintenance) and [tests/README.md](tests/README.md). Report offline checks and behavioral results separately.
