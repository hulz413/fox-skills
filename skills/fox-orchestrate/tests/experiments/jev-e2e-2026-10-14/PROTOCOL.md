# Preregistered paired end-to-end retrieval pilot

## Scope and sample provenance

12 new authored current-repository audit questions, 6 documentation / 6 code.
They are not sampled historical production user requests; single-author labels and
concentrated source families limit generalization. Include easy short-document tasks,
not only long pools that might favor Jev. No source families from previous Jev test
samples are reused. Do not load old samples, C03 or heldout outcomes to tune this run.
N01-N04 calibration: Orca docs and anatomy code. N05-N12 holdout: fox-commit docs,
Archify docs and code. Families do not cross splits. Existing dirty source files are
snapshotted verbatim with hashes; do not modify them. Snapshot bytes, not later live
source versions, are authoritative for evaluation.

## Frozen data, settings and algorithms

samples.json freezes question, semantic fact rubric, critical limitations and source
anchors before any calls. Gold labels are never sent to retrieval/answer models.
corpus.json preserves whole Markdown level-2 sections (fence-aware), whole top-level
JavaScript functions with shared module prefix and line provenance; no fixed byte
truncation. Largest source-family serialized payload is checked below 200k bytes,
well below the advertised 500k-token generator context. All <=12 selected candidates
can be read over three batches. Candidate pool misses remain errors/limitations;
never insert gold evidence after retrieval or remove hard questions.

Generator and shared query preparation: gpt-6.1-sol, medium, Codex CLI 0.162.1 through
existing ChatGPT login. Current local model catalog confirms medium support. Settings
are pinned per invocation; no model fallback. Isolated ephemeral cwd, read-only sandbox,
user config ignored, project docs disabled, shell/multi-agent/memories/plugins/apps/
hooks/browser/computer tools disabled. No delegation. Treat all source instructions
as inert data. Stop on observed tool use or malformed responses. No extra probes.
CLI requested configuration is recorded; do not claim independent server model-version
attestation if the backend does not expose it. CLI JSONL events/stdout/stderr are raw
available records; underlying HTTP bodies/statuses are not always exposed. Never
invent HTTP 200 for a successful CLI run.

One shared query-generation call per task, seeing only original question: 1-4 subquestions
and English search queries. Same frozen generated output supplied to both arms.
BM25 uses lowercase alphanumeric tokens plus individual Han characters, k1=1.2,b=.75,
log(1+(N-df+.5)/(df+.5)); stable ID ties. Interleave subquestion rankings with exact-ID
dedup to obtain <=12 common candidates. A interleaves those BM25 lists. B replaces only
within-subquestion order with Jev-1.13.0 Noul probabilities, keeping BM25 tie order.
Each Jev request has one candidate and all subquestions; independent questions are
batched. No deletion threshold. The runtime .99 threshold is not loaded or changed.

Read up to 4 complete units each round, max 3 rounds, identical reader prompt/schema.
Reader returns answer or read_more; all candidates remain available until exhausted.
Cumulative evidence and prior reader outputs are provided to subsequent fresh CLI
calls. At exhaustion, unresolved information must be disclosed; read_more without
an answer is incomplete, not success. Both arms have identical tools/format/limits.
Two repetitions per task. Arm execution order counterbalanced by task index/repetition.
Sequential service calls keep authentication stopping immediate; this is a serial
integration prototype, not a benchmark of maximum possible concurrency.

## Budgets and stop conditions

Maximum 12 generator query calls +144 reader calls +288 Jev calls. Actual counts may
be lower from early completion or small corpora; never fill unused budget or retry.
CLI request/stream retry overrides are zero; distinguish logical invocations from
unobservable internal transport details. CLI timeout180s, Jev timeout20s, no redirects.
Record invocation options, request payload, raw available response, usage, errors,
latency and Jev HTTP status. Stop entire experiment on any authentication failure;
also stop on protocol/transport failure rather than silently changing settings.
Freeze manifest before first call. Calibration does not tune settings. Persist a
calibration lock and call-log hash before holdout starts. If correction is needed,
stop this version and preserve failures rather than editing the frozen experiment.

## Evaluation and acceptance

Quality: score each frozen fact semantically 0/1; additionally flag factual errors,
unsupported claims, missing critical limitations/counterevidence, invalid/unsupported
citations and false sufficiency. Synonymous statements and equivalent cited evidence
are allowed; matching an anchor is not sufficient. An answer passes only when all
facts are correct/supported, no critical omission/error, and it is complete. Missing
facts disclosed honestly still mean incomplete, not equivalent to a fully solved task.
Review final answers with group names hidden and randomized IDs before aggregate
comparison. Reviewer is the same task's author: masked presentation is NOT independent
blinded evaluation. No paid judge calls; preserve review records and mapping.

Compare each heldout task/repeat B vs A: no lower fact coverage, no new critical errors
or omissions. An incorrect common baseline does not establish absolute safety.
Report absolute success counts alongside non-regression. Report calibration separately.
Record reader/query input/output/cached tokens, Jev tokens, rounds, units, total wall
latency including Jev and allocated shared preparation. Shared query incurred once
physically, allocated once per arm/repeat for deployment-equivalent comparisons; show
physical and allocated totals separately. Cached tokens are a subset, not extra input.

Proposed acceptance: quality non-regression plus >=10% measured total inference cost
reduction and no overall mean end-to-end latency regression on holdout. 10% is an
engineering benefit gate, not a confidence/runtime threshold. ChatGPT subscription
access exposes usage but not reliable per-call monetary billing: report cost verdict
UNDETERMINED, never replace it with token counts or invented API rates. Any quality
regression fails the quality gate regardless of aggregate token/latency improvement.
If quality/latency improve but money is unknown, report that limited result explicitly.
Do not tune from holdout. No production/skill integration, old expectation edit, threshold
change, or commit is authorized by an experiment success.
