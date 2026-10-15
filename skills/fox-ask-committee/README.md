# fox-ask-committee

An analysis-only committee workflow for difficult debugging, planning, research, and tradeoff decisions. It uses available agent tools or a documented CLI that can apply each member's requested provider, model, and reasoning effort, without depending on a particular execution backend or another skill.

Invoke `$fox-ask-committee` with a question or use the current task. By default, two members use Codex and Claude Code, respectively. Model + effort combinations are selected according to task complexity and current provider capabilities, aiming for comparable overall capability and reasoning depth across providers rather than matching effort labels alone. Material uncertainty about comparability is disclosed. Effort selection starts from `medium` and moves down or up as needed before launch; it does not run once at `medium` first.

If discovery confirms only one provider is available, both default members use it with the same resolved model + effort and separate contexts. This is reported without requiring extra confirmation; explicit provider choices remain pinned.

Override any member's provider, model, or effort using structured input or unambiguous natural language; explicit fields take precedence. Partial configurations fill the two default slots in order unless a different target is identified. Supply a longer list for additional members, specifying each additional provider; model and effort can still be selected automatically.

The complete committee is resolved and validated before any member launches. Unresolved assignments or unsupported settings require clarification or a blocker report. Profiles and unrelated runtime defaults do not overwrite the resolved choices. Members analyze independently and then cross-review disagreements for up to two rounds by default. The workflow returns recommendations and unresolved differences in chat, without modifying files or writing implementation code.

If the available execution interface cannot apply and confirm the complete committee's requested configurations, the workflow reports a blocker instead of silently substituting settings or simulating members.

See [SKILL.md](SKILL.md) for the complete input contract and workflow.
