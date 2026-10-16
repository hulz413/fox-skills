# Jev filter initial validation — 2026-10-14

Scope: standalone optional helper; SKILL.md, model routing, existing fixtures and
existing test expectations unchanged. No downstream-agent calls or integration.

- Offline suite: 59 tests passed (53 existing, 6 new test methods with subcases).
- Live run: fixed synthetic `context_filter_case.json`, one request, no retries.
- Model: `jev-1.13.0`; drop threshold fixed before the call at 0.99.
- Input SHA-256: `3d20ff6403100452083527a9972d50070e7d9dd716ec27c03da25af1c8fb49fa`.
- Service usage: 1,393 input tokens, 89 output tokens; measured call latency 1.1789 s.
- Required material bypassed classification. Optional irrelevant probabilities:
  counter 0.07, dependency 0.12, ambiguous 0.20, noise 0.95, injection 0.54.
- Shadow preserved all originals; apply replay used the same captured response,
  without another request, and preserved all critical evidence.
- **Noise removal failed**: 0.95 did not meet the fixed threshold. Both contexts
  contain 680 text bytes. Live evaluation exited 1 for this failed acceptance item.

This is a successful API integration but not demonstrated useful filtering at the
chosen threshold. Do not enable by default or claim token/cost savings. No threshold,
fixture or expectation was changed after observing the result. A future improvement
needs representative labeled evidence and a separate held-out evaluation, followed
by fixed downstream-model comparisons of quality, usage, latency and rework.
