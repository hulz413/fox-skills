# Fox Ask Advisor

Get independent advice from one advisor by default, or multiple advisors when requested. Advisors analyze without modifying files or launching subagents; the initiating agent retains ownership and final judgment.

The skill also applies proactively when the agent is stuck or repeated attempts stop producing useful progress. It does not require a fixed failure count or session mode. Ordinary failures with a clear next step do not trigger consultation, and an unchanged blocker does not justify repeated new consultations.

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

For one advisor, use the initiating agent's provider and its best general reasoning model by default. If the initiating agent already uses that model, choose another available provider's best model. Explicit provider/model choices take precedence; a model-only choice uses its verified provider. A confirmed single-provider environment may use that provider with disclosure, relying on independent context for another perspective. Unverified host identity or capability rankings must be resolved rather than guessed.

For multiple advisors, the first two provider slots still default to Codex and Claude Code with task-appropriate, comparable model + effort combinations; additional slots need explicit providers. A confirmed single-provider environment may fill both unpinned default slots, with disclosure. Effort selection remains unchanged: start from `medium` and move down or up as needed before launch; this is not a trial run.

The execution interface must support independent advisors and applying every resolved configuration. Native subagent tools are preferred; a documented CLI may be used when it can apply the requested settings. Single-advisor consultations retain the one-model fallback rule. Multiple-advisor consultations validate the full list before launch and report failures as incomplete rather than replacing members automatically.

A single advisor uses `--context auto|full|brief`. Multiple advisors start in separate fresh contexts with the same briefing, then cross-review material disagreements for at most two rounds by default. Explicit `full` conflicts with this workflow and requires clarification. Consensus and majority opinion do not establish correctness.

Consultations identify the reviewed material version or state, track substantive open issues when useful, and focus follow-ups on new evidence, changed inputs, and affected conclusions. Results report actual configurations, unresolved issues, and verification gaps.

`--mode once` covers one consultation and its follow-ups while leaving default stuck-trigger consultation enabled. `--mode session` adds key checkpoints and preserves the configured advisor count and per-advisor preferences for the current task. It defaults to one advisor, may incur several runs, and ends with `--mode off`, task completion, or an unrelated task. `--mode off` disables all automatic consultations for the current task until explicitly re-enabled; an explicit one-off request remains allowed without re-enabling them. These prompt-level instructions can be lost after context compaction and do not constitute a background monitor. Implementation between consultations requires its own task authorization.

See [SKILL.md](SKILL.md) for selection, fallback, context, follow-up, and lifecycle rules. Input flags are skill conventions, not assumed runtime tool arguments.
