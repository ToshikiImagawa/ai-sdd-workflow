# ai-sdd-workflow

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)]()

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する Claude Code プラグインのマーケットプレイスリポジトリです。

A marketplace repository for Claude Code plugins supporting
AI-driven Specification-Driven Development (AI-SDD) workflow.

## 概要 / Overview

このリポジトリはプラグインの**カタログ（`.claude-plugin/marketplace.json`）のみ**を持ちます。プラグイン本体・
CHANGELOG・GitHub Release は本体リポジトリ
[ToshikiImagawa/ai-sdd-workflow-dev](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev) にあります。
カタログの各エントリは `git-subdir` ソースで本体リポジトリのサブディレクトリをタグとコミット SHA に固定して参照します。

This repository holds **only the plugin catalog (`.claude-plugin/marketplace.json`)**. The plugin source code,
CHANGELOG, and GitHub Releases live in the main repository,
[ToshikiImagawa/ai-sdd-workflow-dev](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev). Each catalog entry
uses a `git-subdir` source that points to a subdirectory of the main repository, pinned to a tag and commit SHA.

プラグインは、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現します。

The plugin prevents Vibe Coding problems and achieves high-quality implementations using specifications as the
source of truth.

## 利用可能なプラグイン / Available Plugins

| プラグイン / Plugin | 言語 / Language      | 説明 / Description                                                                       | 本体リポジトリ / Source Repository                                                                         |
|:---------------|:-------------------|:---------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------|
| `sdd-workflow` | 多言語 / Multilingual | AI-SDD ワークフローを支援する統合プラグイン（`SDD_LANG` で言語切替）/ Unified plugin supporting AI-SDD workflow | [ToshikiImagawa/ai-sdd-workflow-dev](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev) |

## インストール / Installation

### マーケットプレイスを追加 / Add Marketplace

Claude Code で以下を実行 / Run the following in Claude Code:

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

### プラグインをインストール / Install Plugin

```
/plugin install sdd-workflow@ai-sdd-workflow
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

- [Migration from v4.x (English)](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/blob/main/plugins/sdd-workflow/README.md#migration-from-v4x)
- [v4.x からの移行（日本語）](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/blob/main/plugins/sdd-workflow/README.ja.md#v4x-からの移行)

## プラグイン詳細 / Plugin Details

プラグインの詳細・CHANGELOG・リリースは本体リポジトリを参照してください。

For plugin details, the CHANGELOG, and releases, see the main repository.

- [sdd-workflow README](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/blob/main/plugins/sdd-workflow/README.md)
- [sdd-workflow README（日本語）](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/blob/main/plugins/sdd-workflow/README.ja.md)
- [CHANGELOG](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/blob/main/plugins/sdd-workflow/CHANGELOG.md)
- [CHANGELOG（日本語）](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/blob/main/plugins/sdd-workflow/CHANGELOG.ja.md)
- [Releases](https://github.com/ToshikiImagawa/ai-sdd-workflow-dev/releases)

## カタログの更新 / Updating the Catalog

本体リポジトリでリリースタグ `vX.Y.Z` が打たれると、本体リポジトリの release workflow がこのリポジトリの `main` 向けに
`marketplace.json` の `version` / `ref` / `sha` を更新する PR を作成します。PR をマージすると利用者に新しいバージョンが
配布されます。

When a release tag `vX.Y.Z` is pushed in the main repository, its release workflow opens a PR against `main` of this
repository that updates `version` / `ref` / `sha` in `marketplace.json`. Merging that PR delivers the new version to
users.

### プラグインを追加するとき / Adding a Plugin

`.claude-plugin/marketplace.json` の `plugins` 配列に `git-subdir` ソースのエントリを追加します。`sha` には `ref` の
タグが指すコミットの 40 桁 SHA を指定します（`git ls-remote <url> 'refs/tags/vX.Y.Z*'` で確認でき、annotated tag の
場合は `^{}` の行がコミット SHA です）。

Add an entry with a `git-subdir` source to the `plugins` array in `.claude-plugin/marketplace.json`. Set `sha` to the
40-character SHA of the commit the `ref` tag points to (check it with `git ls-remote <url> 'refs/tags/vX.Y.Z*'`; for
an annotated tag, the `^{}` line is the commit SHA).

```json
{
  "name": "<plugin-name>",
  "source": {
    "source": "git-subdir",
    "url": "<owner>/<repo>",
    "path": "plugins/<plugin-name>",
    "ref": "vX.Y.Z",
    "sha": "<40-char commit SHA>"
  },
  "description": "...",
  "version": "X.Y.Z"
}
```

追加後、ローカルで検証してから PR を作成します。CI でも同じ検証が実行されます。

After adding it, validate locally before opening a PR. CI runs the same checks.

```bash
claude plugin validate .
```

## リポジトリ構成 / Repository Structure

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # プラグインカタログ / Plugin catalog
├── .github/
│   └── workflows/
│       └── ci.yml                 # カタログの検証 / Catalog validation
├── LICENSE
└── README.md
```

## ライセンス / License

MIT License
