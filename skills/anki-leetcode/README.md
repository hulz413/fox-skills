# anki-leetcode

Generate or update one or more LeetCode Anki cards from LeetCode problem URLs, rebuild `leetcode.apkg`, and optionally import the package into your main Anki collection using a dedicated `LeetCode Basic` note type.

This skill is built on top of my own [`fox-anki`](https://github.com/hulz413/fox-anki) Anki CLI.

This skill is designed around the workflow described in `SKILL.md`, `references/workflow-rules.md`, and the helper scripts in `scripts/`. The primary entrypoint is `scripts/run_anki_leetcode.py`, which orchestrates fetch / reuse / rebuild / import end to end.

## What it does

- accepts one or more LeetCode problem URLs
- fetches the problem content from `leetcode.com` or `leetcode.cn`
- generates one YAML source file per problem, and can reuse existing YAML on repeated runs
- rebuilds `output/anki-leetcode/leetcode.apkg` only when card data changed or the user explicitly asks to rebuild
- on macOS, can import the package into the main Anki collection
- if Anki is already running on macOS, asks before closing and reopening it

## Requirements

- a skill runner that can execute `SKILL.md` style skills
- Python 3.11 or newer
- access to LeetCode problem pages
- Anki installed if you want the macOS import flow
- write access to the current working directory so the skill can create `output/anki-leetcode/`

## Install

A simple install flow is:

1. Copy this folder into your local skills directory.
2. Make sure the main skill file is available as `anki-leetcode/SKILL.md`.
3. Keep the bundled `references/` and `scripts/` directories alongside it.
4. During local development, set `FOX_ANKI_REPO_PATH=~/Developer/SideProjects/fox-anki` so bootstrap uses your local fox-anki repo.
5. Run the skill from the working directory where you want `output/anki-leetcode/` to be created.

For Claude Code-style setups, that usually means placing this folder under your local skills path, for example:

```text
.claude/skills/anki-leetcode/
├── README.md
├── SKILL.md
├── references/
└── scripts/
```

On first run, the skill bootstraps fox-anki into `output/anki-leetcode/.fox-anki`, creates its virtual environment there, and writes hidden card YAML / batch files under `output/anki-leetcode/.anki-leetcode`.

Bootstrap source selection:
- if `FOX_ANKI_REPO_PATH` is set, use that local repo's current working tree
- otherwise resolve the latest git tag from `https://github.com/hulz413/fox-anki` and bootstrap from that upstream release

## Usage

Invoke the skill with one or more LeetCode problem URLs.

The one-click orchestrator is:

```text
skills/anki-leetcode/scripts/run_anki_leetcode.py
```

Typical argument shape:

```text
<leetcode problem url> [more urls...] [card language] [code language]
```

Examples:

```text
anki-leetcode https://leetcode.com/problems/two-sum/
anki-leetcode https://leetcode.com/problems/two-sum/ zh-CN java
anki-leetcode https://leetcode.com/problems/two-sum/ https://leetcode.com/problems/add-two-numbers/ en python
FOX_ANKI_REPO_PATH=~/Developer/SideProjects/fox-anki python3 skills/anki-leetcode/scripts/run_anki_leetcode.py https://leetcode.cn/problems/3sum/description/
FOX_ANKI_REPO_PATH=~/Developer/SideProjects/fox-anki python3 skills/anki-leetcode/scripts/run_anki_leetcode.py https://leetcode.cn/problems/3sum/description/ --refresh
```

Behavior summary:

- if no card language is given, each card follows the language of its problem page
- if no code language is given, the skill defaults to Python 3 / `python`
- runtime artifacts are written under `output/anki-leetcode/` in the current working directory
- hidden per-problem YAML and batch files live under `output/anki-leetcode/.anki-leetcode/`
- cards are built with the dedicated `LeetCode Basic` note type to avoid stock `Basic` / `Basic+` drift
- the orchestrator script automatically bootstraps the hidden runtime from `FOX_ANKI_REPO_PATH` when provided, otherwise from the latest tagged upstream `fox-anki` release; it reuses existing YAML when possible and only rebuilds once per invocation
- rebuilds are based on the current batch only, not on a long-lived sandbox collection
- on macOS, the skill can automatically import the rebuilt package into the main Anki collection, normalize `LeetCode Basic` note type variants back to the canonical model, and update the existing note for the same `leetcode-<id>` instead of conflicting
- if nothing changed and the user did not explicitly ask to rebuild or import, the skill can skip rebuild/import work entirely
- on non-macOS platforms, the workflow stops after rebuilding `leetcode.apkg`, and you need to import the package manually

## Implementation notes

- `fox-anki` handles collection-facing APKG import and export operations.
- The skill keeps LeetCode-specific behavior in its own scripts, including code block highlighting, stable LeetCode GUID generation, and batch-only package construction.
