# Shared-evidence rerun: stopped on HTTP 429

## Result

The user authorized one fresh rerun using the original frozen experiment. All eight frozen inputs (samples, labels, split, policy, prompts, schemas, models/effort, budget and acceptance protocol) are byte-identical to jev-distribute-2026-10-14. No old heldout outcomes were used to tune anything.

A first local launch in r2 was blocked before inference because references/claude-code-cli.md changed externally between freeze and verification. Its manifest and launch-failure.json are preserved. r3 refreshed only the protected-workspace baseline, then ran the identical experiment.

r3 made two generator invocations:

| Task | Result | Seconds | Usage |
|---|---|---:|---|
| S01-t1 / calibration / A | Initial answer returned; not independently reviewed | 31.43 | input24538, output780 |
| S01-t2 / calibration / A | HTTP429 / turn.failed | 4.74 | Not returned |

Exact raw error:

> exceeded retry limit, last status: 429 Too Many Requests, request id: dbb63dd8-f20c-4e58-a8db-38b1fb411d04

CLI returned exit1. This is a reported HTTP429 service/rate-limit response, not an observed authentication failure. It does not establish whether account quota, shared backend capacity or a transient service limit caused it. Original calls.jsonl records http_status=null because the wrapper only extracts authentication codes; the explicit429 is preserved in error_events/stdout and recorded as derived metadata in verification.json. Original records were not rewritten.

The controller stopped immediately after this failure. No alternate model, manual retry, resumed call or Jev invocation followed. Configured request/stream retries are both0; the backend error wording alone does not prove the number of internal transport attempts.

Completed packet arms:0/12. Initial task answers:1/36. Jev calls:0/6. No reviewer, repair or holdout calls occurred. Therefore no paired token, end-to-end time, omission or rework comparison can be made, and acceptance is INCOMPLETE. The one answer is retained in outputs.jsonl and raw stdout; it is not an accepted/verified task result.

Known token subtotal25318 (24538input+780output; reasoning80 is included in output). Failed-call usage is unknown, so actual total usage cannot be asserted. Total measured CLI call time36.18seconds is partial service time, not a completed packet's end-to-end latency.

## Integrity

Frozen inputs match the original manifest exactly. The new protected baseline verifies, as do the original run files protected by this manifest. The experiment did not modify skill, existing test expectations or runtime threshold. The external reference edit was preserved. Original six experiment checks and59 existing checks remain the prior validation for unchanged code; they were not rerun merely for this launch. New integrity and diff-whitespace checks were run.

Original capacity failure is retained in jev-distribute-2026-10-14. Preflight interruption is retained in jev-distribute-2026-10-14-r2. Current HTTP429 raw request/response/error and successful initial answer are in this directory. No commit or publication.

Artifacts: PROTOCOL.md, manifest.json, prior-run.json, calls.jsonl, outputs.jsonl, raw/, run-status.json, summary.json, verification.json. The empty masked review files indicate that no complete packet was available for final scoring, not that quality passed.
