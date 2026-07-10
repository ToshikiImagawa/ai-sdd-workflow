# プラグイン Lint レポート（出力例）

## サマリー

| チェック項目 | ステータス | 問題数 |
|:-----------|:---------|:------|
| 1. プロンプトMarkdown内のコードブロック | ⚠️ 警告 | 12 件 |
| 2.1 ディレクトリ名の正確性 | ✅ パス | 0 件 |
| 2.2 ファイル名規約（snake_case） | ⚠️ 警告 | 1 件 |
| 2.3 言語ディレクトリの完全性 | ✅ パス | 0 件 |
| 2.4 言語間ファイルセットの一致 | ⚠️ 警告 | 2 件 |
| 2.5 サポートファイルの拡張子（.md） | ✅ パス | 0 件 |

---

## チェック1: プロンプトMarkdown内のコードブロック

以下のプロンプトファイルでコードブロックが検出されました:

| # | ファイル | 行番号 | ブロックタイプ |
|:--|:--------|:------|:------------|
| 1 | plugins/sdd-workflow/agents/spec-reviewer.md | 45 | json |
| 2 | plugins/sdd-workflow/agents/spec-reviewer.md | 52 | plain |
| 3 | plugins/sdd-workflow/skills/check-spec/SKILL.md | 38 | plain |
| 4 | plugins/sdd-workflow/skills/check-spec/SKILL.md | 45 | markdown |
| 5 | plugins/sdd-workflow/skills/generate-spec/SKILL.md | 22 | plain |
| 6 | plugins/sdd-workflow/skills/generate-spec/SKILL.md | 30 | plain |

**推奨事項**: コードブロックを `templates/`、`examples/`、`reference/` ディレクトリに移動し、LLM出力時の混同を防止してください。

---

## チェック2: サポートファイル構造

### 2.1 ディレクトリ名の正確性

想定外のディレクトリはありません。 ✅

### 2.2 ファイル名規約（snake_case）

snake_case 規約に従っていないファイル:

| ファイルパス | 現在の名前 | 推奨名 |
|:-----------|:---------|:------|
| plugins/sdd-workflow/skills/vibe-detector/templates/en/Risk-Report.md | Risk-Report.md | risk_report.md |

### 2.3 言語ディレクトリの完全性

全スキルで `en/` と `ja/` の両方が存在します。 ✅

### 2.4 言語間ファイルセットの一致

片方の言語にのみ存在するファイル:

| スキル | ファイル | 存在する側 | 不足する側 |
|:------|:--------|:---------|:---------|
| generate-spec | design_example.md | en | ja |
| output-templates | summary_format.md | ja | en |

### 2.5 サポートファイルの拡張子

非 `.md` ファイルはありません。 ✅

---

## 全体ステータス

⚠️ 15 件の問題が見つかりました

## 次のアクション

- コードブロックを含むプロンプトファイルを確認し、必要に応じて `templates/` や `examples/` に分離する
- `Risk-Report.md` を `risk_report.md` にリネームする
- `generate-spec` と `output-templates` の不足している言語ファイルを追加する