# PLUGIN.md

Claude Codeプラグインとマーケットプレイスの作成ガイド

## 概要

このドキュメントは、[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
リポジトリの解析結果に基づき、Claude Codeプラグインの構造、設計、公開方法を包括的にまとめたものです。

## 目次

1. [プラグイン基本構造](#プラグイン基本構造)
2. [マニフェストファイル](#マニフェストファイル)
3. [コマンド (Commands)](#コマンド-commands)
4. [エージェント (Agents)](#エージェント-agents)
5. [スキル (Skills)](#スキル-skills)
6. [MCP サーバー連携](#mcp-サーバー連携)
7. [フック (Hooks)](#フック-hooks)
8. [マーケットプレイス公開](#マーケットプレイス公開)
9. [ベストプラクティス](#ベストプラクティス)

---

## プラグイン基本構造

### 標準ディレクトリレイアウト

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json              # プラグインマニフェスト（必須）
├── .mcp.json                    # MCP サーバー設定（任意）
├── commands/                    # スラッシュコマンド（任意）
│   ├── command-name.md
│   └── another-command.md
├── agents/                      # 自律エージェント（任意）
│   ├── agent-name.md
│   └── another-agent.md
├── skills/                      # モデル呼び出しスキル（任意）
│   └── skill-name/
│       ├── SKILL.md            # スキル定義
│       ├── README.md           # ドキュメント
│       └── examples/           # サポートファイル（任意）
├── hooks/                       # イベントフック（任意、高度な機能）
│   ├── session-start.sh
│   └── other-hooks.sh
└── README.md                    # プラグインドキュメント（推奨）
```

### マーケットプレイスリポジトリ構造

```
marketplace-repository/
├── .claude-plugin/
│   └── marketplace.json         # マーケットプレイスマニフェスト
├── plugins/                     # 内部プラグイン（公式管理）
│   ├── plugin-a/
│   └── plugin-b/
├── external_plugins/            # 外部プラグイン（サードパーティ）
│   ├── plugin-c/
│   └── plugin-d/
└── README.md
```

---

## マニフェストファイル

### plugin.json（プラグインマニフェスト）

**配置場所**: `{plugin-name}/.claude-plugin/plugin.json`

#### 必須フィールド

```json
{
  "name": "plugin-name",
  "description": "プラグインの機能を明確に説明",
  "author": {
    "name": "作成者名",
    "email": "author@example.com"
  }
}
```

#### 任意フィールド

```json
{
  "version": "1.0.0",
  "license": "MIT",
  "homepage": "https://github.com/username/plugin-name",
  "url": "https://..."
}
```

#### LSP専用フィールド（Language Server Protocol統合）

```json
{
  "strict": false,
  "lspServers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": [
        "--stdio"
      ],
      "extensionToLanguage": {
        ".ts": "typescript",
        ".tsx": "typescriptreact",
        ".js": "javascript",
        ".jsx": "javascriptreact"
      }
    }
  }
}
```

### marketplace.json（マーケットプレイスマニフェスト）

**配置場所**: リポジトリルート `.claude-plugin/marketplace.json`

```json
{
  "name": "repository-name",
  "metadata": {
    "description": "リポジトリの説明",
    "version": "1.0.0"
  },
  "owner": {
    "name": "owner-name",
    "url": "https://github.com/username"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "description": "プラグインの説明",
      "version": "1.0.0",
      "author": {
        "name": "作成者名",
        "url": "https://github.com/username"
      },
      "category": "development",
      "license": "MIT",
      "tags": [
        "tag1",
        "tag2"
      ]
    }
  ]
}
```

**pluginsフィールドの説明**:

| フィールド       | 必須  | 説明                                      |
|:------------|:----|:----------------------------------------|
| name        | Yes | プラグイン識別子（kebab-case）                    |
| source      | Yes | プラグインディレクトリへの相対パス                       |
| description | Yes | プラグインの機能説明                              |
| version     | Yes | セマンティックバージョン（例: `1.0.0`）                |
| author      | Yes | 作成者情報（name, url）                        |
| category    | No  | カテゴリ（`development`, `productivity`, など） |
| license     | No  | ライセンスタイプ                                |
| tags        | No  | 検索・フィルタリング用タグ                           |

---

## コマンド (Commands)

### コマンドファイル形式

- **配置場所**: `commands/command-name.md`
- **形式**: YAMLフロントマター付きMarkdown

### フロントマターフィールド

```yaml
---
description: "/help に表示される簡潔な説明"
argument-hint: "<必須引数> [任意引数]"
allowed-tools: [ Read, Glob, Grep, Bash, Edit, Write ]
model: sonnet
---
```

**利用可能なフィールド**:

| フィールド         | 型      | 必須  | 説明                                    |
|:--------------|:-------|:----|:--------------------------------------|
| description   | string | Yes | ヘルプテキストに表示される短い説明                     |
| argument-hint | string | No  | 使用方法のヒント（例: `<file> [options]`）       |
| allowed-tools | array  | No  | コマンドで使用可能なツールのリスト                     |
| model         | string | No  | モデルオーバーライド（`sonnet`, `opus`, `haiku`） |

### コマンド本体構造

```markdown
---
description: "gitコミットを作成"
allowed-tools: [Bash]
---

# コマンド実装

ユーザーが指定した引数: $ARGUMENTS

## 指示

1. $ARGUMENTS から引数をパース
2. 許可されたツールを使用してタスクを実行
3. 結果を報告

## 使用例

/command arg1 arg2
```

**重要な変数**:

- `$ARGUMENTS`: ユーザーがコマンドに渡した引数

### コマンド設計のベストプラクティス

1. **単一責任**: 各コマンドは1つのタスクに集中
2. **ツール制限**: `allowed-tools` で必要なツールのみ許可
3. **明確なヒント**: `argument-hint` でユーザーをガイド
4. **引数処理**: `$ARGUMENTS` を適切にパース

---

## エージェント (Agents)

### エージェントファイル形式

- **配置場所**: `agents/agent-name.md`
- **形式**: YAMLフロントマター付きMarkdown

### フロントマターフィールド

```yaml
---
name: agent-name
description: "このエージェントを呼び出すタイミング、トリガーフレーズ、ユースケースの詳細な説明"
model: sonnet
color: blue
allowed-tools: [ Read, Glob, Grep, Edit, Bash, TodoWrite ]
---
```

**利用可能なフィールド**:

| フィールド         | 型      | 必須  | 説明                                    |
|:--------------|:-------|:----|:--------------------------------------|
| name          | string | Yes | エージェント識別子（kebab-case）                 |
| description   | string | Yes | いつ・どのように呼び出すかの説明（具体的に！）               |
| model         | string | No  | モデル選択（`sonnet`, `opus`, `haiku`）      |
| color         | string | No  | ターミナル出力の色（`red`, `green`, `blue`, など） |
| allowed-tools | array  | No  | エージェントが使用できるツールのリスト                   |
| tools         | array  | No  | `allowed-tools` の代替フィールド              |

### モデル選択ガイド

| モデル    | 特性           | 使用場面               |
|:-------|:-------------|:-------------------|
| sonnet | バランス型（デフォルト） | 一般的なタスク            |
| opus   | 最も高機能、低速     | 複雑な分析・設計タスク        |
| haiku  | 高速、機能は限定的    | シンプルなタスク、クイックレスポンス |

### 色選択ガイド

| 色      | 用途例         |
|:-------|:------------|
| red    | エラー検出、警告    |
| green  | 成功、承認、レビュー  |
| blue   | 情報提供、分析     |
| yellow | 注意喚起、警告     |
| purple | 特殊タスク、実験的機能 |
| cyan   | ヘルパー、補助タスク  |

### description フィールドのベストプラクティス

descriptionは**エージェント呼び出しのトリガー**となる最も重要なフィールドです。

**含めるべき要素**:

1. **具体的なトリガーフレーズ**: 「〜を依頼されたとき」
2. **コンテキスト指標**: 「〜の後に」「〜の前に」
3. **タスク境界**: エージェントが**実行すること**と**実行しないこと**
4. **入力要件**: エージェントが必要とする情報

**良い例**（公式プラグインより）:

```yaml
description: "プロジェクトガイドライン、スタイルガイド、ベストプラクティスへの準拠をレビューするために使用します。コードの記述・変更後、特にコミットやプルリクエスト作成前に積極的に使用すべきです。スタイル違反、潜在的な問題をチェックし、CLAUDE.mdに定義されたパターンに従っているかを確認します。レビューに集中すべきファイルを知る必要があります。"
```

**悪い例**（曖昧で不明確）:

```yaml
description: "コードをレビューする"
```

### エージェント本体構造

```markdown
---
name: code-reviewer
description: "..."
model: opus
color: green
allowed-tools: [Read, Glob, Grep]
---

あなたは[ドメイン]を専門とするシニアコードレビュアーです。

## 入力

$ARGUMENTS

## 役割と責任

[詳細な役割説明]

## 分析プロセス

1. [ステップ1]
2. [ステップ2]
3. [ステップ3]

## 出力形式

以下を含む構造化されたフィードバックを提供:

- [セクション1]
- [セクション2]

## 制約条件

- [制約1]
- [制約2]
```

**重要な変数**:

- `$ARGUMENTS`: メインエージェントから渡された引数・コンテキスト

### エージェント設計のベストプラクティス

1. **詳細なdescription**: 具体的なトリガーフレーズを複数記載
2. **適切なモデル選択**: タスクの複雑さに応じて選択
3. **色分け**: ターミナル出力を視認しやすく
4. **明確な入出力**: 期待する入力と出力形式を定義
5. **ツール制限**: `allowed-tools` で必要最小限のツールのみ許可
6. **役割の明確化**: エージェントのペルソナと専門性を明示

詳細なエージェント設計原則は [AGENTS.md](./AGENTS.md) を参照してください。

---

## スキル (Skills)

### スキルファイル形式

- **配置場所**: `skills/skill-name/SKILL.md`
- **形式**: YAMLフロントマター付きMarkdown

### フロントマターフィールド

```yaml
---
name: skill-name
description: "このスキルは、ユーザーが「トリガーフレーズ」と尋ねたとき、または[トピック]について議論するときに使用されます。[機能]を提供します。"
version: 1.0.0
license: MIT
---
```

**利用可能なフィールド**:

| フィールド       | 型      | 必須  | 説明           |
|:------------|:-------|:----|:-------------|
| name        | string | Yes | スキル識別子       |
| description | string | Yes | トリガー条件と機能    |
| version     | string | No  | セマンティックバージョン |
| license     | string | No  | ライセンスタイプ     |

### description フィールドのベストプラクティス

具体的なトリガーフレーズを含める:

```yaml
description: "このスキルは、ユーザーが「スキルをデモンストレート」「スキルフォーマットを表示」「スキルテンプレートを作成」と尋ねたとき、またはスキル開発パターンについて議論するときに使用されます。Claude Codeプラグインスキル作成のリファレンステンプレートを提供します。"
```

### スキルディレクトリ構造

```
skills/
└── skill-name/
    ├── SKILL.md              # スキル定義（必須）
    ├── README.md             # ドキュメント（任意）
    ├── examples/             # 例ファイル（任意）
    │   ├── example1.md
    │   └── example2.md
    └── reference/            # 参照資料（任意）
        └── reference.md
```

### スキル設計のベストプラクティス

1. **明確なトリガーフレーズ**: description に具体的なフレーズを列挙
2. **単一機能**: スキルは1つの能力に集中
3. **構造化された整理**: 複雑なスキルはサブディレクトリで整理
4. **例とリファレンス**: examples/ と reference/ を活用
5. **バージョン管理**: version フィールドで変更を追跡

---

## MCP サーバー連携

### .mcp.json 形式

- **配置場所**: `{plugin-name}/.mcp.json`
- **目的**: Model Context Protocol サーバーを設定し、外部ツールと統合

### MCP 設定構造

```json
{
  "server-name": {
    "type": "http",
    "url": "https://api.example.com/mcp/",
    "headers": {
      "Authorization": "Bearer ${ENV_VAR_NAME}"
    }
  },
  "another-server": {
    "type": "http",
    "url": "https://another-api.example.com"
  }
}
```

**フィールド説明**:

| フィールド   | 必須  | 説明                                  |
|:--------|:----|:------------------------------------|
| type    | Yes | サーバータイプ（通常は `"http"`）               |
| url     | Yes | MCP サーバーのエンドポイント URL                |
| headers | No  | HTTP ヘッダー（`${VAR_NAME}` で環境変数を参照可能） |

### 実例: GitHub プラグイン

```json
{
  "github": {
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {
      "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
    }
  }
}
```

### MCP 統合のベストプラクティス

1. **環境変数の使用**: 認証情報は `${ENV_VAR_NAME}` で参照
2. **セキュリティ**: トークンをハードコードしない
3. **ドキュメント化**: README に必要な環境変数を記載
4. **エラーハンドリング**: 接続失敗時の挙動を定義

---

## フック (Hooks)

フックは高度な機能で、特定のイベントでスクリプトを自動実行します。

### フックの種類（Hookify プラグインより）

1. **bash フック**: Bash ツールコマンドで発火
2. **file フック**: Edit/Write/MultiEdit 操作で発火
3. **stop フック**: Claude が応答を終了しようとする時に発火
4. **prompt フック**: ユーザープロンプト送信時に発火
5. **all フック**: すべてのイベントで発火

### フック設定形式

フックは `.claude/plugin-name.local.md` ファイルで設定:

```yaml
---
name: block-dangerous-rm
enabled: true
event: bash
pattern: "rm -rf"
action: block
---

# 警告メッセージ

このコマンドは重要なファイルを削除する可能性があります。以下を確認してください:
  - パスが正しいか確認
  - より安全な方法を検討
  - バックアップがあるか確認
```

**フロントマターフィールド**:

| フィールド   | 型       | 説明                                              |
|:--------|:--------|:------------------------------------------------|
| name    | string  | フック識別子                                          |
| enabled | boolean | フックの有効/無効                                       |
| event   | string  | フックタイプ（`bash`, `file`, `stop`, `prompt`, `all`） |
| pattern | string  | マッチする正規表現パターン                                   |
| action  | string  | 実行するアクション（`warn`, `block`）                      |

### フック実装例: session-start

```bash
#!/bin/bash
# hooks/session-start.sh

# .sdd-config.json を読み込み、環境変数を設定
if [ -f ".sdd-config.json" ]; then
  export SDD_ROOT=$(jq -r '.root // ".sdd"' .sdd-config.json)
  export SDD_REQUIREMENT_DIR=$(jq -r '.directories.requirement // "requirement"' .sdd-config.json)
  # ...
fi

# AI-SDD Instructions を表示
if [ -f "${SDD_ROOT}/CONSTITUTION.md" ]; then
  cat "${SDD_ROOT}/CONSTITUTION.md"
fi
```

### フックのベストプラクティス

1. **軽量に保つ**: フックは高速に実行すべき
2. **エラーハンドリング**: 失敗時の挙動を明確に
3. **ユーザー通知**: 何が起きているかを明示
4. **設定可能に**: enabled フラグで有効/無効を切り替え可能に
5. **ドキュメント化**: フックの目的と挙動を README に記載

---

## マーケットプレイス公開

### 品質とセキュリティ要件

公式リポジトリ README より:

> 「外部プラグインは、承認のために品質とセキュリティ基準を満たす必要があります」

**セキュリティ通知**:
> 「プラグインをインストール、更新、使用する前に、そのプラグインを信頼していることを確認してください。Anthropic
> は、プラグインに含まれる MCP サーバー、ファイル、その他のソフトウェアを管理しておらず、意図したとおりに機能すること、または変更されないことを保証できません。」

### プラグインの配布モデル

#### 内部プラグイン（`plugins/` ディレクトリ）

- Anthropic チームが開発
- 公式マーケットプレイスに含まれる
- Anthropic がメンテナンス

#### 外部プラグイン（`external_plugins/` ディレクトリ）

- サードパーティパートナーとコミュニティ
- 品質とセキュリティ基準を満たす必要がある
- 主に MCP ベースの統合

### インストール方法

1. **直接インストール**:
   ```
   /plugin install {plugin-name}@claude-plugin-directory
   ```

2. **マーケットプレイスを閲覧**:
   ```
   /plugin
   # その後「Discover」を選択
   ```

### 公開プロセス

#### 1. リポジトリセットアップ

- 標準プラグイン構造でリポジトリを作成
- ルートに `.claude-plugin/marketplace.json` を含める
- `plugins/` ディレクトリに個別プラグインを追加

#### 2. プラグイン構造要件

- `.claude-plugin/` に有効な `plugin.json`
- 完全な `README.md` ドキュメント
- すべての commands/agents/skills が適切にフォーマットされている
- 任意だが推奨: LICENSE ファイル

#### 3. マーケットプレイス登録

- Anthropic に公式マーケットプレイス掲載を申請
- 品質とセキュリティレビューを通過する必要がある
- 外部プラグインは `external_plugins/` ディレクトリに配置

#### 4. ドキュメント要件

- 明確なインストール手順
- 使用例
- 機能説明
- 要件と依存関係

### プラグインカテゴリ

マーケットプレイスでは、以下のカテゴリでプラグインが分類されます:

1. **Language Servers**（LSP 統合）
    - TypeScript, Python, Go, Rust, C/C++, PHP, Swift, Kotlin, C#, Java, Lua

2. **Development Tools**（開発ツール）
    - Agent SDK, 機能開発, プラグイン開発, コード簡素化

3. **Productivity & Collaboration**（生産性とコラボレーション）
    - PR レビュー, コミットコマンド, GitHub, GitLab, Linear, Asana, Slack

4. **Database & Backend**（データベースとバックエンド）
    - Supabase, Firebase, Pinecone, Laravel ツール

5. **External Integrations**（外部統合）
    - サードパーティサービス統合（Stripe, Vercel, Notion など）

---

## ベストプラクティス

### コマンド設計

- **単一責任の原則**: 各コマンドは1つのタスクに集中
- **ツールアクセス制限**: `allowed-tools` で必要なツールのみ許可
- **明確なヒント**: `argument-hint` でユーザーをガイド
- **引数処理**: `$ARGUMENTS` 変数を適切に活用

### エージェント設計

- **詳細な description**: 具体的なトリガーフレーズを記載
- **適切なモデル選択**:
    - 複雑なタスク → `opus`
    - バランス型 → `sonnet`
    - シンプルなタスク → `haiku`
- **色分けの活用**: ターミナル出力を読みやすく
- **入出力の明確化**: 期待する入力と出力形式を定義
- **ツール制限**: `allowed-tools` を必要最小限に

### スキル設計

- **具体的なトリガーフレーズ**: description に明確なフレーズを列挙
- **単一機能に集中**: スキルは1つの能力に特化
- **構造化された整理**: 複雑なスキルはサブディレクトリで整理
- **例とリファレンス**: examples/ と reference/ を活用

### 一般的なガイドライン

1. **包括的な README.md**: 必ず含める
2. **セマンティックバージョニング**: 適切なバージョン管理
3. **命名規則**: kebab-case を使用
4. **徹底的なテスト**: 公開前に十分なテスト
5. **依存関係の明示**: すべての要件と依存関係をドキュメント化
6. **セキュリティ考慮**: 認証情報をハードコードしない
7. **ライセンス明示**: LICENSE ファイルを含める
8. **変更履歴**: CHANGELOG.md で変更を追跡

---

## 現在の ai-sdd-workflow プラグインとの比較

### 正しく実装されている点 ✓

1. リポジトリルートに適切な `marketplace.json`
2. 各プラグインに個別の `plugin.json`
3. 適切なフロントマター（name, description, model, color, allowed-tools）を持つエージェント
4. Commands 構造の実装
5. Skills ディレクトリの存在
6. session-start 機能を持つフック
7. 包括的なドキュメント（CLAUDE.md, AGENTS.md）

### 推奨される改善点

1. **バージョンフィールド**: `plugin.json` に `version` を追加（marketplace.json にはある）
2. **エージェント description**: より具体的なトリガーフレーズを追加
3. **MCP 統合**: 外部ツール統合が必要な場合、`.mcp.json` の追加を検討
4. **カテゴリフィールド**: マーケットプレイスプラグインに `category` を追加
5. **例の追加**: skills ディレクトリに例ファイルを追加することを検討

### 総評

現在の `ai-sdd-workflow` プラグイン構造は、公式の規約に非常によく準拠しており、プロフェッショナルで整理されたClaude
Codeプラグインマーケットプレイスを表現しています。

---

## 参考リンク

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) -
  公式プラグインリポジトリ
- [Claude Code プラグイン公式ドキュメント](https://code.claude.com/docs/en/plugins)
- [プラグイン設計ガイド](./AGENTS.md) - AI-SDD ワークフロープラグインのエージェント設計原則
- [プロジェクト概要](./CLAUDE.md) - AI-SDD ワークフローの全体像

---

## バージョン履歴

| バージョン | 日付         | 変更内容                         |
|:------|:-----------|:-----------------------------|
| 1.0.0 | 2026-01-15 | 初版作成 - 公式リポジトリ解析に基づく包括的ガイド作成 |
