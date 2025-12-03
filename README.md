# ai-sdd-workflow

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する Claude Code プラグインのマーケットプレイスリポジトリです。

A marketplace repository for Claude Code plugins supporting AI-driven Specification-Driven Development (AI-SDD) workflow.

## 概要 / Overview

このリポジトリには、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのプラグインが含まれています。

This repository contains plugins to prevent Vibe Coding problems and achieve high-quality implementations using specifications as the source of truth.

## 利用可能なプラグイン / Available Plugins

| プラグイン / Plugin | 言語 / Language | 説明 / Description |
|:---|:---|:---|
| `sdd-workflow-ja` | 日本語 | AI-SDD ワークフローを支援する日本語プラグイン |
| `sdd-workflow` | English | English plugin supporting AI-SDD workflow |

## インストール / Installation

### マーケットプレイスを追加 / Add Marketplace

Claude Code で以下を実行 / Run the following in Claude Code:

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

### プラグインをインストール / Install Plugin

**日本語版 / Japanese version:**

```
/plugin install sdd-workflow-ja@ToshikiImagawa/ai-sdd-workflow
```

**English version:**

```
/plugin install sdd-workflow@ToshikiImagawa/ai-sdd-workflow
```

## プラグイン詳細 / Plugin Details

各プラグインの詳細はそれぞれのREADMEを参照してください。

For details on each plugin, see their respective READMEs.

- [sdd-workflow-ja README](./plugins/sdd-workflow-ja/README.md)
- [sdd-workflow README](./plugins/sdd-workflow/README.md)

## リポジトリ構成 / Repository Structure

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── plugins/
│   ├── sdd-workflow-ja/           # 日本語プラグイン
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── skills/
│   │   ├── hooks/
│   │   ├── LICENSE
│   │   └── README.md
│   └── sdd-workflow/              # English plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       ├── skills/
│       ├── hooks/
│       ├── LICENSE
│       └── README.md
├── CHANGELOG.md
├── CLAUDE.md
└── README.md
```

## ライセンス / License

MIT License
