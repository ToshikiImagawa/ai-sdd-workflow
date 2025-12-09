# sdd-workflow-ja

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する日本語 Claude Code プラグインです。

## 概要

このプラグインは、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのツール群を提供します。

### Vibe Codingとは？

曖昧な指示によりAIが数千の未定義要件を推測せざるを得ない問題のことです。
このプラグインは、仕様書を中心とした開発フローを提供することで、この問題を解決します。

## インストール

### 方法1: マーケットプレイスからインストール（推奨）

Claude Codeで以下を実行：

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

その後、プラグインをインストール：

```
/plugin install sdd-workflow-ja@ToshikiImagawa/ai-sdd-workflow
```

### 方法2: GitHubからクローン

```bash
git clone https://github.com/ToshikiImagawa/ai-sdd-workflow.git ~/.claude/plugins/sdd-workflow-ja
```

インストール後、Claude Codeを再起動してください。

### 確認

Claude Codeで `/plugin` コマンドを実行し、`sdd-workflow-ja` が表示されることを確認してください。

## クイックスタート

### 1. プロジェクトの初期化

**初めてこのプラグインを使用するプロジェクトでは、`/sdd_init` を実行してください。**

```
/sdd_init
```

このコマンドは以下を自動的に設定します：

- プロジェクトの `CLAUDE.md` にAI-SDD Instructionsセクションを追加
- `.sdd/` ディレクトリ構造を作成（requirement/, specification/, task/）
- PRD、仕様書、設計書のテンプレートファイルを生成

## 含まれるコンポーネント

### エージェント

| エージェント                 | 説明                                                |
|:-----------------------|:--------------------------------------------------|
| `sdd-workflow`         | AI-SDD開発フローの管理。フェーズ判定、Vibe Coding防止、ドキュメント整合性チェック |
| `spec-reviewer`        | 仕様書の品質レビューと改善提案。曖昧な記述の検出、不足セクションの指摘               |
| `requirement-analyzer` | SysML要求図に基づく要求分析、トラッキング、検証                        |

### コマンド

| コマンド              | 説明                                    |
|:------------------|:--------------------------------------|
| `/sdd_init`       | AI-SDDワークフローの初期化。CLAUDE.md設定とテンプレート生成 |
| `/sdd_migrate`    | 旧バージョン（v1.x）からの移行。新構成への移行または互換性設定の生成  |
| `/generate_spec`  | 入力から抽象仕様書と技術設計書を生成                    |
| `/generate_prd`   | ビジネス要求からPRD（要求仕様書）をSysML要求図形式で生成      |
| `/check_spec`     | 実装コードと仕様書の整合性をチェックし、差異を検出             |
| `/task_cleanup`   | 実装完了後のtask/ディレクトリを整理し、設計判断を統合         |
| `/task_breakdown` | 技術設計書からタスクを分解し、小タスクのリストを生成            |

### スキル

| スキル                       | 説明                                  |
|:--------------------------|:------------------------------------|
| `vibe-detector`           | ユーザー入力を分析し、Vibe Coding（曖昧な指示）を自動検出  |
| `doc-consistency-checker` | ドキュメント間（PRD、spec、design）の整合性を自動チェック |
| `sdd-templates`           | PRD、仕様書、設計書テンプレートのフォールバック提供         |

### フック

| フック             | トリガー         | 説明                                    |
|:----------------|:-------------|:--------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json`から設定を読み込み、環境変数を自動設定 |

**注意**: フックはプラグインインストール時に自動的に有効化されます。追加の設定は不要です。

## 使用方法

### sdd-workflow エージェント

タスク開始時に自動的に以下を実行します：

1. **フェーズ判定**: タスクの性質に応じて必要なフェーズを特定
2. **Vibe Coding防止**: 曖昧な指示を検出し、仕様の明確化を促進
3. **ドキュメント管理**: 仕様書・設計書の作成・更新をガイド

### コマンドの使用例

#### PRD生成

```
/generate_prd ユーザーがタスクを管理できる機能。
ログイン済みのユーザーのみ利用可能。
```

#### 仕様書・設計書生成

```
/generate_spec ユーザー認証機能。メールアドレスとパスワードによるログイン・ログアウトに対応。
```

#### 整合性チェック

```
/check_spec user-auth
```

#### タスク分解

```
/task_breakdown task-management TICKET-123
```

#### タスククリーンアップ

```
/task_cleanup TICKET-123
```

## フックについて

このプラグインは、セッション開始時に自動的に `.sdd-config.json` を読み込み、環境変数を設定します。
**プラグインインストール時に自動的に有効化されるため、追加の設定は不要です。**

### フックの動作

| フック             | トリガー         | 説明                                  |
|:----------------|:-------------|:------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json`から設定を読み込み、環境変数を設定 |

### 設定される環境変数

以下の環境変数がセッション開始時に自動的に設定されます：

| 環境変数                     | デフォルト値               | 説明                |
|:-------------------------|:---------------------|:------------------|
| `SDD_DOCS_ROOT`          | `.sdd`               | ドキュメントルート         |
| `SDD_REQUIREMENT_DIR`    | `requirement`        | 要求仕様書ディレクトリ名      |
| `SDD_SPECIFICATION_DIR`  | `specification`      | 仕様書・設計書ディレクトリ名    |
| `SDD_TASK_DIR`           | `task`               | タスクログディレクトリ名      |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | 要求仕様書フルパス         |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書・設計書フルパス       |
| `SDD_TASK_PATH`          | `.sdd/task`          | タスクログフルパス         |

### フックのデバッグ

フックの登録状況を確認するには：

```bash
claude --debug
```

## Serena MCP 統合（オプション）

[Serena](https://github.com/oraios/serena) MCP を設定することで、セマンティックコード分析による機能強化が可能です。

### Serena とは

Serena は LSP（Language Server Protocol）ベースのセマンティックコード分析ツールで、30以上のプログラミング言語に対応しています。シンボルレベルでのコード検索・分析が可能です。

### 設定方法

プロジェクトの `.mcp.json` に以下を追加：

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

| コマンド              | Serena による強化内容                    |
|:------------------|:----------------------------------|
| `/generate_spec`  | 既存コードから API・型定義を参照し、一貫性のある仕様を生成   |
| `/check_spec`     | シンボルベースで API 実装の存在・シグネチャ一致を高精度に検証 |
| `/task_breakdown` | 変更の影響範囲を分析し、依存関係を正確にタスク化          |

### Serena 未設定時

Serena がなくても全機能は動作します。テキストベース検索（Grep/Glob）による分析となり、言語非依存で動作します。

## AI-SDD 開発フロー

```
Specify（仕様化） → Plan（計画） → Tasks（タスク分解） → Implement & Review（実装と検証）
```

### 推奨ディレクトリ構造

フラット構造と階層構造の両方をサポートします。

#### フラット構造（小〜中規模プロジェクト向け）

```
.sdd/
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（任意）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（任意）
├── requirement/          # PRD（要求仕様書）
│   └── {機能名}.md
├── specification/                # 永続的な知識資産
│   ├── {機能名}_spec.md         # 抽象仕様書
│   └── {機能名}_design.md       # 技術設計書
└── task/                         # 一時的なタスクログ（実装完了後に削除）
    └── {チケット番号}/
```

#### 階層構造（中〜大規模プロジェクト向け）

```
.sdd/
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（任意）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（任意）
├── requirement/          # PRD（要求仕様書）
│   ├── {機能名}.md              # トップレベル機能（フラット構造との互換性）
│   └── {親機能名}/              # 親機能ディレクトリ
│       ├── index.md             # 親機能の概要・要求一覧
│       └── {子機能名}.md        # 子機能の要求仕様
├── specification/                # 永続的な知識資産
│   ├── {機能名}_spec.md         # トップレベル機能（フラット構造との互換性）
│   ├── {機能名}_design.md
│   └── {親機能名}/              # 親機能ディレクトリ
│       ├── index_spec.md        # 親機能の抽象仕様書
│       ├── index_design.md      # 親機能の技術設計書
│       ├── {子機能名}_spec.md   # 子機能の抽象仕様書
│       └── {子機能名}_design.md # 子機能の技術設計書
└── task/                         # 一時的なタスクログ（実装完了後に削除）
    └── {チケット番号}/
```

**階層構造の使用例**:

```
/generate_prd auth/user-login   # 認証ドメイン配下にユーザーログイン機能のPRDを生成
/generate_spec auth/user-login  # 認証ドメイン配下に仕様書を生成
/check_spec auth                # 認証ドメイン全体の整合性をチェック
```

### プロジェクト設定ファイル

プロジェクトルートに `.sdd-config.json` を配置することで、ディレクトリ名をカスタマイズできます。

```json
{
  "docsRoot": ".sdd",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
```

| 設定項目                        | デフォルト値          | 説明                |
|:----------------------------|:----------------|:------------------|
| `docsRoot`                  | `.sdd`          | ドキュメントルートディレクトリ   |
| `directories.requirement`   | `requirement`   | PRD（要求仕様書）ディレクトリ名 |
| `directories.specification` | `specification` | 仕様書・設計書ディレクトリ名    |
| `directories.task`          | `task`          | 一時的なタスクログディレクトリ名  |

**注意**:

- 設定ファイルが存在しない場合、デフォルト値が使用されます
- 部分的な設定も可能です（指定されていない項目はデフォルト値を使用）

**カスタム設定の例**:

```json
{
  "docsRoot": "docs",
  "directories": {
    "requirement": "requirements",
    "specification": "specs"
  }
}
```

この設定では以下のディレクトリ構造になります：

```
docs/
├── requirements/       # PRD（要求仕様書）
├── specs/              # 仕様書・設計書
└── task/               # 一時的なタスクログ（デフォルト値）
```

## プラグイン構造

```
sdd-workflow-ja/
├── .claude-plugin/
│   └── plugin.json              # プラグインマニフェスト
├── agents/
│   ├── sdd-workflow.md          # AI-SDD開発フローエージェント
│   ├── spec-reviewer.md         # 仕様書レビューエージェント
│   └── requirement-analyzer.md  # 要求仕様分析エージェント
├── commands/
│   ├── sdd_init.md              # AI-SDDワークフロー初期化
│   ├── sdd_migrate.md           # 旧バージョンからの移行
│   ├── generate_spec.md         # 仕様書・設計書生成
│   ├── generate_prd.md          # PRD生成
│   ├── check_spec.md            # 整合性チェック
│   ├── task_cleanup.md          # タスククリーンアップ
│   └── task_breakdown.md        # タスク分解
├── skills/
│   ├── vibe-detector/           # Vibe Coding検出スキル
│   │   ├── SKILL.md
│   │   └── templates/
│   ├── doc-consistency-checker/ # ドキュメント整合性チェック
│   │   ├── SKILL.md
│   │   └── templates/
│   └── sdd-templates/           # AI-SDDテンプレート
│       ├── SKILL.md
│       └── templates/
├── hooks/
│   └── hooks.json               # フック設定
├── scripts/
│   └── session-start.sh         # セッション開始時の初期化スクリプト
├── LICENSE
└── README.md
```

## ライセンス

MIT License
