# New retrieval reranking pilot — preregistration

Scope: documentation and code search only. No production integration, context deletion,
skill changes, existing expectation changes, threshold changes, or agent delegation.
Read current TypeSafe HTTP/Noul docs on 2026-10-14. Fixed model jev-1.13.0.

## Samples and split

Eight authored repository questions, four Chinese and four English. They are source-grounded
retrieval tasks, not captured production incidents or a random population sample.
Calibration: D01/D02 advisor docs, C01/C02 installer code.
Holdout: D03/D04 Playwright docs, C03/C04 creator code. Source families do not cross splits.
These four families were not sources of the previous threshold experiment. Old holdout
labels/results are not read or used for prompt, budget, query, or parameter selection.
Old files are hashed only for preservation. New holdout labels are authored before calls,
not independently blinded; acknowledge single-author annotation bias.

corpus.json contains verbatim local snapshots with file, first line and file SHA256.
Segments pack adjacent semantic units to <=1200 UTF-8 bytes where possible, splitting
large units at whole lines. This may divide functions or fences: it is a retrieval
window, not a claim of standalone executable code. Labels list essential factual
requirements, supporting/contradicting evidence, alternatives, and jointly required
passages. Unmarked passages are background, not certified irrelevant. Anchor-based
labels are a minimum evidence rubric, not an exhaustive semantic relevance annotation.
User task is always supplied separately; no mandatory instruction is filtered.

## Three arms and fixed budget

All arms share the same 12 BM25 candidates from the family's full snapshotted corpus.
BM25: ASCII alphanumeric lowercase tokens, predeclared English search terms for all
arms, k1=1.2, b=.75, IDF log(1+(N-df+.5)/(df+.5)), tie path then line.
This isolates second-stage ordering; it does not compare full search strategies.

A: common candidates in deterministic file/line order, a proxy for bounded direct
reading of search hits, NOT a measured reproduction of the current agent workflow.
B: BM25 order.
C: same BM25 candidates, one Noul usefulness question per task/passage; descending
probability, BM25 tie break. No probability threshold, top-k tuning, rewriting, or
runtime deletion. All candidates remain available in the saved output.

Reading budget: 3000 UTF-8 bytes including path/line headers and newline separators.
Read whole passages in order; stop at first passage that would exceed the budget.
No skipping oversized next passages. Equal byte budgets are not equal model-token
budgets; report bytes accurately without estimating main-model token savings.

## Call budget and freezing

192 maximum Jev HTTP attempts: 8 tasks x 12 candidates x 2 repetitions.
A/B use no model calls and are repeated only as paired deterministic baselines.
No generative-model/answer-quality calls; no main-model effort setting applies.
Order: calibration D01,D02,C01,C02 then holdout D03,D04,C03,C04; each task rep1 then rep2,
passages in BM25 order. Sequential HTTP, 20s timeout, no redirects/retries/probes.
Record status, response/model/usage, request hash and elapsed time; never headers/key.
Stop the whole experiment on 401/403 or any invalid response; no replacement calls.

Before calls: review annotations, run offline checks, write manifest hashes covering
samples/corpus/scripts/protocol and protected existing files. No edits after freezing.
Calibration only checks validity; it selects no prompt/threshold/budget/policy.
Write calibration-lock.json before first holdout request. No outcome-based extra calls.

## Frozen metrics and decision rule

Primary: task-macro essential-fact recall at budget; all-essential-facts-covered tasks.
Safety diagnostic: counterevidence recall; per-task regressions versus BOTH A and B.
Retrieval ceiling: essential facts present anywhere in the 12 candidates.
Cost diagnostics: selected bytes; oracle bytes to cover all essential facts (null if
pool lacks a fact); actual Jev input/output tokens, HTTP counts, serial latency.
Oracle reading cost uses labels offline; it is NOT an implemented stopping policy.
Timing measures local ordering and API wait; it is not end-to-end task latency.
Repeat stability: C ordering/selected evidence and recall across two repetitions.
Report calibration and holdout separately, by task and code/docs. Repeats are not
independent task samples. No p-values or broad generalization from four heldout tasks.

Evidence sufficient to justify another integration experiment only if C has no
per-task essential/counterevidence recall regression against either baseline in either
holdout repetition, plus strictly better heldout macro recall or strictly lower mean
oracle reading bytes with all compared oracle values finite. Otherwise report the
failed gate without adjusting anything. This gate does NOT authorize production use.

Final task correctness, downstream rework, main-model/cache tokens, and money saved
are explicitly unmeasured in this retrieval-only pilot. A positive retrieval result
would still require a separate controlled end-to-end test before a savings claim.
