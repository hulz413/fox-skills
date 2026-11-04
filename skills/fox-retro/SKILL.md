---
name: fox-retro
description: Review an agent work session, identify evidenced problems, and propose practical improvements to its tools, instructions, checks, and collaboration workflow. Use when the user requests a retrospective, analysis of repeated mistakes, or workflow improvements grounded in a session. Not a substitute for code review or a handoff.
---

# Fox Retro

Turn concrete session difficulties into minimal, verifiable improvements for future work. Identify problems and recommend changes; a retrospective request alone does not authorize implementing them. Honor any implementation scope the user has already authorized without asking again.

Use this workflow when the user requests a retrospective, including in natural language. Do not initiate one automatically after every task. This skill is self-contained: use available reading and inspection capabilities without requiring another skill, a particular MCP server, or an external service. Write the report in the user's conversation language unless they request otherwise.

## Establish the evidence

Default to the current conversation. If the user specifies another session, read its available original record. Limit retrieval to that session and relevant supporting artifacts; do not scan unrelated history.

Identify the intended outcome, material constraints, and actual result. Extract consequential events such as user corrections, avoidable retries, rework, missed verification, expensive unproductive calls, and information blockers. Preserve enough context to distinguish an error from reasonable exploration, an authorized tradeoff, or a requirement that changed later.

Point each finding to an identifiable message, tool result, log entry, or file location. If records are unavailable or only a summary remains, state the coverage limit and qualify conclusions. Ask for missing evidence only when it is necessary to resolve a material question; otherwise report what the available evidence supports. Never reconstruct unseen events as facts.

## Investigate the mechanism

For each material event, explain the observed impact and distinguish confirmed facts, causal hypotheses, and verification gaps. Inspect relevant instructions, callers, tool behavior, documentation, and check configuration as needed to test the explanation. Session evidence establishes what happened; current files establish what exists now. Account for changes between them.

Before recommending a new mechanism, determine whether the existing one was absent, undiscoverable, disconnected, broken, contradictory, or read but not followed. An existing check that was never run calls for examining its execution path, not duplicating the check. An ignored instruction calls for investigating the failure, not adding synonymous wording.

Do not infer general model ability, recurring frequency, or universal rules from a single failure. Do not invent time savings, costs, or severity thresholds. Separate an unresolved task defect from the workflow weakness that may have allowed it; do not expand the retrospective into an unsolicited code audit or repair.

## Select proportionate improvements

Prefer repairing or simplifying an existing mechanism, connecting an existing check, resolving conflicting instructions, or improving a navigation pointer before adding something new. Use these as options, not categories that must each produce a finding:

- Navigation and information access: make needed sources discoverable or propose the minimum missing visibility. Missing access is not permission to broaden credentials or access rights.
- Deterministic checks: use existing tests, types, linting, or validation for mechanically detectable failures when the benefit justifies execution, maintenance, and false-positive costs. Lack of a hook or CI job alone does not establish the need for one.
- Judgment and instructions: clarify the relevant skill, project guidance, or review criteria. Put constraints where they must first influence behavior; authorization, data protection, and essential contracts must be available before consequential actions.
- Tool use and collaboration: improve a concrete inefficient call pattern, ambiguous decision point, or completion condition supported by the session.
- Removal and simplification: propose deleting or consolidating redundant, conflicting, obsolete, or ineffective steps and rules. Verify their original purpose and remaining callers or protected cases; non-use in one session is not evidence of obsolescence.

Keep each rule in one authoritative location. Prefer the narrowest applicable scope: the affected tool or skill, then project guidance, and only genuinely stable cross-project requirements in global instructions. Check existing documentation before proposing a new document; no particular standards filename is required.

Merge findings with the same cause. Prioritize by demonstrated impact, plausible recurrence supported by evidence, and the cost of the proposed change. A rare but serious failure can merit a safeguard; a cheap one-off inconvenience may merit no permanent change. Do not create findings to fill a quota, and distinguish issues already resolved from remaining improvement candidates.

## Present problems and recommendations

Lead with the most useful conclusion and any material evidence limitation. For each actionable candidate, include:

- **Problem and impact:** what happened and why it mattered.
- **Evidence:** the specific supporting event or artifact.
- **Cause and uncertainty:** the supported explanation and what remains unverified.
- **Minimal recommendation:** the exact file, tool, or workflow to change, the intended behavior, and why it addresses the cause. State when the target is not yet confirmed.
- **Verification and cost:** an observable way to check the improvement and any material maintenance burden, false-positive risk, or tradeoff.

Keep the report proportional to the findings; concise connected prose is fine. If no worthwhile change is supported, say so. When the cause is unresolved, recommend a bounded evidence-gathering step rather than presenting a speculative permanent fix as settled.

If the user has requested implementation, carry out only the authorized changes, preserve unrelated work, and verify the affected behavior. Report what changed, what was checked, and remaining limitations. Do not claim future recurrence is prevented merely because a check passed. Without implementation authorization, stop at concrete, reviewable recommendations; do not edit instructions, install hooks, change access, or store memories automatically.
