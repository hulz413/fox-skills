---
name: gen-pdf-bookmark
description: Use when adding, generating, replacing, or rebuilding hierarchical bookmarks, outlines, table-of-contents navigation, or “标签” for PDF files, especially when the user invokes /gen-pdf-bookmark or provides a PDF and wants heading-based PDF navigation.
---

# Gen PDF Bookmark

## Overview

Generate PDF bookmarks from visible heading text and preserve heading hierarchy as PDF outline levels. The bundled script detects existing PDF bookmarks and refuses to overwrite them unless the user confirms replacement.

## Workflow

1. Identify the target `.pdf` path.
2. Run a dry run first:

```bash
python3 scripts/gen_pdf_bookmark.py /path/to/file.pdf --dry-run
```

If `python3` cannot import `pypdf`, call `load_workspace_dependencies` and rerun with the bundled Python executable.

3. If the script prints `EXISTING_OUTLINE`, stop and ask the user to confirm deleting/replacing the existing bookmarks. Do not pass `--force` until the user explicitly confirms.
4. After confirmation, or if no existing bookmarks are present, write in place unless the user asks for a separate output:

```bash
python3 scripts/gen_pdf_bookmark.py /path/to/file.pdf --in-place
python3 scripts/gen_pdf_bookmark.py /path/to/file.pdf --in-place --force
```

Use `--output /path/to/out.pdf` instead of `--in-place` when the user wants a copy.

5. Verify by reading the output PDF and reporting page count plus bookmark count from the script output.

## Script Notes

- `scripts/gen_pdf_bookmark.py` uses `pdftohtml -xml` for layout extraction, then `pypdf` to rebuild the PDF outline.
- It infers heading levels from numbering patterns, Chinese chapter/section labels, font-size differences, and wrapped heading lines.
- It removes old bookmarks only when `--force` is used; page content is preserved.
- If the PDF is scanned or has no extractable text/style hierarchy, tell the user automatic bookmark generation cannot be reliable without OCR or a supplied table of contents.

## User Confirmation Wording

When existing bookmarks are detected, ask plainly:

> This PDF already has N bookmark(s). Do you want me to delete the existing bookmarks and replace them with newly generated bookmarks?

Proceed only after the user says yes/confirm/replace/overwrite/delete existing bookmarks.
