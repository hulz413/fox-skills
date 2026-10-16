# Fox Orchestrate experiment archive

This repository-only archive preserves the standalone Jev context filter and frozen experiments formerly shipped under `skills/fox-orchestrate`. None is enabled by the skill. Install `skills/fox-orchestrate` without this archive; offline experiment checks are separate from runtime-skill checks.

- [Helper guide](references/jev-context-filter.md): explicit external calls, fallback behavior and evaluation limits.
- `tests/experiments/*/PROTOCOL.md`, `REPORT.md` and retained receipts: historical protocols, results and raw evidence.

The frozen experiment files are moved byte-for-byte, including historical paths, source hashes and incomplete or failed runs. Relocation does not make those results current or authorize more service calls. Do not rewrite frozen manifests or regenerate evidence in place. Reproducing a historical run requires its recorded source revision and original inputs; use a separate authorized working directory and new output locations.

Run the helper's offline checks from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/fox-orchestrate/tests -p 'test_*.py'
```

This command makes no external calls. The live evaluation command in the helper guide remains an explicit paid API call.
