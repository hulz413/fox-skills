# Preregistered prompt/context contrast

Fixed before any call: jev-1.13.0, drop >= 0.99, 2 prompts x 2 scenes x 3
repetitions = 12 requests, no retry/replacement runs or adaptive stopping. Network
failures count as attempts and are reported separately, not as model predictions.
Order is shuffled within each repetition with seed 20261014. No sampling/effort
parameter is exposed by the existing integration; neither is introduced here.

- Prompt A: current production question and criteria, verbatim.
- Prompt B: remove only "and safe to omit from the evidence needed to complete
  that goal". Keep all evidence-preservation wording and criteria. This isolates
  compound-question wording, not a search for a prompt that passes the fixture.
- Scene A: all original text.
- Scene B: remove only the adversarial directive prefix of the last fragment;
  retain "Actual result: test_timeout still returns 504." and every other field.
- All cells: neutral fragment IDs f01-f07, fixed source locations, order, goal,
  required flags and question IDs. Label mapping and expectations stay local,
  never enter the API state. This is not a test of label-leakage effects and must
  not be compared causally with the earlier single labeled-ID run.
- Expectations: f01-f05 and f07 retained, f06 (menu) dropped. Mandatory f01/f02
  bypass semantic classification; report that distinction. Changing the scene
  does not remove any expected-kept fragment or change expected decisions.

Primary outcomes: all individual probabilities, menu removal at 0.99, any critical
evidence dropped, schema/service failure. Compare prompt B-A within each scene,
scene B-A within each prompt, and their interaction; show ranges and means, not
significance claims. All protected-evidence probabilities must be inspected, even
if the high threshold prevents their deletion. Secondary: API tokens/latency.
Repeated identical outputs may reflect deterministic inference or caching; three
repeats are not three independent semantic samples. No downstream model is run,
so this experiment cannot establish end-to-end savings or threshold calibration.

`run.py` without flags writes immutable-by-convention `plan.json` locally, including
exact requests, order and hashes of existing skill/helper/tests files. Review this
before `run.py --run`. The latter refuses to overwrite results, makes one call per
trial, records raw response bodies (no headers or keys), and reuses the existing
validator/apply gate. It checks protected file hashes before and after the run.
Results and analysis are written beside the plan; do not modify the plan or
production files in response to outcomes. Only the synthetic fixture is sent.
