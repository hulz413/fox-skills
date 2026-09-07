---
name: orchestrate
description: Coordinate agents when a substantial task contains independent work that benefits from parallel execution, or when the user requests multi-agent orchestration. Keep small or tightly coupled work local.
---

# Orchestrate

Use the current task's subagent tools to divide useful work while keeping one coordinator responsible for the outcome. Respect the available tool contract, user choices, and session restrictions; this skill does not authorize creating separate user-facing tasks or expanding the requested scope.

## Decide what to delegate

Delegate a bounded assignment only when it can proceed independently alongside useful local work and its benefit exceeds the cost of briefing and integration. Keep small changes and tightly coupled decisions local. Use actual available concurrency, including the coordinator, as a ceiling rather than a target. Avoid filling slots merely because they exist.

The coordinator continues dependency analysis, interface decisions, integration, or other useful work while agents run. Stay available to the user, incorporate steering, and propagate changes that affect active assignments. Do not duplicate a delegated investigation unless a concrete gap or conflicting evidence requires it.

## Choose effort and context

Default to the current model; do not hardcode model names. Where the tool supports effort overrides, use these starting points:

- Scout: low effort for narrow, read-only discovery, such as locating files, tracing callers, or finding tests.
- Worker: medium effort for scoped implementation and routine verification.
- Difficult worker: high effort for ambiguous requirements or complex implementation.

Adjust to the assignment rather than treating these as mandatory tiers. Use only combinations supported by the active tools. If inheriting full history prevents an override, preserve the necessary context instead of forcing the override.

Use `fork_turns: "none"` for a self-contained assignment. Include the relevant decisions, paths, constraints, and evidence it needs. Inherit conversation history when prior decisions materially affect correctness; do not assume a fresh-context agent knows task-specific restrictions.

## Give clear assignments

Include only the details the assignment needs:

- Outcome and boundaries: the concrete question or change, and what is out of scope.
- Ownership: files or responsibility the agent may change, or an explicit read-only boundary.
- Context: relevant decisions, dependencies, sources, and applicable project constraints.
- Completion evidence: expected deliverable, appropriate checks, and unresolved questions to report.
- Delegation boundary: complete the assignment directly; do not spawn agents. Parent orchestration instructions apply only to the parent.

Default workers to leaves. Allow further delegation only for a concrete independent subtask within the shared concurrency budget and with explicit ownership.

Agents share a workspace unless tools explicitly provide isolation. Avoid concurrent edits to the same files; serialize shared-file changes or assign a single owner. Preserve unrelated work. Agents may exchange dependency findings directly, but ownership or scope changes go through the coordinator. Surface blockers promptly; do not silently replace agreed requirements with workarounds.

## Integrate and verify

Track active assignments and their dependencies without adding unnecessary bookkeeping files. Use supported messaging and waits; when nothing useful remains locally, wait instead of repeatedly polling unchanged status. Reuse an existing agent for a relevant follow-up rather than repeating discovery in a fresh agent.

Review returned evidence and actual changes before accepting completion. Resolve incompatible assumptions, integrate results, and run checks appropriate to the combined change. A worker's completion report alone is not proof that the whole task is correct. Verify material gaps or conflicting claims rather than rerunning every investigation.

Keep approvals with the user under the existing authorization rules; delegation grants no additional permissions. Report the overall result, meaningful verification, and remaining limitations. If delegation is unavailable, continue the feasible work locally and state any material impact.
