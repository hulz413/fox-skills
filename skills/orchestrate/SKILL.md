---
name: orchestrate
description: Coordinate subagents when the user requests delegation or expected gains in quality, time, or cost justify the coordination overhead. Keep other work local.
---

# Orchestrate

Own the plan, delegation, and final outcome. Choose the approach, divide work, and decide what needs independent checking; provide agents with relevant domain context and workflows.

Stay in the main session by default; invoking this skill does not require delegation. Delegate when expected gains in quality, time, or cost justify context transfer, coordination, and integration. Routine fixes and small tasks often stay local; complexity alone does not require delegation, especially for tightly coupled work. Honor explicit requests within runtime limits. Choose the number and mix of roles for bounded independent work or useful review; there is no mandatory pipeline or agent count.

## Roles

| Role | Responsibility and boundary |
| --- | --- |
| `explorer` | Investigate sources, current state, dependencies, or unknowns. Return evidence and material uncertainties without changing the subject. |
| `worker` | Complete the assigned work and check it. Return the deliverable, relevant evidence, and blockers; modify only assigned resources. |
| `reviewer` | Independently assess a proposal or result against requirements. Report material, actionable, evidence-backed findings, their impact, and meaningful verification gaps. No findings is valid; preferences alone are not blockers. Keep the subject read-only; the coordinator or assigned worker owns repairs. |
| `advisor` | Analyze direction, competing explanations, or complex decisions. Return recommendations, supporting evidence, unresolved questions, and proposed checks. Advice only: do not modify resources or take over execution. |

Name the role in each assignment unless the runtime registers it; multiple agents may share a role. The coordinator owns planning and decisions. Independent review uses an agent other than the producer.

## Advisor context

Consult an advisor only for a concrete decision or direction problem that warrants the overhead, not automatically at startup, after an error, or before completion. Advisor and reviewer are distinct roles; neither requires the strongest model.

Start an advisor with `fork_turns: "none"` and explicitly supply the question, goal, constraints, relevant prior decisions, key raw evidence, attempted approaches and their observed failures. Do not fork an App conversation or automatically inherit full history for consultation. A summary organizes evidence; it must not replace original evidence that could change the judgment. If context is insufficient, the advisor identifies the missing evidence; the coordinator supplies it in a follow-up, or the advisor requests it directly from a relevant agent under the communication rules below, reusing retained context when possible. Missing information alone does not justify model escalation or a conversation fork. This advisor-specific context rule takes precedence over the general history options in model routing.

## Delegate and coordinate

Before dispatch, define the goal, constraints, resource owner, and acceptance criteria. Supply necessary context and prior decisions. Prefer fresh or limited context when it preserves them; do not copy full history or the orchestration process just for convenience. Adapt assignments to new evidence or blockers. Agents normally execute directly; further delegation stays within shared limits. For follow-ups, send only changed requirements or findings when context is retained; restore needed context when it is not.

Give each mutable resource one owner; keep coordinator and agent assignments distinct, and serialize conflicts. Reuse valid findings and checks, revisiting them when inputs change, evidence conflicts, or verification requires it. Reviewers must assess results independently. Preserve unrelated work, authorization boundaries, and tool permissions, and keep active agents aligned as scope or ownership changes.

Agents may exchange necessary facts directly when supported and authorized by the runtime: request evidence, clarify interfaces, or ask about a finding. Share relevant agent identities in assignments only when useful; do not create a fixed communication network or extra agents for messaging. Keep exchanges focused and avoid repeated forwarding or copying full histories. Direct messages do not change scope, approve a new approach, transfer resource ownership, or declare completion; those decisions remain with the coordinator. Send material new evidence, contradictions, and blockers back to the coordinator. Reviewers may ask workers for explanations but must independently verify findings; repairs remain with the coordinator-assigned owner. Advisors may request evidence from peers, but return their final recommendations to the coordinator for adoption rather than directing execution. If direct messaging is unavailable, use a concise coordinator relay.

Follow runtime concurrency and lifecycle rules: a returned result may not release a slot, so reuse or release agents through supported tools. Continue useful local work while agents run; prefer completion notifications or bounded waits to repeated unchanged reads. Coordinate blockers, material decisions, and scope changes, and maintain required user progress updates.

## Choose models

For routing-only tests or previews, return decisions without dispatching or executing the described tasks. After editing this skill, run the routing-only regression procedure in [tests/README.md](tests/README.md).

Before dispatch, apply [model routing](references/model-routing.md) to each assignment. Choose model, effort, and context-transfer mode together, then pass supported settings explicitly. This skill permits task-specific overrides unless the user or higher-priority instructions pin them.

Whenever you dispatch work to a subagent, you MUST show the user a Markdown table in the dispatch update, with one row for every dispatched agent even when configurations match. Include the agent or role, assignment, requested model, requested effort, selection reason, and whether settings are runtime-confirmed, requested, or inherited. Repeat the table when a later dispatch adds or replaces agents. If a setting cannot be verified, label it unknown or inherited; never imply runtime confirmation.

## Evidence and handoffs

Read relevant sources and expand the investigation when evidence warrants it. Summarize successful checks and include diagnostic details for failures. Keep long logs in an artifact and link to them. Handoffs should include conclusions, relevant file or artifact paths, checks and results, and unresolved issues or verification gaps. Avoid repeating the assignment, full diffs, or chronology unless needed; scale detail to the finding. Inspect referenced evidence when needed for acceptance, not routinely. Never omit evidence needed to assess correctness or conceal failures through truncation.

## Integrate and finish

During implementation, intervene for blockers, key decisions, scope changes, or material problems; avoid repeatedly reviewing unfinished work. Once stable, review requirements, affected callers, and critical failure paths; resolve conflicts and verify the combined result proportionately. Own final acceptance and use independent review when worthwhile. When authorized, have the coordinator or assigned worker fix confirmed in-scope findings, then have the independent reviewer recheck the affected scope to closure. After corrections, recheck affected behavior and downstream effects, reusing valid evidence. Repeat review only for new changes, evidence, or unresolved issues. Report actual results and meaningful verification gaps; do not claim required work is complete when it remains unfinished.

Classify a stall before changing configuration: missing information calls for evidence; environment failures for fixing the environment; reasoning omissions in a sound approach for targeted verification or effort adjustment; an approach contradicted by evidence for replanning and, when worthwhile, advisor consultation; demonstrated capability mismatch for model reselection.

When progress stalls, use evidence to decide whether to add context, change approach, reuse or replace an agent, or stop an unproductive attempt. Preserve useful results and address material blockers; hand off results and settle ownership before replacement. If delegation is unavailable, continue feasible work locally and explain material limits.
