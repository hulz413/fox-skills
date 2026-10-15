# Runtime discovery validation

Validated on 2026-10-15. Policy and fixture SHA-256:

- `SKILL.md`: `dbd8e651412c0e40b2f2dd7e0134e26f7bef8b4ba468a8de48b79716804f1deb`
- `references/model-routing.md`: `6dfd60189bdee37a76c453bacbd86f3765fd355f440f95bf1b972b9217149e81`
- `tests/routing_cases.json`: `1677233cf45b7a31255b5c4144e1475dc7b5b577b3c30a8477ec7b21e8b24ea4`

## Change and checks

The policy separates observed inventory from dispatch eligibility. Codex discovery prefers the target running runtime's `model/list`, falls back to the effectively configured catalog when necessary, and checks actual tool/model/effort/context restrictions. It does not bind discovery to a gateway, maintain production model IDs, start replacement app-servers, or launch trial agents.

- Offline suite: 68 tests passed. These validate the existing checkers/helpers and fixed expectation legality, not live discovery.
- Skill structure validator: passed. System Python lacked PyYAML; validation used isolated `uv --with pyyaml` and a temporary cache, with no global dependency change.
- Local documentation links and `git diff --check`: passed.
- One fresh-context evaluator: GPT-6 Luna / medium, supplied only current policy and public routing/cooperation prompts. No expected answers, scenario execution, or delegated scenario tasks.
- All six new discovery cases (`case_062`–`case_067`) matched their fixed expectations on the first pass. The coordinator reviewed their reasons: closed-enum exclusion, effort conflict, profile-specific file fallback, unknown provider, unconfirmed string model, and stale capability invalidation.

## First-pass failures and bounded rechecks

The first routing output was structurally valid, but selected unsupported efforts in three existing cases (`011`, `017`, `020`) and failed to block an unsatisfiable effort pin in `044`. These were not treated as calibration differences. Two bounded follow-ups used the same evaluator/settings, unchanged policy/fixtures, public runtime-legality diagnostics, and specific policy contradictions. Original and revised routing predictions were retained separately; decisions were not presented as format-only repairs. The coordinator did not supply hidden expected answers.

Cooperation output initially failed during JSON generation (tuple unpacking), before a file existed. The subsequent gate failed because the file was absent. After generation succeeded, six nested route IDs failed structure validation and were corrected. The evaluator reported no decision changes, but overwrote that schema-invalid intermediate JSON instead of retaining it; intermediate schema recovery therefore has an audit gap. The final prediction and generation/schema failure account were retained.

## Final results and reason review

| Check | Result |
| --- | --- |
| Routing structure | Valid, 63 cases |
| New discovery scenarios | 6/6 fixed expectations and reasons accepted |
| Rules expectation matches | 50/51 |
| Autonomous expectation matches | 11/12 |
| Routing runtime legality | 55/55 selected combinations valid; 8 blocked cases reviewed separately |
| Cooperation structure/actions | Valid; 20/20 expectations and reasons accepted |
| New-agent cooperation runtime legality | 6/6 valid |
| Proportionate-work cases c15–c17 | 3/3 accepted |
| Boundary cases c18–c20 | 3/3 accepted |

The coordinator inspected every final routing/cooperation reason and the blocked explanations. Two existing fixed expectations still differ:

- `case_031`: frontier/xhigh rather than workhorse/xhigh for the interacting migration/rollback proof. The reason supports demanding integrated delivery, but does not establish that frontier is necessary or economical. Retained as an unvalidated capability-calibration difference.
- `case_033`: efficient/low rather than efficient/medium for one supplied-pattern formatter. The low-effort rationale is permitted for brief, bounded implementation; the task leaves some judgment about remaining implementation reasoning. The fixed expectation was not changed.

No combined routing accuracy or first-pass full-suite success is claimed. Final selected configurations have no detected runtime violations; this does not prove optimal model/effort choices or repeatable compliance.

## Limits

This is an instruction/policy change, not a new discovery executable. The previews do not establish a live connection to the current App's `model/list`, real effective-profile resolution, exact UI inventory, upstream model access, or provider-side effort behavior. No Codex/OpenCodex configuration was changed, no App restart was requested, and no hypothetical scenario was dispatched. A host without the necessary introspection interface must disclose that gap and follow the documented fallback rules.

## Full inventory follow-up

Validated on 2026-10-15 against the follow-up policy below. The earlier sections retain their original revision and results. This change explicitly separates abbreviated tool advertisements from exclusive acceptance limits, preserves full pagination/hidden entries and per-model effort metadata, and separates connection-provider evidence from upstream associations. No production model table, gateway adapter or discovery executable was added.

Policy and fixture SHA-256:

- `SKILL.md`: `26938c67f1f0bad1ca3d4d1e5d32fd7fd0fe7975795bc58e0ac098c93a004ba8`
- `references/model-routing.md`: `c81c5eb92d817be04d49dec1480a0419ab5b8307503b04a9b1c57183c6d083d5`
- `tests/routing_cases.json`: `0def25a627046b990b7fec1e7ca057782e2c587a009cf35d32624b4bd2529591`

Validation:

- Offline suite: 68 tests passed. Skill structure, local documentation links and `git diff --check` passed.
- One fresh-context evaluator used inherited model/effort without overrides, read only policy/public prompts, and produced 65 routing and 20 cooperation decisions. No invalid first outputs, format repairs or semantic repairs. The exact effective evaluator model/effort was not independently established from an execution receipt.
- Routing rules: 53/53 fixed expectations matched; autonomous routing: 11/12. All 57 selected configurations passed runtime legality. Eight blocked decisions were reviewed separately; their explanations respected pins, closed enums, unavailable controls, unconfirmed support and refreshed permissions. All eight discovery cases (`062`–`069`) and their reasons passed.
- One existing calibration difference remains: `case_029` selected efficient/low rather than efficient/medium for connecting a settled cancellation service with direct state-return checks. Its reason follows the policy's narrow-invocation allowance; no runtime constraint was violated. The fixed expectation was preserved. No full-suite or combined-accuracy pass is claimed.
- Cooperation: 20/20 fixed expectations and reasons accepted; six new-agent routes passed runtime legality. Proportionate-work cases c15–c17 and boundary cases c18–c20 each passed 3/3. The coordinator reviewed all routing/cooperation reasons.
- A separate supplied two-page inventory scenario retained all seven models, including a hidden model with unknown efforts. It selected a sixth, unadvertised model by exact ID using the supplied full-catalog validation contract; no execution was attempted. The coordinator compared every row's ID, effort/default and visibility with the supplied source and checked that upstream identity stayed unknown. This tests interpretation of paginated evidence, not a live pagination client.
- Actual configured-file discovery read the root Codex configuration's referenced catalog and retained all 13 file entries: seven visible, six hidden. The coordinator compared every ID, display name, effort list/default and visibility against the source file. Opus and Sonnet remained in inventory with unconfirmed eligibility, rather than being rejected because the tool description omitted them. No model-specific trial dispatch was performed.
- The root configuration and catalog provided no explicit model-to-upstream-provider associations. Provider identity remained unknown; this is not proof of a complete upstream provider list. No auth files were read.
- No supported connection to the target App's live `model/list` was exposed. App overrides/effective configuration layers and cached UI inventory were not established. Results prove completeness for the referenced file, not the exact running App inventory.
- Codex and OCX configuration SHA-256 values matched before and after validation. No configuration changes or App restarts occurred.

Raw prompts, predictions, inventory snapshots, score reports, config fingerprints and coordinator comparisons were retained in the local task's `outputs/fox-orchestrate-full-inventory/` directory. These are session evidence, not a persistent skill model registry.

## Current-session provider default

The final policy defaults automatic model selection and fallback to the current session model's upstream provider. Explicit user model/provider selections override this boundary for the specified assignment. Unknown upstream ownership preserves the current route when supported; a gateway label does not establish provider identity. Model and effort remain task-specific within this boundary.

- Offline suite: 68 tests passed; skill structure, local documentation links and whitespace checks passed.
- Fresh GPT-6.1 Sol / medium decision previews: all three structure gates passed first attempt without repair. Five focused provider scenarios and their reasons passed: same-provider defaults in both directions, an explicit cross-provider model pin, no automatic cross-provider fallback, and preserving a confirmed current route with unknown upstream identity.
- Existing rules: 53/53 expectation matches. Autonomous calibration: 11/12, retaining the `case_029` medium-versus-low difference described above without changing its expectation. All 57 selected routing configurations were runtime-valid; eight blocked/inherited explanations were reviewed. Cooperation: 20/20, with all six selected configurations runtime-valid and reasons reviewed.
- Synthetic previews supplied explicit current-provider associations missing from the historical fixtures, except where a case states otherwise. No provider ownership was inferred from fixture IDs.
- Actual App-native dispatch with no user model/provider pin selected GPT-6 Luna / low; runtime context confirmed those settings and OCX recorded three OpenAI requests, all HTTP 200. An explicit Opus pin selected Opus 5.5 / low; runtime context confirmed those settings and OCX recorded two Anthropic requests, all HTTP 200. Both agents actually executed the same Python calculation, returning 391 with exit code 0.
- Codex and OCX configuration fingerprints were unchanged by the live policy test. No service/App restart or alternative CLI backend was used. These two live cases demonstrate the exercised routing decisions, not universal enforcement, task-quality gains or cost savings.

Final policy SHA-256:

- `SKILL.md`: `2866832b5a5a1dbd2023f67293d52a388b7c16a4f94253270075ffe04c396d30`
- `references/model-routing.md`: `df4c5de46fb53b3d90caa3ef5eadc758ca6464511791653858bbea075967a046`
