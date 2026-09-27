---
name: orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Orchestrate

Own the plan, delegation, and final outcome. Choose the approach, divide work, and decide what needs independent checking; provide agents with relevant domain context and workflows.

Stay in the main session by default; invoking this skill does not require delegation. Routine fixes and small tasks often stay local; complexity alone does not require delegation, especially for tightly coupled work. Honor explicit requests within runtime limits. Choose the number and mix of roles for bounded independent work or useful review; there is no mandatory pipeline or agent count.

## Work proportionately

- **Clear benefit.** Extra delegation, consultation, broader investigation or repeated checks must advance the current deliverable, meet acceptance criteria or resolve uncertainty that affects the result. Expected gains in quality, time or cost must justify the extra context, coordination and integration.
- **Smallest sufficient scope.** Reuse existing tools, valid evidence and retained context. Send only changes or missing information in follow-ups; restore necessary context when it is unavailable. Preserve necessary constraints, key raw evidence and counterevidence. Summaries do not replace required verification.
- **Stop at acceptance.** Finish when acceptance criteria are met. Reopen relevant work only for changed inputs, new evidence, a different approach to an unresolved problem or an identified verification gap. Make these judgments internally; this adds no reporting or approval step.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, current state, dependencies, or unknowns. Return evidence and material uncertainties without changing the subject. |
| `worker` | Complete the assigned work and check it. Return the deliverable, relevant evidence, and blockers; modify only assigned resources. |
| `reviewer` | Independently assess a proposal or result against requirements. Report material, actionable, evidence-backed findings, their impact, and meaningful verification gaps. No findings is valid; preferences alone are not blockers. Keep the subject read-only; the coordinator or assigned worker owns repairs. |
| `advisor` | Analyze direction, competing explanations, or complex decisions. Return recommendations, supporting evidence, unresolved questions, and proposed checks. Advice only: do not modify resources or take over execution. |

Name the role and include its responsibilities and boundaries in each assignment unless the runtime supplies that role definition; fresh agents do not automatically receive this skill. Multiple agents may share a role. The coordinator owns planning and decisions. Independent review uses an agent other than the producer.

## Advisor context

Consult an advisor only for a concrete decision or direction problem that warrants the overhead, not automatically at startup, after an error, or before completion. Advisor and reviewer are distinct roles; neither requires the strongest model.

Start an advisor with `fork_turns: "none"` and explicitly supply the question, goal, constraints, relevant prior decisions, key raw evidence, attempted approaches and their observed failures. Do not fork an App conversation or automatically inherit full history for consultation. If context is insufficient, the advisor identifies the missing evidence; the coordinator supplies it in a follow-up, or the advisor requests it directly from a relevant agent under the communication rules below. This advisor-specific context rule takes precedence over the general history options in model routing.

## Delegate and coordinate

Before dispatch, define the goal, constraints, resource owner, and acceptance criteria. Supply necessary context and prior decisions. Prefer fresh or limited context when it preserves them; do not copy full history or the orchestration process just for convenience. Adapt assignments to new evidence or blockers. The main coordinator decides new agent dispatches unless it explicitly delegates a bounded coordination responsibility. Pass this boundary to subagents; delegated coordination stays within shared limits and reports new assignments and resource owners back to the main coordinator.

Give each mutable resource one owner; keep coordinator and agent assignments distinct, and serialize conflicts. Preserve unrelated work, authorization boundaries, and tool permissions, and keep active agents aligned as scope or ownership changes.

Agents may exchange necessary facts directly when supported and authorized by the runtime: request evidence, clarify interfaces, or ask about a finding. Share relevant agent identities in assignments only when useful; do not create a fixed communication network or extra agents for messaging. Direct messages do not change scope, approve a new approach, transfer resource ownership, or declare completion; those decisions remain with the coordinator. Send material new evidence, contradictions, and blockers back to the coordinator. Reviewers may ask workers for explanations but must independently verify findings; repairs remain with the coordinator-assigned owner. Advisors may request evidence from peers, but return their final recommendations to the coordinator for adoption rather than directing execution. If direct messaging is unavailable, use a concise coordinator relay.

Follow runtime concurrency and lifecycle rules: a returned result may not release a slot, so reuse suitable agents under the model-routing rules or release them through supported tools. Continue useful local work while agents run; prefer completion notifications or bounded waits to repeated unchanged reads. Coordinate blockers, material decisions, and scope changes, and maintain required user progress updates.

## Choose models

For routing-only tests or previews, return decisions without dispatching or executing the described tasks. After editing this skill, run the routing-only regression procedure in [tests/README.md](tests/README.md).

Before the first dispatch of each assignment, apply [model routing](references/model-routing.md). Select model, effort and context mode for the task, pass supported settings explicitly, and keep that configuration for the assignment. This skill permits initial task-specific overrides unless the user or higher-priority instructions pin them.

Whenever you dispatch work to a subagent, show the user a Markdown table with one row per agent: agent or role, assignment, model, effort, and selection reason. Repeat it when a later dispatch adds agents. For normal explicit settings, omit a status column and routine unconfirmed-configuration disclaimers in both the table and surrounding prose. Successful explicit dispatch needs no commentary about a missing configuration echo. Explain inheritance, fallback, unsupported settings or dispatch errors when they occur, and report known effective values if the runtime supplies different ones. Distinguish planned dispatch from successful creation; previews do not establish execution.

## Evidence and handoffs

Summarize successful checks and include diagnostic details for failures. Keep long logs in an artifact and link to them. Handoffs should include conclusions, relevant file or artifact paths, checks and results, and unresolved issues or verification gaps. Avoid repeating the assignment, full diffs, or chronology unless needed; scale detail to the finding. Never omit evidence needed to assess correctness or conceal failures through truncation.

## Integrate and finish

During implementation, intervene for blockers, key decisions, scope changes, or material problems; avoid repeatedly reviewing unfinished work. Once stable, review requirements, affected callers, and critical failure paths; resolve conflicts and verify the combined result proportionately. Own final acceptance and use independent review when worthwhile. When authorized, have the coordinator or assigned worker fix confirmed in-scope findings, then have the independent reviewer recheck the affected scope to closure. After corrections, recheck affected behavior and downstream effects. Report actual results and meaningful verification gaps; do not claim required work is complete when it remains unfinished.

When progress stalls, add missing evidence, fix environment problems, correct the approach or seek useful advice while keeping each existing assignment's model and effort unchanged. If the task cannot proceed, report the concrete blocker or capability limit. If delegation is unavailable, continue feasible work locally and explain material limits.
