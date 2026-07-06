---
name: review-pr
description: |
  PR のレビューコメントを読み取り、対応する Skill (本リポジトリ ai-sdd-workflow 専用)。
  gh CLI で PR のレビューコメントを取得し、各コメントを分析して妥当な指摘にはコード修正で対応、
  対応不要と判断したものには理由を説明する返信コメントを PR に残す。
  ユーザーが「レビュー対応して」「PR のコメント対応」「review 対応」「レビュー見て」
  「PR #123 のレビュー対応」と言ったとき、または PR にレビューコメントが付いて対応が必要な場面で使用する。
  検証コマンドは本リポジトリの CI (.github/workflows/ci.yml) に合わせた
  shellcheck / plugin-lint.sh / validate-marketplace.sh / test-session-start.sh を使う
  (npm/pnpm 系コマンドは使わない。本リポジトリに package.json は存在しない)。
user-invocable: true
---

# PR レビュー対応 Skill (ai-sdd-workflow 専用)

PR に付いたレビューコメントを読み取り、コード修正または返信コメントで対応する。

## 前提条件

- `gh` CLI がインストール済みで認証済みであること
- `github.com` host の Active account が本リポジトリ (`ToshikiImagawa/ai-sdd-workflow`) の owner と一致すること
  (複数アカウントが紐づく環境では `gh auth status` で確認し、不一致なら `gh auth switch --hostname github.com --user <対象アカウント>`)
- 対象 PR のブランチがチェックアウト済みであること

## ワークフロー

### Step 1: 対象 PR を特定する

引数で PR 番号が指定されていればそれを使う。指定がなければ現在のブランチに紐づく PR を取得する:

```bash
gh pr view --json number,title,url,headRefName,baseRefName
```

PR が見つからなければユーザーに確認する。

### Step 2: レビューコメントを取得する

```bash
# PR のレビューコメント一覧を取得
gh api repos/{owner}/{repo}/pulls/{number}/reviews --jq '.[] | select(.state != "PENDING")'

# 個別のレビューコメント（インラインコメント）を取得
gh api repos/{owner}/{repo}/pulls/{number}/comments
```

取得したコメントから以下を抽出する:
- コメント ID
- コメント本文
- 対象ファイル・行番号（インラインコメントの場合）
- コメントの種別（`[must]`, `[recommend]`, `[nits]` プレフィックスがあれば分類に活用。`.github/PULL_REQUEST_TEMPLATE.md` の Copilot レビュールールに準拠）
- スレッドの状態（resolved かどうか）

既に resolved 済みのコメントはスキップする。

### Step 3: コメントを分析・分類する

各コメントを読み、以下の 3 カテゴリに分類する:

- **対応する**: コードの修正で解決できる妥当な指摘
  - バグ、セキュリティ問題、設計上の問題
  - 可読性やパフォーマンスの改善で明らかに有益なもの
  - `[must]` プレフィックスの指摘は原則このカテゴリ

- **対応しない（説明を返す）**: 意図的な設計判断や、コンテキストを踏まえると不要な変更
  - 既存の方針（CLAUDE.md、`.claude/rules/`、`.sdd/AI-SDD-PRINCIPLES.md` 等）に基づく判断
  - トレードオフがあり、現在の実装が合理的な理由がある場合

- **判断保留（ユーザーに確認）**: 自分だけでは判断できないもの
  - プラグイン仕様やワークフロー設計に関わる変更
  - 大きなリファクタリングを伴う提案

### Step 4: 対応計画をユーザーに提示する

分類結果を一覧でユーザーに提示する。各コメントについて:

```
## 対応する（N 件）
1. [ファイル名:行] コメント要約 → 修正方針
2. ...

## 対応しない（N 件）
1. [ファイル名:行] コメント要約 → 返信予定の説明

## 判断保留（N 件）
1. [ファイル名:行] コメント要約 → 判断に必要な情報
```

ユーザーの承認を得てから次のステップに進む。分類の変更指示があれば反映する。

### Step 5: コード修正を実施する

「対応する」に分類されたコメントについて:

1. 対象ファイルを読み、コメントの指摘内容を理解する
2. 修正を実施する
3. 変更内容に応じて本リポジトリの検証コマンドで壊れていないか確認する（該当するものだけ実行すればよい）:

```bash
# プラグインJSON構文チェック (plugin.json / marketplace.json を変更した場合)
cat plugins/*/.claude-plugin/*.json | jq .

# マーケットプレイス/プラグイン構造の検証
bash scripts/validate-marketplace.sh

# .sh ファイルを変更した場合
shellcheck -S warning -e SC1091 <変更した.shファイル>

# スキル/エージェントのプロンプト構造 lint
bash scripts/plugin-lint.sh

# plugins/sdd-workflow/scripts/session-start.py を変更した場合
bash scripts/test-session-start.sh
```

フォーマッタは本リポジトリに存在しないため実行しない。Markdown を変更した場合は相対リンクの整合性を目視確認する。

すべての修正が完了したらコミットする。コミットメッセージは CLAUDE.md の規約に従い日本語 + プレフィックスを付ける:
```
[fix] PR レビュー指摘対応
```

### Step 6: PR にコメントを返信する

「対応しない」に分類されたコメントについて、各コメントに返信する。
返信は `gh api` でインラインコメントへのリプライとして投稿する:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies \
  -f body="返信内容"
```

返信の書き方:
- 丁寧な日本語で書く
- 指摘への感謝を述べつつ、対応しない理由を具体的に説明する
- 設計判断に基づく場合は、根拠となるドキュメント（CLAUDE.md、`.claude/rules/`、`.sdd/AI-SDD-PRINCIPLES.md` 等）を参照する
- レビュアーが追加の意見を持っている場合に備え、議論の余地を残す書き方にする

返信の末尾に以下を付ける:
```
---
*このコメントは Claude Code が生成しました。追加のご意見があればお知らせください。*
```

### Step 7: 変更を push してサマリーを報告する

```bash
git push
```

ユーザーに対応結果のサマリーを報告する:
- 修正したファイル数・コミット
- 返信したコメント数
- PR の URL

## 関連スキル / 設定

- `ship` skill — 本スキルを Step 3 (レビュー対応) で呼び出す
- `create-pr` skill — PR 作成時に使用（別スキル）
- CLAUDE.md 「コミットメッセージ」セクション — Step 5 のコミット規約
- `.github/workflows/ci.yml` — Step 5 検証コマンドの整合性確認元
- `.github/PULL_REQUEST_TEMPLATE.md` — `[must]`/`[recommend]`/`[nits]` 分類ルールの出典
