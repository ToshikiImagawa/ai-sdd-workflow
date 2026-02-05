# PLUGIN.md

Claude Codeプラグインとマーケットプレイスの作成ガイド

## 概要

このドキュメントは、Claude Codeプラグインの構造、設計、公開方法を包括的にまとめたものです。
[公式ドキュメント](https://code.claude.com/docs/en/plugins)
および[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)リポジトリに基づいています。

## 目次

1. [プラグイン基本構造](#プラグイン基本構造)
2. [マニフェストファイル](#マニフェストファイル)
3. [コマンド (Commands)](#コマンド-commands)
4. [エージェント (Agents)](#エージェント-agents)
5. [スキル (Skills)](#スキル-skills)
6. [MCP サーバー連携](#mcp-サーバー連携)
7. [LSP サーバー連携](#lsp-サーバー連携)
8. [フック (Hooks)](#フック-hooks)
9. [プラグインキャッシュとインストールスコープ](#プラグインキャッシュとインストールスコープ)
10. [マーケットプレイス公開](#マーケットプレイス公開)
11. [CLI コマンドリファレンス](#cli-コマンドリファレンス)
12. [デバッグ](#デバッグ)
13. [ベストプラクティス](#ベストプラクティス)

---

## プラグイン基本構造

### 標準ディレクトリレイアウト

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json              # プラグインマニフェスト（必須）
├── .mcp.json                    # MCP サーバー設定（任意）
├── .lsp.json                    # LSP サーバー設定（任意）
├── commands/                    # スラッシュコマンド（任意、legacy）
│   ├── command-name.md
│   └── another-command.md
├── agents/                      # 自律エージェント（任意）
│   ├── agent-name.md
│   └── another-agent.md
├── skills/                      # スキル（推奨、任意）
│   └── skill-name/
│       ├── SKILL.md            # スキル定義
│       ├── README.md           # ドキュメント
│       └── examples/           # サポートファイル（任意）
├── hooks/                       # フック設定（任意）
│   └── hooks.json              # フック定義ファイル
├── scripts/                     # フック用スクリプト（任意）
│   └── session-start.sh
└── README.md                    # プラグインドキュメント（推奨）
```

> **Note**: `commands/` は引き続き動作しますが、新規作成は `skills/` を推奨します。スキルはコマンドの上位互換であり、より多くの機能（
`context: fork`、フック設定、動的コンテキスト注入など）を利用できます。

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
  "url": "https://...",
  "strict": false
}
```

#### コンポーネントパスフィールド

plugin.json でコンポーネントの配置場所をカスタマイズできます。カスタムパスはデフォルトパスを**補完**します（上書きではない）。パスは
`./` で始まる必要があります。

```json
{
  "name": "plugin-name",
  "description": "プラグインの説明",
  "author": {
    "name": "作成者名"
  },
  "commands": "./custom-commands",
  "agents": "./custom-agents",
  "skills": "./custom-skills",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json",
  "outputStyles": "./styles"
}
```

| フィールド        | 型             | 説明                                 |
|:-------------|:--------------|:-----------------------------------|
| commands     | string        | コマンドディレクトリのカスタムパス                  |
| agents       | string        | エージェントディレクトリのカスタムパス                |
| skills       | string        | スキルディレクトリのカスタムパス                   |
| hooks        | string/object | フック設定ファイルのパス、またはインラインでフック定義        |
| mcpServers   | string/object | MCP 設定ファイルのパス、またはインラインで MCP サーバー定義 |
| lspServers   | string/object | LSP 設定ファイルのパス、またはインラインで LSP サーバー定義 |
| outputStyles | string        | 出力スタイルディレクトリのカスタムパス                |

#### `${CLAUDE_PLUGIN_ROOT}` 環境変数

プラグイン内のスクリプトやフックから、プラグインのルートディレクトリを参照するために `${CLAUDE_PLUGIN_ROOT}`
環境変数が利用できます。これにより、プラグインがどこにインストールされても正しいパスを解決できます。

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"
      }
    ]
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

> **Note**: `commands/` は引き続き動作しますが、新規作成は `skills/` を推奨します。

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

- `$ARGUMENTS`: ユーザーがコマンドに渡した引数全体
- `$ARGUMENTS[N]`: N番目の引数（0始まり）
- `$N`: N番目の引数の省略記法（`$0`, `$1`, ...）

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
skills: [ "plugin-name:skill-name" ]
hooks:
  PostToolUse:
    - type: prompt
      prompt: "ツール使用後の検証プロンプト"
      matcher: Edit
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
| skills        | array  | No  | プリロードするスキルのリスト                        |
| hooks         | object | No  | エージェントスコープのフック設定                      |

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

**良い例**:

```yaml
description: "プロジェクトガイドライン、スタイルガイド、ベストプラクティスへの準拠をレビューするために使用します。コードの記述・変更後、特にコミットやプルリクエスト作成前に積極的に使用すべきです。スタイル違反、潜在的な問題をチェックし、CLAUDE.mdに定義されたパターンに従っているかを確認します。レビューに集中すべきファイルを知る必要があります。"
```

**悪い例**:

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

スキルはClaude Codeの拡張ポイントとして最も推奨されるコンポーネントです。コマンドの上位互換として、より柔軟な設定と実行モデルを提供します。

### commands との違い

| 機能            | commands         | skills                               |
|:--------------|:-----------------|:-------------------------------------|
| ユーザーからの直接呼び出し | `/command` で呼び出し | `user-invocable: true` で呼び出し可能       |
| サブエージェントとして実行 | 不可               | `context: fork` で可能                  |
| モデル自動呼び出し無効化  | 不可               | `disable-model-invocation: true` で可能 |
| フック設定         | 不可               | スキルスコープのフック定義可能                      |
| 動的コンテキスト注入    | 不可               | `` !`command` `` 構文で可能               |
| サポートファイル      | 不可               | 同一ディレクトリ内のファイルを参照可能                  |

### スキルファイル形式

- **配置場所**: `skills/skill-name/SKILL.md`
- **形式**: YAMLフロントマター付きMarkdown

### フロントマターフィールド

```yaml
---
name: skill-name
description: "このスキルは、ユーザーが「トリガーフレーズ」と尋ねたとき、または[トピック]について議論するときに使用されます。"
version: 1.0.0
license: MIT
user-invocable: true
argument-hint: "<引数の説明>"
disable-model-invocation: false
allowed-tools: [ Read, Glob, Grep, Edit ]
context: fork
agent: sonnet
hooks:
  PostToolUse:
    - type: prompt
      prompt: "検証プロンプト"
      matcher: Edit
---
```

**利用可能なフィールド**:

| フィールド                    | 型       | 必須  | 説明                                                     |
|:-------------------------|:--------|:----|:-------------------------------------------------------|
| name                     | string  | Yes | スキル識別子                                                 |
| description              | string  | Yes | トリガー条件と機能の説明                                           |
| version                  | string  | No  | セマンティックバージョン                                           |
| license                  | string  | No  | ライセンスタイプ                                               |
| user-invocable           | boolean | No  | `true` でユーザーが `/skill-name` で直接呼び出し可能                  |
| argument-hint            | string  | No  | 引数のヒント（ユーザー呼び出し時に表示）                                   |
| disable-model-invocation | boolean | No  | `true` でモデルによる自動呼び出しを無効化（ユーザー明示呼び出しのみ）                 |
| allowed-tools            | array   | No  | スキル実行時に使用可能なツールのリスト                                    |
| context                  | string  | No  | `fork` でサブエージェントコンテキストで実行                              |
| agent                    | string  | No  | `context: fork` 時のエージェントタイプ（`sonnet`, `opus`, `haiku`） |
| hooks                    | object  | No  | スキルスコープのフック設定                                          |

### 文字列置換変数

スキル本体（Markdown部分）では以下の変数が使用できます:

| 変数                     | 説明                           |
|:-----------------------|:-----------------------------|
| `$ARGUMENTS`           | ユーザーが渡した引数全体                 |
| `$ARGUMENTS[N]`        | N番目の引数（0始まり）                 |
| `$N`                   | N番目の引数の省略記法（`$0`, `$1`, ...） |
| `${CLAUDE_SESSION_ID}` | 現在のセッション ID                  |

### 動的コンテキスト注入

`` !`command` `` 構文を使用すると、スキル読み込み時にコマンドを実行し、その出力をスキルのコンテキストに注入できます。

```markdown
---
name: project-info
description: "プロジェクト情報を提供するスキル"
---

## 現在のGit状態

!`git status --short`

## 最近のコミット

!`git log --oneline -5`

## 指示

上記のプロジェクト状態を踏まえて回答してください。
```

### サポートファイル

`SKILL.md` と同じディレクトリ内のファイルは、スキルの実行時にコンテキストとして利用できます。

```
skills/
└── my-skill/
    ├── SKILL.md              # スキル定義（必須）
    ├── templates/            # テンプレートファイル
    │   └── template.md
    ├── examples/             # 例ファイル
    │   └── example.md
    └── references/           # 参照資料
        └── guide.md
```

SKILL.md 内で相対パスを使ってこれらのファイルを参照できます。

### description フィールドのベストプラクティス

具体的なトリガーフレーズを含める:

```yaml
description: "このスキルは、ユーザーが「スキルをデモンストレート」「スキルフォーマットを表示」「スキルテンプレートを作成」と尋ねたとき、またはスキル開発パターンについて議論するときに使用されます。Claude Codeプラグインスキル作成のリファレンステンプレートを提供します。"
```

### スキル設計のベストプラクティス

1. **明確なトリガーフレーズ**: description に具体的なフレーズを列挙
2. **単一機能**: スキルは1つの能力に集中
3. **構造化された整理**: 複雑なスキルはサブディレクトリで整理
4. **例とリファレンス**: examples/ と references/ を活用
5. **バージョン管理**: version フィールドで変更を追跡
6. **`context: fork` の活用**: 重い処理はサブエージェントとして実行
7. **ツール制限**: `allowed-tools` で最小限のツールのみ許可

---

## MCP サーバー連携

### .mcp.json 形式

- **配置場所**: `{plugin-name}/.mcp.json` または plugin.json の `mcpServers` でインライン定義
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

### MCP 統合のベストプラクティス

1. **環境変数の使用**: 認証情報は `${ENV_VAR_NAME}` で参照
2. **セキュリティ**: トークンをハードコードしない
3. **ドキュメント化**: README に必要な環境変数を記載
4. **エラーハンドリング**: 接続失敗時の挙動を定義

---

## LSP サーバー連携

### LSP 設定形式

- **配置場所**: `{plugin-name}/.lsp.json` または plugin.json の `lspServers` でインライン定義
- **目的**: Language Server Protocol サーバーを設定し、IDE機能を提供

### .lsp.json 構造

```json
{
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
```

### plugin.json でのインライン定義

```json
{
  "name": "my-lsp-plugin",
  "description": "LSP統合プラグイン",
  "author": {
    "name": "作成者名"
  },
  "strict": false,
  "lspServers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": [
        "--stdio"
      ],
      "extensionToLanguage": {
        ".ts": "typescript",
        ".tsx": "typescriptreact"
      }
    }
  }
}
```

**フィールド説明**:

| フィールド               | 必須  | 説明                 |
|:--------------------|:----|:-------------------|
| command             | Yes | LSP サーバーの実行コマンド    |
| args                | No  | コマンドライン引数          |
| extensionToLanguage | Yes | ファイル拡張子と言語IDのマッピング |

### `strict` フィールド

plugin.json の `strict` フィールドは LSP サーバー専用です。`false`（デフォルト）の場合、LSP
サーバーが起動に失敗しても警告のみでプラグインの読み込みは続行されます。

---

## フック (Hooks)

フックは特定のイベントで自動的にコードや検証を実行する機能です。

### フック設定形式

フックは `hooks/hooks.json` ファイルまたは plugin.json 内でインライン定義します。

#### hooks/hooks.json での定義

```json
{
  "SessionStart": [
    {
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"
    }
  ],
  "PreToolUse": [
    {
      "type": "command",
      "command": "echo 'Tool about to be used'",
      "matcher": "Bash"
    }
  ],
  "PostToolUse": [
    {
      "type": "prompt",
      "prompt": "ツール実行結果を検証し、問題があれば報告してください。",
      "matcher": "Edit"
    }
  ]
}
```

#### plugin.json でのインライン定義

```json
{
  "name": "my-plugin",
  "description": "フック付きプラグイン",
  "author": {
    "name": "作成者名"
  },
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate-prompt.sh"
      }
    ]
  }
}
```

### イベント一覧

| イベント               | 発火タイミング              |
|:-------------------|:---------------------|
| SessionStart       | セッション開始時             |
| SessionEnd         | セッション終了時             |
| UserPromptSubmit   | ユーザーがプロンプトを送信した時     |
| PreToolUse         | ツール実行前               |
| PostToolUse        | ツール実行後（成功時）          |
| PostToolUseFailure | ツール実行後（失敗時）          |
| PermissionRequest  | 権限リクエスト時             |
| Notification       | 通知発生時                |
| SubagentStart      | サブエージェント起動時          |
| SubagentStop       | サブエージェント停止時          |
| Stop               | Claude が応答を終了しようとする時 |
| PreCompact         | コンテキストコンパクト前         |

### フックタイプ

| タイプ     | 説明              | 主な用途                     |
|:--------|:----------------|:-------------------------|
| command | シェルコマンドを実行      | スクリプト実行、環境変数設定、外部ツール呼び出し |
| prompt  | Claudeにプロンプトを挿入 | 品質検証、ガイダンス注入             |
| agent   | サブエージェントを起動     | 複雑な検証やレビュー               |

### マッチャー (matcher)

`PreToolUse`, `PostToolUse`, `PostToolUseFailure` イベントでは `matcher` フィールドでツール名を指定してフィルタリングできます。

```json
{
  "PostToolUse": [
    {
      "type": "prompt",
      "prompt": "編集内容がコーディング規約に準拠しているか確認してください。",
      "matcher": "Edit"
    },
    {
      "type": "command",
      "command": "npm run lint",
      "matcher": "Write"
    }
  ]
}
```

### command タイプの入出力

**入力**: フックコマンドには stdin で JSON が渡されます。JSON の内容はイベントタイプによって異なります。

**出力**: コマンドの終了コードと stdout の JSON で制御できます。

| 終了コード | 動作            |
|:------|:--------------|
| 0     | 正常終了（続行）      |
| 2     | ブロック（操作を中止）   |
| その他   | エラー（警告表示して続行） |

**stdout JSON 出力例**:

```json
{
  "result": "表示するメッセージ",
  "suppressPrompt": true
}
```

### フックのベストプラクティス

1. **軽量に保つ**: フックは高速に実行すべき
2. **マッチャーの活用**: 必要なイベントのみにフィルタリング
3. **エラーハンドリング**: 失敗時の挙動を明確に
4. **`${CLAUDE_PLUGIN_ROOT}`の使用**: スクリプトパスの解決に利用
5. **prompt タイプの活用**: 品質ゲートとして検証プロンプトを挿入

---

## プラグインキャッシュとインストールスコープ

### プラグインキャッシュ

インストールされたプラグインは `~/.claude/plugins/` ディレクトリにキャッシュされます。プラグインの更新時には
`claude plugin update` でキャッシュを更新します。

### インストールスコープ

| スコープ    | 説明                | 有効範囲                   |
|:--------|:------------------|:-----------------------|
| user    | ユーザーレベルのインストール    | そのユーザーの全プロジェクト         |
| project | プロジェクトレベルのインストール  | 特定のプロジェクトのみ            |
| local   | ローカルディレクトリのプラグイン  | `--plugin-dir` で指定した場合 |
| managed | マーケットプレイス管理のプラグイン | マーケットプレイス経由            |

### パストラバーサルの制限

プラグインはセキュリティ上の理由から、プラグインルートディレクトリの外側にアクセスするパスを指定できません（`../`
によるトラバーサルは禁止）。

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

## CLI コマンドリファレンス

### プラグイン管理コマンド

```bash
# プラグインのインストール
claude plugin install <plugin-name>

# プラグインのアンインストール
claude plugin uninstall <plugin-name>

# プラグインの有効化
claude plugin enable <plugin-name>

# プラグインの無効化
claude plugin disable <plugin-name>

# プラグインの更新
claude plugin update [plugin-name]

# インストール済みプラグインの一覧
claude plugin list

# マーケットプレイスの閲覧
claude plugin
# その後「Discover」を選択
```

### ローカル開発用コマンド

```bash
# ローカルディレクトリのプラグインを使用してClaude Codeを起動
claude --plugin-dir ./path/to/plugin
```

---

## デバッグ

### デバッグモードの使用

```bash
# デバッグモードでClaude Codeを起動
claude --debug
```

デバッグモードでは、プラグインの読み込み、フックの実行、エージェントの呼び出しなどの詳細なログが表示されます。

### 一般的な問題と解決策

| 問題                              | 原因                       | 解決策                              |
|:--------------------------------|:-------------------------|:---------------------------------|
| プラグインが読み込まれない                   | plugin.json の構文エラー       | `jq .` で JSON 構文チェック             |
| コマンドが表示されない                     | フロントマターの形式エラー            | YAML フロントマターの区切り `---` を確認       |
| フックが実行されない                      | hooks.json のパスまたは構文エラー   | `claude --debug` でフック読み込みを確認     |
| エージェントが呼び出されない                  | description が不十分         | より具体的なトリガーフレーズを追加                |
| `${CLAUDE_PLUGIN_ROOT}` が解決されない | プラグインがキャッシュにない           | `claude plugin update` でキャッシュを更新 |
| スキルが自動的に呼び出されない                 | description にトリガーフレーズがない | 具体的なトリガーフレーズを description に追加    |

### ログの確認

```
~/.claude/projects/<project-name>/
  ├── conversation.jsonl  # メイン会話
  └── sidechains/         # サブエージェントログ
```

---

## ベストプラクティス

### コマンド/スキル設計

- **単一責任の原則**: 各コマンド/スキルは1つのタスクに集中
- **ツールアクセス制限**: `allowed-tools` で必要なツールのみ許可
- **明確なヒント**: `argument-hint` でユーザーをガイド
- **引数処理**: `$ARGUMENTS` 変数を適切に活用
- **新規はスキルで作成**: `commands/` ではなく `skills/` を使用

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
- **`context: fork` の活用**: 重い処理はサブエージェントとして実行
- **`disable-model-invocation` の活用**: ユーザー明示呼び出しのみの場合に設定

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

## 参考リンク

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) -
  公式プラグインリポジトリ
- [Claude Code プラグイン公式ドキュメント](https://code.claude.com/docs/en/plugins)
- [プラグイン設計ガイド](./AGENTS.md) - AI-SDD ワークフロープラグインのエージェント設計原則
- [プロジェクト概要](./CLAUDE.md) - AI-SDD ワークフローの全体像

---

## バージョン履歴

| バージョン | 日付         | 変更内容                                                 |
|:------|:-----------|:-----------------------------------------------------|
| 2.0.0 | 2026-02-03 | 公式ドキュメント（2026年版）に基づく全面更新 - スキル/フック/LSP/プラグインスキーマの最新化 |
| 1.0.0 | 2026-01-15 | 初版作成 - 公式リポジトリ解析に基づく包括的ガイド作成                         |
