# Optional Jev context filter (experimental)

This standalone helper is not enabled by SKILL.md and does not intercept native
Codex tools. Use it on saved supplementary evidence **before** a model reads the
full output. It neither routes agents nor decides completion or permissions.
Python 3.9+ and its standard library are sufficient.

## Input and invocation

Input is a JSON object containing a nonempty `goal` and a `fragments` list. Every
fragment must have unique string `id`, nonempty `text` and `source`, and an explicit
boolean `required`. Source should identify location and version; additional fields
(e.g. original command exit status) are preserved. See the small synthetic
[fixture](../tests/context_filter_case.json).

The caller must mark user constraints, acceptance evidence, necessary diagnostics
and known critical counterevidence `required: true`. The helper cannot independently
prove that the caller supplied or protected everything required. Supply enough
context to judge dependencies; do not split a diagnostic from its qualifying text.
Keep the input file available for expanding inspection. Do not send secrets or
materials unauthorized for the external TypeSafe service; the complete input,
including required fragments and metadata, is sent as state when a call is made.

With `TYPESAFE_API_KEY` exported locally:

```sh
python3 skills/fox-orchestrate/scripts/filter_context.py evidence.json > shadow.json
python3 skills/fox-orchestrate/scripts/filter_context.py evidence.json --apply > filtered.json
```

Each invocation makes at most one request (no retries), so the two commands make
separate calls. Default shadow output preserves all fragments and reports proposed
omissions. `--apply` removes only optional fragments classified clearly irrelevant
with Noul probability >= 0.99. This is an **experimental threshold**, not a calibrated
correctness guarantee. All other fragments retain original order, text and metadata;
there is no summary generation, automatic deduplication or output token quota.
Pass only `goal` and `fragments` onward; retain judgments/usage as the local receipt.

The model is pinned in the script. A missing key, oversized request, timeout,
service error, model mismatch or malformed response returns all input fragments
with `status: fallback` and exit code 1. No optional fragments means no API call.
Invalid input produces no JSON, leaves the source file untouched and exits 2.
Consumers must inspect exit status and status rather than treating fallback as
successful filtering. Error bodies and credentials are never included in diagnostics.
The 24,000 UTF-8-byte request guard bounds this experiment; it is not an exact token
or dollar cap. Oversized evidence follows the existing targeted-reading workflow,
not silent truncation. The network operation has a 20-second socket timeout.

## Verification and rollout

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/fox-orchestrate/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 skills/fox-orchestrate/tests/eval_context_filter.py
```

The [initial validation](../tests/context-filter-validation.md) records the first run, including its failed noise-removal check.

The second command explicitly calls the paid API once on synthetic evidence. It
replays that response for apply mode, tests fixed evidence-retention expectations,
and reports measured service usage, latency and text bytes. Bytes removed are not
token or cost savings; this smoke test does not run a downstream model.

Before enabling routinely, shadow representative authorized workloads with fixed
labels, then compare complete and filtered snapshots using the same downstream
model, effort, task and acceptance checks. Measure total service/coordinator/worker
usage, cache effects, latency, rework and missed evidence. Do not change routing
expectations or claim a net saving from this smoke test. Existing skill instructions
remain unchanged until end-to-end results justify integration.

API contract and design references: [HTTP API](https://docs.typesafe.ai/api),
[Noul](https://docs.typesafe.ai/primitives/noul),
[passage classification](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).
