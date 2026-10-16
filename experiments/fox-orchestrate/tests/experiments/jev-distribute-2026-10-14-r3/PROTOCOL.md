# Preregistered shared-evidence distribution pilot

## Frozen question and scope

Compare direct broadcast (A) with per-task Jev allocation (B) of one shared evidence
packet to three already-defined read-only audits. No task/model routing, code editing,
production integration, old expectation changes or runtime .99 threshold changes.
All new tasks/source snapshots are in samples.json, labelled before any inference.
S01 PDF code and S02 Chinese editing rules are calibration; S03 Anki docs/code,
S04 plan creation, S05 plan reconciliation and S06 handoff are holdout. Related plan
sources stay on holdout. No old holdout outcomes or C03 are loaded for tuning.

Two mostly-separate packets, two cross-dependency packets, two short/shared packets.
These are authored current-repository audit questions, NOT production traces, and
most material is documentation. Gold labels are single-author minimum fact rubrics;
equivalent valid evidence counts. Relevance labels are task-relative: necessary if
needed by a gold fact, auxiliary for shared prelude, otherwise unrelated to the
bounded task. They are not a universal ground truth about all useful context.
Dependencies are sufficient evidence sets, not arbitrary byte windows.

Snapshots preserve full H2 sections (code-fence aware) or top-level Python
functions/classes with shared module prelude. S02 deliberately uses the complete
first four normative sections plus prelude, not the long teaching examples. No
post-outcome rechunking or sample replacement. Exact duplicate texts would be
removed before freezing; no duplicate texts exist here. All candidate documents
are already in scope. A broadcasts this common pool; it is not a claim to beat an
optimized deterministic dependency-aware router.

## Allocation policy, fixed before calls

Both groups receive identical common read-only instructions, task question,
acceptance criteria and ID/path/title catalogue. Shared document/module preludes
are mandatory to preserve identity, authorization boundaries and code constants.
Gold facts, task-to-fragment labels and dependency labels never enter Jev, worker
or operational reviewer prompts. Known mandatory common constraints stay direct;
undiscovered task-specific exceptions remain a measured risk, not an oracle mask.

A sends all frozen fragments in original order. B makes one Jev request per packet,
with all public tasks/fragments in shared state and one Choice per optional
fragment/task pair: relevant, irrelevant, uncertain. A fragment may reach multiple
tasks. Omit ONLY when choice=irrelevant and P(irrelevant)>=0.95; retain all other
outcomes. This is a new experimental allocation guard, not calibrated reliability,
not copied from old heldout results, and not a modification/use of the production
context filter's 0.99 threshold. No threshold tuning in calibration or holdout.
Keep original text/order/provenance, no top-k, quota, summary or automatic omission
of required fragments. Invalid judgment or service failure stops the run.

## Model, execution and measurement

Jev pinned jev-1.13.0. Workers and independent fresh-context reviewer pinned
 gpt-6.1-sol / medium, Codex CLI0.162.1 using existing ChatGPT login. Local catalog
confirms support; log requested settings, do not claim independent server attestation.
Use the previously verified named eval_openai provider to disable request/stream
retries, ignore user config, ephemeral empty cwd, read-only sandbox, project docs
and tools disabled. These are evaluation calls, not live delegated work. Existing
credentials are consumed without logging their values. Raw CLI stdout/stderr and
logical prompts are retained; underlying generator HTTP status is unavailable and
is null unless exposed by an error. Jev records HTTP status and original body.

One repetition. Packet order S01..S06. A-first for odd IDs, B-first for even IDs.
Both arms use concurrency=1 so observed failures prevent any later invocation;
wall time is actual serial end-to-end time, not projected parallel performance.
Each arm's timer begins before allocation/context assembly and ends after review
and any repair/recheck; human experiment setup and post-run scoring are excluded.
No per-arm query generation: the three tasks are already frozen and identical.

Three initial worker calls, then one reviewer call over all three answers with
complete evidence but no group/gold labels. Reviewer checks only task-relevant
correctness/completeness and source support, not style. Each task with worker
missing/requested evidence or reviewer rejection receives at most one repair:
full original packet plus its prior answer and review feedback. Returning full
context is the frozen conservative recovery policy, identical in A/B; record it
as rework. If any repair occurs, one complete packet recheck follows. A task still
missing evidence or rejected stays incomplete. No gold is used to trigger repairs.

Max96 generator calls:36 initial+12 review+36 repair+12 recheck; max6 Jev calls.
No extra judges, probes, retries, replacement calls or resume. CLI timeout180sec,
Jev20sec; no redirects. Stop globally on authentication, transport, HTTP, schema
or unexpected protocol failure; preserve partial outputs and failure before exit.
Freeze file hashes and protect all pre-existing fox-orchestrate files. Lock the
calibration log before holdout without tuning. Corrections require a separate
future protocol, never editing frozen rules after observing outcomes.

## Evaluation and gates

Report calibration separately and aggregate heldout by packet, task and kind.
Token totals include Jev allocation, all workers, review, material refill, repair
and recheck. Report input/output/cached tokens by backend plus arithmetic total
input+output; cached is a subset, not double-counted. Reasoning output is also a
subset when exposed. Unlike-model token totals are not money. Missing usage is
unknown, not free. Record all actual calls including failed/unpaired work; evaluate
paired comparisons only for fully completed pairs and mark interrupted run incomplete.

Report actual per-packet end-to-end seconds and aggregate mean/sum. Report worker
requests, initial reviewed failures, repair tasks, additional calls/tokens/time and
unresolved tasks. Compare evidence delivery to frozen sufficient sets (with manual
review of legitimate alternatives) and semantic initial/final fact coverage,
critical omissions/errors and unsupported claims/citations. Operational reviewer
acceptance is not the gold score. After running, randomized IDs hide arm labels
for primary-agent scoring before aggregate comparison. This is not independent
human blind review; retain mapping and scores. No inference calls for scoring.

Success requires all heldout tasks complete, no new critical omissions/errors or
lower final quality vs A, at least15% reduction in total heldout tokens including
Jev/rework AND at least10% reduction in mean actual end-to-end time. Report rework
without excluding inconvenient short packets. Successful averages do not excuse
critical regressions. Gates are engineering pilot targets, not calibrated confidence.
One repetition and four heldout packets cannot establish statistical significance.
A failed/incomplete run never validates integration. No code/skill changes or commit
follow automatically from any result.
