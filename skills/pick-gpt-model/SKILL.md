---
name: pick-gpt-model
description: Recommend one GPT-5.6 model and reasoning-effort combination for a user-provided scenario, with a concise explanation of quality, latency, cost, and parallelism trade-offs. Match the output language to the user's prompt and use a fixed Recommended/Model/Effort/Reason/Trade-off structure. Use when the user asks which Sol, Terra, or Luna model and which Light, Medium, High, Extra High, Max, or Ultra effort to choose for coding, research, writing, design, analysis, review, batch processing, or other Codex work.
---

# Pick GPT Model

Recommend one primary model-and-effort combination. Make a decision from the supplied scenario instead of returning a generic catalog.

## Workflow

1. Infer the task's ambiguity, complexity, stakes, volume, tool use, required polish, latency sensitivity, cost sensitivity, and parallelizability.
2. Choose the model from the task profile.
3. Choose the lowest effort likely to produce a reliable result.
4. Check whether increasing the model is more useful than increasing effort.
5. Detect the dominant language of the user's latest scenario or prompt. Write every heading, reason, trade-off, and optional alternative in that language; keep canonical model names, model IDs, and effort labels in English so they remain unambiguous.

Do not ask a follow-up question merely because the scenario is brief. State a reasonable assumption and choose. If the scenario is too vague to distinguish options, default to **Sol × Medium**.

## Choose the Model

- **Sol (`gpt-5.6-sol`)**: Choose for ambiguous, difficult, open-ended, high-value, or presentation-quality work. Prefer it when judgment, architecture, creative direction, deep research, polished writing, UI design, or final quality matters most.
- **Terra (`gpt-5.6-terra`)**: Choose for everyday implementation, debugging, code review, refactoring, and reliable tool use when strong results and efficiency both matter.
- **Luna (`gpt-5.6-luna`)**: Choose for clear, repeatable, high-volume work with an objective definition of success, such as extraction, classification, transformation, formatting, or structured summaries.

When the task is underspecified or sits between models, prefer the more capable model unless the user explicitly prioritizes cost or latency.

## Choose the Effort

- **Light**: Small, tightly scoped, deterministic work where speed matters and verification needs are low.
- **Medium**: Balanced default for ordinary work that needs some planning and checking.
- **High**: Difficult multi-step work, architecture, complex debugging, design decisions, or important edge cases.
- **Extra High (`xhigh`)**: High-risk work, security or compliance analysis, complex trade-offs, or extensive verification.
- **Max**: One exceptionally hard, indivisible problem where deeper single-agent reasoning matters more than speed or usage.
- **Ultra**: A large task that splits into meaningful independent subproblems. Use it when parallel agents can work separately and synthesis is cheaper than sequential execution. It may reduce wall-clock time but normally consumes more total tokens.

## Avoid Inefficient Combinations

- Upgrade the model before pushing Luna to Extra High or Max when the limitation is judgment or capability.
- Prefer Sol × High or Sol × Extra High over Terra × Max when the task needs a higher capability ceiling.
- Do not choose Max for work that can be divided into independent parts; consider Ultra.
- Do not choose Ultra for small tasks, serial workflows, shared-state debugging, or concurrent edits to the same files.
- Do not invent fixed token, latency, quality, or price multipliers.

## Output Contract

Return only this compact structure, translated to the user's prompt language while preserving the same order and list style:

```text
推荐
- Model: Sol
- Effort: Ultra

理由
- The task is ambiguous and quality-sensitive.
- It needs multi-step judgment and verification, but not parallel agents.

权衡
- Higher latency and usage than Terra × Medium, in exchange for stronger judgment and polish.
```

For an English prompt, translate the headings to `Recommended`, `Reason`, and `Trade-off`; keep the `- Model:` and `- Effort:` labels, model names, and effort labels exactly as shown. Do not include model IDs unless the user asks for them. Use two to four reason bullets and one or two trade-off bullets. In `Reason`, explain both why the selected combination fits and why at least two plausible adjacent combinations were not selected. Prefer contrasts such as the same model with one effort step lower or higher, and a neighboring model at the same effort; name each rejected combination explicitly. If the recommendation is already at an edge (for example, Light or Max), compare the nearest valid alternatives instead. Do not add an introduction, generic model catalog, or closing summary. Add one `Alternative` section only when a different stated priority, such as minimum cost or minimum latency, would materially change the recommendation; localize that heading too.

## Calibration Examples

- Build and polish a new product landing page: **Sol × High**.
- Fix an ordinary application bug with clear reproduction steps: **Terra × Medium**.
- Extract the same fields from thousands of documents: **Luna × Light** or **Luna × Medium** when validation is important.
- Review security, tests, and performance as independent workstreams: **Sol × Ultra**.
- Resolve one subtle, non-decomposable concurrency proof: **Sol × Max**.

If the user asks for current availability, pricing, quotas, or newly released models, verify official OpenAI documentation before answering. Otherwise, answer directly from this decision framework.
