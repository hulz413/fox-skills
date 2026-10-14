# Jev reranking pilot — results

Status: completed. Preregistered next-experiment gate: **FAIL**.

Eight authored source-grounded tasks, 4 calibration / 4 holdout, 12 shared candidates, two repeats. Four source families are separated by split. No old holdout tuning. No production integration.

HTTP attempts: 192/192; statuses: {'200': 192}. Known usage: {'input_tokens': 132052, 'output_tokens': 4032}; unknown usage responses: 0. Serial API wait: 200.074s.

## Frozen primary results

| Split | Arm | Fact recall (task macro) | Counterevidence recall | Complete / case-repeats | Selected UTF-8 bytes |
|---|---|---:|---:|---:|---:|
| calibration | A | 6.2% | 12.5% | 0/8 | 16160 |
| calibration | B | 87.5% | 87.5% | 6/8 | 19690 |
| calibration | C | 93.8% | 100.0% | 6/8 | 19684 |
| holdout | A | 6.2% | 14.3% | 0/8 | 17112 |
| holdout | B | 81.2% | 85.7% | 4/8 | 17952 |
| holdout | C | 81.2% | 85.7% | 4/8 | 17952 |

A=file/line order proxy; B=BM25; C=BM25+Jev. All use the identical 12-candidate pool and 3000-byte prefix budget. Repeated A/B are identical baselines, not independent trials.

## Per-task evidence coverage

| Task | Split | A facts r1/r2 | B facts r1/r2 | C facts r1/r2 | Facts available in pool |
|---|---|---|---|---|---|
| D01 | calibration | 0/3 / 0/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 |
| D02 | calibration | 0/3 / 0/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 |
| C01 | calibration | 0/4 / 0/4 | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 |
| C02 | calibration | 1/4 / 1/4 | 2/4 / 2/4 | 3/4 / 3/4 | 4/4 |
| D03 | holdout | 1/4 / 1/4 | 2/4 / 2/4 | 3/4 / 3/4 | 4/4 |
| D04 | holdout | 0/4 / 0/4 | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 |
| C03 | holdout | 0/4 / 0/4 | 3/4 / 3/4 | 2/4 / 2/4 | 4/4 |
| C04 | holdout | 0/3 / 0/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 |

## Regressions and stability

Heldout task/repeat/baseline regression comparisons: 2.
C order changed in 6/8 tasks; selection changed in 1; recall changed in 0.

- {"case": "C03", "repeat": 1, "against": "B", "C_facts": ["dedupe", "examples"], "baseline_facts": ["dedupe", "existing", "examples"], "C_counter_hit": 1, "baseline_counter_hit": 2}
- {"case": "C03", "repeat": 2, "against": "B", "C_facts": ["dedupe", "examples"], "baseline_facts": ["dedupe", "existing", "examples"], "C_counter_hit": 1, "baseline_counter_hit": 2}

## Offline oracle reading cost

Bytes required to encounter all labeled evidence; computed using gold labels, NOT a deployable stopping rule. Null means missing evidence in the candidate pool.

- calibration/A: [8388, 8388, 5556, 5556, 6599, 6599, 8589, 8589]; mean=7283.0
- calibration/B: [1977, 1977, 1573, 1573, 1202, 1202, 4118, 4118]; mean=2217.5
- calibration/C: [1015, 1015, 1573, 1573, 1202, 1202, 5366, 5366]; mean=2289.0
- holdout/A: [5768, 5768, 12524, 12524, 11683, 11683, 13340, 13340]; mean=10828.8
- holdout/B: [5973, 5973, 1785, 1785, 8855, 8855, 1926, 1926]; mean=4634.8
- holdout/C: [7162, 7162, 1785, 1785, 6465, 7662, 1926, 1926]; mean=4484.1

## Interpretation limits

- This isolates ordering within a common BM25 pool; A is not a live agent baseline. Queries and labels were authored, not captured from production. Four heldout tasks cannot establish general reliability.
- Essential facts are an anchor-based minimum rubric. Single-author labels may miss equivalent evidence. Some facts share passages, so fact observations are correlated.
- Byte budgets are not token budgets. No answer-generation model was called: final correctness, actual stop/expansion behavior, rework, cache effects, total downstream tokens, and monetary savings remain unmeasured.
- Each Jev call has the task and one candidate only. Long semantic relationships across windows may be absent; this run does not change windows after observing results.
- All new protocols, corpus, labels, scripts and previous fox-orchestrate files were hash-verified after collection. Skill, old expectations and runtime threshold are unchanged.
- Offline verification: 9 experiment checks and all 59 existing fox-orchestrate checks passed. HTTP authentication stop and exact 192-call budget were tested using fake local transport.

## Artifacts

`manifest.json`, `PROTOCOL.md`, `samples.json`, `corpus.json`, `calibration-lock.json`, `calls.jsonl`, `results.jsonl`, `summary.json`, `analysis.json`.

## Observed failure mechanism (post-run inspection, no tuning)

In heldout C03, both repeats rank `creator-012` (resource-directory creation) at 0.84 above `creator-014` (existing skill-directory refusal) at 0.80. BM25 reads the latter within budget; Jev moves it to rank 5 outside the reading prefix. It was not classified as irrelevant or deleted. Independent usefulness ordering failed to preserve coverage of all parts of the multi-part question under this budget. This explains the observed omission; it does not isolate whether different window boundaries or another judgment would fix it. No final-answer errors were measured.

Post-run integrity checks are recorded in `verification.json`. No additional inference calls or policy adjustments were made.
