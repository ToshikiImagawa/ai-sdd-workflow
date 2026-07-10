# Claude Code プラグイン開発ガイド

[Plugins reference](https://code.claude.com/docs/en/plugins-reference)に基づくプラグイン開発のリファレンス。

## プラグインの概要

プラグインは、Claude Codeの機能を拡張するための軽量なパッケージ。以下のコンポーネントをバンドルできる:

| コンポーネント      | 説明                                          | ディレクトリ      |
|:-------------|:--------------------------------------------|:------------|
| **Skills**   | 知識・ワークフロー。Claudeが自律的に使用を決定                  | `skills/`   |
| **Commands** | ユーザーが明示的に呼び出すスラッシュコマンド（legacy、新規はskills/推奨） | `commands/` |
| **Agents**   | 専門知識を持つサブエージェント                             | `agents/`   |
| **Hooks**    | イベントに応じて自動実行されるスクリプト                        | `hooks/`    |
| **MCP**      | 外部ツール連携の設定                                  | `.mcp.json` |
| **LSP**      | Language Server Protocol によるコードインテリジェンス     | `.lsp.json` |

## ファイル構造

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # プラグインマニフェスト（必須）
├── agents/                  # サブエージェント（任意）
│   └── my-agent.md
├── skills/                  # Agent Skills（任意）
│   └── my-skill/
│       ├── SKILL.md         # スキル定義（必須）
│       ├── references/      # 参照ドキュメント（任意）
│       ├── templates/       # テンプレートファイル（任意）
│       └── scripts/         # 実行スクリプト（任意）
├── hooks/                   # イベントフック（任意）
│   └── hooks.json
├── scripts/                 # フック実行スクリプト
│   └── format-code.sh
├── .mcp.json                # MCP設定（任意）
├── .lsp.json                # LSP設定（任意）
└── README.md
```

### 重要なルール

- **`.claude-plugin/` にはマニフェストのみ**: `plugin.json` のみを配置
- **コンポーネントはルートレベル**: `commands/`, `agents/`, `skills/`, `hooks/` はプラグインルート直下
- **命名規則**: kebab-caseを使用
- **必要なディレクトリのみ作成**: 使用しないコンポーネントのディレクトリは作成しない

## plugin.json

### 必須フィールド

| フィールド  | 型      | 説明                        |
|:-------|:-------|:--------------------------|
| `name` | string | 一意の識別子（kebab-case、スペースなし） |

### メタデータフィールド

| フィールド         | 型      | 説明                           |
|:--------------|:-------|:-----------------------------|
| `version`     | string | セマンティックバージョン                 |
| `description` | string | プラグインの簡潔な説明                  |
| `author`      | object | 作者情報（`name`, `email`, `url`） |
| `homepage`    | string | ドキュメントURL                    |
| `repository`  | string | ソースコードURL                    |
| `license`     | string | ライセンス識別子                     |
| `keywords`    | array  | 検索タグ                         |

### コンポーネントパスフィールド（オプション）

**重要: デフォルトディレクトリは自動検出される。** 以下のディレクトリがプラグインルート直下に存在すれば、
`plugin.json` で明示的に指定しなくても自動的に認識される：

| デフォルトディレクトリ        | 自動検出 |
|:-------------------|:----:|
| `agents/`          |  ✓   |
| `skills/`          |  ✓   |
| `hooks/hooks.json` |  ✓   |
| `commands/`        |  ✓   |

以下のフィールドは、**デフォルト以外の追加パス**を指定する場合にのみ使用する：

| フィールド          | 型              | 説明                  |
|:---------------|:---------------|:--------------------|
| `agents`       | string\|array  | 追加エージェントファイル        |
| `skills`       | string\|array  | 追加スキルディレクトリ         |
| `hooks`        | string\|object | フック設定パスまたはインライン設定   |
| `mcpServers`   | string\|object | MCP設定パスまたはインライン設定   |
| `lspServers`   | string\|object | LSP設定パスまたはインライン設定   |
| `outputStyles` | string\|array  | 追加出力スタイルファイル/ディレクトリ |

**カスタムパスはデフォルトディレクトリを補完する（置き換えない）。**

## Skills の作成

### SKILL.md のベストプラクティス

| 項目                | 推奨                                     |
|:------------------|:---------------------------------------|
| **文字数**           | 5,000語以下を推奨                            |
| **description**   | 何をするか + いつ使うべきかを明確に                    |
| **allowed-tools** | 必要最小限のツールのみ指定                          |
| **補助ファイル**        | 詳細情報は `references/` や `templates/` に分離 |

**Progressive Disclosure**: Claudeは SKILL.md を最初に読み、必要に応じて補助ファイルを読み込む。

## Agents の作成

```markdown
---
description: What this agent specializes in
capabilities: ["task1", "task2", "task3"]
---

# Agent Name

Detailed description of the agent's role, expertise, and when Claude should invoke it.
```

- **専門性の明確化**: 特定のドメインに特化
- **責務の定義**: 何をするか、何をしないかを明確に
- **model**: タスクの複雑さに応じて選択（haiku/sonnet/opus）

## Hooks の作成

### フック設定の配置

1. **個別ファイル**: `hooks/hooks.json`（推奨）
2. **インライン設定**: `plugin.json` に直接記載

**plugin.json での参照:**

```json
{
  "name": "plugin-name",
  "hooks": "./hooks/hooks.json"
}
```

### 利用可能なイベント

| イベント                 | トリガー                  |
|:---------------------|:----------------------|
| `PreToolUse`         | Claudeがツールを使用する前      |
| `PostToolUse`        | Claudeがツールを使用した後      |
| `PostToolUseFailure` | Claudeのツール実行が失敗した後    |
| `PermissionRequest`  | パーミッションダイアログが表示された時   |
| `UserPromptSubmit`   | ユーザーがプロンプトを送信するとき     |
| `Notification`       | Claude Codeが通知を送信するとき |
| `Stop`               | Claudeが停止しようとするとき     |
| `SubagentStart`      | サブエージェントが開始されるとき      |
| `SubagentStop`       | サブエージェントが停止しようとするとき   |
| `SessionStart`       | セッションの開始時             |
| `SessionEnd`         | セッションの終了時             |
| `PreCompact`         | 会話履歴がコンパクト化される前       |

### フックタイプ

| タイプ         | 説明                                      |
|:------------|:----------------------------------------|
| **command** | シェルコマンドまたはスクリプトを実行                      |
| **prompt**  | LLMでプロンプトを評価（`$ARGUMENTS` でコンテキストを受け取る） |
| **agent**   | ツール付きエージェントで複雑な検証タスクを実行                 |

## LSP サーバーの作成

LSPサーバーにより、リアルタイムのコードインテリジェンス（診断、定義へ移動、参照検索等）を提供可能。

**.lsp.json の例:**

```json
{
  "go": {
    "command": "gopls",
    "args": [
      "serve"
    ],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

**必須フィールド**: `command`（LSPバイナリ）、`extensionToLanguage`（拡張子→言語のマッピング）

**注意**: LSPプラグインはサーバーバイナリを含まない。別途インストールが必要。

## 環境変数

| 変数                      | 説明                |
|:------------------------|:------------------|
| `${CLAUDE_PLUGIN_ROOT}` | プラグインのルートディレクトリパス |
| `$TOOL_INPUT`           | ツールへの入力（Hooks用）   |
| `$ARGUMENTS`            | コマンド/スキルへの引数      |

## インストールスコープ

| スコープ      | 設定ファイル                        | 用途                  |
|:----------|:------------------------------|:--------------------|
| `user`    | `~/.claude/settings.json`     | 全プロジェクトで利用（デフォルト）   |
| `project` | `.claude/settings.json`       | チームで共有（バージョン管理）     |
| `local`   | `.claude/settings.local.json` | プロジェクト固有（gitignore） |
| `managed` | `managed-settings.json`       | 管理者用（読み取り専用）        |

## プラグインキャッシュ

プラグインはキャッシュディレクトリにコピーされて使用される。プラグインルート外のファイルは参照不可。外部依存にはシンボリックリンクを使用。

## デバッグ

```bash
claude --debug
```

### 一般的な問題と解決策

| 問題             | 原因                          | 解決策                   |
|:---------------|:----------------------------|:----------------------|
| プラグインが読み込まれない  | 無効な`plugin.json`            | JSON構文を検証             |
| コマンドが表示されない    | ディレクトリ構造が不正                 | `commands/`をルートレベルに配置 |
| フックが発火しない      | スクリプトが実行可能でない               | `chmod +x script.sh`  |
| MCPサーバーが失敗     | `${CLAUDE_PLUGIN_ROOT}`が未使用 | すべてのパスに変数を使用          |
| パスエラー          | 絶対パスが使用されている                | すべてのパスは相対で`./`始まり     |
| LSPバイナリが見つからない | サーバー未インストール                 | バイナリを別途インストール         |

## 参考リンク

- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Plugins](https://code.claude.com/docs/en/plugins)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Skills](https://code.claude.com/docs/en/skills)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Hooks](https://code.claude.com/docs/en/hooks)
