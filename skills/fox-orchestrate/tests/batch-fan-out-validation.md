# Batch fan-out live validation

Date: 2026-10-15. Result: the scoped synthetic smoke test passed. This records an existing run; documenting it made no additional worker calls or changes to execution policy.

## Tested artifact and setup

- Repository commit: `c112b4784ebb253abf254b2b69379c03b927efb3`.
- Runner SHA-256: `bd416dbde3c672c7dee19774e729f4dd010964f2142fac246a43bbd296d0ac57`.
- Claude Code 2.1.299, configured firstParty authentication, requested and reported model `claude-haiku-5-5`, requested effort `low`. Assigned-session assistant records reported both `effort` and `perTurnEffort` as `low` throughout. These are CLI/transcript observations, not independent provider-side configuration attestation.
- Two detached worktrees from one synthetic fixture commit, with unchanged common input and distinct owner markers. Workers generated JSON data artifacts, not business-code changes.
- Only Read and Write tools were exposed/allowed, with `restricted`, `dontAsk`, `permission-prompts none`, hooks disabled and an empty strict MCP configuration. A one-off harness launched two fixed CC processes through the unchanged runner; no scheduler or native subagent dispatch was exercised.
- Frozen limits: two tasks, at most three invocations, concurrency two, six agentic turns and a 120-second host timeout per invocation. No additional CLI invocation, model substitution or unplanned retry occurred. Neither per-invocation turn nor timeout limit was reached; their enforcement was not tested here.

## Tasks, execution and acceptance

Task A deduplicated three synthetic contact records case-insensitively, lowercased and sorted the emails, producing two unique entries. Task B counted amounts `[10, 20, 30]` and ultimately produced total 60.

B's first prompt explicitly required total 50 as a negative-test candidate. The coordinator's acceptance rule required 60 throughout. This was an intentionally seeded acceptance failure, not a spontaneous model mistake or a process failure.

| Task / invocation | Process phase | Artifact acceptance | Runner elapsed seconds | Reported total tokens |
| --- | --- | --- | ---: | ---: |
| A / turn-1 | completed | passed | 8.760 | 15,712 |
| B / turn-1 | completed | failed: seeded total 50 | 9.450 | 16,064 |
| B / turn-2 | completed | passed: total 60 | 7.348 | 12,213 |

All CC and runner exits were zero. Before explicit coordinator decisions, acceptance was pending despite process completion. `record-acceptance` saved artifact snapshot references and check evidence; B's failed decision remained intact after repair.

## Observed coverage

| Area | Evidence and observed result |
| --- | --- |
| Concurrent execution | Initial host process intervals overlapped by 8.824 seconds; recorded assistant-event intervals overlapped by 2.430 seconds. |
| Task isolation | Distinct initial sessions/worktrees wrote separate files both named `result.json`. Initial calls read their own input and owner files; all observed file-tool paths stayed in the assigned worktree, and writes targeted only `result.json`. Input/owner hashes and tracked fixture files remained unchanged. |
| Failed acceptance and repair | The coordinator rejected B's seeded artifact and accepted A independently, retaining all attempts. B resumed the exact session with unchanged model, effort, cwd and permission options; its final response returned the initial context marker, and its repaired artifact passed. Initial results were classified after both processes finished; cancellation of still-active work was not exercised. |
| Combined acceptance | Coordinator checks verified two task identities, distinct owners, two unique emails and amount total 60 in the combined artifact. Individual acceptance was not used as a substitute for this check. |
| Invocation accounting | Two tasks mapped to three invocations. `summarize` counted a repeated A directory once and included B's rejected invocation. An independent calculation from saved result usage matched every token subtotal and unknown count. |
| Preservation and cleanup | During the live run, the existing fox-skills repository status and runner hash remained unchanged. Worker file writes were limited to fixture outputs. Both temporary worktrees were removed after artifact/evidence snapshots were saved. |

The [sanitized receipt](batch-fan-out-live-evidence.json) retains timestamps, hashed session identities, configuration observations, relative file paths, artifact references and numeric results. Session hashes demonstrate B's identity match without publishing raw session IDs. Artifact hashes identify saved JSON content snapshots, not source-code commits. Full prompts, raw events, acceptance sidecars and one-off checks remain in the originating local run directory; they are not repository dependencies. The committed receipt is an audit record, not a self-contained replay fixture.

## Token totals

| Category | Reported subtotal | Unknown invocations |
| --- | ---: | ---: |
| Input, excluding cache | 16 | 0 |
| Output | 1,305 | 0 |
| Cache read | 34,654 | 0 |
| Cache creation | 8,014 | 0 |
| Total | 43,989 | 0 |

Scope: three CC `main_loop_invocation` records, including the rejected candidate and repair. The total adds input, output and the two cache categories; thinking tokens are not added again. Session-cumulative `modelUsage` was not summed across the continuation. Coordinator usage, nested agents, hidden service activity and monetary billing are outside this measurement. All fields were reported; live behavior with missing usage was not exercised.

## Not verified by this run

- General reliability, quality, token savings or speedup versus a serial baseline. Process/event overlap does not establish simultaneous provider GPU execution or a throughput benefit.
- Hostile filesystem escape, OS/container isolation, shared-service safety or correctness beyond the observed file operations.
- Source-code migrations, dirty-input transfer, merge conflicts, interdependent tasks or cross-module integration; the artifacts here were synthetic JSON.
- Native subagent scheduling/lifecycle, queue refill, multiple waves, large batches or other models/efforts/providers.
- Authentication, rate-limit, network, permission-denial, crash, timeout or cancellation failures; shared-blocker pause/resume behavior and lost-session recovery were not exercised.
- A live independent reviewer/worker repair loop. Acceptance and integration used coordinator-side deterministic checks.

The existing offline suite and earlier CLI/background reports cover different scenarios; their passes must not be attributed to this live run. See [validation procedure](README.md), [CLI validation](claude-code-cli-validation.md) and [background validation](cc-background-validation.md).
