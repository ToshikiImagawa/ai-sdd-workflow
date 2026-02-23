---
name: prepare-release
description: "Prepare a release by updating EN/JA CHANGELOGs and version manifests. Analyzes git history, supplements existing [Unreleased] entries, and generates bilingual release notes."
version: 1.0.0
license: MIT
user-invocable: true
argument-hint: "<version>"
allowed-tools: Read, Edit, Glob, Grep, Bash
---

# Prepare Release - リリース準備スキル

EN/JA 両方の CHANGELOG を更新し、マニフェストファイルのバージョンを一括更新するリリース準備スキル。

**ハイブリッド方式**: `[Unreleased]` セクションに既存内容があればそれを活用し、git 変更履歴から不足分を補完する。

## Input

$ARGUMENTS

バージョン番号を引数として受け取る（`v` プレフィックスなし）。

### Input Examples

```
/prepare-release 3.2.0
/prepare-release 4.0.0-alpha
```

### Validation

- 引数が空の場合はエラー終了し、使用例を表示する
- セマンティックバージョニング形式（`X.Y.Z` または `X.Y.Z-prerelease`）であることを確認する

## Target Files

### CHANGELOG Files

| ファイル | 言語 |
|:---|:---|
| `plugins/sdd-workflow/CHANGELOG.md` | English |
| `plugins/sdd-workflow-ja/CHANGELOG.md` | Japanese |

### Version Manifest Files

| ファイル | フィールド |
|:---|:---|
| `.claude-plugin/marketplace.json` | `metadata.version` |
| `.claude-plugin/marketplace.json` | `plugins[].version`（全エントリ） |
| `plugins/sdd-workflow/.claude-plugin/plugin.json` | `version` |
| `plugins/sdd-workflow-ja/.claude-plugin/plugin.json` | `version` |

## Processing Flow

### Step 1: Validate Version Argument

1. `$ARGUMENTS` からバージョン番号をパースする
2. セマンティックバージョニング形式を検証する
3. 不正な場合はエラーメッセージと使用例を表示して終了する

### Step 2: Detect Previous Release

1. `git tag --list 'v*' --sort=-version:refname` で最新のリリースタグを取得する
2. タグが存在しない場合は初回リリースとして扱う
3. 比較基点を記録する（例: `v3.1.0`）

### Step 3: Read Current [Unreleased] Content

両方の CHANGELOG ファイルを Read で読み込み、`## [Unreleased]` セクションの内容を抽出する。

- **内容あり**: 既存エントリをベースとして保持する
- **内容なし**: Step 4 で全エントリを生成する

### Step 4: Analyze Git Changes

前回タグから HEAD までの変更を分析する。

```bash
# コミット一覧
git log <previous-tag>..HEAD --oneline --no-merges

# 変更ファイル統計
git diff <previous-tag>..HEAD --stat
```

変更内容を以下のカテゴリに分類する:

| EN Category | JA Category | 判定基準 |
|:---|:---|:---|
| Breaking Changes | 破壊的変更 | 互換性を破る変更、API 変更 |
| Added | 追加 | 新機能、新ファイル、新スキル/エージェント |
| Changed | 変更 | 既存機能の変更、リファクタリング |
| Fixed | 修正 | バグ修正、不具合対応 |
| Removed | 削除 | 機能やファイルの削除 |

### Step 5: Generate / Supplement CHANGELOG Entries

**重要: CHANGELOG はプラグイン利用者向けである。**

以下の変更は CHANGELOG に**含めない**:

- CI/CD ワークフロー（`.github/workflows/`）の追加・変更
- 開発者向けスクリプト（`scripts/`）の追加・変更
- テストコード・テストフィクスチャ（`tests/`）の追加・変更
- `.claude/skills/` 配下の開発者向けスキル
- `.gitignore`、PR テンプレート等のリポジトリ管理ファイル
- その他、プラグインをインストールしたユーザーに影響しない変更

以下の変更は CHANGELOG に**含める**:

- `plugins/` 配下のスキル、エージェント、フック、テンプレートの変更
- プラグインマニフェスト（`plugin.json`）のスキーマ変更
- プラグイン利用者に影響するバグ修正・機能追加・破壊的変更

**ハイブリッドロジック:**

1. `[Unreleased]` に既存内容がある場合:
   - 既存エントリをベースとする
   - git 変更履歴と照合し、カバーされていない**利用者向け変更**を特定する
   - 不足分のエントリのみ追加生成する
2. `[Unreleased]` が空の場合:
   - git 変更履歴から**利用者向け変更**のエントリを生成する
3. 利用者向け変更が存在しない場合:
   - ユーザーに「プラグイン利用者向けの変更がありません」と報告し、CHANGELOG 更新をスキップするか確認する

**EN/JA 同期ルール:**

- 両言語で同じ構造（カテゴリ、項目数、順序）を維持する
- EN が技術的正確性の基準、JA はその翻訳
- 一方にのみ既存エントリがある場合、他方にも対応エントリを生成する

**記述スタイル（既存 CHANGELOG に準拠）:**

- 各エントリは `- **対象名** - 変更内容の要約` 形式
- サブ項目はインデント2スペースで `- 詳細内容`
- 機能グループがある場合は `####` サブヘッダーで分類

### Step 6: Update CHANGELOG Files

両 CHANGELOG ファイルに対して以下を実行する:

1. `## [Unreleased]` セクションの既存内容をクリアする
2. `## [Unreleased]` の直後に空行を挟んで新バージョンセクションを挿入する:
   ```
   ## [VERSION] - YYYY-MM-DD
   ```
3. 日付は実行日（`date +%Y-%m-%d` で取得）を使用する
4. Step 5 で生成/統合したエントリを配置する

### Step 7: Update Version Manifests

4箇所のバージョンフィールドをすべて新バージョンに更新する:

1. `.claude-plugin/marketplace.json` → `metadata.version`
2. `.claude-plugin/marketplace.json` → `plugins[].version`（全プラグイン）
3. `plugins/sdd-workflow/.claude-plugin/plugin.json` → `version`
4. `plugins/sdd-workflow-ja/.claude-plugin/plugin.json` → `version`

### Step 8: Summary

更新結果のサマリーを表示する:

- 更新されたバージョン: `OLD_VERSION` → `NEW_VERSION`
- CHANGELOG エントリ数（カテゴリ別）
- 更新されたファイル一覧
- 次のステップ（レビュー → コミット → タグ → プッシュ）

## Output Format

```
## Release Preparation Complete

**Version**: OLD_VERSION → NEW_VERSION
**Date**: YYYY-MM-DD

### CHANGELOG Updates

| Category | EN entries | JA entries | Source |
|:---|:---|:---|:---|
| Added | N | N | existing / generated / mixed |
| Changed | N | N | ... |
| Fixed | N | N | ... |

### Updated Files

- [ ] `plugins/sdd-workflow/CHANGELOG.md`
- [ ] `plugins/sdd-workflow-ja/CHANGELOG.md`
- [ ] `.claude-plugin/marketplace.json`
- [ ] `plugins/sdd-workflow/.claude-plugin/plugin.json`
- [ ] `plugins/sdd-workflow-ja/.claude-plugin/plugin.json`

### Next Steps

1. 変更内容をレビューする
2. コミットする: `git add -A && git commit -m "[add] v{VERSION} リリース準備"`
3. タグを作成する: `git tag v{VERSION}`
4. プッシュする: `git push origin main --tags`
5. GitHub Actions の Release ワークフローが自動実行される
```

## Notes

- このスキルは CHANGELOG の **生成・編集** と **バージョン更新** を行う。コミットやタグ作成は行わない
- 生成されたエントリは必ずユーザーにレビューを促す
- プレリリースバージョン（`-alpha`, `-rc.1` 等）もサポートする
- EN CHANGELOG が `plugins/sdd-workflow/CHANGELOG.md`、JA CHANGELOG が `plugins/sdd-workflow-ja/CHANGELOG.md` である
