---
name: anki-leetcode
description: Generate or update one or more LeetCode Anki cards from LeetCode problem URLs, rebuild leetcode.apkg once, and import it into the main Anki collection. Use when the user provides one or more LeetCode problem URLs and wants Anki cards generated or imported.
argument-hint: <leetcode problem url> [more urls...] [card language] [code language]
allowed-tools: Read, Write, Edit, Glob, WebFetch, Bash, AskUserQuestion
---

# anki-leetcode

The user input is: `$ARGUMENTS`

Your job is to turn one or more LeetCode problems into `LeetCode Basic` Anki cards and run the full project workflow:
- bootstrap the hidden `.fox-anki` runtime and `.venv` under `output/anki-leetcode/` if needed
- generate or overwrite one YAML source file per problem
- rebuild `output/anki-leetcode/leetcode.apkg` from the current batch only
- on macOS, if the main Anki collection already has a `LeetCode` deck, merge into that canonical deck before import
- on macOS, import into the main Anki collection once
- if Anki is already running on macOS, ask first; after confirmation, close it, import, then reopen it
- on non-macOS platforms, stop after generating `leetcode.apkg`

## Read the rules first

Before doing anything else, read:
- `references/workflow-rules.md`
- `references/card-example.md`

Follow those rules exactly for paths, naming, deck, tags, language handling, and import behavior.

## Input parsing rules

Parse `$ARGUMENTS` into:
1. one or more LeetCode problem URLs
2. an optional shared card language override for the whole batch
3. an optional shared code language for the whole batch

Rules:
- At least one URL is required.
- Multiple URLs may be separated by spaces or newlines.
- By default, each card should follow the language of its own LeetCode page.
- If the user explicitly specifies a card language, use that language for all cards in the batch instead of the page language.
- The code language is optional and applies to all URLs in the same invocation.
- If the user does not specify a code language, default to `Python 3`.
- Store the YAML metadata using a machine-friendly code language such as `python`, `java`, `cpp`, `javascript`, `typescript`, or `go`.

## Content generation rules

### Card language

By default, each card must follow the language of its own LeetCode page:
- `leetcode.cn` or Chinese page content → generate that card in Chinese
- `leetcode.com` or English page content → generate that card in English

If the user explicitly specifies a card language in the prompt, that override wins and applies to every generated card in the batch.

### Front

Front must be left-aligned HTML and include:
- the bold problem title as a clickable link to the original LeetCode problem URL
- the problem statement
- examples
- constraints / hints

Wrap it like this:

```html
<div style="text-align: left;"> ... </div>
```

### Back

Back must be left-aligned HTML and include:
- a short approach summary
- complexity
- the best solution in the selected code language

The section labels must match the final card language.
For example:
- Chinese: `思路`, `复杂度`, `题解（Java）`
- English: `Approach`, `Complexity`, `Solution (Java)`

Write solution code as plain:

```html
<pre><code>...</code></pre>
```

Do not hand-write syntax-highlighting spans. The hidden builder applies syntax highlighting during package generation based on the YAML `code_language` field.

## Steps

1. Read `references/workflow-rules.md` and `references/card-example.md` first.
2. Parse `$ARGUMENTS` using this contract:
   - `<leetcode problem url> [more urls...] [card language] [code language]`
3. Validate that every parsed URL is a `leetcode.cn` or `leetcode.com` problem URL.
4. Run the one-click orchestrator script from the repository root:
   - `python3 "skills/anki-leetcode/scripts/run_anki_leetcode.py" $ARGUMENTS`
5. Preserve the workflow contract while running it:
   - fixed runtime paths under `output/anki-leetcode/.fox-anki/`
   - fixed per-problem YAML paths under `output/anki-leetcode/.anki-leetcode/cards/`
   - bootstrap `fox-anki` from `FOX_ANKI_REPO_PATH` when provided, otherwise from the latest tagged upstream release at `https://github.com/hulz413/fox-anki`
   - reuse existing YAML unless the user explicitly asks to refresh / regenerate / update
   - rebuild `leetcode.apkg` at most once per invocation
   - on macOS, import into the main collection only once per invocation
6. If Anki is already running on macOS and the orchestrator needs to close it before import:
   - ask the user first
   - then rerun the orchestrator with `--close-anki-if-running`
7. Keep the final response short and report only:
   - the generated or updated YAML paths
   - that `leetcode.apkg` was updated
   - whether the main Anki collection was imported
   - whether Anki was closed and reopened

## Extra requirements

- Reuse the existing workflow contract; do not change the skill's external input or output format.
- Do not search for runtime paths or per-problem YAML files during normal execution; use the fixed runtime paths and the exact derived YAML path.
- Each problem must reuse the same per-problem YAML path. Visible tags should be `leetcode` plus official LeetCode topic tags only; note identity is tracked internally via `frontend_id`-based stable GUIDs, and any legacy `leetcode-<id>` tags should be removed after import.
- If the YAML already exists and the user did not ask to refresh or regenerate it, reuse it instead of regenerating the card.
- Run the package rebuild/import flow only once per invocation, not once per problem.
- If all requested problems reused existing YAML files and the user did not explicitly ask to rebuild or import anyway, skip rebuild/import entirely.
- Keep the final response short.
