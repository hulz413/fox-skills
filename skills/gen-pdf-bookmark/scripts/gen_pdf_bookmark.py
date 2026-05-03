#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import Fit
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing Python package 'pypdf'. Use Codex bundled Python or install pypdf."
    ) from exc


EXISTING_OUTLINE_EXIT = 3
RADICAL_MAP = str.maketrans(
    {
        "⺟": "母",
        "⺠": "民",
        "⻄": "西",
        "⻅": "见",
        "⻆": "角",
        "⻋": "车",
        "⻓": "长",
        "⻔": "门",
        "⻚": "页",
        "⻛": "风",
        "⻜": "飞",
        "⻣": "骨",
        "⻩": "黄",
        "⻬": "齐",
    }
)


@dataclass
class TextLine:
    page: int
    top: int
    left: int
    max_size: int
    min_size: int
    text: str


@dataclass
class Bookmark:
    level: int
    title: str
    page: int
    top: int


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(RADICAL_MAP)
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(\d+)\s+\.(\d+)", r"\1.\2", text)
    text = re.sub(r"^(\d+)\s+\.\s*", r"\1. ", text)
    text = re.sub(r"^(\d+\.)(?=[^\d\s])", r"\1 ", text)
    text = re.sub(r"^(\d+\.\d+)(?=[^\d\.\s])", r"\1 ", text)
    text = re.sub(r"^(Q\d+)\s*[:：]\s*", r"\1：", text)
    text = re.sub(r"^(第[一二三四五六七八九十百]+[章节卷篇部分类])[:：]\s*", r"\1：", text)
    text = re.sub(r"^(附录?|小结|结语)\s*[:：]\s*", r"\1：", text)
    text = re.sub(r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])\s*:\s*", "：", text)
    return text


def outline_count(outline: Iterable[object]) -> int:
    total = 0
    for item in outline:
        total += outline_count(item) if isinstance(item, list) else 1
    return total


def extract_xml(pdf_path: Path, work_dir: Path) -> Path:
    if not shutil.which("pdftohtml"):
        raise SystemExit("Missing 'pdftohtml'. Install Poppler or provide --xml.")
    prefix = work_dir / "pdf-layout"
    cmd = ["pdftohtml", "-xml", "-i", "-enc", "UTF-8", str(pdf_path), str(prefix)]
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    xml_path = prefix.with_suffix(".xml")
    if result.returncode != 0 or not xml_path.exists():
        raise SystemExit(
            "pdftohtml failed while extracting layout XML.\n"
            + result.stdout
            + result.stderr
        )
    return xml_path


def parse_lines(xml_path: Path) -> list[TextLine]:
    root = ET.parse(xml_path).getroot()
    fonts = {fs.attrib["id"]: int(float(fs.attrib["size"])) for fs in root.iter("fontspec")}
    lines: list[TextLine] = []

    for page in root.findall("page"):
        page_number = int(page.attrib["number"])
        items: list[tuple[int, int, int, str]] = []
        for node in page.findall("text"):
            text = clean_text("".join(node.itertext()))
            if not text:
                continue
            items.append(
                (
                    int(float(node.attrib["top"])),
                    int(float(node.attrib["left"])),
                    fonts[node.attrib["font"]],
                    text,
                )
            )

        items.sort(key=lambda item: (item[0], item[1]))
        grouped: list[tuple[int, list[tuple[int, int, int, str]]]] = []
        for item in items:
            top = item[0]
            if grouped and abs(top - grouped[-1][0]) <= 4:
                grouped[-1][1].append(item)
                grouped[-1] = (min(grouped[-1][0], top), grouped[-1][1])
            else:
                grouped.append((top, [item]))

        for top, group in grouped:
            group = sorted(group, key=lambda item: item[1])
            text = clean_text("".join(item[3] for item in group))
            if not text:
                continue
            sizes = [item[2] for item in group]
            lines.append(
                TextLine(
                    page=page_number,
                    top=top,
                    left=min(item[1] for item in group),
                    max_size=max(sizes),
                    min_size=min(sizes),
                    text=text,
                )
            )
    return lines


def body_font_size(lines: list[TextLine]) -> int:
    counts = Counter(line.max_size for line in lines if len(line.text) >= 12)
    if counts:
        return counts.most_common(1)[0][0]
    return Counter(line.max_size for line in lines).most_common(1)[0][0]


def starts_new_heading(text: str) -> bool:
    return bool(
        re.match(
            r"^(\d{1,2}\s+\S|\d+\.\s|\d+\.\d+|Q\d+：|第[一二三四五六七八九十百]+[章节卷篇部分类]：|目录$|本篇目录$|附录|小结|结语)",
            text,
        )
    )


def looks_like_heading(line: TextLine, body_size: int) -> bool:
    text = line.text
    if len(text) > 120:
        return False
    if re.fullmatch(r"\d+", text):
        return False
    if text.lower() in {"bash", "python", "java", "go", "json", "yaml", "sql"}:
        return False
    if starts_new_heading(text):
        return line.max_size >= max(10, body_size - 1)
    if re.search(r"(指南|目录|总目录|分析|笔记|问答集|面试稿|全攻略)", text) and line.max_size >= body_size + 4:
        return True
    return line.max_size >= body_size + 3


def merge_wrapped(lines: list[TextLine]) -> list[TextLine]:
    merged: list[TextLine] = []
    for line in lines:
        if not merged:
            merged.append(line)
            continue
        prev = merged[-1]
        same_visual_heading = (
            line.page == prev.page
            and 12 <= line.top - prev.top <= 70
            and abs(line.max_size - prev.max_size) <= 1
            and not starts_new_heading(line.text)
            and not prev.text.endswith(("。", "？", "?", "！", "!", "）", ")"))
        )
        wrapped_question = (
            line.page == prev.page
            and prev.text.startswith("Q")
            and not starts_new_heading(line.text)
            and 12 <= line.top - prev.top <= 70
        )
        if same_visual_heading or wrapped_question:
            prev.text = clean_text(prev.text + line.text)
            continue
        merged.append(line)
    return merged


def classify_level(line: TextLine, body_size: int) -> int:
    text = line.text
    if re.match(r"^\d{2}\s+\S", text):
        return 1
    if re.match(r"^\d+\.\d+", text):
        return min(6, len(text.split()[0].split(".")) + 1)
    if re.match(r"^\d+\.\s", text):
        return 2
    if line.page == 1 and line.max_size >= body_size + 8:
        return 1
    if re.match(r"^Q\d+：", text):
        return 3
    if re.match(r"^第[一二三四五六七八九十百]+[章节卷篇]", text):
        return 1
    if re.match(r"^第[一二三四五六七八九十百]+[部分类]", text):
        return 2
    if text in {"目录", "本篇目录"}:
        return 2
    if re.match(r"^(附录|小结|结语)", text):
        return 2
    if line.max_size >= body_size + 10 and line.top < 180:
        return 1
    if line.max_size >= body_size + 10:
        return 2
    return 3


def build_bookmarks(xml_path: Path) -> list[Bookmark]:
    lines = parse_lines(xml_path)
    if not lines:
        raise SystemExit("No extractable text was found in the PDF layout XML.")
    body_size = body_font_size(lines)
    candidates = [line for line in lines if looks_like_heading(line, body_size)]
    candidates = merge_wrapped(candidates)

    bookmarks: list[Bookmark] = []
    seen: set[tuple[int, str]] = set()
    for line in candidates:
        title = clean_text(line.text)
        key = (line.page, title)
        if key in seen:
            continue
        seen.add(key)
        bookmarks.append(
            Bookmark(
                level=classify_level(line, body_size),
                title=title,
                page=line.page,
                top=line.top,
            )
        )
    if not bookmarks:
        raise SystemExit("No heading-like lines were detected. The PDF may be scanned or have flat styling.")
    return bookmarks


def top_to_pdf_y(reader: PdfReader, bookmark: Bookmark, xml_page_height: float = 1264.0) -> float:
    page = reader.pages[bookmark.page - 1]
    pdf_height = float(page.mediabox.height)
    y_from_top = bookmark.top / xml_page_height * pdf_height
    return max(0, min(pdf_height, pdf_height - y_from_top + 20))


def write_pdf_with_bookmarks(pdf_path: Path, output_path: Path, bookmarks: list[Bookmark]) -> None:
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    version_match = re.match(rb"%PDF-(\d\.\d)", pdf_path.read_bytes()[:16])
    writer.pdf_header = f"%PDF-{version_match.group(1).decode()}" if version_match else "%PDF-1.7"

    for page in reader.pages:
        writer.add_page(page)
    if reader.metadata:
        writer.add_metadata(dict(reader.metadata))

    parents: dict[int, object] = {}
    for bookmark in bookmarks:
        level = max(1, bookmark.level)
        parent = parents.get(level - 1)
        dest = writer.add_outline_item(
            bookmark.title,
            bookmark.page - 1,
            parent=parent,
            fit=Fit.fit_horizontally(top=top_to_pdf_y(reader, bookmark)),
            is_open=level <= 2,
        )
        parents[level] = dest
        for deeper in list(parents):
            if deeper > level:
                parents.pop(deeper, None)

    with output_path.open("wb") as handle:
        writer.write(handle)


def replace_original(src: Path, dest: Path) -> None:
    with tempfile.NamedTemporaryFile(delete=False, dir=str(dest.parent), suffix=".pdf") as handle:
        tmp = Path(handle.name)
    try:
        shutil.copyfile(src, tmp)
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink()


def print_preview(bookmarks: list[Bookmark], limit: int | None) -> None:
    rows = bookmarks if limit is None else bookmarks[:limit]
    for bookmark in rows:
        indent = "  " * (bookmark.level - 1)
        print(f"{indent}- p{bookmark.page:03d} {bookmark.title}")
    if limit is not None and len(bookmarks) > limit:
        print(f"... {len(bookmarks) - limit} more")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate hierarchical PDF bookmarks from visible headings.")
    parser.add_argument("pdf", help="PDF file to process")
    parser.add_argument("--output", help="Output PDF path. Defaults to '<name>-bookmarked.pdf'.")
    parser.add_argument("--in-place", action="store_true", help="Replace the input PDF atomically.")
    parser.add_argument("--force", action="store_true", help="Replace existing PDF outline/bookmarks.")
    parser.add_argument("--dry-run", action="store_true", help="Print detected bookmarks without writing.")
    parser.add_argument("--preview-limit", type=int, default=80, help="Number of dry-run bookmarks to print.")
    parser.add_argument("--xml", help="Use an existing pdftohtml XML file instead of extracting one.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise SystemExit(f"Input is not a PDF: {pdf_path}")
    if args.in_place and args.output:
        raise SystemExit("Use either --in-place or --output, not both.")

    reader = PdfReader(str(pdf_path))
    existing = outline_count(reader.outline)
    if existing and not args.force:
        print(
            f"EXISTING_OUTLINE: {existing} existing bookmark(s) found in {pdf_path}.\n"
            "Ask the user to confirm deleting/replacing existing bookmarks, then rerun with --force.",
            file=sys.stderr,
        )
        return EXISTING_OUTLINE_EXIT

    with tempfile.TemporaryDirectory(prefix="gen-pdf-bookmark-") as tmp_dir:
        xml_path = Path(args.xml).expanduser().resolve() if args.xml else extract_xml(pdf_path, Path(tmp_dir))
        bookmarks = build_bookmarks(xml_path)
        if args.dry_run:
            print(f"Detected {len(bookmarks)} bookmark(s).")
            print_preview(bookmarks, args.preview_limit)
            return 0

        if args.in_place:
            output_path = Path(tmp_dir) / "bookmarked.pdf"
        elif args.output:
            output_path = Path(args.output).expanduser().resolve()
        else:
            output_path = pdf_path.with_name(f"{pdf_path.stem}-bookmarked.pdf")

        write_pdf_with_bookmarks(pdf_path, output_path, bookmarks)
        if args.in_place:
            replace_original(output_path, pdf_path)
            output_path = pdf_path

    verified = PdfReader(str(output_path))
    print(f"wrote {outline_count(verified.outline)} bookmark(s)")
    print(f"pages {len(verified.pages)}")
    print(f"output {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
