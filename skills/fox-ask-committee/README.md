# fox-ask-committee

An analysis-only committee workflow for difficult debugging, planning, research, and tradeoff decisions. It uses available agent tools or a documented CLI that can apply each member's requested provider, model, and reasoning effort, without depending on a particular execution backend or another skill.

Invoke `$fox-ask-committee` with a question and an explicit provider, model, and effort for every member. Two members are the default; provide a longer list to convene more. Structured input and unambiguous natural language are both accepted. Use actual identifiers and reasoning settings supported by your execution environment.

Missing or unsupported settings require clarification before any member launches. Profiles and runtime defaults do not fill missing values. Members analyze independently and then cross-review disagreements for up to two rounds by default. The workflow returns recommendations and unresolved differences in chat, without modifying files or writing implementation code.

If the available execution interface cannot apply and confirm the complete committee's requested configurations, the workflow reports a blocker instead of silently substituting settings or simulating members.

See [SKILL.md](SKILL.md) for the complete input contract and workflow.
