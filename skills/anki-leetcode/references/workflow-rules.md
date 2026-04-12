# LeetCode → Anki workflow rules

## Primary entrypoint

- Preferred one-click entrypoint: `<cwd>/skills/anki-leetcode/scripts/run_anki_leetcode.py`
- `bootstrap_fox_anki.py`, `build_leetcode_apkg.py`, and `merge_leetcode_deck.py` are internal helpers used by the orchestrator.

## Fixed paths

- Runtime root: `<cwd>/output/anki-leetcode/`
- Hidden runtime: `<cwd>/output/anki-leetcode/.fox-anki/`
- Hidden CLI: `<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/fox-anki`
- Hidden Python: `<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/python`
- Card YAML directory: `<cwd>/output/anki-leetcode/.anki-leetcode/cards/`
- Final package: `<cwd>/output/anki-leetcode/leetcode.apkg`
- Main Anki collection: `~/Library/Application Support/Anki2/User 1/collection.anki2`
- Bootstrap script: `skills/anki-leetcode/scripts/bootstrap_fox_anki.py`
- Package build script: `skills/anki-leetcode/scripts/build_leetcode_apkg.py`
- Temporary batch YAML directory: `<cwd>/output/anki-leetcode/.anki-leetcode/`
- Temporary build collection: `<cwd>/output/anki-leetcode/.fox-anki/build-current/collection.anki2`

## Bootstrap rules

- Use these runtime paths directly during normal execution:
  - `<cwd>/output/anki-leetcode/.fox-anki/`
  - `<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/python`
  - `<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/fox-anki`
- Do not search for `.fox-anki`, `.venv`, or related runtime files during normal execution.
- If the hidden `.fox-anki/` runtime is missing or `.fox-anki/.venv/` is missing, run the bootstrap script first.
- The bootstrap script will:
  - if `FOX_ANKI_REPO_PATH` is set, sync that local fox-anki repo's current working tree into `<cwd>/output/anki-leetcode/.fox-anki/`
  - otherwise resolve the latest git tag from `https://github.com/hulz413/fox-anki` and sync that tagged upstream source into `<cwd>/output/anki-leetcode/.fox-anki/`
  - rebuild `.venv`
  - install:
    - `anki==25.9.2`
    - `PyYAML`
    - `Pygments`
    - the editable hidden `fox-anki` package
- Current development default: `FOX_ANKI_REPO_PATH=~/Developer/SideProjects/fox-anki`
- Remote bootstrap requires `git` to be available.
- The bootstrap script must be safe to run repeatedly. Repeat runs should repair missing pieces without destroying the existing runtime environment.

## Batch input rules

- One invocation may include one or more LeetCode problem URLs.
- Multiple URLs may be separated by spaces or newlines.
- One optional shared card language override may be provided for the whole batch.
- One optional shared code language may be provided for the whole batch.
- By default, each card should follow the language of its own LeetCode page.
- If the user explicitly specifies a card language, that override wins and applies to every generated card in the batch.
- If no code language is specified, default to `python` (Python 3 syntax) for every generated card in that batch.

## Card rules

- Note type: `LeetCode Basic`
- Deck: `LeetCode`
- Both Front and Back must be left-aligned using:
  - `<div style="text-align: left;"> ... </div>`
- By default, the card language must follow the LeetCode problem page language for each problem independently:
  - `leetcode.cn` or Chinese page content → Chinese card
  - `leetcode.com` or English page content → English card
- If the user explicitly specifies a card language, use that language for all cards in the batch instead.
- Front content must include:
  - the bold problem title, without the leading LeetCode problem number, and linked to the original LeetCode problem URL
  - the problem statement
  - examples
  - constraints / hints
- Back content must include:
  - a short approach summary
  - complexity
  - the best solution in the selected code language
- Solution code in the YAML must remain plain:
  - `<pre><code>...</code></pre>`
  - do not hand-write highlighted `<span ...>` markup
  - the hidden builder will add syntax highlighting during package generation
- Add a top-level `code_language` field to generated YAML.
  - If the user specifies a code language, use it.
  - Otherwise default to `python`.

## Tag rules

- Every card must include:
  - `leetcode`
  - `leetcode-<frontend id>`
- Add 2–4 English algorithm tags where appropriate, such as:
  - `array`
  - `two-pointers`
  - `hash-table`
  - `sliding-window`
  - `sorting`
  - `string`
  - `intervals`

## File naming rules

- Per-problem YAML file path:
  - `<cwd>/output/anki-leetcode/.anki-leetcode/cards/leetcode_<id>_<slug>.yaml`
- Prefer the slug from the problem page or URL.
- Use lowercase in filenames and replace `-` with `_`.
- The same problem must always map to the same per-problem YAML file.
- Use the exact derived YAML path directly; do not search for alternate candidate files during normal execution.
- If that YAML file already exists and the user did not explicitly ask to refresh or regenerate it, reuse it instead of rewriting it.
- For a multi-problem invocation, create one temporary hidden batch YAML under `<cwd>/output/anki-leetcode/.anki-leetcode/` only if at least one card was newly generated or updated, or if the user explicitly asked to rebuild anyway.

## Rebuild command

Run once per invocation:

```bash
"<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/python" "skills/anki-leetcode/scripts/build_leetcode_apkg.py" \
  "<batchYamlPath>" \
  "<cwd>/output/anki-leetcode/leetcode.apkg" \
  --deck "LeetCode"
```

This rebuild must use a fresh temporary collection for the current batch only, rather than a persistent sandbox collection.

## Import into the main Anki collection

This app-import step is **macOS-only**.

- On **macOS**:
  - Before importing, resolve the canonical target deck in the main collection.
  - If a deck named exactly `LeetCode` already exists, reuse and merge into that deck.
  - If LeetCode-related edge-case decks actually exist and should be consolidated first, run:

```bash
"<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/python" "skills/anki-leetcode/scripts/merge_leetcode_deck.py" \
  --collection "~/Library/Application Support/Anki2/User 1/collection.anki2"
```

  - That helper script must move cards from `LeetCode`-related edge-case decks into the canonical `LeetCode` deck and remove the emptied decks before importing.
  - If no exact-name `LeetCode` deck exists, let the import create it normally.
  - Then use the hidden CLI once per invocation:

```bash
"<cwd>/output/anki-leetcode/.fox-anki/.venv/bin/fox-anki" import apkg \
  "<cwd>/output/anki-leetcode/leetcode.apkg" \
  --merge-notetypes \
  --update-notes always \
  --update-notetypes always \
  --collection "~/Library/Application Support/Anki2/User 1/collection.anki2"
```

- On **non-macOS platforms**:
  - do not attempt to import into the Anki app or collection
  - do not attempt deck merge, Anki close, or Anki reopen
  - stop after rebuilding `<cwd>/output/anki-leetcode/leetcode.apkg`

## When Anki is already open

This section applies on **macOS only**.

1. Detect it first with `ps aux | grep '[A]nki'`
2. If Anki is running, ask the user before continuing
3. After confirmation:
   - run `osascript -e 'tell application "Anki" to quit' || true`
   - keep checking with `ps aux | grep '[A]nki'` until the process is actually gone
   - even if AppleScript returns `User canceled (-128)`, continue if process checks confirm that Anki really exited
4. After the import completes, run `open -a Anki`
5. In a batch invocation, do this close/import/reopen flow only once

## Dedupe / stability rules

- Notes are deduped by the `leetcode-<id>` tag and stable GUIDs derived from those tags
- Re-importing the same problem should replace the old note instead of creating duplicates
- This dedupe behavior must still hold inside a multi-problem batch
- After import, normalize any `LeetCode Basic+`-style note type variants back to the canonical `LeetCode Basic` model when their schema is compatible
- If the main collection already contains a canonical `LeetCode` deck, imports should merge into that existing deck instead of creating a parallel one

## Final reply

Keep the final reply short and report only:
- the generated or updated YAML paths
- that `leetcode.apkg` was updated
- whether the main Anki collection was imported
- whether Anki was closed and reopened
