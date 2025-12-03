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
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow-ja
```

その後、プラグインをインストール：

```
/plugin install sdd-workflow-ja@ToshikiImagawa/ai-sdd-workflow-ja
```

### 方法2: GitHubからクローン

```bash
git clone https://github.com/ToshikiImagawa/ai-sdd-workflow-ja.git ~/.claude/plugins/sdd-workflow-ja
```

インストール後、Claude Codeを再起動してください。

### 確認

Claude Codeで `/plugin` コマンドを実行し、`sdd-workflow-ja` が表示されることを確認してください。

## 含まれるコンポーネント

### エージェント

| エージェント          | 説明                                                |
|:----------------|:--------------------------------------------------|
| `sdd-workflow`  | AI-SDD開発フローの管理。フェーズ判定、Vibe Coding防止、ドキュメント整合性チェック |
| `spec-reviewer` | 仕様書の品質レビューと改善提案。曖昧な記述の検出、不足セクションの指摘               |

### コマンド

| コマンド              | 説明                               |
|:------------------|:---------------------------------|
| `/generate_spec`  | 入力から抽象仕様書と技術設計書を生成               |
| `/generate_prd`   | ビジネス要求からPRD（要求仕様書）をSysML要求図形式で生成 |
| `/check_spec`     | 実装コードと仕様書の整合性をチェックし、差異を検出        |
| `/review_cleanup` | 実装完了後のreview/ディレクトリを整理し、設計判断を統合  |
| `/task_breakdown` | 技術設計書からタスクを分解し、小タスクのリストを生成       |

### スキル

| スキル                       | 説明                                  |
|:--------------------------|:------------------------------------|
| `vibe-detector`           | ユーザー入力を分析し、Vibe Coding（曖昧な指示）を自動検出  |
| `doc-consistency-checker` | ドキュメント間（PRD、spec、design）の整合性を自動チェック |

### フック

| フック                   | トリガー                   | 説明                   |
|:----------------------|:-----------------------|:---------------------|
| `check-spec-exists`   | PreToolUse（Edit/Write） | 実装前に仕様書の存在を確認し、警告を表示 |
| `check-commit-prefix` | PostToolUse（Bash）      | コミットメッセージ規約をチェック     |

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

#### レビュークリーンアップ

```
/review_cleanup TICKET-123
```

## フックの設定

フックを有効にするには、プロジェクトの `.claude/settings.json` に以下を追加してください：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "hooks/check-spec-exists.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "hooks/check-commit-prefix.sh"
          }
        ]
      }
    ]
  }
}
```

設定例は `hooks/settings.example.json` を参照してください。

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

```
.docs/
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（任意）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（任意）
├── requirement-diagram/          # PRD（要求仕様書）
│   └── {機能名}.md
├── specification/                # 永続的な知識資産
│   ├── {機能名}_spec.md         # 抽象仕様書
│   └── {機能名}_design.md       # 技術設計書
└── review/                       # 一時的な作業ログ（実装完了後に削除）
    └── {チケット番号}/
```

## プラグイン構造

```
sdd-workflow-ja/
├── .claude-plugin/
│   └── plugin.json              # プラグインマニフェスト
├── agents/
│   ├── sdd-workflow.md          # AI-SDD開発フローエージェント
│   └── spec-reviewer.md         # 仕様書レビューエージェント
├── commands/
│   ├── generate_spec.md         # 仕様書・設計書生成
│   ├── generate_prd.md          # PRD生成
│   ├── check_spec.md            # 整合性チェック
│   ├── review_cleanup.md        # レビュークリーンアップ
│   └── task_breakdown.md        # タスク分解
├── skills/
│   ├── vibe-detector.md         # Vibe Coding検出スキル
│   └── doc-consistency-checker.md
├── hooks/
│   ├── check-spec-exists.sh
│   ├── check-commit-prefix.sh
│   └── settings.example.json
├── LICENSE
└── README.md
```

## コミットメッセージ規約

| プレフィックス    | 用途                       |
|:-----------|:-------------------------|
| `[docs]`   | ドキュメントの追加・更新             |
| `[spec]`   | 仕様書の追加・更新（`*_spec.md`）   |
| `[design]` | 設計書の追加・更新（`*_design.md`） |

## ライセンス

MIT License
