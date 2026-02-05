---
name: plugin-lint
description: "Lint check for AI-SDD plugin prompt files and support file structure. Detects code blocks in prompt Markdown and validates naming conventions."
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
---

# Plugin Lint - プラグイン構造品質チェック

プラグインのプロンプトMarkdownファイルとサポートファイル構造をlintチェックし、問題をレポートする。自動修正は行わない。

## Input

$ARGUMENTS

引数なしで全体チェックを実行する。

### Input Examples

```
/plugin-lint
```

## Check Items

### Check 1: Code Block Detection in Prompt Markdown

プロンプトMarkdownファイル内のコードブロック（` ``` ` で始まる行）を検出する。

#### Target Files

- `plugins/sdd-workflow/agents/*.md`
- `plugins/sdd-workflow/skills/*/SKILL.md`

#### Excluded Paths

以下のディレクトリ配下のファイルはチェック対象外:

- `templates/`
- `examples/`
- `references/`

#### Detection Pattern

` ``` ` で始まる行（コードブロックの開始/終了）を検出する。

#### Report Content

検出されたコードブロックごとに以下を報告:

- ファイルパス（プロジェクトルートからの相対パス）
- 行番号
- ブロックタイプ（` ``` ` の後に続く言語指定、なければ `plain`）

#### Recommendation

プロンプトMarkdown内のコードブロックは、LLMが出力時にコードブロックの開始/終了を混同するリスクがある。以下を推奨:

- 構造例やフォーマット定義 → `templates/` 配下に分離
- コード例 → `examples/` 配下に分離
- 参考資料 → `references/` 配下に分離

### Check 2: Support File Structure Validation

スキルディレクトリ配下のサポートファイル構造を検証する。

#### Target

`plugins/sdd-workflow/skills/*/` 配下の以下のディレクトリ:

- `templates/`
- `examples/`
- `references/`

#### 2.1 Directory Name Accuracy

サポートファイル用ディレクトリ名が正確であることを検証する。
SKILL.md、README.md 以外のファイル・ディレクトリが `templates`, `examples`, `references`, `scripts` のいずれかであるか。

#### 2.2 File Name Convention (snake_case)

サポートファイルのファイル名がスネークケース（`^[a-z0-9_]+\.[a-z]+$`）であるかチェックする。

対象: `templates/`, `examples/`, `references/` 配下の全ファイル

#### 2.3 Language Directory Completeness

`templates/` ディレクトリに `en/` と `ja/` の両方が存在するかチェックする。

#### 2.4 Language File Set Consistency

`templates/en/` と `templates/ja/` で同じファイルセットを持つかチェックする。片方にのみ存在するファイルを報告する。

#### 2.5 Support File Extension

サポートファイル（`templates/`, `examples/`, `references/` 配下）の拡張子が `.md` であるかチェックする。ただし `scripts/` 配下は対象外。

## Processing Flow

### Step 1: Target File Discovery

Glob で以下のパターンのファイルを取得:

- `plugins/sdd-workflow/agents/*.md`
- `plugins/sdd-workflow/skills/*/SKILL.md`

### Step 2: Code Block Detection (Check 1)

Step 1 で取得した各ファイルに対して:

1. Grep で `` ^``` `` パターンを検索
2. ヒットした行番号とブロックタイプを記録
3. `templates/`, `examples/`, `references/` 配下のファイルは除外

### Step 3: Support File Structure Scan (Check 2)

Glob で `plugins/sdd-workflow/skills/*/` 配下のディレクトリとファイルを取得し、各サブチェック（2.1〜2.5）を実行。

### Step 4: Report Generation

`templates/ja/lint_report.md` テンプレートに基づいてレポートを生成・出力する。

## Output

Read `templates/ja/lint_report.md` and use it for lint check output formatting.

## Notes

- このスキルは **検出とレポートのみ** を行い、自動修正は行わない
- コードブロック検出は誤検知の可能性がある（意図的に含めている場合）ため、開発者の判断に委ねる
- サポートファイル構造の検証は AI-SDD プラグインの規約に基づく