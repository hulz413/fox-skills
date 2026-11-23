# Worker brief

What every worker brief from [SKILL.md](../SKILL.md) section 6 step 3 must contain. Pass pointers, not copies of the reports.

- The instruction to read the fox-fix-issue skill directly at its absolute path (it is manual-only, so not through a skill tool) and run it in dispatched mode.
- The keys, their source, and where each report lives (links, file paths, or the runner's failure evidence).
- The fix workspace, acceptance workspace, acceptance branch, slot, and lock path.
- The vitest worker cap: `RUN_VITEST_MAX_WORKERS` set to 100% divided by the concurrency (20% at 5), so parallel runs together stay near the core count.
- Flags from triage.
- That the coordinator is this task, and questions reach it by ending the turn as the fix skill's host table describes.
- That shared local middleware (for example Temporal) is already running; if it is found down, the worker reports to the coordinator instead of starting or stopping anything, and never stops or kills an instance it did not start.
- Whether one model escalation is allowed.
- That the worker makes no external writes and returns write-back drafts instead.
- The expected final report.
