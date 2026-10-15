# Acceptance evidence binding validation

Date: 2026-10-15. Result: scoped validation passed: 97 offline tests, including seven evidence-binding test methods, plus retained-record compatibility checks and an isolated evidence-binding replay. No new CC worker invocations were made for implementation or this documentation follow-up. Replay used local record/summary commands, not fresh worker execution or new business acceptance.

## Tested artifact and evidence

- Implementation commit: `2c9170013226102efa3ec52e26ec821a9b74ea1e`.
- Runner SHA-256, matching the retained replay receipt and committed implementation: `18bb0460429a8008daf737e496ad9e061c37b552c571ba9d078d688cb547beeb`.
- Compatibility base: `ae4a710` (the implementation before content binding).
- Contract: [CLI recording and summaries](../references/claude-code-cli.md#lightweight-records-and-summaries) and [task summaries](../references/claude-code-cli.md#task-summaries). Focused checks: [test_evidence_binding.py](test_evidence_binding.py); publication and selection regressions: [test_acceptance_publication.py](test_acceptance_publication.py) and [test_task_summary.py](test_task_summary.py).
- New decisions store a raw-byte SHA-256 alongside the evidence path. Invocation readers compute integrity once and selected task metadata reuses that result. Execution, acceptance guards, task selection and token rules remain separate from integrity.

## Offline coverage

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s skills/fox-orchestrate/tests -p 'test_*.py' -v
```

The full suite passed 97 tests: the previous 90 plus seven evidence-binding test methods with subcases. These are test-method counts, not worker calls, independent live trials or stress iterations. Tests use synthetic local records, Python CLI subprocesses and fault injection; they do not call CC or services.

| Area | Offline coverage and boundary |
| --- | --- |
| Raw-byte binding | A multi-block binary fixture includes non-UTF-8 bytes and CRLF. The writer's stored digest matches SHA-256 of the original bytes; changing only line endings produces a mismatch. Task rows and selected acceptance reuse one digest computation per invocation. |
| No decision / legacy | No decision yields `evidence_integrity: null` and pending acceptance. A legacy decision without the digest field yields `unbound` even after evidence deletion; a patched digest function confirms legacy evidence is not read. No backfill or record mutation occurs. |
| Bound evidence states | Unchanged bytes yield `matched`, changed bytes `mismatch`, deletion `missing`, and replacement by a directory `unreadable`. An injected `PermissionError` also yields `unreadable` in the invocation reader; this is not a real filesystem-permission trial. |
| Historical acceptance | For both passed and failed decisions on completed executions, integrity changes preserve the original outcome, selected run, acceptance counts, execution-reason counts and known token totals. Evidence problems are not execution failures or new acceptance decisions. Protected status/summary/acceptance/index bytes remain unchanged. |
| Mixed history and selection | A legacy passed call, bound rejected call with changed evidence, and pending call remain distinct. Null, explicitly selected legacy and explicitly selected rejected snapshots retain the existing selection behavior; all three calls contribute tokens regardless of selection or integrity. |
| Invalid digest records | Present but null, non-string, empty, wrong-length, uppercase, non-hex or newline-suffixed digests fail both summary CLIs with exit 1 and no partial stdout/traceback. Only an absent field is legacy-compatible. |
| Write failures | Missing evidence, a directory, and injected hashing permission failure publish no acceptance and leave no acceptance temporary files; summary remains pending. Existing publication tests continue to cover complete concurrent publication, collision/duplicate rejection and write/link failure cleanup. |
| CLI and privacy | Both summary CLIs exit 0 for `matched`, `mismatch` and `missing`, exposing status without evidence bodies. A process-launch guard confirms task summaries start no worker/checker; read-only fixture hashes remain unchanged. Directory/permission `unreadable` branches above are helper-level checks. |

The existing suite also retains unfinished/unsuccessful-execution acceptance guards, explicit task ownership/selection, partial and unknown token rules, failed-call consumption and publication safeguards. Integrity adds no aggregate validity count, automatic reselection or token filtering; the new integrity-transition cases use known usage, while partial/unknown usage retains its existing separate regression coverage.

## Retained-record compatibility and isolated replay

The three compact records from the [earlier fan-out run](batch-fan-out-validation.md) were read directly by the new invocation and task summary CLIs. After removing only the added `evidence_integrity` fields from parsed output, both reports equaled results from the pre-binding implementation. All three legacy invocations were `unbound`. Existing explicit selections, task/invocation acceptance counts and token subtotals were preserved; total reported usage remained 43,989 with zero unknown invocations.

For the binding path, the coordinator copied A/turn-1 status, summary and referenced evidence into an isolated directory, then supplied its historical outcome/artifact reference to `record-acceptance`. This records a local replay decision for testing the writer; checks were not rerun and the original business artifact was not reassessed.

| Replay check | Observed result |
| --- | --- |
| First bound publication | CLI exit 0; stored digest equals SHA-256 of the copied evidence |
| Unchanged / changed / deleted evidence | Selected task integrity reports `matched`, `mismatch`, then `missing`; each task-summary CLI exits 0 |
| Acceptance and usage separation | All three observations retain passed acceptance and 15,712 reported tokens with zero unknown invocations; published decision bytes remain unchanged |
| Duplicate publication | Sequential repeat exits 1 with `FileExistsError`, emits no stdout and preserves the original bound decision |
| Cleanup and source preservation | No acceptance temporary files remain; hashes of nine original status/summary/acceptance files and three referenced evidence files remain unchanged |
| Worker activity | Zero new CC worker invocations; no raw-event replay, checker execution or business acceptance |

The originating chat retains `work/evidence-binding-validation/` with the receipt, offline test log, replay harness, compatibility summary and isolated records; source records remain under `work/fan-out-live-20261015/`. These local files are not repository dependencies or a portable fixture. Raw session identifiers and absolute local paths are not copied here. Implementation changes are additive summary metadata, not a claim that the old and new JSON outputs are byte-identical.

## Not verified

- Fresh CC execution, new task quality/acceptance, same-session repair, model/effort/provider attestation or routing/cooperation previews. Historical live results retain their original scope; these checks invoke no worker or scheduler.
- Retained-record replay of `unreadable`, invalid digests, pending/null selections, selected failed decisions or partial/unknown tokens. Those cases have the offline coverage above; the isolated replay uses a passed completed invocation with complete usage.
- Concurrent evidence mutation, pathname/symlink replacement while hashing, cross-file atomic snapshots, crash consistency, SIGKILL/power loss or durable recovery. Hashing records bytes read, and files can change during or after reading; evidence must be finalized before acceptance.
- Real OS permission refusal, mid-read I/O failure, disk-full conditions, network filesystems, other platforms/CLI versions, very large evidence performance or high-concurrency stress. The permission cases inject an exception; binary multi-block coverage is not a resource benchmark.
- Check correctness, current artifact/input applicability, authenticity or protection against coordinated changes to evidence and its recorded digest. `matched` proves only equality with the stored digest for bytes read; it does not validate the artifact or turn a historical pass into current acceptance. Old decisions remain unbound, without automatic migration.
- New dispatch/retry behavior, automatic reselection or an independent reviewer/worker repair loop. None was introduced or evaluated.

See the [validation entrypoint](README.md), [publication validation](acceptance-publication-validation.md) and [task summary validation](task-summary-validation.md). Earlier reports retain their historical counts and unverified items.
