English | [简体中文](README.zh-CN.md)

# fox-skills

A collection of my personal AI skills.

This repo is intentionally simple: each skill lives in its own folder, with a user-facing `README.md` and a canonical `SKILL.md` entrypoint.

## Repository layout

```text
fox-skills/
├── README.md
├── README.zh-CN.md
├── .gitignore
├── skills/
│   └── <skill-id>/
│       ├── README.md
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── assets/
└── .github/
    └── workflows/
        └── validate.yml
```

## Skill format

Each skill folder can contain a few focused files:

- `skills/<skill-id>/README.md` — user-facing overview, install, and usage
- `skills/<skill-id>/SKILL.md` — canonical skill instructions / entrypoint
- `skills/<skill-id>/references/` — rules, examples, or supporting docs
- `skills/<skill-id>/scripts/` — helper scripts if the skill needs them
- `skills/<skill-id>/assets/` — bundled support files or vendor patches when needed

## How to add a new skill

1. Create `skills/<your-skill-id>/`.
2. Add `README.md` for human-facing install and usage notes.
3. Add `SKILL.md` as the main skill entrypoint.
4. Add `references/`, `scripts/`, or `assets/` only if the skill actually needs them.

## Skills

For installation and usage details, see the `README.md` inside each skill folder.

- [`anki-leetcode`](skills/anki-leetcode/README.md) — Generate or update LeetCode Anki cards, rebuild `leetcode.apkg`, and optionally import into the main Anki collection.

## Compatibility

This repo does not keep a separate compatibility framework.

If a skill is meant for a specific runtime or agent, document that directly inside the skill's own `README.md` or `SKILL.md`.

## Validation

A small GitHub Actions workflow checks the minimal structure:

- `README.md`
- `README.zh-CN.md`
- every first-level folder under `skills/` contains `README.md`
- every first-level folder under `skills/` contains `SKILL.md`

## Notes

- This repository is for sharing skills, not building a full framework.
- Keep each skill easy to read directly on GitHub.
- Add a real `LICENSE` before publishing publicly.
