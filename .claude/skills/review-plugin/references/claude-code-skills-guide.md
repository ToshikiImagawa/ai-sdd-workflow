# Claude Code Skills ガイド

[Claude Code公式ドキュメントのSkills](https://code.claude.com/docs/en/skills)に基づくSkill設計・実装のリファレンス。

## Skillsの概要

Skillsは `SKILL.md` ファイルで定義される拡張機能。Claudeが関連性を判断して自動的に使用するか、ユーザーが `/skill-name`
で直接呼び出す。

**Custom slash commandsはSkillsに統合済み**: `.claude/commands/review.md` と `.claude/skills/review/SKILL.md` は同じ
`/review` を作成し同様に動作する。既存の `.claude/commands/` ファイルは引き続き動作。Skillsはサポートファイル、フロントマター、自動読み込みなどの追加機能を提供。

SkillsはAgent Skills（https://agentskills.io）オープンスタンダードに準拠。Claude Codeは呼び出し制御、サブエージェント実行、動的コンテキスト注入などを独自に拡張。

## Skillの配置場所

| スコープ       | パス                                       | 適用範囲       |
|:-----------|:-----------------------------------------|:-----------|
| Enterprise | managed settings参照                       | 組織内全ユーザー   |
| Personal   | `~/.claude/skills/<skill-name>/SKILL.md` | 全プロジェクト    |
| Project    | `.claude/skills/<skill-name>/SKILL.md`   | 該当プロジェクトのみ |
| Plugin     | `<plugin>/skills/<skill-name>/SKILL.md`  | プラグイン有効範囲  |

**優先順位**: enterprise > personal > project。Plugin skillsは `plugin-name:skill-name`
名前空間のため衝突しない。同名のskillとcommandがある場合、skillが優先。

**自動検出**: サブディレクトリで作業中、ネストされた `.claude/skills/` も自動検出（モノレポ対応）。

## SKILL.md 構造

```
my-skill/
├── SKILL.md           # メイン指示（必須）
├── template.md        # テンプレート
├── examples/
│   └── sample.md      # 出力例
└── scripts/
    └── validate.sh    # 実行スクリプト
```

### フロントマターリファレンス

`SKILL.md` 先頭の `---` マーカー間にYAMLフロントマターを記述。全フィールドはオプション。`description` のみ推奨。

| フィールド                      | 必須 | 説明                                                                |
|:---------------------------|:---|:------------------------------------------------------------------|
| `name`                     | No | 表示名。省略時はディレクトリ名を使用。小文字・数字・ハイフンのみ（最大64文字）                          |
| `description`              | 推奨 | 何をするか・いつ使うか。Claudeがスキル適用判断に使用。省略時はマークダウン本文の最初の段落を使用               |
| `argument-hint`            | No | オートコンプリート時に表示される引数ヒント（例: `[issue-number]`）                        |
| `disable-model-invocation` | No | `true` でClaude自動読み込みを禁止。手動 `/name` 呼び出し専用。デフォルト: `false`          |
| `user-invocable`           | No | `false` で `/` メニューから非表示。ユーザーが直接呼び出すべきでないバックグラウンド知識用。デフォルト: `true` |
| `allowed-tools`            | No | スキル有効時にClaudeが許可なしで使用できるツール                                       |
| `model`                    | No | スキル有効時に使用するモデル                                                    |
| `context`                  | No | `fork` でサブエージェントコンテキストで実行                                         |
| `agent`                    | No | `context: fork` 時に使用するサブエージェントタイプ                                 |
| `hooks`                    | No | スキルライフサイクルにスコープされたフック                                             |

### 文字列置換

| 変数                     | 説明                                                                           |
|:-----------------------|:-----------------------------------------------------------------------------|
| `$ARGUMENTS`           | スキル呼び出し時に渡された全引数。コンテンツに `$ARGUMENTS` がない場合、引数は末尾に `ARGUMENTS: <value>` として追加 |
| `$ARGUMENTS[N]`        | 0ベースインデックスで特定の引数にアクセス                                                        |
| `$N`                   | `$ARGUMENTS[N]` の短縮形                                                         |
| `${CLAUDE_SESSION_ID}` | 現在のセッションID                                                                   |

## Skillコンテンツの種類

### リファレンスコンテンツ

Claudeが現在の作業に適用する知識（規約、パターン、スタイルガイド、ドメイン知識）。インラインで実行され会話コンテキストと併用。

### タスクコンテンツ

特定のアクションのためのステップバイステップ指示（デプロイ、コミット、コード生成等）。`/skill-name` で直接呼び出すことが多い。
`disable-model-invocation: true` でClaude自動トリガーを防止。

## 呼び出し制御

| フロントマター                          | ユーザー呼び出し | Claude呼び出し | コンテキスト読み込み                                 |
|:---------------------------------|:---------|:-----------|:-------------------------------------------|
| （デフォルト）                          | 可        | 可          | descriptionは常時コンテキスト内、フルskillは呼び出し時に読み込み   |
| `disable-model-invocation: true` | 可        | 不可         | descriptionはコンテキスト外、フルskillはユーザー呼び出し時に読み込み |
| `user-invocable: false`          | 不可       | 可          | descriptionは常時コンテキスト内、フルskillは呼び出し時に読み込み   |

**注意**: サブエージェントにプリロードされたskillsでは、起動時にフルskillコンテンツが注入される（通常セッションとは異なる）。

## サポートファイル

`SKILL.md` を500行以下に保ち、詳細なリファレンス資料は別ファイルに分離。`SKILL.md`
からファイルを参照してClaudeが内容と読み込みタイミングを把握できるようにする。

### ディレクトリ構造

```
my-skill/
├── SKILL.md           # メイン指示（必須）
├── references/        # リファレンス資料（必要に応じて読み込み）
│   ├── api-docs.md
│   └── schema.md
├── templates/         # テンプレートファイル（出力生成用）
│   └── report.md
├── scripts/           # 実行スクリプト（実行されるがコンテキストには読み込まれない）
│   └── validate.sh
├── assets/            # 出力に使用するファイル（画像、フォント等）
│   └── logo.png
└── examples/          # 出力例
    └── sample.md
```

| ディレクトリ        | 用途                    | コンテキスト読み込み           |
|:--------------|:----------------------|:---------------------|
| `references/` | ドメイン知識、APIドキュメント、スキーマ | Claudeが必要と判断した時に読み込み |
| `templates/`  | 出力生成用テンプレート           | 使用時に読み込み             |
| `scripts/`    | 実行スクリプト（Python/Bash等） | 実行のみ。コンテキストに読み込まず    |
| `assets/`     | 出力に使用するファイル（画像、フォント等） | コンテキストに読み込まず         |
| `examples/`   | 期待される出力の例             | 必要時に読み込み             |

### バンドルリソース（任意）

#### Scripts (`scripts/`)

決定論的な信頼性が必要なタスクや、繰り返し再生成されるタスク向けの実行コード（Python/Bash等）。

- **含めるタイミング**: 同じコードが繰り返し再生成される場合や、決定論的な信頼性が必要な場合
- **例**: PDF回転タスク用の `scripts/rotate_pdf.py`
- **利点**: トークン効率が良い、決定論的、コンテキストに読み込まずに実行可能
- **注意**: パッチ適用や環境固有の調整のため、Claudeがスクリプトを読み取る必要がある場合もある

#### References (`references/`)

Claudeの処理や思考に情報を提供するため、必要に応じてコンテキストに読み込むドキュメントやリファレンス資料。

- **含めるタイミング**: Claudeが作業中に参照すべきドキュメントがある場合
- **例**: 財務スキーマ用の `references/finance.md`、社内NDAテンプレート用の `references/mnda.md`、社内ポリシー用の `references/policies.md`、API仕様用の `references/api_docs.md`
- **ユースケース**: データベーススキーマ、APIドキュメント、ドメイン知識、社内ポリシー、詳細なワークフローガイド
- **利点**: SKILL.mdをスリムに保ち、Claudeが必要と判断した時のみ読み込む
- **ベストプラクティス**: ファイルが大きい場合（1万語超）、SKILL.mdにgrep検索パターンを含める
- **重複の回避**: 情報はSKILL.mdかreferencesファイルのどちらか一方にのみ配置する。スキルの核心でない限り、詳細な情報はreferencesファイルに配置することを推奨—これによりSKILL.mdをスリムに保ちつつ、コンテキストウィンドウを圧迫せずに情報を発見可能にする。SKILL.mdには必要最低限の手順指示とワークフローガイダンスのみを残し、詳細なリファレンス資料、スキーマ、例はreferencesファイルに移動する。

#### Assets (`assets/`)

コンテキストに読み込むことを意図せず、Claudeが生成する出力内で使用するファイル。

- **含めるタイミング**: スキルが最終出力で使用するファイルがある場合
- **例**: ブランドアセット用の `assets/logo.png`、PowerPointテンプレート用の `assets/slides.pptx`、HTML/Reactボイラープレート用の `assets/frontend-template/`、タイポグラフィ用の `assets/font.ttf`
- **ユースケース**: テンプレート、画像、アイコン、ボイラープレートコード、フォント、コピーまたは変更されるサンプルドキュメント
- **利点**: 出力リソースをドキュメントから分離し、Claudeがコンテキストに読み込まずにファイルを使用できる

### SKILL.md からの参照方法

```markdown
## Additional resources

- 完全なAPIの詳細は [reference.md](references/reference.md) を参照
- 使用例は [examples.md](examples/examples.md) を参照
```

## 動的コンテキスト注入

`` !`command` `` 構文でスキルコンテンツ送信前にシェルコマンドを実行。コマンド出力がプレースホルダーを置換し、Claudeは実データを受け取る。

```yaml
---
name: pr-summary
description: PRの変更をまとめる
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
```

## サブエージェント実行

`context: fork` でスキルを分離実行。スキルコンテンツがサブエージェントのプロンプトになる。会話履歴にはアクセスできない。

| アプローチ                    | システムプロンプト                  | タスク            | 追加読み込み                  |
|:-------------------------|:---------------------------|:---------------|:------------------------|
| Skill + `context: fork`  | agentタイプから（Explore, Plan等） | SKILL.mdコンテンツ  | CLAUDE.md               |
| Subagent + `skills`フィールド | サブエージェントのmarkdown本文        | Claudeの委任メッセージ | プリロードskills + CLAUDE.md |

`agent` フィールド: 組み込みエージェント（`Explore`, `Plan`, `general-purpose`）またはカスタムサブエージェント（
`.claude/agents/`）。省略時は `general-purpose`。

**注意**: `context: fork` は明示的な指示を持つスキルでのみ有効。ガイドラインのみ（タスクなし）のスキルではサブエージェントが有意義な出力なしで終了する。

## Claudeのスキルアクセス制限

3つの制御方法:

1. **全スキル無効化**: `/permissions` で `Skill` ツールを拒否
2. **個別スキル許可/拒否**: パーミッションルールで `Skill(name)` （完全一致）または `Skill(name *)` （プレフィックス一致）
3. **個別スキル非表示**: `disable-model-invocation: true` でClaudeのコンテキストから完全除外

**注意**: `user-invocable` はメニュー表示のみ制御。Skillツールアクセスをブロックするには `disable-model-invocation: true`
を使用。

## スキル文字バジェット

多数のスキルがある場合、description がコンテキストの文字バジェット（デフォルト15,000文字）を超える可能性がある。`/context`
で警告を確認。`SLASH_COMMAND_TOOL_CHAR_BUDGET` 環境変数で上限を変更可能。

## Extended Thinking

スキルコンテンツに "ultrathink" を含めるとextended thinkingが有効になる。

## レビュー観点

### 観点1: SKILL.md の設計

- `SKILL.md` が500行以下に収まっているか
- フロントマターの `description` が明確か（何をするか + いつ使うべきか）
- `name` がkebab-case、64文字以下か
- 不要なフロントマターフィールドが含まれていないか

### 観点2: 呼び出し制御の適切性

- 副作用のあるワークフロー（deploy, commit等）に `disable-model-invocation: true` が設定されているか
- バックグラウンド知識に `user-invocable: false` が設定されているか
- `allowed-tools` が必要最小限か

### 観点3: サポートファイルの設計

- 詳細リファレンスが `SKILL.md` から分離されているか
- `SKILL.md` からサポートファイルが適切に参照されているか
- スクリプトが `scripts/` に配置されているか

### 観点4: コンテキスト効率

- `context: fork` が適切に使用されているか（分離が必要なタスクのみ）
- 動的コンテキスト注入が有効活用されているか
- description が簡潔でトリガー条件が明確か
