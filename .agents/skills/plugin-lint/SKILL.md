---
name: plugin-lint
description: "Lint check for AI-SDD plugin prompt files and support file structure. Detects code blocks in prompt Markdown and validates naming conventions."
version: 3.0.0
license: MIT
user-invocable: true
argument-hint: "[none]"
allowed-tools: Bash, Read
---

# Plugin Lint - プラグイン構造品質チェック

プラグインのプロンプトMarkdownファイルとサポートファイル構造をlintチェックし、問題をレポートする。自動修正は行わない。

検出ロジックはすべて Python スクリプト（`scripts/plugin_lint.py`）に実装されている。このスキルの役割は、スクリプトの実行と結果の整形レポートのみ。

## Input

$ARGUMENTS

引数なしで全体チェックを実行する。

### Input Examples

/plugin-lint

## Check Items

スクリプトが以下をチェックする（詳細は `scripts/plugin_lint.py` を参照）:

| Check ID | 内容 |
|:---|:---|
| 1 | プロンプトMarkdown（`plugins/sdd-workflow/agents/*.md`, `skills/*/SKILL.md`）内のコードブロック検出。`templates/`, `examples/`, `references/` 配下は除外 |
| 2.1 | スキルディレクトリ直下のエントリが `SKILL.md`, `README.md`, `templates`, `examples`, `references`, `scripts` のいずれかであること |
| 2.2 | サポートファイル名が snake_case（`^[a-z0-9_]+\.[a-z]+$`）であること（`shared/references/` を含む） |
| 2.3 | `templates/` に `en/` と `ja/` の両方が存在すること |
| 2.4 | `templates/en/` と `templates/ja/` のファイルセットが一致すること |
| 2.5 | サポートファイルの拡張子が `.md` であること（`scripts/` は対象外） |
| 3.1 | スキル `SKILL.md` の `allowed-tools` に列挙されたツール名が実在すること |
| 3.2 | `allowed-tools` にツール名の重複がないこと |

## Processing Flow

### Step 1: Run Lint Script

Bash でスクリプトを実行する:

    python3 "$(git rev-parse --show-toplevel)/.agents/skills/plugin-lint/scripts/plugin_lint.py"

- 終了コード 0: 問題なし
- 終了コード 1: 問題あり（stdout の JSON に findings が含まれる）
- 終了コード 2: 実行エラー（stderr を確認して報告する）

出力 JSON の構造: `{"total": n, "summary_by_check": {"<check_id>": n}, "findings": [{"check_id", "file", "line", "message", ...}]}`

findings が多い場合は出力をファイルにリダイレクトし、Read で読み取る。

### Step 2: Report Generation

JSON 結果を `templates/lint_report.md` テンプレートの形式で整形して報告する。

- 各チェック項目のステータス（✅ パス / ⚠️ 警告）と件数を summary_by_check から埋める
- Check 1 の findings には推奨事項（`templates/`, `examples/`, `references/` への分離）を添える
- 件数が多い場合はファイル単位で集約して報告してよい

## Notes

- このスキルは **検出とレポートのみ** を行い、自動修正は行わない
- コードブロック検出は誤検知の可能性がある（意図的に含めている場合）ため、開発者の判断に委ねる
- チェックロジックの変更は `scripts/plugin_lint.py` を編集する（SKILL.md ではなく）
