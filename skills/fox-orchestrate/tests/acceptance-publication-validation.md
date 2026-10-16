# Acceptance publication validation

Date: 2026-10-15. Result: scoped validation passed: 90 offline tests, including six publication tests, plus an isolated publication replay using retained invocation/decision metadata. No new CC worker invocations were made for this fix or documentation follow-up. This report distinguishes controlled filesystem concurrency, sequential CLI checks and replay from fresh task execution or crash testing.

## Artifact and regression evidence

- Implementation commit: `636cd3514fdfcb7acc48683bcb5d84a9e2272509`.
- Runner SHA-256, matching the replay receipt and committed implementation: `5c3bd04456e9fd23487efb59020dbcad060dd66a7b59763ff87ae3860592355e`.
- Pre-fix base: `df24fb5b48c5cecd20f8208413dbb285e6c2995e`. The concurrent-reader regression test failed with `JSONDecodeError`: the old writer created the public file before serializing its contents, allowing a reader to see an empty decision.
- The fix writes a unique same-directory temporary file, closes it, then publishes with a hard link that cannot replace an existing directory entry. Only the `record_acceptance` function body and a standard-library import changed in the runner; execution, acceptance guards, summaries and token rules were unchanged.
- Contract: [CLI recording and acceptance](../references/cc-records.md#invocation-records-and-acceptance). Tests: [test_acceptance_publication.py](test_acceptance_publication.py).

## Offline coverage

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s skills/fox-orchestrate/tests -p 'test_*.py' -v
```

The full suite passed 90 tests: the previous 84 plus six publication test methods. The focused six-test suite also passed after the pre-fix reader failure. Counts are test methods, not worker invocations, stress iterations or sampled race schedules. Tests use local synthetic records, threads, Python CLI subprocesses and fault injection without CC/service calls.

| Area | Controlled setup and observed result |
| --- | --- |
| Concurrent reading | A writer thread is paused at JSON serialization while the coordinator reads both invocation and task summaries. The public `acceptance.json` remains absent and summaries report pending; after releasing the writer, invocation acceptance is passed. Selecting the newly published record then returns the complete task acceptance metadata. No empty public record is read. |
| Competing publication | Two writer threads prepare distinct candidates and meet at a barrier before invoking the real `os.link`. Both temporary candidates are already readable JSON. Exactly one writer succeeds and one raises `FileExistsError`; the final JSON matches the winning candidate's outcome, artifact reference and evidence path. Both writers' temporary paths are cleaned up. |
| Repeated CLI writing | Two sequential `record-acceptance` subprocesses target the same directory. The first passed decision exits 0; the second requests a failed decision with a different artifact reference, exits 1 with `FileExistsError` and emits no stdout. Original decision bytes and passed summary outcome remain unchanged. |
| Partial-write failure | A wrapper writes the first ten characters to the private temporary file, then raises `OSError`. No public decision is created, the invocation summary remains pending and the temporary file is removed. |
| Publication failure | Injected `OSError` from `os.link`, before a link is created, leaves neither a public decision nor a temporary file. This tests handled-error cleanup, not a real unsupported-filesystem or disk-failure event. |
| Existing symlink | A dangling symlink already occupying `acceptance.json` causes `FileExistsError`; the symlink and its target path remain unchanged, and the new temporary file is removed. |

Thread events/barriers make the relevant interleavings deterministic. The filesystem performs the actual successful link operations; this is not a multi-process contention benchmark or exhaustive scheduling proof. Cleanup assertions also cover normal success, competing writers and duplicate writes. The existing suite continues to check invalid acceptance rejection, immutable earlier decisions, task selection and token behavior.

## Isolated retained-record publication replay

The coordinator copied the saved A/turn-1 `status.json` and `summary.json` from the [earlier fan-out run](batch-fan-out-validation.md) into a new isolated directory. Its prior decision metadata and existing evidence-file reference were supplied to the new writer. This replay exercised local Python CLI record/summary commands; it did not replay the raw event stream, invoke CC, rerun checks or reassess the original business artifact.

| Check | Observed result |
| --- | --- |
| First publication | CLI exit 0; parsed published record equals the retained decision metadata |
| Duplicate publication | A subsequent failed-decision request exits 1 with `FileExistsError`; stdout is empty and published bytes are unchanged |
| Reader compatibility | Invocation summary still reports passed |
| Cleanup | No `.acceptance-*.tmp` files remain in the isolated directory |
| Source preservation | Hashes of the three original status/summary/acceptance files and the referenced evidence file remain unchanged |
| Worker activity | Zero new CC/model invocations |

The originating chat retains `work/acceptance-publication-validation/` with the isolated records and receipt; originals remain under `work/fan-out-live-20261015/`. These local files are not repository dependencies or a portable replay fixture. Raw session identifiers and absolute local paths are not copied here. Replay records compatibility and preservation, not a new artifact acceptance result or model/provider configuration attestation.

## Not verified

- Multiple independent CLI processes contending simultaneously, high writer counts, exhaustive race schedules, large records or sustained reader stress. Concurrency coverage above uses threads and a real local filesystem; CLI duplicate/replay calls are sequential.
- SIGKILL, machine/power failure, `fsync` durability, crash recovery or cleanup of files left by abrupt termination. Atomic publication visibility does not guarantee power-loss persistence; abrupt termination can leave an unpublished temporary file.
- Real filesystem refusal, permission changes, disk-full events, close/cleanup failures, network filesystems or portability across environments. Link/write failures above were injected; the publication path requires hard-link support and has no overwrite fallback.
- Atomic snapshots across status, acceptance, evidence and task-index files, or simultaneous modification of those inputs. Existing malformed acceptance files are not repaired or overwritten by this fix.
- Artifact/evidence content correctness, recorded evidence-digest binding, changed-input applicability, new worker execution, fresh business acceptance or same-session repair. The coordinator still owns acceptance; execution and acceptance remain separate.
- New scheduling/retry behavior, routing/cooperation model previews or an independent reviewer/worker repair loop. No scheduling, retry or model-selection logic changed.

See [validation entrypoint](README.md) and [task summary validation](task-summary-validation.md) for adjacent coverage. Historical reports retain their original artifacts, counts and limits.
