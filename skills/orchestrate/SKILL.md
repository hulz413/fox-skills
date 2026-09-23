---
name: orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Orchestrate

Own the plan, delegation, and final outcome of the current task. Use judgment to choose the approach, divide work, and decide what needs independent checking. Supply domain expertise and local workflows through each assignment.

Delegate when expected gains in quality, time, or cost justify briefing and integration overhead; otherwise, work locally. Honor explicit requests for agent delegation within runtime limits. Choose the number and mix of agents to suit the task; there is no minimum workstream count or mandatory pipeline.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, existing state, dependencies, or unknowns. Return evidence and material uncertainties; keep the subject unchanged. |
| `worker` | Complete the assigned work and check the result. Return the deliverable, relevant evidence, and blockers; modify only assigned resources. |
| `reviewer` | Independently assess a proposal or result against its requirements. Return only material, actionable, evidence-backed findings and their impact, plus meaningful verification gaps; no findings is valid and preferences alone are not blockers. Keep the subject read-only unless repair is separately assigned. |

These are reusable role instructions. Include the selected role in the task message unless the runtime already registers it. Multiple agents may share a role; independent review uses an instance other than the producer. The coordinator retains overall planning and decisions.

## Delegate and coordinate

Give each agent a clear goal, necessary context, ownership, and what would demonstrate completion. Adapt the handoff to the work, and ask for concise results with evidence and unresolved issues. Pass relevant decisions and constraints without copying the entire orchestration workflow into every child. Children normally execute directly; coordinate any further delegation within the shared limits.

Assign one owner per mutable resource or serialize conflicting changes. Preserve unrelated work and keep assignments within the user's authorization and actual tool permissions. Keep active agents aligned when requirements or ownership change.

Follow the runtime's concurrency and lifecycle rules; a returned result may not release a slot. Reuse suitable instances or release capacity through supported tools. Stay productive alongside delegated work and wait when no useful local work remains.

## Choose models

Before dispatch, apply [model routing](references/model-routing.md) to the actual assignment. The coordinator chooses the supported model and reasoning effort; this skill permits task-specific overrides unless the user or higher-priority instructions pin them. Keep the routing reference in the coordinator's context and reuse it while it remains applicable.

## Integrate and finish

Inspect returned artifacts and evidence, resolve incompatible assumptions, and verify the combined outcome at a depth appropriate to the task. The coordinator owns final acceptance and uses independent review when worthwhile. When fixes are authorized, coordinate worker corrections for confirmed material findings and reviewer follow-up until a complete pass finds no material issues within scope or a blocker needs user input. Reuse still-valid evidence when rechecking repairs and their effects, without routinely repeating the entire review. Account for required work before claiming completion. Report actual results and meaningful verification gaps.

When work stalls, use the evidence to decide whether to supply context, revise the approach, reuse or replace an agent, or stop an unproductive attempt. Preserve useful results and address material blockers. If delegation is unavailable, continue feasible work locally and explain any material limitation.
