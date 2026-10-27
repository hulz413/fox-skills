# Fox Ask Advisor

Get independent advice from one advisor by default, or multiple advisors when requested. Advisors analyze without modifying files or launching subagents; the initiating agent retains ownership and final judgment.

## Usage

```text
$fox-ask-advisor Evaluate the current approach.
$fox-ask-advisor --provider claude Evaluate the current approach.
$fox-ask-advisor --provider codex --model MODEL_ID --effort medium Review this decision.
$fox-ask-advisor --context full Review what I just changed.
$fox-ask-advisor --advisors 2 Compare these approaches independently.
$fox-ask-advisor Ask one Codex advisor and one Claude Code advisor to review this plan.
$fox-ask-advisor --mode session
```

Natural-language preferences and per-advisor configurations are accepted. Explicit fields override their corresponding defaults. A request for multiple advisors without a count means two; a list of multiple members implies its length unless a count is supplied.

For one advisor, the provider defaults to the initiating agent's provider and the model to that provider's best general reasoning model. For multiple advisors, the first two provider slots default to Codex and Claude Code with task-appropriate, comparable model + effort combinations; additional slots need explicit providers. A confirmed single-provider environment may fill both unpinned default slots, with disclosure. Effort selection starts from `medium` and moves down or up as needed before launch; this is not a trial run.

The execution interface must support independent advisors and applying every resolved configuration. Native subagent tools are preferred; a documented CLI may be used when it can apply the requested settings. Single-advisor consultations retain the one-model fallback rule. Multiple-advisor consultations validate the full list before launch and report failures as incomplete rather than replacing members automatically.

A single advisor uses `--context auto|full|brief`. Multiple advisors start in separate fresh contexts with the same briefing, then cross-review material disagreements for at most two rounds by default. Explicit `full` conflicts with this workflow and requires clarification. Consensus and majority opinion do not establish correctness.

Consultations identify the reviewed material version or state, track substantive open issues when useful, and focus follow-ups on new evidence, changed inputs, and affected conclusions. Results report actual configurations, unresolved issues, and verification gaps.

`--mode session` preserves the configured advisor count and per-advisor preferences at key checkpoints for the current task. It defaults to one advisor, may incur several runs, and ends with `--mode off`, task completion, or an unrelated task. This prompt-level commitment can be lost after context compaction. Implementation between consultations requires its own task authorization.

See [SKILL.md](SKILL.md) for selection, fallback, context, follow-up, and lifecycle rules. Input flags are skill conventions, not assumed runtime tool arguments.
