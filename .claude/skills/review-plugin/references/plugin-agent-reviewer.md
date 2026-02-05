# プラグインエージェント設計レビュー観点

AI-SDDワークフロープラグインのサブエージェント設計をレビューするための観点とチェック項目。
[AGENTS.md](../../../../AGENTS.md) の設計ガイドに基づく。

## レビュー観点

### 1. description の明確性

**チェック項目**:

- 何をするか（動詞）が明確か
- どのドキュメントを対象とするか明示されているか
- どのような観点でチェックするか記述されているか
- 結果としてどうなるか（修正提案の出力等）が記載されているか

**Good descriptionの例**:

```markdown
description: "
仕様書の品質レビューとCONSTITUTION.md準拠チェックを行うエージェント。曖昧な記述、不足セクション、SysMLとしての妥当性をチェックし、違反時は修正提案を出力します。"
```

**Bad descriptionの例**:

```markdown
description: "仕様書をレビューする"  # 曖昧、何をどうチェックするのか不明
```

### 2. 入出力インターフェース

**必須要素**:

- `## 入力` セクション
    - `$ARGUMENTS` の使用
    - `### 入力形式` セクション（必須/オプションを明示）
    - `### 入力例` セクション（複数の例を提示）
- `## 前提条件` セクション
    - AI-SDD原則ドキュメント（`.sdd/AI-SDD-PRINCIPLES.md`）の読み込み明記
    - 環境変数 `SDD_*` によるパス解決の説明
- `## 出力` セクション（出力フォーマットの定義）

**標準テンプレート**:

```markdown
## 入力

$ARGUMENTS

### 入力形式

対象ファイルパス（必須）: .sdd/specification/{機能名}_spec.md
オプション: --summary （簡易出力モード）

### 入力例

sdd-workflow-ja:spec-reviewer .sdd/specification/user-auth_spec.md
sdd-workflow-ja:spec-reviewer .sdd/specification/user-auth_spec.md --summary

## 前提条件

**実行前に必ず AI-SDD原則ドキュメントを読み込んでください。**

AI-SDD原則ドキュメントパス: `.sdd/AI-SDD-PRINCIPLES.md`

### ディレクトリパスの解決

**環境変数 `SDD_*` を使用してディレクトリパスを解決します。**

| 環境変数 | デフォルト値 | 説明 |
|:--|:--|:--|
| `SDD_ROOT` | `.sdd` | ルートディレクトリ |
| `SDD_REQUIREMENT_PATH` | `.sdd/requirement` | PRD/要求仕様書ディレクトリ |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書・設計書ディレクトリ |
| `SDD_TASK_PATH` | `.sdd/task` | タスクログディレクトリ |

**パス解決の優先順位:**

1. 環境変数 `SDD_*` が設定されている場合はそれを使用
2. 環境変数がない場合は `.sdd-config.json` を確認
3. どちらもない場合はデフォルト値を使用

## 出力

レビュー結果レポート（評価サマリー、要修正項目、改善推奨項目、修正提案サマリー）
```

### 3. フロントマターフィールドの設計

**標準フィールド**:

```yaml
---
name: agent-name
description: "詳細なトリガー説明"
model: sonnet
color: green
allowed-tools: [ Read, Glob, Grep, AskUserQuestion ]
---
```

**拡張フィールド**:

| フィールド  | 型      | 説明                                |
|:-------|:-------|:----------------------------------|
| tools  | array  | `allowed-tools` の代替フィールド          |
| skills | array  | プリロードするスキル（例: `["plugin:skill"]`） |
| hooks  | object | エージェントスコープのフック設定                  |

### 4. allowed-tools の設計

**設計パターン**:

| エージェントタイプ                                               | allowed-tools                     | 理由                     |
|:--------------------------------------------------------|:----------------------------------|:-----------------------|
| **レビュー系** (prd-reviewer, spec-reviewer)                 | Read, Glob, Grep, AskUserQuestion | 読み取り専用。修正提案を出力し、メインが適用 |
| **分析系** (requirement-analyzer, clarification-assistant) | Read, Glob, Grep, AskUserQuestion | 読み取り専用。分析結果と提案を出力      |

**チェック項目**:

- タスクの性質（READ系 or WRITE系）に応じて適切なツールが選択されているか
- 不要なツールが含まれていないか（特にTaskツール）
- レビュー系エージェントでTaskツールが許可されている場合、正当な理由があるか

**重要な制約**:

- **レビュー系エージェント（spec-reviewer, prd-reviewer）は Task ツールを使用しない**
- 理由: ドキュメント間トレーサビリティチェックで大量のファイル読み込みが発生し、Taskツールで再帰的に探索するとコンテキストが爆発的に増加するため
- **WRITE系はメインエージェントのみ**: サブエージェントは修正提案を出力し、メインエージェントが Edit を実行

### 5. 前提条件の記述

**必須記述**:

- `.sdd/AI-SDD-PRINCIPLES.md` の読み込み明記（session-start.sh により自動更新）
- 環境変数 `SDD_*` によるディレクトリパス解決の説明
- パス解決の優先順位（環境変数 → `.sdd-config.json` → デフォルト値）

### 6. 再委譲の禁止

**チェック項目**:

- エージェントマニフェストで再委譲を避ける設計意図が明記されているか
- allowed-tools に Task が含まれる場合、正当な理由が説明されているか

**許可されるパターン**:

- Read, Glob, Grep で必要な情報を取得
- 必要に応じて Edit で自動修正（メインエージェントのみ）

**禁止パターン**:

- Task tool で自分自身を呼び出す（無限ループ）
- Task tool で他のサブエージェントを呼び出す（コンテキスト効率化の意図を損なう）

## エージェント間連携パターン

### スキル連携

| パターン                   | 使用場面                  | メリット            |
|:-----------------------|:----------------------|:----------------|
| スキルに `context: fork`   | スキル単体で独立した処理を行いたい場合   | メインコンテキストを汚染しない |
| エージェントに `skills` プリロード | エージェントにスキルの知識を付与したい場合 | エージェントの能力を拡張できる |

### フック連携

| タイプ      | 用途            | 例                           |
|:---------|:--------------|:----------------------------|
| `prompt` | ツール使用後の品質検証   | Edit後にCONSTITUTION.md準拠チェック |
| `agent`  | ツール使用後の自動レビュー | Write後にspec-reviewerを自動起動   |

## Hooks 作成のTips

### シェルスクリプトでのエラーハンドリング

**重要な教訓**: `2>/dev/null` でエラーを抑制する場合、副作用（一時ファイルの作成など）を必ず確認する。

**Bad example**:

```bash
if sed "s|pattern|replacement|" "$SOURCE" > "$TEMP_FILE" 2>/dev/null; then
    mv "$TEMP_FILE" "$TARGET"  # sedが失敗しても一時ファイルが作成されず、mvがエラーになる
else
    cp "$SOURCE" "$TARGET"
fi
```

**Good example**:

```bash
if sed "s|pattern|replacement|" "$SOURCE" > "$TEMP_FILE" 2>/dev/null && [ -f "$TEMP_FILE" ]; then
    mv "$TEMP_FILE" "$TARGET"  # 一時ファイルが確実に存在する
else
    cp "$SOURCE" "$TARGET"
fi
```

### Hooks 作成時の推奨事項

1. **エラー抑制時は副作用を確認** - `2>/dev/null` 使用時はファイル作成等の副作用を必ず確認
2. **一時ファイルの扱い** - 作成後は存在確認、失敗時はクリーンアップ（`rm -f "$TEMP_FILE"`）
3. **stderr出力の活用** - `>&2` で情報提供は問題なし
4. **終了コードの明示** - `exit 0` / `exit 1` を明示的に記述

### Hooks のテスト方法

インストール済みhooksディレクトリで直接テストする:

1. `~/.claude/plugins/cache/{plugin-name}/{version}/hooks/` を確認
2. `hooks.json` を直接編集してテスト
3. Claude Code を再起動して動作確認

## レビュー評価基準

各観点を以下の3段階で評価する:

| 評価      | 意味             |
|:--------|:---------------|
| 🟢 良好   | 設計ガイドに準拠       |
| 🟡 改善推奨 | 機能するが改善の余地あり   |
| 🔴 要修正  | 設計ガイドに違反、修正が必要 |
