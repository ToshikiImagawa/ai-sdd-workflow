# ai-sdd-workflow

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)]()

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する Claude Code プラグインのマーケットプレイスリポジトリです。

A marketplace repository for Claude Code plugins supporting
AI-driven Specification-Driven Development (AI-SDD) workflow.

## 概要 / Overview

このリポジトリには、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのプラグインが含まれています。

This repository contains plugins to prevent Vibe Coding problems and achieve high-quality implementations using
specifications as the source of truth.

## 利用可能なプラグイン / Available Plugins

| プラグイン / Plugin | 言語 / Language      | 説明 / Description                                                                       |
|:---------------|:-------------------|:---------------------------------------------------------------------------------------|
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

### インストール済みプラグインの更新 / Updating an Installed Plugin

すでに `sdd-workflow` をインストールしている場合は、キャッシュを更新してから Claude Code を再起動します。

If `sdd-workflow` is already installed, refresh the cache and then restart Claude Code.

```bash
claude plugin update sdd-workflow
```

再起動後、`session-start` フックが `.sdd/AI-SDD-PRINCIPLES.md` と `.claude/rules/ai-sdd-instructions.md` を
新しいバージョンに同期します。`CLAUDE.md` の AI-SDD セクションが古い場合は `.sdd/UPDATE_REQUIRED.md` が
書き出されるので、`/sdd-init` を実行してください。

After the restart, the `session-start` hook syncs `.sdd/AI-SDD-PRINCIPLES.md` and
`.claude/rules/ai-sdd-instructions.md` to the new version. If your `CLAUDE.md` AI-SDD section is outdated,
`.sdd/UPDATE_REQUIRED.md` is written — run `/sdd-init` to bring it up to date.

## v5.0.0 の破壊的変更 / Breaking Changes in v5.0.0

**v4.x からの更新には移行作業が必要です。** 主な変更は次の2点です。

**Updating from v4.x requires migration.** The two headline changes are:

- `specification/{feature-name}_design.md` は永続ドキュメントではなくなりました。技術設計書は
  `task/{ticket-number}/design-draft.md` の一時ドラフトになり、実装完了後に削除されます /
  `specification/{feature-name}_design.md` is no longer a persistent document. A technical design is now a
  temporary draft at `task/{ticket-number}/design-draft.md`, deleted after implementation
- 新しい `adr/` ディレクトリに、決定・理由・却下した代替案のみが `adr/{feature-name}.md`（追記専用）として
  永続化されます / A new `adr/` directory persists only the decisions, their rationale, and rejected
  alternatives in `adr/{feature-name}.md` (append-only)

既存の `specification/*_design.md` は**引き続き有効**で、削除を求められることはありません。移行は急ぐ必要が
なく、機能単位で進められます。破壊的変更の全一覧・移行手順・既知の制約はプラグイン README を参照してください。

Existing `specification/*_design.md` files **remain valid** and you are never asked to delete them. The
migration is not urgent and can be done feature by feature. For the full list of breaking changes, the
migration steps, and the known limitations, see the plugin README:

- [Migration from v4.x (English)](./plugins/sdd-workflow/README.md#migration-from-v4x)
- [v4.x からの移行（日本語）](./plugins/sdd-workflow/README.ja.md#v4x-からの移行)

## プラグイン詳細 / Plugin Details

プラグインの詳細は README を参照してください。

For plugin details, see the README.

- [sdd-workflow README](./plugins/sdd-workflow/README.md)
- [sdd-workflow README（日本語）](./plugins/sdd-workflow/README.ja.md)

## リポジトリ構成 / Repository Structure

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ / Marketplace metadata
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
├── LICENSE
└── README.md
```

## ライセンス / License

MIT License
