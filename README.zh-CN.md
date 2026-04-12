[English](README.md) | 简体中文

# fox-skills

一个个人 AI skills 仓库。

这个仓库刻意保持简单：每个 skill 一个目录，并包含面向使用者的 `README.md` 和作为主入口的 `SKILL.md`。

## 仓库结构

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

## Skill 结构

每个 skill 目录可以包含几类清晰分工的文件：

- `skills/<skill-id>/README.md` — 给人看的简介、安装和使用方式
- `skills/<skill-id>/SKILL.md` — 作为 skill 主入口的说明文件
- `skills/<skill-id>/references/` — 规则、样例或补充说明
- `skills/<skill-id>/scripts/` — 这个 skill 需要的辅助脚本
- `skills/<skill-id>/assets/` — 必要的资源文件或 vendor 补丁

## 如何新增一个 skill

1. 创建 `skills/<your-skill-id>/`。
2. 添加 `README.md`，写安装和使用方式。
3. 添加 `SKILL.md`，作为主 skill 文件。
4. 只有在确实需要时，再添加 `references/`、`scripts/` 或 `assets/`。

## Skills

每个 skill 的安装和使用方式，请查看各自目录下的 `README.md`。

- [`anki-leetcode`](skills/anki-leetcode/README.md) — 生成或更新 LeetCode Anki 卡片，重建 `leetcode.apkg`，并可在 macOS 上导入主 Anki 集合。

## 兼容性说明

这个仓库不维护单独的兼容性框架。

如果某个 skill 只适用于特定 runtime 或 agent，直接在该 skill 自己的 `README.md` 或 `SKILL.md` 中说明即可。

## 校验

仓库保留了一个很轻的 GitHub Actions workflow，只检查最基本结构：

- `README.md`
- `README.zh-CN.md`
- `skills/` 下每个一级目录里都有 `README.md`
- `skills/` 下每个一级目录里都有 `SKILL.md`

## 说明

- 这个仓库的目标是分享 skills，不是做一个完整框架。
- 每个 skill 都应该能在 GitHub 上直接读懂。
- 在公开发布前，请补充正式的 `LICENSE`。
