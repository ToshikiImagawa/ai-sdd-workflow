---
name: review-plugin
description: "Claude Codeプラグインの品質レビュー。Agents, Skills, Hooks, プラグイン構造を設計ガイドに基づいてチェックし、改善提案を提供します。"
argument-hint: "[対象パス|--agents|--skills|--hooks|--all] [--ja|--en]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Task
---

# Review Plugin - プラグイン品質レビュー

Claude Codeプラグインの各コンポーネント（Agents, Skills, Hooks, 構造）をレビューし、改善提案を提供する。

## 入力

$ARGUMENTS

### 入力形式

```
/review-plugin {対象パス}                    # 個別ファイルをレビュー
/review-plugin --agents [プラグイン名]        # 全エージェントをレビュー
/review-plugin --skills [プラグイン名]        # 全スキルをレビュー
/review-plugin --hooks [プラグイン名]         # Hooks設定をレビュー
/review-plugin --all [プラグイン名]           # プラグイン全体をレビュー
```

### オプション

- `--agents`: 指定プラグインの全エージェントをレビュー
- `--skills`: 指定プラグインの全スキルをレビュー
- `--hooks`: 指定プラグインのHooks設定をレビュー
- `--all`: プラグイン全体（Agents + Skills + Hooks + 構造）をレビュー
- `--ja`: 日本語プラグイン (sdd-workflow-ja) のみ対象
- `--en`: 英語プラグイン (sdd-workflow) のみ対象
- プラグイン名省略時は全プラグインが対象

## 処理フロー

### Step 1: 対象の特定

| オプション      | 対象パターン                                   |
|:-----------|:-----------------------------------------|
| `--agents` | `plugins/sdd-workflow{-ja}/agents/*.md`  |
| `--skills` | `plugins/sdd-workflow{-ja}/skills/*/`    |
| `--hooks`  | `plugins/sdd-workflow{-ja}/hooks/*.json` |
| `--all`    | 上記すべて + `plugin.json`                    |
| 個別パス       | 指定パスをそのまま使用                              |

### Step 2: 設計原則の読み込み

対象に応じて参照リファレンスを読み込む。

### Step 3: レビュー実行

各対象ファイルに対して Task ツールでレビューを実行する。Task の prompt に対象ファイルパスと該当するレビュー観点を渡す。

### Step 4: 結果統合（複数ファイル時）

評価サマリーテーブルと全体推奨アクションを統合出力する。

---

## エージェントレビュー観点

各観点を 🟢 良好 / 🟡 改善推奨 / 🔴 要修正 の3段階で評価する。

### A1: description の明確性

- 何をするか（動詞）が明確か
- 対象ドキュメントが明示されているか
- チェック観点が記述されているか
- 結果（修正提案の出力等）が記載されているか

**🔴 例**: `"仕様書をレビューする"` — 曖昧、何をどうチェックするか不明
**🟢 例**: `"仕様書の品質レビューとCONSTITUTION.md準拠チェックを行う。曖昧な記述、不足セクションをチェックし、修正提案を出力"`

### A2: 入出力インターフェース

- `## 入力` セクション（`$ARGUMENTS` 使用、入力形式、入力例）
- `## 前提条件` セクション（AI-SDD原則ドキュメント読み込み、`SDD_*` 環境変数によるパス解決）
- `## 出力` セクション（出力フォーマット定義）

### A3: フロントマターの設計

- 標準フィールド（name, description, model, color, allowed-tools）が適切か
- 拡張フィールド（tools, skills, hooks）の使用が妥当か

### A4: allowed-tools の設計

| エージェントタイプ | 期待される allowed-tools               | 理由                    |
|:----------|:----------------------------------|:----------------------|
| レビュー系     | Read, Glob, Grep, AskUserQuestion | 読み取り専用。修正提案を出力しメインが適用 |
| 分析系       | Read, Glob, Grep, AskUserQuestion | 読み取り専用。分析結果と提案を出力     |

チェック項目:

- タスクの性質（READ系 or WRITE系）に応じた適切なツール選択か
- 不要なツール（特にTask）が含まれていないか
- **レビュー系エージェントはTaskツールを使用しない**（コンテキスト爆発防止）
- **WRITE系はメインエージェントのみ**（サブエージェントは修正提案出力のみ）

### A5: 前提条件の記述

- `.sdd/AI-SDD-PRINCIPLES.md` の読み込み明記
- `SDD_*` 環境変数によるパス解決の説明
- パス解決の優先順位（環境変数 → `.sdd-config.json` → デフォルト値）

### A6: 再委譲の禁止

- 再委譲を避ける設計意図が明記されているか
- Task tool で自分自身や他のサブエージェントを呼び出していないか

### A7: コンテキスト効率

- 重い処理がサブエージェントに委任されているか
- メインコンテキストの汚染を防ぐ設計か
- 無限探索を防ぐスコープ限定があるか

---

## スキルレビュー観点

### S1: フロントマターの設計

- 必須フィールド（name, description）が存在するか
- `argument-hint` が適切に設定されているか
- `allowed-tools` がタスクの性質に合っているか
- `disable-model-invocation` の使用が適切か（Skill自体がプロンプトの場合）

### S2: 入力設計

- `## Input` または `## 入力` セクションが存在するか
- セクション内で `$ARGUMENTS` を使用して引数を受け取っているか
- 入力形式（引数テーブル、入力例）が明確に定義されているか
- オプションの説明が十分か

**注意**: セクション名は英語（`## Input`）または日本語（`## 入力`）のどちらでも可。

### S3: 処理フローの明確性

- ステップが明確に分かれているか
- 各ステップで何をするかが具体的か
- 条件分岐やエラーハンドリングが考慮されているか

### S4: 出力設計

- 出力フォーマットが明確に定義されているか
- 単一/複数の場合で出力形式が区別されているか
- テンプレートファイルが適切に参照されているか

### S5: リファレンス構成

- 参照ドキュメントが適切な場所に整理されているか:
    - スキル固有: `skills/{skill-name}/references/`
    - 共通リファレンス: `shared/references/`（複数スキルで共有）
- 用途に応じた適切なファイル分割がされているか
- テンプレートが `templates/{lang}/` に配置されているか（多言語対応: `en/`, `ja/` など）

**注意**: 共通リファレンス（`prerequisites_*.md` など）は `shared/references/` に配置し、各スキルから相対パスで参照するパターンが推奨される。

---

## Hooksレビュー観点

### H1: JSON構造の正当性

- `hooks.json` がJSONとして valid か
- イベント名（SessionStart, PreToolUse, PostToolUse, Notification等）が正しいか
- matcher（toolName, message等）が適切に設定されているか（オプション）

**正しい hooks.json の構造（3レベルのネスト）:**

```json
{
  "description": "オプションの説明",
  "hooks": {
    "EventName": [
      {
        "matcher": "オプションのフィルター",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/example.sh"
          }
        ]
      }
    ]
  }
}
```

- **レベル1**: トップレベルの `"hooks"` オブジェクト（`"description"` はオプション）
- **レベル2**: イベント名（`"SessionStart"`, `"PreToolUse"` 等）の配列
- **レベル3**: matcher group 内の `"hooks"` 配列（hook handlers を定義）

**注意**: この3レベル構造は正しい設計。「二重ネスト」と誤解しないこと。

### H2: フックタイプの適切性

| タイプ     | 用途           | 注意点             |
|:--------|:-------------|:----------------|
| command | シェルコマンド実行    | 非同期実行に注意        |
| prompt  | LLMへの追加プロンプト | コンテキスト汚染に注意     |
| agent   | サブエージェント呼び出し | allowed-tools制限 |

**command タイプの実行方法:**

- 直接実行: `"command": "${CLAUDE_PLUGIN_ROOT}/scripts/example.sh"` （推奨、要 `chmod +x`）
- source 実行: `"command": "source ${CLAUDE_PLUGIN_ROOT}/scripts/example.sh"` （直接実行が動作しない場合の代替）
- bash 明示: `"command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/example.sh"`

**注意**: `source` や bash スクリプトは **Mac/Linux 専用**。Windows 対応が必要な場合は Python スクリプトを検討。

**SessionStart での環境変数設定:**

`CLAUDE_ENV_FILE` 環境変数を使用して永続化する（SessionStart フック専用）:

```bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo 'export VAR_NAME="value"' >> "$CLAUDE_ENV_FILE"
fi
# CLAUDE_ENV_FILE がない場合は何も出力しない（stdout と混ざるため）
```

**重要**: `CLAUDE_ENV_FILE` がない場合に stdout へ出力すると JSON レスポンスと混ざるため、何も出力しないのが正しい動作。

### H3: セキュリティ考慮

- コマンドインジェクションのリスクがないか
- 環境変数の使用が適切か
- ユーザー入力を直接コマンドに渡していないか

### H4: イベント選択の適切性

- 適切なライフサイクルイベントが選択されているか
- 不必要に多くのイベントにフックしていないか
- matcherで適切にフィルタリングされているか

---

## プラグイン構造レビュー観点

### P1: ディレクトリ構成

- `.claude-plugin/plugin.json` が存在するか
- `agents/`, `skills/`, `hooks/` が適切に配置されているか
- 不要なファイルが含まれていないか

### P2: plugin.json の設計

- 必須フィールド（`name`）が存在するか
- 推奨フィールド（`version`, `description`）が存在するか
- **デフォルトディレクトリの自動検出を理解しているか**:
    - `agents/`, `skills/`, `hooks/hooks.json` はプラグインルート直下に配置すれば自動検出される
    - `plugin.json` でのパス指定は**オプション**（追加パスを指定する場合のみ必要）
    - カスタムパスはデフォルトを**補完**する（置き換えない）
- Hooksスクリプト内で `${CLAUDE_PLUGIN_ROOT}` が適切に使用されているか

### P3: 機能選択の適切性

- 目的に対して適切な拡張機能（Skill/Agent/Hook/MCP）が選択されているか
- コンテキスト分離が必要なタスクにSubagentが使用されているか
- 決定論的に実行すべきアクションがHooksで実装されているか

---

## 参考リファレンス

詳細なチェック項目やドメイン知識は以下のリファレンスを参照。レビュー実行時に必要に応じて読み込む。

| 参照ファイル                                                                                      | 用途                                     |
|:--------------------------------------------------------------------------------------------|:---------------------------------------|
| [plugin-agent-reviewer.md](references/plugin-agent-reviewer.md)                             | エージェント設計パターン、エージェント間連携、Hooks作成Tips     |
| [claude-code-best-practices-reviewer.md](references/claude-code-best-practices-reviewer.md) | ベストプラクティス（検証方法、ワークフロー設計、失敗パターン）        |
| [claude-code-features-reviewer.md](references/claude-code-features-reviewer.md)             | 拡張機能の比較（Skills vs Subagents、コンテキストコスト） |
| [claude-code-plugin-developer.md](references/claude-code-plugin-developer.md)               | プラグイン構造、Hooks/LSP設定、デバッグ               |
| [claude-code-skills-guide.md](references/claude-code-skills-guide.md)                       | Skill設計（フロントマター、呼び出し制御、サブエージェント実行）     |

## 出力形式

### 単一ファイルの場合

各観点の評価と改善提案をそのまま出力する。

### 複数ファイルの場合

[batch-review-output.md](templates/batch-review-output.md) のテンプレートに従って出力する。
