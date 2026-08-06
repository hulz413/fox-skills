---
name: gen-kids-comic
description: Create colorful, age-appropriate multi-page comics and picture-story books for young children. Use when a user asks to generate a children's comic, serial picture story, 连环画, 漫画绘本, comic panels, or storyboard with characters, dialogue, narration, page and panel planning, image generation, and visual quality checks.
---

# Gen Comic

Create a readable, child-safe illustrated story, not merely a collection of unrelated images. Generate the page artwork with the built-in image generation tool, then add final Chinese dialogue and narration deterministically with `scripts/compose_comic_page.py`.

## Default format for age 3

Unless the user specifies otherwise, make 8 pages with 4 panels per page. Allow 8–12 pages and 4–6 panels per page when requested. Use a left-to-right, top-to-bottom reading order; use varied manga-inspired panel sizes only when they improve pacing. Keep each panel to one clear action and at least one short spoken line or narration; never leave a wordless panel.

Use bright color, thick readable outlines, friendly facial expressions, safe home or fantasy settings, and large high-contrast Chinese text. Target 4–12 Chinese characters per caption when possible. Do not omit dialogue or narration from any panel.

## Workflow

1. Establish the story before generating: protagonist, goal, gentle obstacle, resolution, age-appropriate emotional arc, page count, and panel count. Infer safe defaults when possible; ask only when a missing choice changes the story materially.
2. Write a page-by-page beat sheet before generating. For every panel, define: page and panel number, action, setting/prop, speaker or narrator, text type (dialogue or narration), exact Chinese line, text-box rectangle, and continuity state (clothing, props, time of day, emotion). When dialogue does not fit naturally, add a parent-friendly narration line instead. This sheet is the source of truth for generation and review.
3. Create a compact character-and-world bible: recognizable appearance, palette, recurring props, locations, and prohibited changes. Preserve it in every image prompt.
4. Generate each page as clean artwork. State the exact page number, panel count, desired reading order, panel layout, each panel's action, and intentional open space for its caption. Require thick borders or obvious gutters, no printed text, no speech bubbles with lettering, no logos, and no watermark.
5. Overlay every approved dialogue or narration line with `scripts/compose_comic_page.py`. Use the beat sheet's exact text and rectangles. Keep generated artwork unchanged; write a new final page file rather than overwriting it.
6. Inspect each final page visually before delivery. Check panel count, reading order, exact text, text legibility, continuity, age suitability, and whether every panel advances the story. Regenerate artwork when a panel is missing or continuity is broken; adjust the overlay configuration when text collides, overflows, or lacks contrast.
7. Save all selected pages in an ordered, user-facing folder using zero-padded names such as `01-cover.png`, `02-page.png`. Preserve the beat sheet and overlay configuration beside the artwork. Report the final page paths and summarize the story.

## Panel and dialogue rules

- Use regular grids for calm explanatory scenes. Use one larger panel plus smaller reaction/detail panels for surprise, discovery, or a gentle turn in the story. Do not use confusing diagonal splits or densely packed tiny panels for a three-year-old.
- Put at least one dialogue bubble or narration box in every panel, with sufficient contrast. Overlay the final Chinese text rather than trusting the image model to render it. Keep the wording natural for a parent to read aloud. Prefer short, rhythmic phrases and repetition.
- Show rather than explain: the drawing carries the action; the caption supplies voice, feeling, or a simple prompt.
- Keep a parent/caregiver nearby when the scene involves water, cooking, traffic, heights, or other hazards. Avoid frightening threats, injury, shame, or unsafe imitation.

## Prompt template

Use this structure for each page:

```text
Use case: illustration-story
Asset type: page {N} of a {total}-page colorful Chinese children's comic for a three-year-old
Series bible: {character appearance, palette, setting, recurring props, locked continuity}
Page layout: {landscape or portrait}; exactly {count} panels; {reading order and manga-inspired layout}
Panel 1: {action}; reserve open space at {rectangle} for its caption.
Panel 2: {action}; reserve open space at {rectangle} for its caption.
...
Style: friendly preschool picture-book illustration, saturated but soft colors, clear outlines
Text: do not render lettering; leave the specified caption areas clean for deterministic overlay
Constraints: one action per panel; all panels advance the story; child-safe; no logo or watermark
Avoid: scary imagery, clutter, tiny panels, garbled text, inconsistent character design
```

## Text overlay

Use `scripts/compose_comic_page.py` after artwork approval. Its JSON configuration contains the exact Chinese text and one rectangle per caption. Use `kind: "dialogue"` for a white rounded speech bubble and `kind: "narration"` for a pale yellow rounded narration box.

```bash
python scripts/compose_comic_page.py --input page-art.png --config page-text.json --output page-final.png
```

Use a Python environment with Pillow installed. In Codex Desktop, load workspace dependencies and use its bundled Python if the system `python3` lacks Pillow. The configuration shape is:

```json
{
  "captions": [
    {"text": "泡泡真好玩！", "kind": "dialogue", "rect": [60, 50, 360, 150]},
    {"text": "小鸭子游呀游。", "kind": "narration", "rect": [460, 50, 360, 130]}
  ]
}
```

Use pixel rectangles `[x, y, width, height]` that stay within one panel. Review the final PNG at reading size; shorten the line or enlarge its rectangle if the script reports that text cannot fit.

## Delivery checklist

- Deliver 8–12 pages unless the user chooses another length.
- Deliver 4–6 panels on every page, including cover/story pages only when the user explicitly asks for them.
- Verify every panel contains at least one readable dialogue or narration line; reject any wordless panel.
- Verify final text against the beat sheet character by character; do not accept model-rendered Chinese as final copy.
- Verify page dimensions and output format; preserve the ordered source files rather than overwriting earlier accepted pages.
- If the user asks for printing, make a separate print-ready export only after confirming trim size, bleed, and binding direction.
