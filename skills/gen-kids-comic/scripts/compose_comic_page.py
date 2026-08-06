#!/usr/bin/env python3
"""Overlay exact Chinese dialogue and narration on a comic artwork page.

Config JSON:
{"font": "/optional/font.ttc", "captions": [
  {"text": "泡泡真好玩！", "kind": "dialogue", "rect": [60, 50, 360, 150]}
]}
"""

import argparse
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as error:
    raise SystemExit(
        "Pillow is required. Run this script with a Python environment that has Pillow installed."
    ) from error


DEFAULT_FONTS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]


def font_path(config: dict) -> str:
    candidates = [config.get("font"), *DEFAULT_FONTS]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError("No Chinese font found; pass config.font with a valid font path.")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int):
    lines, current = [], ""
    for char in text:
        candidate = current + char
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def fit_font(draw, text, path, width, height, requested):
    for size in range(requested, 15, -1):
        font = ImageFont.truetype(path, size=size)
        lines = wrap_text(draw, text, font, width)
        line_height = draw.textbbox((0, 0), "测", font=font)[3]
        if len(lines) * int(line_height * 1.25) <= height:
            return font, lines, int(line_height * 1.25)
    raise ValueError(f"Text does not fit its rectangle: {text}")


def draw_caption(draw, caption, path):
    text = caption["text"]
    kind = caption.get("kind", "dialogue")
    if kind not in {"dialogue", "narration"}:
        raise ValueError("caption.kind must be dialogue or narration.")
    rect = caption["rect"]
    if not isinstance(rect, list) or len(rect) != 4:
        raise ValueError("caption.rect must be [x, y, width, height].")
    x, y, width, height = rect
    if width <= 0 or height <= 0:
        raise ValueError("caption.rect width and height must be positive.")
    padding = int(caption.get("padding", max(16, min(width, height) * 0.10)))
    requested = int(caption.get("font_size", min(54, max(26, height * 0.30))))
    font, lines, line_height = fit_font(draw, text, path, width - padding * 2, height - padding * 2, requested)

    fill = "#FFFFFF" if kind == "dialogue" else "#FFF3B0"
    draw.rounded_rectangle((x, y, x + width, y + height), radius=min(28, height // 4), fill=fill, outline="#193A70", width=4)
    text_height = len(lines) * line_height
    cursor_y = y + (height - text_height) // 2
    for line in lines:
        text_width = draw.textbbox((0, 0), line, font=font)[2]
        draw.text((x + (width - text_width) // 2, cursor_y), line, font=font, fill="#172B4D")
        cursor_y += line_height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    captions = config.get("captions", [])
    if not captions:
        raise ValueError("config.captions must contain at least one caption.")

    image = Image.open(args.input).convert("RGB")
    draw = ImageDraw.Draw(image)
    path = font_path(config)
    for caption in captions:
        if not {"text", "rect"}.issubset(caption):
            raise ValueError("Every caption requires text and rect.")
        x, y, width, height = caption["rect"]
        if x < 0 or y < 0 or x + width > image.width or y + height > image.height:
            raise ValueError(f"Caption rectangle lies outside image bounds: {caption['rect']}")
        draw_caption(draw, caption, path)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, "PNG")


if __name__ == "__main__":
    main()
