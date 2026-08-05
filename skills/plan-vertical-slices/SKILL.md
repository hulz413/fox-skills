---
name: plan-vertical-slices
description: Create a compact coding-plan Markdown file by decomposing an existing technical design into prioritized, dependency-ordered business vertical slices. Accept readable local files, Feishu documents, web pages, PDFs, Word documents, and similar sources. Use before coding when the user wants an implementation sequence derived from a technical design. Do not use product requirements alone, invent or revise technical decisions, or implement the slices.
---

# Plan Vertical Slices

Turn an existing technical design into a small execution index. Treat the source
technical design as authoritative and output only its source reference and an ordered
business vertical-slice table.

## Workflow

1. Resolve and read the complete source with the best available source-native tool:
   use file readers for local files, Feishu capabilities for Feishu documents, a
   browser for web pages, and PDF or Word tooling for those formats.
2. Verify that the source contains a technical design with enough implementation
   decisions to identify end-to-end business capabilities and their dependencies.
   Stop and request a technical design when the input is only a product requirement.
   Stop when the source is inaccessible, incomplete for slicing, or lacks a stable
   reference.
3. Extract the source identity:
   - Preserve the original visible document title as `source_title`.
   - Derive `subject_title` by removing a trailing document-type label such as
     `技术方案`, `技术设计`, `Technical Design`, `Tech Design`, or `Design`, including
     adjacent separators.
   - For a local file without a usable embedded title, use its filename stem as
     `source_title`, then derive `subject_title` from it.
   - Ask the user for a title when the source has no meaningful title; never use a
     document ID or URL ID as the title.
4. Decompose the design into business vertical slices according to the rules below.
5. Resolve the destination and filename, check for collisions, and write exactly the
   output contract below.
6. Re-read the generated file and validate its title, source link, table columns,
   naming, priority order, dependencies, statuses, and absence of implementation
   details before reporting completion.

## Vertical-Slice Rules

- Make every slice deliver an end-to-end business capability or observable business
  outcome across the required technical layers.
- Do not create horizontal slices for frontend, backend, API, database, migrations,
  infrastructure, tests, or similar technical layers.
- Name every slice in English `kebab-case` as a verb followed by a noun, such as
  `create-order`, `view-order`, or `cancel-order`.
- Avoid technical names such as `add-order-table`, `implement-order-api`, or
  `build-order-page`.
- Include every business capability required by the technical design exactly once.
- Do not add requirements, technical decisions, abstractions, or follow-up work that
  the technical design does not establish.

## Priority and Dependency Rules

- Use only these priorities:
  - `P0`: the first working business loop or a prerequisite that blocks other slices.
  - `P1`: core capabilities that follow the first working loop.
  - `P2`: enhancements, supplementary cases, or capabilities that may be deferred.
- Sort rows by priority in the order `P0`, `P1`, `P2`.
- Allow multiple slices at the same priority. Within one priority, place dependencies
  before their dependents.
- Never make a higher-priority slice depend on a lower-priority slice. A dependency's
  numeric priority must be less than or equal to the dependent slice's priority.
- Refer to dependencies by their exact slice names. Separate multiple dependencies
  with commas. Write `无` when there is no dependency.
- Set every generated implementation status to `pending`.

## Destination and Naming

- If the user supplies an output directory, write there.
- Otherwise, write under `docs/` in the current Git repository root. If there is no
  Git repository, use `docs/` under the current working directory.
- Create the destination directory when it does not exist.
- Generate the filename as `{slug}-coding-plan.md`, where `{slug}` is a concise,
  semantic English `kebab-case` rendering of `subject_title`.
- Translate non-English subjects by meaning. Do not use pinyin, a document ID, or a
  URL ID. For example, `Geo Agent MVP 技术方案` becomes
  `geo-agent-mvp-coding-plan.md`, and `订单取消技术设计` becomes
  `cancel-order-coding-plan.md`.
- If the destination file already exists, ask before overwriting it. Never overwrite
  it silently.

## Source Reference

- For a local source, calculate a Markdown path relative to the generated coding-plan
  file, regardless of whether the source is Markdown, PDF, Word, HTML, or another
  local format.
- For a Feishu document or web page, preserve the original URL supplied by the user.
- Stop and request a durable source reference when one cannot be generated.

## Output Contract

Write no sections, prose, implementation steps, code locations, acceptance criteria,
test plans, risk analysis, or design explanation beyond this exact structure:

```markdown
# <subject_title> 编码计划

> 技术实现以[《<source_title>》](<source_reference>)为准。本文档仅提供业务垂直切片及推荐实现顺序，不新增、修改或替代技术方案中的设计决策。如两者存在冲突，以技术方案为准。

## 业务垂直切片

| 切片名称 | 优先级 | 实现状态 | 依赖切片 |
|---|---|---|---|
| `create-example` | `P0` | `pending` | 无 |
| `view-example` | `P1` | `pending` | `create-example` |
| `enhance-example` | `P2` | `pending` | `view-example` |
```

Replace the example rows with slices derived from the source. Keep the Chinese
headings and source disclaimer exactly as shown. Preserve `source_title` in its
original language and render `subject_title` as a readable human-facing title in its
original language after removing the document-type suffix.
