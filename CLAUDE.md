# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援するClaude Codeプラグイン（日本語対応）のマーケットプレイスリポジトリ。Vibe
Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現する。

## リポジトリ構成

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── plugins/
│   ├── sdd-workflow-ja/           # 日本語プラグイン
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json        # プラグインマニフェスト
│   │   ├── agents/
│   │   │   ├── sdd-workflow.md    # AI-SDD開発フローエージェント
│   │   │   ├── spec-reviewer.md   # 仕様書レビューエージェント
│   │   │   └── requirement-analyzer.md  # 要求仕様分析エージェント
│   │   ├── commands/
│   │   │   ├── sdd_init.md        # AI-SDDワークフロー初期化
│   │   │   ├── sdd_migrate.md     # 旧バージョンからの移行
│   │   │   ├── generate_spec.md   # 仕様書・設計書生成
│   │   │   ├── generate_prd.md    # PRD生成
│   │   │   ├── check_spec.md      # 整合性チェック
│   │   │   ├── task_cleanup.md    # タスククリーンアップ
│   │   │   └── task_breakdown.md  # タスク分解
│   │   ├── skills/
│   │   │   ├── vibe-detector/     # Vibe Coding検出
│   │   │   ├── doc-consistency-checker/
│   │   │   └── sdd-templates/     # AI-SDDテンプレート
│   │   ├── hooks/
│   │   │   ├── session-start.sh   # セッション開始時の初期化
│   │   │   └── settings.example.json
│   │   ├── LICENSE
│   │   ├── README.md
│   │   └── CHANGELOG.md
│   └── sdd-workflow/              # 英語プラグイン
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       ├── skills/
│       ├── hooks/
│       ├── LICENSE
│       ├── README.md
│       └── CHANGELOG.md
├── CLAUDE.md
└── README.md
```

## AI-SDD 開発フロー

```
Specify（仕様化） → Plan（計画） → Tasks（タスク分解） → Implement & Review（実装と検証）
```

### ドキュメント構造

```
.sdd/
├── CONSTITUTION.md               # プロジェクト原則（最上位）
├── *_TEMPLATE.md                 # 各種テンプレート
├── requirement/                  # PRD（要求仕様書）- 永続
├── specification/                # 仕様書・設計書 - 永続
└── task/                         # タスクログ - 一時的（実装完了後に削除）
```

フラット構造（小〜中規模）と階層構造（中〜大規模）の両方をサポート。詳細は `plugins/sdd-workflow-ja/README.md` を参照。

### ファイル命名規則

**IMPORTANT: requirement と specification でサフィックスの有無が異なります。混同しないでください。**

- `requirement/` 配下: サフィックス**なし**（例: `user-login.md`）
- `specification/` 配下: `_spec.md` または `_design.md` サフィックス**必須**

| ディレクトリ            | ファイル種別 | 命名パターン                               | 例                                         |
|:------------------|:-------|:-------------------------------------|:------------------------------------------|
| **requirement**   | 全ファイル  | `{名前}.md`（サフィックスなし）                  | `user-login.md`, `index.md`               |
| **specification** | 抽象仕様書  | `{名前}_spec.md`（`_spec` サフィックス必須）     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | 技術設計書  | `{名前}_design.md`（`_design` サフィックス必須） | `user-login_design.md`, `index_design.md` |

### ドキュメント永続性ルール

**IMPORTANT: task/ ディレクトリは一時的なものです。実装完了後に削除してください。**

- `requirement/`, `specification/*_spec.md`, `specification/*_design.md`: **永続**
- `task/`: **一時的** - 重要な設計判断は `*_design.md` に統合してから削除

### ドキュメント依存関係

すべてのドキュメントは `CONSTITUTION.md` のプロジェクト原則に従って作成されます。

```
CONSTITUTION.md → requirement/ → *_spec.md → *_design.md → task/ → 実装
```

### プロジェクト設定ファイル

プロジェクトルートに `.sdd-config.json` を配置することで、ディレクトリ名をカスタマイズできます。

```json
{
  "root": ".sdd",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
```

- 設定ファイルが存在しない場合はデフォルト値が使用されます
- 部分的な設定も可能（指定されていない項目はデフォルト値）

### 環境変数によるパス解決

セッション開始時に `session-start` フックが `.sdd-config.json` を読み込み、以下の環境変数を設定します。

| 環境変数                     | デフォルト値               | 説明             |
|:-------------------------|:---------------------|:---------------|
| `SDD_ROOT`               | `.sdd`               | ルートディレクトリ      |
| `SDD_REQUIREMENT_DIR`    | `requirement`        | 要求仕様書ディレクトリ名   |
| `SDD_SPECIFICATION_DIR`  | `specification`      | 仕様書・設計書ディレクトリ名 |
| `SDD_TASK_DIR`           | `task`               | タスクログディレクトリ名   |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | 要求仕様書フルパス      |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書・設計書フルパス    |
| `SDD_TASK_PATH`          | `.sdd/task`          | タスクログフルパス      |

**パス解決の優先順位:**

1. 環境変数 `SDD_*` が設定されている場合はそれを使用
2. 環境変数がない場合は `.sdd-config.json` を確認
3. どちらもない場合はデフォルト値を使用

## Vibe Coding防止

曖昧な指示（「いい感じに」「適当に」「前と同じように」など）を検出した場合、仕様の明確化を促す。仕様書なしでの実装は避け、最低限
`task/` に推測仕様を記録する。

## テストと検証

- プラグインJSON構文チェック: `cat plugins/*/.claude-plugin/*.json | jq .`
- Markdownリンクの整合性: 各ドキュメント内の相対リンクが有効か確認
- **IMPORTANT**: 新規コマンド/エージェント追加時は `plugin.json` への登録を忘れずに

## 開発時の注意

- プラグイン修正時は対象プラグインディレクトリ（`plugins/{plugin-name}/`）に限定して作業
- 全プラグインへの変更が必要な場合は、明示的に確認してから実施
- 「調査して」と依頼された場合は、まずスコープを確認してから探索

## プラグインエージェント設計ガイド

AI-SDDワークフロープラグインのサブエージェント設計・実装に関する原則とベストプラクティスは、[AGENTS.md](./AGENTS.md) を参照してください。

このガイドでは以下の内容を定義しています：

1. **サブエージェントの基本概念**（コンテキスト独立性、トークン効率化）
2. **エージェント設計原則**（役割、入出力、allowed-tools、前提条件）
3. **委任すべきタスク vs メインで実行すべきタスク**
4. **エージェント間連携パターン**
5. **実践Tips**

## プラグイン開発ガイド

Claude Codeプラグインとマーケットプレイスの作成に関する包括的なガイドは、[PLUGIN.md](./PLUGIN.md) を参照してください。

このガイドでは以下の内容を定義しています：

1. **プラグイン基本構造**（ディレクトリレイアウト、マーケットプレイス構成）
2. **マニフェストファイル**（plugin.json, marketplace.json の詳細）
3. **コマンド、エージェント、スキルの実装**（フロントマター、ベストプラクティス）
4. **MCP サーバー連携**（外部ツール統合）
5. **フック実装**（イベント駆動型自動化）
6. **マーケットプレイス公開プロセス**（品質基準、配布モデル）

## 新しいプラグインの追加

1. `plugins/{plugin-name}/` ディレクトリを作成
2. `.claude-plugin/plugin.json` にプラグインマニフェストを配置
3. agents, commands, skills, hooks を必要に応じて追加
4. `.claude-plugin/marketplace.json` の `plugins` 配列に追加
