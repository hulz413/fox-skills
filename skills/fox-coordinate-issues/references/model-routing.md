# Model routing for issue tasks

Choose a model and effort for each worker task before its first dispatch. This file is self-contained; it adapts the routing approach of `fox-orchestrate` to issue fixing without depending on that skill.

## 1. Refresh the inventory every run

At the start of every run, list the models the current host can dispatch to, per provider, with each model's supported effort values and defaults (the host-specific call is in [host capabilities](hosts.md)). Read the complete list; a tool description or error may show an abbreviated one. Never reuse an inventory from an earlier run, never infer availability or provider from a model name, and never hard-code model IDs in this skill.

Treat a provider as usable only if the host reports it enabled and able to run child tasks. If the host cannot dispatch to another provider at all, say so in the plan and use what it can run.

## 2. Pick the provider

1. An explicit user choice of provider, model, version, or effort wins, scoped to what they named. If it cannot be honored, report it as a blocker instead of substituting.
2. Otherwise use the provider the coordinator itself runs on (for example Claude when the dispatch task runs on a Claude model, OpenAI when it runs on GPT). Establish it from the host's report of the current task's provider or model, not from guessing; if the host does not report it, say so and ask.
3. Within the provider, consider only the latest available version of each model family; superseded versions are not candidates unless pinned.

## 3. Pick capability from the issue evidence

Judge from the triage evidence: impact, uncertainty, and how much context the worker must rebuild. File counts, text length, and severity alone do not decide it.

| Issue evidence | Capability tier |
|---|---|
| Clear symptom and expected result, likely one module, established fix pattern, direct check available (copy, style, a wrong field, a missed condition) | efficient |
| Needs causal investigation, several modules or a service boundary, or reconstructing context from code and data | workhorse |
| Root cause unclear across services, concurrency or data consistency, conflicting reports, or a group whose fix must reconcile several issues | frontier |

Map tiers to the host's model descriptions and recommendations. Prefer the host's recommended model for a tier, then its default. Disclose ambiguity instead of guessing which model is stronger or cheaper.

## 4. Pick effort independently

| Effort | Issue evidence |
|---|---|
| low | A settled fix with complete boundaries and a narrow check |
| medium | Ordinary investigation, local implementation, and reliable checks |
| high | Hard debugging, interacting conditions, or conflicting evidence where deeper analysis should improve correctness |
| xhigh | Demanding cross-service or cross-issue consistency where analysis beyond a normal deep pass materially helps |
| max | Only the hardest analysis, with depth explicitly worth the latency and usage |

Capability and effort are separate choices: a frontier task does not imply high effort, nor an efficient one low. Use only effort values the chosen model supports; if one is unsupported, take that model's nearest supported lower value and say so.

## 5. Apply and report

Set model and effort through the dispatch tool's own parameters, not prompt text. Give each worker fresh context with the brief. In the plan table, give one short reason for capability and one for effort. Report effective settings only from what the host returns.

## 6. Escalate at most once

Keep the configuration fixed through follow-ups. Missing inputs, permissions, local data, or a single failure are not evidence of insufficient capability; fix those first. When concrete evidence shows the reasoning is inadequate, the coordinator may start one new attempt at one stronger configuration (higher tier or effort), handing off verified facts, failed approaches, and open questions. A second escalation needs the user's approval.

## 7. Service failures

If a dispatch fails because the model service is unavailable (an outage or a transient rate limit, confirmed from the diagnostic), retry once later or switch to an equivalent model of an enabled provider, unless the user pinned the provider or model. Never treat authentication, permission, billing, or policy errors as a reason to switch; report them.
