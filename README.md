# ai-sdd-workflow

[![CI](https://github.com/ToshikiImagawa/ai-sdd-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/ToshikiImagawa/ai-sdd-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)]()

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する Claude Code プラグインのマーケットプレイスリポジトリです。

A marketplace repository for Claude Code plugins supporting AI-driven Specification-Driven Development (AI-SDD)
workflow.

## 概要 / Overview

このリポジトリには、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのプラグインが含まれています。

This repository contains plugins to prevent Vibe Coding problems and achieve high-quality implementations using
specifications as the source of truth.

## 利用可能なプラグイン / Available Plugins

| プラグイン / Plugin | 言語 / Language        | 説明 / Description                                                                                  |
|:---------------|:---------------------|:---------------------------------------------------------------------------------------------------|
| `sdd-workflow` | 多言語 / Multilingual | AI-SDD ワークフローを支援する統合プラグイン（`SDD_LANG` で言語切替）/ Unified plugin supporting AI-SDD workflow |

## インストール / Installation

### マーケットプレイスを追加 / Add Marketplace

Claude Code で以下を実行 / Run the following in Claude Code:

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

### プラグインをインストール / Install Plugin

```
/plugin install sdd-workflow@ToshikiImagawa/ai-sdd-workflow
```

言語は `.sdd-config.json` の `lang` フィールド（`en` / `ja`）で設定できます。
The language can be configured via the `lang` field (`en` / `ja`) in `.sdd-config.json`.

## プラグイン詳細 / Plugin Details

プラグインの詳細は README を参照してください。

For plugin details, see the README.

- [sdd-workflow README](./plugins/sdd-workflow/README.md)
- [sdd-workflow README（日本語）](./plugins/sdd-workflow/README.ja.md)

## リポジトリ構成 / Repository Structure

Codex と Claude Code は共通のプロジェクト指示として `CLAUDE.md` を使用します。
Codex では `~/.codex/config.toml` に `project_doc_fallback_filenames = ["CLAUDE.md"]` を設定してください。
開発スキルは Codex が `.agents/skills/`、Claude Code が `.claude/skills/` を使用します。

Codex and Claude Code use `CLAUDE.md` as the shared project guidance.
For Codex, set `project_doc_fallback_filenames = ["CLAUDE.md"]` in `~/.codex/config.toml`.
Codex uses `.agents/skills/`, while Claude Code uses `.claude/skills/`.

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── .agents/skills/                # Codex向け開発スキル
├── .claude/skills/                # Claude Code向け開発スキル
├── plugins/
│   └── sdd-workflow/              # 統合プラグイン（多言語対応）/ Unified plugin (multilingual)
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── skills/
│       ├── hooks/
│       ├── scripts/
│       ├── CHANGELOG.md
│       ├── CHANGELOG.ja.md
│       ├── LICENSE
│       ├── README.md
│       └── README.ja.md
├── CLAUDE.md                       # 共通プロジェクト指示（正本）
├── PLUGIN_AGENTS.md                # プラグインエージェント設計ガイド
├── LICENSE
└── README.md
```

## ライセンス / License

MIT License
