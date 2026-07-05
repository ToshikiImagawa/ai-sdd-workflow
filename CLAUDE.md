# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援するClaude Codeプラグインのマーケットプレイスリポジトリ。Vibe
Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現する。`SDD_LANG` 環境変数による多言語対応。

## リポジトリ構成

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── plugins/
│   └── sdd-workflow/              # 統合プラグイン（多言語対応）
│       ├── .claude-plugin/
│       │   └── plugin.json        # プラグインマニフェスト
│       ├── agents/
│       │   ├── spec-reviewer.md   # 仕様書レビューエージェント
│       │   ├── prd-reviewer.md    # PRDレビューエージェント
│       │   ├── requirement-analyzer.md  # 要求仕様分析エージェント
│       │   └── clarification-assistant.md  # 仕様明確化アシスタント
│       ├── skills/                # 11スキル（旧commands）+ 4スキル（既存）
│       │   ├── sdd-init/          # AI-SDDワークフロー初期化
│       │   ├── constitution/      # プロジェクト原則管理
│       │   ├── generate-spec/     # 仕様書・設計書生成
│       │   ├── generate-prd/      # PRD生成
│       │   ├── check-spec/        # 整合性チェック
│       │   ├── task-breakdown/    # タスク分解
│       │   ├── implement/         # TDD実装
│       │   ├── clarify/           # 仕様明確化
│       │   ├── task-cleanup/      # タスククリーンアップ
│       │   ├── sdd-migrate/       # マイグレーション
│       │   ├── checklist/         # 品質チェックリスト
│       │   ├── vibe-detector/     # Vibe Coding検出
│       │   │   └── templates/{en,ja}/
│       │   ├── sdd-templates/     # AI-SDDテンプレート
│       │   │   └── templates/{en,ja}/
│       │   ├── doc-consistency-checker/  # ドキュメント整合性チェッカー
│       │   │   └── templates/{en,ja}/
│       │   └── output-templates/  # 出力テンプレート
│       │       └── templates/{en,ja}/
│       ├── hooks/
│       │   └── hooks.json         # フック設定（JSON形式）
│       ├── scripts/
│       │   └── session-start.py   # セッション開始時の初期化
│       ├── AI-SDD-PRINCIPLES.source.md
│       ├── LICENSE
│       ├── README.md
│       └── CHANGELOG.md
├── CLAUDE.md
├── AGENTS.md
├── PLUGIN.md
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

フラット構造（小〜中規模）と階層構造（中〜大規模）の両方をサポート。詳細は `plugins/sdd-workflow/README.md` を参照。

### ファイル命名規則

**IMPORTANT: requirement と specification でサフィックスの有無が異なります。混同しないでください。**

- `requirement/` 配下: サフィックス**なし**（例: `user-login.md`）
- `specification/` 配下: `_spec.md` または `_design.md` サフィックス**必須**

| ディレクトリ            | ファイル種別 | 命名パターン                               | 例                                         |
|:------------------|:-------|:-------------------------------------|:------------------------------------------|
| **requirement**   | 全ファイル  | `{名前}.md`（サフィックスなし）                  | `user-login.md`, `index.md`               |
| **specification** | 抽象仕様書  | `{名前}_spec.md`（`_spec` サフィックス必須）     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | 技術設計書  | `{名前}_design.md`（`_design` サフィックス必須） | `user-login_design.md`, `index_design.md` |

### YAML Front Matter

各ドキュメントにはオプションでYAML front matterを追加できる。機械的な検索・フィルタリングに活用される。

| ドキュメント種別 | `type`                 | `id` パターン         | 固有フィールド                                                        |
|:---------|:-----------------------|:------------------|:---------------------------------------------------------------|
| PRD      | `"prd"`                | `"prd-{name}"`    | `priority`, `risk`                                             |
| Spec     | `"spec"`               | `"spec-{name}"`   | `sdd-phase: "specify"`                                         |
| Design   | `"design"`             | `"design-{name}"` | `sdd-phase: "plan"`, `impl-status`                             |
| Task     | `"task"`               | `"task-{name}"`   | `sdd-phase: "tasks"`, `ticket`                                 |
| Impl Log | `"implementation-log"` | `"impl-{name}"`   | `sdd-phase: "implement"`, `ticket`, `completed`, `implementer` |

共通フィールド: `id`, `title`, `type`, `status`, `created`, `updated`, `depends-on`, `tags`, `category`

**依存方向**: `depends-on` は上流方向のみ。下位ドキュメントへの参照は持たない。

```
prd ← spec (depends-on: prd) ← design (depends-on: spec) ← task (depends-on: design)
```

- 階層構造の場合: `id` にパスを含める（例: `"spec-auth-user-login"`）
- front matterなしの既存ドキュメントも引き続き有効（後方互換）

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

プロジェクトルートに `.sdd-config.json` を配置することで、ディレクトリ名や言語をカスタマイズできます。

```json
{
  "root": ".sdd",
  "lang": "en",
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
| `SDD_LANG`               | `en`                 | 言語設定           |
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
- **IMPORTANT**: 新規エージェント/スキル追加時は `plugin.json` への登録を忘れずに
- プラグインデバッグ: `claude --debug` でプラグインの読み込み、フック実行、エージェント呼び出しの詳細ログを確認
- ローカルテスト: `claude --plugin-dir ./plugins/sdd-workflow` でローカルのプラグインを直接テスト

## 開発時の注意

- プラグイン修正時は `plugins/sdd-workflow/` に限定して作業
- 「調査して」と依頼された場合は、まずスコープを確認してから探索

## CLAUDE.md 執筆のベストプラクティス

公式ドキュメントに基づく CLAUDE.md の効果的な執筆ガイドライン:

- **簡潔に保つ**: Claudeが推測できる一般的な情報は除外し、プロジェクト固有の重要事項のみ記載する
- **`@path/to/file` 構文**: 他のファイルの内容をインポートできる。大きなドキュメントを分割して管理する際に活用
- **検証方法の提供が最も効果が高い**: ビルドコマンド、テストコマンド、リントコマンドなどを明記することで、Claudeが自律的に品質を確認できる
- **コンテキスト管理**: `/clear` コマンドでコンテキストをリセットし、サブエージェント（Task ツール）を活用して調査タスクを委任する

## プラグインエージェント設計ガイド

AI-SDDワークフロープラグインのサブエージェント設計・実装に関する原則とベストプラクティスは、
[AGENTS.md](./AGENTS.md) を参照してください。

このガイドでは以下の内容を定義しています：

1. **サブエージェントの基本概念**（コンテキスト独立性、トークン効率化）
2. **エージェント設計原則**（役割、入出力、allowed-tools/tools/skills/hooks、前提条件）
3. **委任すべきタスク vs メインで実行すべきタスク**
4. **エージェント間連携パターン**（スキル連携、フック連携を含む）
5. **実践Tips**（デバッグ方法、`claude --debug` の活用）

## プラグイン開発ガイド

Claude Codeプラグインとマーケットプレイスの作成に関する包括的なガイドは、[PLUGIN.md](./PLUGIN.md) を参照してください。

このガイドでは以下の内容を定義しています：

1. **プラグイン基本構造**（ディレクトリレイアウト、マーケットプレイス構成）
2. **マニフェストファイル**（plugin.json のコンポーネントパスフィールド、`${CLAUDE_PLUGIN_ROOT}` 環境変数）
3. **コマンド（legacy）、エージェント、スキルの実装**（フロントマター、`context: fork`、動的コンテキスト注入）
4. **MCP / LSP サーバー連携**（外部ツール統合、Language Server Protocol 統合）
5. **フック実装**（JSON形式の `hooks.json`、イベント一覧、フックタイプ: command/prompt/agent）
6. **プラグインキャッシュとインストールスコープ**（user/project/local/managed）
7. **マーケットプレイス公開プロセス**（品質基準、配布モデル）
8. **CLI コマンドリファレンス / デバッグ**

## 新しいプラグインの追加

1. `plugins/{plugin-name}/` ディレクトリを作成
2. `.claude-plugin/plugin.json` にプラグインマニフェストを配置
3. agents, skills, hooks を必要に応じて追加（新規コマンドは `skills/` を推奨）
4. `.claude-plugin/marketplace.json` の `plugins` 配列に追加

## AI-SDD Instructions (v3.3.0)

<!-- sdd-workflow version: "3.3.0" -->

このプロジェクトは AI-SDD（AI駆動仕様駆動開発）ワークフローに従います。

### ドキュメント操作

`.sdd/` ディレクトリ配下のファイルを操作する際は、`.sdd/AI-SDD-PRINCIPLES.md` を参照し、AI-SDDワークフローに準拠してください。

**トリガー条件**:

- `.sdd/` 配下のファイルの読み取りまたは変更
- 新しい仕様書、設計書、要求仕様書の作成
- `.sdd/` ドキュメントを参照する機能の実装

### ディレクトリ構造

フラット構造と階層構造の両方をサポートしています。

**フラット構造（小〜中規模プロジェクト向け）**:

    .sdd/
    |- CONSTITUTION.md               # プロジェクト原則（最上位）
    |- PRD_TEMPLATE.md               # PRDテンプレート
    |- SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート
    |- DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート
    |- requirement/                  # PRD（要求仕様書）
    |   |- {feature-name}.md
    |- specification/                # 仕様書・設計書
    |   |- {feature-name}_spec.md    # 抽象仕様書
    |   |- {feature-name}_design.md  # 技術設計書
    |- task/                         # 一時タスクログ
        |- {ticket-number}/

**階層構造（中〜大規模プロジェクト向け）**:

    .sdd/
    |- CONSTITUTION.md               # プロジェクト原則（最上位）
    |- PRD_TEMPLATE.md               # PRDテンプレート
    |- SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート
    |- DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート
    |- requirement/                  # PRD（要求仕様書）
    |   |- {feature-name}.md         # トップレベル機能
    |   |- {parent-feature}/         # 親機能ディレクトリ
    |       |- index.md              # 親機能概要・要求一覧
    |       |- {child-feature}.md    # 子機能要求仕様
    |- specification/                # 仕様書・設計書
    |   |- {feature-name}_spec.md    # トップレベル機能
    |   |- {feature-name}_design.md
    |   |- {parent-feature}/         # 親機能ディレクトリ
    |       |- index_spec.md         # 親機能抽象仕様書
    |       |- index_design.md       # 親機能技術設計書
    |       |- {child-feature}_spec.md   # 子機能抽象仕様書
    |       |- {child-feature}_design.md # 子機能技術設計書
    |- task/                         # 一時タスクログ
        |- {ticket-number}/

### ファイル命名規則（重要）

**注意: requirement と specification でサフィックスの有無が異なります。混同しないでください。**

| ディレクトリ            | ファイル種別 | 命名パターン                                 | 例                                         |
|:------------------|:-------|:---------------------------------------|:------------------------------------------|
| **requirement**   | 全ファイル  | `{name}.md`（サフィックスなし）                  | `user-login.md`, `index.md`               |
| **specification** | 抽象仕様書  | `{name}_spec.md`（`_spec` サフィックス必須）     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | 技術設計書  | `{name}_design.md`（`_design` サフィックス必須） | `user-login_design.md`, `index_design.md` |

#### 命名パターン早見表

```
# 正しい命名
requirement/auth/index.md              # 親機能概要（サフィックスなし）
requirement/auth/user-login.md         # 子機能要求仕様（サフィックスなし）
specification/auth/index_spec.md       # 親機能抽象仕様書（_spec 必須）
specification/auth/index_design.md     # 親機能技術設計書（_design 必須）
specification/auth/user-login_spec.md  # 子機能抽象仕様書（_spec 必須）
specification/auth/user-login_design.md # 子機能技術設計書（_design 必須）

# 誤った命名（使用しないこと）
requirement/auth/index_spec.md         # requirement に _spec は不要
specification/auth/user-login.md       # specification には _spec/_design が必須
specification/auth/index.md            # specification には _spec/_design が必須
```

### ドキュメントリンク規約

ドキュメント内のマークダウンリンクは以下の形式に従ってください:

| リンク先       | 形式                                    | リンクテキスト   | 例                                                    |
|:-----------|:--------------------------------------|:----------|:-----------------------------------------------------|
| **ファイル**   | `[filename.md](パスまたはURL)`             | ファイル名を含める | `[user-login.md](../requirement/auth/user-login.md)` |
| **ディレクトリ** | `[directory-name](パスまたはURL/index.md)` | ディレクトリ名のみ | `[auth](../requirement/auth/index.md)`               |

この規約により、リンク先がファイルかディレクトリかが視覚的に明確になります。
