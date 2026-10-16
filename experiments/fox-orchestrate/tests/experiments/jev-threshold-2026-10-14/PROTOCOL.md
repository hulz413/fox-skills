# Frozen threshold validation protocol

This is a bounded experiment, not a production threshold change. Only this directory
is added. Existing skill, runtime 0.99, prior fixtures and prior expectations stay
unchanged. No subagents, downstream-model calls, retries, extra sampling or commits.

## Corpus and annotations fixed before API calls

24 scenarios, seven fragments each: six each for logs, code search, documentation
and investigation handoffs. In every category IDs 01–03 are calibration and 04–06
held out. Source-file families do not cross the split. All fragment IDs are neutral,
and fragment order is shuffled once with a case-specific deterministic seed.

12 code/docs scenarios contain verified literal repository excerpts with source
locations and SHA-256 versions plus explicitly synthetic observations. 12 logs and
handoffs are synthetic reconstructions of distinct operational situations, not
claims about incidents in this repository. No private business logs are sent. This
is a small, single-author benchmark, not an independent sample of production traffic.
The existing menu fixture is excluded. Near-topic false hits, version differences,
negative/counterevidence, uncertain dependencies and embedded instructions are
included. H03/H04 include a redundant copy of a code-protected goal; they have no
unique information and can be omitted. Current prompt may not consider redundancy
"unrelated"; retain the labels and report that limitation, do not retune the prompt.

Every case has 1 code-required goal, 3 critical optional fragments, 1 uncertain
optional fragment, and 2 clearly droppable fragments. Each label includes a local
rationale. Labels, provenance classifications, case/split/category IDs and rationales
are never passed to the API. State contains only goal and original fragment fields.
Required and semantic preservation are reported separately. Labels are fixed before
inference; ambiguities discovered afterward must be disclosed, not relabeled.

## Frozen evaluation

- Model jev-1.13.0; unchanged production prompt and criteria.
- Candidates [0.90, 0.95, 0.97, 0.99], plus keep-all baseline.
- Two repetitions per case, 24 calls per split, exactly 48 attempted calls total.
- One request per case with all six optional-fragment questions batched. No retries
  or replacement calls for API failures. Missing credentials halt before calls.
- Order shuffled per repetition, calibration first, seed 2026101402.
- Reuse identical returned probabilities to score thresholds offline; do not call
  models separately per threshold. Repetition scores are never averaged for gating.
- Freeze sample/runner/protocol/production-file hashes and exact requests in plan.json
  before calling. Record raw response bodies without headers or credentials.

A candidate is admissible only with 24 valid calibration responses and zero critical,
uncertain or required omissions, counting both repetitions separately. Require at
least one true noise deletion in each repetition to beat the keep-all baseline.
Rank admissible candidates lexicographically by: minimum true noise count across
the two repetitions; total true noise count; total correctly removed UTF-8 text
bytes; fewer fragments whose keep/drop decision flips; higher threshold. This
operationalizes coverage, removed volume and stability without arbitrary new targets.
Text bytes are not tokens or dollar savings.

Write selection.json and its calibration-results hash **before starting held-out
calls**. Evaluate only that locked policy on held-out results; do not select a new
threshold or score a new candidate to salvage failure. Acceptance requires 24 valid
held-out responses, zero critical/uncertain/required omissions, and at least one
true noise deletion in each repetition. If no calibration candidate qualifies,
lock keep-all, still complete the precommitted 24 held-out calls, report failure to
select a candidate, and do not derive another policy from them.

## Reporting boundaries

Report per-threshold calibration metrics, selected-policy held-out metrics, all
misdeletions, repetition variability, API usage/latency, and label uncertainty. Zero
observed errors does not establish zero risk or a <1% population error rate. Two
repetitions share the same cases; they are not additional independent semantic
samples. Selection success would justify broader shadow testing only, not automatic
integration. No downstream task is executed, so there is no measured end-to-end
quality, rework, token or cost improvement.

Run locally without flags to freeze a plan, inspect it, then run `run.py --run` once.
Existing result files block additional runs. Offline fake-response tests exercise
selection, rejection, threshold boundaries and the keep-all case without network.
