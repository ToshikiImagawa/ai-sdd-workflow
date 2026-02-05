# sdd-workflow-ja

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する統合 Claude Code プラグイン（多言語対応）。

## 概要

このプラグインは Vibe Coding 問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのツールを提供します。`SDD_LANG`
設定による多言語対応。

## 対応環境

| OS      | サポート | 備考             |
|:--------|:----:|:---------------|
| macOS   |  ✅   | 完全サポート         |
| Linux   |  ✅   | 完全サポート         |
| Windows |  ❌   | 非対応（下記の代替案を参照） |

### Windows の制限事項

このプラグインの `session-start.sh` フックは bash スクリプトとして実装されており、Windows では動作しません。

### Windows ユーザー向けの代替案

1. **WSL (Windows Subsystem for Linux) の使用**（推奨）
    - WSL2 をインストールし、Linux 環境内で Claude Code を実行
    - [WSL インストールガイド](https://learn.microsoft.com/ja-jp/windows/wsl/install)

2. **Git Bash の使用**
    - Git for Windows に含まれる Git Bash で bash スクリプトを実行可能
    - [Git for Windows](https://gitforwindows.org/)

### 今後のサポート予定

- PowerShell 版スクリプトの追加を検討中
- クロスプラットフォーム実装（例: Node.js）への移行を検討中

### Vibe Coding とは？

Vibe Coding は、曖昧な指示によって AI が数千もの未定義の要件を推測しなければならない状況で発生します。
このプラグインは、仕様を中心とした開発フローを提供することでこの問題を解決します。

## インストール

### 方法 1: マーケットプレイスからインストール（推奨）

Claude Code で以下を実行:

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

次にプラグインをインストール:

```
/plugin install sdd-workflow-ja@ToshikiImagawa/ai-sdd-workflow
```

### 方法 2: GitHub からクローン

```bash
git clone https://github.com/ToshikiImagawa/ai-sdd-workflow.git ~/.claude/plugins/sdd-workflow-ja
```

インストール後、Claude Code を再起動してください。

### 確認

Claude Code で `/plugin` コマンドを実行し、`sdd-workflow-ja` が表示されることを確認してください。

## 言語設定

`.sdd-config.json` で言語を設定:

```json
{
  "lang": "ja"
}
```

対応言語: `en`（デフォルト）, `ja`

セッション開始時に、この設定から `SDD_LANG` 環境変数が自動的に設定されます。

## クイックスタート

### 1. プロジェクト初期化

**このプラグインを初めて使用するプロジェクトでは、`/sdd-init` を実行してください。**

```
/sdd-init
```

このコマンドは自動的に:

- プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
- `.sdd/` ディレクトリ構造を作成（requirement/, specification/, task/）
- PRD、仕様書、設計書のテンプレートファイルを生成

## 含まれるコンポーネント

### エージェント

| エージェント                    | 説明                                             |
|:--------------------------|:-----------------------------------------------|
| `prd-reviewer`            | PRD の品質と CONSTITUTION.md 準拠をレビュー。違反に対する修正提案を生成 |
| `spec-reviewer`           | 仕様書の品質と CONSTITUTION.md 準拠をレビュー。違反に対する修正提案を生成  |
| `requirement-analyzer`    | SysML 要件図ベースの分析、要件のトレーサビリティと検証                 |
| `clarification-assistant` | 仕様明確化支援。9つのカテゴリで要件を分析し、統合提案を出力                 |

### スキル（ユーザー起動可能）

| スキル               | 説明                                               |
|:------------------|:-------------------------------------------------|
| `/sdd-init`       | AI-SDD ワークフロー初期化。CLAUDE.md セットアップとテンプレート生成       |
| `/sdd-migrate`    | 旧バージョン（v1.x/v2.x）からの移行。新構造への移行または互換設定の生成         |
| `/generate-spec`  | 入力から抽象仕様書と技術設計書を生成                               |
| `/generate-prd`   | ビジネス要件から SysML 要件図形式の PRD（要求仕様書）を生成              |
| `/check-spec`     | 実装コードと仕様書の整合性をチェックし、不整合を検出                       |
| `/task-cleanup`   | 実装完了後の task/ ディレクトリをクリーンアップし、設計判断を統合             |
| `/task-breakdown` | 技術設計書からタスクを小タスクのリストに分解                           |
| `/clarify`        | 仕様を9つのカテゴリでスキャンし、曖昧さを明確化するための質問を生成               |
| `/implement`      | TDD ベースの5フェーズ実装。TaskList で進捗を追跡し、tasks.md に自動マーク |
| `/checklist`      | 仕様書と設計書から9カテゴリの品質チェックリストを自動生成                    |
| `/run-checklist`  | チェックリスト項目をテスト、リンター、セキュリティスキャンで自動検証               |
| `/constitution`   | プロジェクトの非交渉可能な原則（constitution）を定義・管理              |

### スキル（自動）

| スキル                       | 説明                                 |
|:--------------------------|:-----------------------------------|
| `vibe-detector`           | ユーザー入力を分析し、Vibe Coding（曖昧な指示）を自動検出 |
| `doc-consistency-checker` | ドキュメント間（PRD、仕様書、設計書）の整合性を自動チェック    |

### フック

| フック             | トリガー         | 説明                                     |
|:----------------|:-------------|:---------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json` から設定を読み込み、環境変数を自動設定 |

**注**: フックはプラグインインストール時に自動的に有効化されます。追加の設定は不要です。

## 使用方法

### コマンド使用例

#### PRD 生成

```
/generate-prd ユーザーがタスクを管理する機能。
ログインユーザーのみ利用可能。
```

#### 仕様書/設計書生成

```
/generate-spec ユーザー認証機能。メールアドレスとパスワードでのログイン・ログアウトをサポート。
```

#### 整合性チェック

```
/check-spec user-auth
```

#### タスク分解

```
/task-breakdown task-management TICKET-123
```

#### タスククリーンアップ

```
/task-cleanup TICKET-123
```

#### 仕様明確化

```
/clarify user-auth
```

9つのカテゴリで仕様をスキャンし、最大5つの明確化質問を生成します。

#### TDD ベース実装

```
/implement user-auth TICKET-123
```

5つのフェーズ（Setup→Tests→Core→Integration→Polish）で実装を実行し、tasks.md に進捗を自動マークします。

#### 品質チェックリスト生成

```
/checklist user-auth TICKET-123
```

仕様書と設計書から9カテゴリの品質チェックリストを自動生成します。

#### 自動チェックリスト検証

```
/run-checklist user-auth TICKET-123
/run-checklist user-auth TICKET-123 --priority P1  # P1 項目のみ実行
/run-checklist user-auth TICKET-123 --category testing  # テストカテゴリのみ実行
```

検証コマンド（テスト、リンター、セキュリティスキャン）を自動実行し、結果をチェックリストに記録します。

#### プロジェクト憲章管理

```
/constitution show                    # 現在の憲章を表示
/constitution add "Library-First"     # 新しい原則を追加
/constitution validate                # 仕様/設計が憲章に準拠しているか検証
```

プロジェクトの非交渉可能な原則を定義・管理します。最初に `/constitution init` で憲章ファイルを作成してください。

### 完全なワークフロー例

新しい「ユーザー認証」機能を実装する完全なワークフローです。

#### Step 1: プロジェクト初期化（初回のみ）

```
/sdd-init
```

プロジェクト憲章（CONSTITUTION.md）とテンプレートを生成します。

#### Step 2: 要求仕様書（PRD）の作成

```
/generate-prd ユーザー認証機能。メールアドレスとパスワードでのログイン・ログアウト。
セッション管理とパスワードリセット機能を含む。
```

→ `.sdd/requirement/user-auth.md` が生成されます。

#### Step 3: 仕様書と設計書の生成

```
/generate-spec user-auth
```

→ `.sdd/specification/user-auth_spec.md` と `user-auth_design.md` が生成されます。

#### Step 4: 仕様の明確化

```
/clarify user-auth
```

9つのカテゴリで仕様をスキャンし、不明確な点について質問を生成します。回答は仕様書に自動統合されます。

#### Step 5: タスク分解

```
/task-breakdown user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/tasks.md` にタスクリストが生成されます。

#### Step 6: 品質チェックリスト生成

```
/checklist user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/checklist.md` に9カテゴリの品質チェックリストが生成されます。

#### Step 7: TDD ベース実装

```
/implement user-auth TICKET-123
```

5つのフェーズ（Setup→Tests→Core→Integration→Polish）で進行し、進捗を自動マークします。

#### Step 8: チェックリスト項目の検証

```
/run-checklist user-auth TICKET-123
```

テスト、リンター、セキュリティスキャンを自動実行し、チェックリスト項目を検証します。検証レポートを生成します。

#### Step 9: 整合性チェック

```
/check-spec user-auth
```

実装と仕様書の整合性を検証し、不整合を報告します。

#### Step 10: タスククリーンアップ

```
/task-cleanup TICKET-123
```

一時ファイルをクリーンアップし、重要な設計判断を `*_design.md` に統合します。

## v2.x からの移行

### v3.0.0 の破壊的変更

1. **2つのプラグインを1つに統合**: `sdd-workflow-ja` と `sdd-workflow` は `SDD_LANG` による多言語対応を持つ単一の
   `sdd-workflow` プラグインに統合
2. **コマンドをスキルに変換**: 11のコマンドすべてがハイフン区切りの名前を持つスキルに移行
3. **コマンド名の変更**: アンダースコアをハイフンに置換（例: `/sdd_init` → `/sdd-init`）

### コマンド名の移行

| 旧 (v2.x)          | 新 (v3.0.0)        |
|:------------------|:------------------|
| `/sdd_init`       | `/sdd-init`       |
| `/generate_spec`  | `/generate-spec`  |
| `/generate_prd`   | `/generate-prd`   |
| `/check_spec`     | `/check-spec`     |
| `/task_breakdown` | `/task-breakdown` |
| `/task_cleanup`   | `/task-cleanup`   |
| `/sdd_migrate`    | `/sdd-migrate`    |
| `/implement`      | `/implement`      |
| `/clarify`        | `/clarify`        |
| `/constitution`   | `/constitution`   |
| `/checklist`      | `/checklist`      |

### 移行手順

1. `sdd-workflow-ja` を使用している場合、アンインストールして `sdd-workflow` をインストール
2. 日本語サポートのために `.sdd-config.json` に `"lang": "ja"` を設定
3. 自動化スクリプトを新しいコマンド名（アンダースコアからハイフン）に更新

## フックについて

このプラグインはセッション開始時に `.sdd-config.json` を自動的に読み込み、環境変数を設定します。
**フックはプラグインインストール時に自動的に有効化されます。追加の設定は不要です。**

### フックの動作

| フック             | トリガー         | 説明                                   |
|:----------------|:-------------|:-------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json` から設定を読み込み、環境変数を設定 |

### 設定される環境変数

セッション開始時に以下の環境変数が自動的に設定されます:

| 環境変数                     | デフォルト                | 説明            |
|:-------------------------|:---------------------|:--------------|
| `SDD_ROOT`               | `.sdd`               | ルートディレクトリ     |
| `SDD_LANG`               | `ja`                 | 言語設定          |
| `SDD_REQUIREMENT_DIR`    | `requirement`        | 要求仕様書ディレクトリ   |
| `SDD_SPECIFICATION_DIR`  | `specification`      | 仕様書/設計書ディレクトリ |
| `SDD_TASK_DIR`           | `task`               | タスクログディレクトリ   |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | 要求仕様書フルパス     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書/設計書フルパス   |
| `SDD_TASK_PATH`          | `.sdd/task`          | タスクログフルパス     |

### フックのデバッグ

フックの登録状態を確認するには:

```bash
claude --debug
```

## Serena MCP 連携（オプション）

[Serena](https://github.com/oraios/serena) MCP を設定すると、セマンティックコード分析による機能強化が可能です。

### Serena とは？

Serena は LSP（Language Server Protocol）ベースのセマンティックコード分析ツールで、30以上のプログラミング言語をサポートしています。
シンボルレベルのコード検索と分析が可能です。

### 設定

プロジェクトの `.mcp.json` に以下を追加:

```json
{
  "mcpServers": {
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        ".",
        "--enable-web-dashboard",
        "false"
      ]
    }
  }
}
```

### 強化される機能

| スキル               | Serena 連携時の強化内容                 |
|:------------------|:--------------------------------|
| `/generate-spec`  | 既存コードの API/型定義を参照して一貫性のある仕様生成   |
| `/check-spec`     | シンボルベース検索による高精度な API 実装とシグネチャ検証 |
| `/task-breakdown` | 変更影響範囲を分析して正確なタスク依存関係をマッピング     |

### Serena なしの場合

すべての機能は Serena なしでも動作します。分析にはテキストベース検索（Grep/Glob）が使用され、言語に依存しません。

## AI-SDD 開発フロー

```
仕様化 → 計画 → タスク → 実装 & レビュー
```

### 推奨ディレクトリ構造

フラット構造と階層構造の両方をサポートしています。

#### フラット構造（小〜中規模プロジェクト向け）

```
.sdd/
├── CONSTITUTION.md               # プロジェクト憲章（最上位）
├── PRD_TEMPLATE.md               # PRD テンプレート（オプション）
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（オプション）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（オプション）
├── requirement/                  # PRD（要求仕様書）
│   └── {feature-name}.md
├── specification/                # 永続的な知識資産
│   ├── {feature-name}_spec.md    # 抽象仕様書
│   └── {feature-name}_design.md  # 技術設計書
└── task/                         # 一時的なタスクログ（実装後に削除）
    └── {ticket-number}/
```

#### 階層構造（中〜大規模プロジェクト向け）

```
.sdd/
├── CONSTITUTION.md               # プロジェクト憲章（最上位）
├── PRD_TEMPLATE.md               # PRD テンプレート（オプション）
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（オプション）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（オプション）
├── requirement/                  # PRD（要求仕様書）
│   ├── {feature-name}.md         # トップレベル機能（フラット構造と下位互換）
│   └── {parent-feature}/         # 親機能ディレクトリ
│       ├── index.md              # 親機能の概要と要件リスト
│       └── {child-feature}.md    # 子機能の要件
├── specification/                # 永続的な知識資産
│   ├── {feature-name}_spec.md    # トップレベル機能（フラット構造と下位互換）
│   ├── {feature-name}_design.md
│   └── {parent-feature}/         # 親機能ディレクトリ
│       ├── index_spec.md         # 親機能の抽象仕様書
│       ├── index_design.md       # 親機能の技術設計書
│       ├── {child-feature}_spec.md   # 子機能の抽象仕様書
│       └── {child-feature}_design.md # 子機能の技術設計書
└── task/                         # 一時的なタスクログ（実装後に削除）
    └── {ticket-number}/
```

#### ドキュメント依存関係

```
CONSTITUTION.md → requirement/ → *_spec.md → *_design.md → task/ → 実装
```

すべてのドキュメントは `CONSTITUTION.md` のプロジェクト原則に従って作成されます。

**階層構造の使用例**:

```
/generate-prd auth/user-login   # auth ドメイン下に user-login PRD を生成
/generate-spec auth/user-login  # auth ドメイン下に仕様を生成
/check-spec auth                # auth ドメイン全体の整合性をチェック
```

### プロジェクト設定ファイル

プロジェクトルートに `.sdd-config.json` を配置して、ディレクトリ名と言語をカスタマイズできます。

```json
{
  "root": ".sdd",
  "lang": "ja",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
```

| 設定                          | デフォルト           | 説明                |
|:----------------------------|:----------------|:------------------|
| `root`                      | `.sdd`          | ルートディレクトリ         |
| `lang`                      | `ja`            | 言語（`en` または `ja`） |
| `directories.requirement`   | `requirement`   | PRD（要求仕様書）ディレクトリ  |
| `directories.specification` | `specification` | 仕様書/設計書ディレクトリ     |
| `directories.task`          | `task`          | 一時タスクログディレクトリ     |

**注**:

- 設定ファイルが存在しない場合、デフォルト値が使用されます
- 部分的な設定もサポートされています（未指定の項目はデフォルト値を使用）

## プラグイン構造

```
sdd-workflow-ja/
├── .claude-plugin/
│   └── plugin.json                # プラグインマニフェスト
├── agents -> ../sdd-workflow/agents  # sdd-workflow へのシンボリックリンク
├── skills -> ../sdd-workflow/skills  # sdd-workflow へのシンボリックリンク
├── hooks/
│   └── hooks.json                 # フック設定
├── scripts/
│   └── session-start.sh           # セッション開始初期化スクリプト（SDD_LANG=ja デフォルト）
├── AI-SDD-PRINCIPLES.source.md -> ../sdd-workflow/AI-SDD-PRINCIPLES.source.md
├── LICENSE -> ../sdd-workflow/LICENSE
├── README.md
└── CHANGELOG.md
```

### sdd-workflow との違い

| 項目                          | sdd-workflow | sdd-workflow-ja           |
|:----------------------------|:-------------|:--------------------------|
| `SDD_LANG` デフォルト            | `en`         | `ja`                      |
| `.sdd-config.json` 自動生成時の言語 | `en`         | `ja`                      |
| エージェント・スキル                  | 独自           | sdd-workflow を参照（symlink） |

## ライセンス

MIT License
