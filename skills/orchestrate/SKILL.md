---
name: orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Orchestrate

Own the plan, delegation, and final outcome of the current task. Use judgment to choose the approach, divide work, and decide what needs independent checking. Supply domain expertise and local workflows through each assignment.

Delegate when expected gains in quality, time, or cost justify context transfer, coordination, and integration overhead; otherwise, work locally. Small edits and routine fixes do not require subagents. Assess task complexity separately from delegation value: even complex work may be better kept local when tightly coupled. Delegate when a bounded assignment can proceed independently or independent review offers a clear benefit. Invoking this skill alone does not require delegation; honor explicit requests for agent delegation within runtime limits. Choose the number and mix of agents to suit the task; there is no minimum workstream count or mandatory pipeline.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, existing state, dependencies, or unknowns. Return evidence and material uncertainties; keep the subject unchanged. |
| `worker` | Complete the assigned work and check the result. Return the deliverable, relevant evidence, and blockers; modify only assigned resources. |
| `reviewer` | Independently assess a proposal or result against its requirements. Return only material, actionable, evidence-backed findings and their impact, plus meaningful verification gaps; no findings is valid and preferences alone are not blockers. Keep the subject read-only unless repair is separately assigned. |

These are reusable role instructions. Include the selected role in the task message unless the runtime already registers it. Multiple agents may share a role; independent review uses an instance other than the producer. The coordinator retains overall planning and decisions.

## Delegate and coordinate

Before dispatch, give each agent a clear goal, constraints, resource ownership, and acceptance criteria. Include necessary context and existing evidence so routine requirements do not arrive as piecemeal follow-ups. Use a fresh or limited-context handoff when it preserves these requirements and prior decisions; do not copy full history or the orchestration workflow merely for convenience. Adapt assignments when new evidence, blockers, or scope changes warrant it. Children normally execute directly; coordinate further delegation within the shared limits.

For follow-ups to an agent that retains the relevant context, send the new requirement, finding, or changed scope rather than repeating the whole assignment. Restore necessary context when replacing an agent or when context has been lost.

Assign one owner per mutable resource or serialize conflicting changes. Give the coordinator and children distinct work rather than repeating the same investigation in parallel. Reuse still-valid findings, source readings, reviews, and test results; revisit them when changed inputs, conflicting evidence, or a specific verification need justify it. Independent review must assess the result rather than merely accept the producer's conclusions. Preserve unrelated work and keep assignments within the user's authorization and actual tool permissions. Keep active agents aligned when requirements or ownership change.

Follow the runtime's concurrency and lifecycle rules; a returned result may not release a slot. Reuse suitable instances or release capacity through supported tools. Stay productive alongside delegated work and wait when no useful local work remains. Prefer completion notifications or bounded waits over repeated status requests and reads of unchanged output. Coordinate when a decision, blocker, or material change needs attention, while maintaining required user-facing progress updates.

## Choose models

Before dispatch, apply [model routing](references/model-routing.md) to the actual assignment. Reuse the reference while it remains applicable. This skill permits task-specific model and effort overrides unless the user or higher-priority instructions pin them.

Choose model, effort, and context-transfer mode together, and pass the configuration explicitly through supported tool parameters. Briefly state the assignment, requested model and effort, and selection reason. A sentence is sufficient for one agent; use a table when comparing multiple assignments helps. Distinguish requested settings from runtime-confirmed settings; when inheritance is necessary, state the inherited settings and reason.

## Evidence and handoffs

Search and read the portions relevant to the question, expanding when necessary. Summarize successful checks; include diagnostic details for failures. Keep lengthy logs in an appropriate artifact when needed and provide a usable reference instead of repeatedly inserting them into context. Do not omit evidence needed to assess correctness or conceal failures through truncation.

Agent handoffs should contain conclusions, relevant file or artifact locations, checks actually performed and their results, and unresolved issues or verification gaps. Avoid repeating the assignment, full diffs, or a chronological work log unless needed for a decision. Scale detail to the finding rather than imposing a fixed length. The coordinator should inspect referenced evidence where needed for acceptance, not routinely reread every artifact.

## Integrate and finish

During implementation, intervene for blockers, key decisions, scope changes, or evidence of a material problem; avoid repeatedly reviewing unfinished diffs. Once the result is stable, perform a consolidated review against the requirements, affected callers, and critical failure paths. Resolve incompatible assumptions and verify the combined outcome at a depth appropriate to the task. The coordinator owns final acceptance and uses independent review when worthwhile. When fixes are authorized, coordinate worker corrections for confirmed material findings and reviewer follow-up until a complete pass finds no material issues within scope or a blocker needs user input. After corrections, recheck affected behavior and downstream effects, reusing still-valid evidence. Broaden or repeat review only for new changes, new evidence, or unresolved issues; do not start another review of the same scope after a complete pass without such a reason. Account for required work before claiming completion. Report actual results and meaningful verification gaps.

When work stalls, use the evidence to decide whether to supply context, revise the approach, reuse or replace an agent, or stop an unproductive attempt. Preserve useful results and address material blockers. If delegation is unavailable, continue feasible work locally and explain any material limitation.
