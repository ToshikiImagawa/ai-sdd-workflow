# sdd-workflow-ja

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する日本語 Claude Code プラグインです。

## 概要

このプラグインは、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのツール群を提供します。

## 対応環境

| OS      | 対応状況 | 備考              |
|:--------|:----:|:----------------|
| macOS   |  ✅   | フル対応            |
| Linux   |  ✅   | フル対応            |
| Windows |  ❌   | 非対応（下記の代替手段を参照） |

### Windows環境での制限事項

このプラグインの `session-start.sh` フックはbashスクリプトとして実装されているため、Windows環境では動作しません。

### Windowsユーザー向けの代替手段

1. **WSL (Windows Subsystem for Linux) の使用**（推奨）
    - WSL2をインストールし、Linux環境内でClaude Codeを実行してください
    - [WSL インストールガイド](https://learn.microsoft.com/ja-jp/windows/wsl/install)

2. **Git Bash の使用**
    - Git for Windowsに付属するGit Bashを使用することで、bashスクリプトが実行可能になる場合があります
    - [Git for Windows](https://gitforwindows.org/)

### 将来的な対応方針

- PowerShell版スクリプトの追加を検討中
- Node.js等のクロスプラットフォーム実装への移行を検討中

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

| エージェント                    | 説明                                           |
|:--------------------------|:---------------------------------------------|
| `prd-reviewer`            | PRDの品質レビューとCONSTITUTION.md準拠チェック。違反時は自動修正を試行 |
| `spec-reviewer`           | 仕様書の品質レビューとCONSTITUTION.md準拠チェック。違反時は自動修正を試行 |
| `requirement-analyzer`    | SysML要求図に基づく要求分析、トラッキング、検証                   |
| `clarification-assistant` | 仕様明確化支援。要件を9カテゴリで分析し、質問を生成して仕様書に統合           |

### コマンド

| コマンド              | 説明                                                |
|:------------------|:--------------------------------------------------|
| `/sdd_init`       | AI-SDDワークフローの初期化。CLAUDE.md設定とテンプレート生成             |
| `/sdd_migrate`    | 旧バージョン（v1.x）からの移行。新構成への移行または互換性設定の生成              |
| `/generate_spec`  | 入力から抽象仕様書と技術設計書を生成                                |
| `/generate_prd`   | ビジネス要求からPRD（要求仕様書）をSysML要求図形式で生成                  |
| `/check_spec`     | 実装コードと仕様書の整合性をチェックし、差異を検出                         |
| `/task_cleanup`   | 実装完了後のtask/ディレクトリを整理し、設計判断を統合                     |
| `/task_breakdown` | 技術設計書からタスクを分解し、小タスクのリストを生成                        |
| `/clarify`        | 仕様書の不明点を9カテゴリでスキャンし、質問を生成して仕様を明確化                 |
| `/implement`      | TDDベースで5フェーズ順に実装を実行。TaskListで進捗追跡し、tasks.mdに自動マーク |
| `/checklist`      | 仕様書・設計書から9カテゴリの品質チェックリストを自動生成                     |
| `/constitution`   | プロジェクトの非交渉原則を定義・管理                                |

### スキル

| スキル                       | 説明                                          |
|:--------------------------|:--------------------------------------------|
| `vibe-detector`           | ユーザー入力を分析し、Vibe Coding（曖昧な指示）を自動検出          |
| `doc-consistency-checker` | ドキュメント間（PRD、spec、design）の整合性を自動チェック         |
| `sdd-templates`           | PRD、仕様書、設計書、チェックリスト、原則、実装ログテンプレートのフォールバック提供 |

### フック

| フック             | トリガー         | 説明                                    |
|:----------------|:-------------|:--------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json`から設定を読み込み、環境変数を自動設定 |

**注意**: フックはプラグインインストール時に自動的に有効化されます。追加の設定は不要です。

## 使用方法

### コマンドの使用例

#### 要求仕様書生成

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

#### 仕様明確化

```
/clarify user-auth
```

仕様書の不明点を9カテゴリでスキャンし、最大5つの質問を生成します。

#### TDDベース実装

```
/implement user-auth TICKET-123
```

5フェーズ（Setup→Tests→Core→Integration→Polish）順に実装を実行し、進捗をtasks.mdに自動マークします。

#### 品質チェックリスト生成

```
/checklist user-auth TICKET-123
```

仕様書・設計書から9カテゴリの品質チェックリストを自動生成します。

#### プロジェクト原則管理

```
/constitution show                    # 現在の原則を表示
/constitution add "Library-First"     # 新しい原則を追加
/constitution validate                # 仕様書・設計書が原則に準拠しているか検証
```

プロジェクトの非交渉原則を定義・管理します。初回は `/constitution init` で原則ファイルを作成します。

### 完全なワークフロー例

新機能「ユーザー認証」を実装する場合の完全なワークフローを示します。

#### ステップ1: プロジェクト初期化（初回のみ）

```
/sdd_init
```

プロジェクト原則（CONSTITUTION.md）とテンプレートが生成されます。

#### ステップ2: 要求仕様書（PRD）の作成

```
/generate_prd ユーザー認証機能。メールアドレスとパスワードによるログイン・ログアウト。
セッション管理とパスワードリセット機能も含む。
```

→ `.sdd/requirement/user-auth.md` が生成されます。

#### ステップ3: 仕様書・設計書の生成

```
/generate_spec user-auth
```

→ `.sdd/specification/user-auth_spec.md` と `user-auth_design.md` が生成されます。

#### ステップ4: 仕様の明確化

```
/clarify user-auth
```

9カテゴリで仕様をスキャンし、不明点に対する質問を生成。回答後、仕様書に自動統合されます。

#### ステップ5: タスク分解

```
/task_breakdown user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/tasks.md` にタスクリストが生成されます。

#### ステップ6: 品質チェックリストの生成

```
/checklist user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/checklist.md` に9カテゴリのチェックリストが生成されます。

#### ステップ7: TDDベースの実装

```
/implement user-auth TICKET-123
```

5フェーズ（Setup→Tests→Core→Integration→Polish）で実装を進め、進捗が自動でマークされます。

#### ステップ8: 整合性チェック

```
/check_spec user-auth
```

実装と仕様書の整合性を検証し、差異があれば報告されます。

#### ステップ9: タスククリーンアップ

```
/task_cleanup TICKET-123
```

一時ファイルを整理し、重要な設計判断を `*_design.md` に統合します。

## フックについて

このプラグインは、セッション開始時に自動的に `.sdd-config.json` を読み込み、環境変数を設定します。
**プラグインインストール時に自動的に有効化されるため、追加の設定は不要です。**

### フックの動作

| フック             | トリガー         | 説明                                  |
|:----------------|:-------------|:------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json`から設定を読み込み、環境変数を設定 |

### 設定される環境変数

以下の環境変数がセッション開始時に自動的に設定されます：

| 環境変数                     | デフォルト値               | 説明             |
|:-------------------------|:---------------------|:---------------|
| `SDD_ROOT`               | `.sdd`               | ルートディレクトリ      |
| `SDD_REQUIREMENT_DIR`    | `requirement`        | 要求仕様書ディレクトリ名   |
| `SDD_SPECIFICATION_DIR`  | `specification`      | 仕様書・設計書ディレクトリ名 |
| `SDD_TASK_DIR`           | `task`               | タスクログディレクトリ名   |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | 要求仕様書フルパス      |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書・設計書フルパス    |
| `SDD_TASK_PATH`          | `.sdd/task`          | タスクログフルパス      |

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
├── CONSTITUTION.md               # プロジェクト原則（最上位）
├── PRD_TEMPLATE.md               # PRDテンプレート（任意）
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（任意）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（任意）
├── requirement/                  # PRD（要求仕様書）
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
├── CONSTITUTION.md               # プロジェクト原則（最上位）
├── PRD_TEMPLATE.md               # PRDテンプレート（任意）
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（任意）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（任意）
├── requirement/                  # PRD（要求仕様書）
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

#### ドキュメント依存関係

```
CONSTITUTION.md → requirement/ → *_spec.md → *_design.md → task/ → 実装
```

すべてのドキュメントは `CONSTITUTION.md` のプロジェクト原則に従って作成されます。

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
  "root": ".sdd",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
```

| 設定項目                        | デフォルト値          | 説明                |
|:----------------------------|:----------------|:------------------|
| `root`                      | `.sdd`          | ルートディレクトリ         |
| `directories.requirement`   | `requirement`   | PRD（要求仕様書）ディレクトリ名 |
| `directories.specification` | `specification` | 仕様書・設計書ディレクトリ名    |
| `directories.task`          | `task`          | 一時的なタスクログディレクトリ名  |

**注意**:

- 設定ファイルが存在しない場合、デフォルト値が使用されます
- 部分的な設定も可能です（指定されていない項目はデフォルト値を使用）

**カスタム設定の例**:

```json
{
  "root": "docs",
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
│   └── plugin.json                # プラグインマニフェスト
├── agents/
│   ├── sdd-workflow.md            # AI-SDD開発フローエージェント
│   ├── prd-reviewer.md            # PRDレビュー・CONSTITUTION準拠チェックエージェント
│   ├── spec-reviewer.md           # 仕様書レビュー・CONSTITUTION準拠チェックエージェント
│   ├── requirement-analyzer.md    # 要求仕様分析エージェント
│   └── clarification-assistant.md # 仕様明確化支援エージェント
├── commands/
│   ├── sdd_init.md                # AI-SDDワークフロー初期化
│   ├── sdd_migrate.md             # 旧バージョンからの移行
│   ├── generate_spec.md           # 仕様書・設計書生成
│   ├── generate_prd.md            # PRD生成
│   ├── check_spec.md              # 整合性チェック
│   ├── task_cleanup.md            # タスククリーンアップ
│   ├── task_breakdown.md          # タスク分解
│   ├── clarify.md                 # 仕様明確化支援
│   ├── implement.md               # TDDベース実装実行
│   ├── checklist.md               # 品質チェックリスト生成
│   └── constitution.md            # プロジェクト原則管理
├── skills/
│   ├── vibe-detector/             # Vibe Coding検出スキル
│   │   ├── SKILL.md
│   │   └── templates/
│   ├── doc-consistency-checker/   # ドキュメント整合性チェック
│   │   ├── SKILL.md
│   │   └── templates/
│   └── sdd-templates/             # AI-SDDテンプレート
│       ├── SKILL.md
│       └── templates/
│           ├── prd_template.md
│           ├── spec_template.md
│           ├── design_template.md
│           ├── checklist_template.md
│           ├── constitution_template.md
│           └── implementation_log_template.md
├── hooks/
│   └── hooks.json                 # フック設定
├── scripts/
│   └── session-start.sh           # セッション開始時の初期化スクリプト
├── LICENSE
└── README.md
```

## ライセンス

MIT License
