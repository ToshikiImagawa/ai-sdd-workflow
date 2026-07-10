---
name: ship
description: |
  現在のブランチを PR 作成から merge・ローカルクリーンアップまで一気通貫で出荷するワークフロー。
  「ship」「PR 出して merge まで」「リリースしたい」「マージまで進めて」「PR の続きやって」
  といったユーザー指示で必ず使用する。
  本プロジェクト (ai-sdd-workflow) の CLAUDE.md と CI 設定 (.github/workflows/ci.yml) を
  運用準拠の真実の源として扱い、グローバル skill `create-pr` とリポジトリ専用 skill
  `review-pr` (.agents/skills/review-pr、npm 非依存で本リポジトリの検証コマンドに対応) に
  作成・レビュー対応を委譲する。CI ポーリング・レビュー対応・squash-merge・
  ローカルブランチ削除までを順序立てて実行する。
  破壊的操作 (merge / branch 削除) の直前で人間に確認を取り、CI 失敗時は状況レポートに
  留めて修正判断を人間に委ねる。
user-invocable: true
---

# /ship — PR 出荷フルライフサイクル

現在のブランチを「PR 作成 → CI 監視 → レビュー対応 → squash-merge → ローカルクリーンアップ」まで一気通貫で進める。CLAUDE.md（コミットメッセージ規約）と `.github/workflows/ci.yml`（CI で実行されるコマンド）を真実の源として扱う。

## 設計の前提

- **既存スキルに委譲する**: PR 作成は `create-pr`、レビュー対応は `review-pr` を呼ぶ。本スキルはオーケストレーションに専念し、ロジックを重複させない。
- **破壊的操作は人間の go/no-go を取る**: squash-merge とローカルブランチ削除の直前に確認プロンプトを出す。
- **CI 失敗は自動修正しない**: 失敗ログを構造化して提示し、修正判断は人間に委ねる。
- **コミットメッセージ規約に従う**: 日本語 + プレフィックス (`[add]` / `[update]` / `[fix]` / `[refactoring]` / `[remove]` / `[docs]` / `[test]`)。

## 実行手順

### 0. 事前チェック (必須)

ブランチ未確定状態で誤った PR を作らないよう、以下を順に確認する。失敗した時点で停止しユーザーに状況報告。

```bash
git branch --show-current        # main のときは中断 (出荷対象ではない)
git status --short               # 未コミット変更があれば中断 (commit か stash を促す)
git log --oneline main..HEAD     # main からの差分 1 件以上を確認
gh auth status                   # github.com host の Active account が対象リポジトリの owner と一致するか確認
```

`github.com` host に複数アカウントが紐づいている環境では、`gh auth status` の `Active account: true` が対象リポジトリの owner と異なる場合がある。一致しない場合は `gh auth switch --hostname github.com --user <対象アカウント>` で切り替えてから進める。

その後、CI (`.github/workflows/ci.yml`) と同等の事前検証を実行する。いずれか失敗で中断:

```bash
# validate ジョブ相当
bash scripts/validate-marketplace.sh

# shellcheck ジョブ相当 (変更した .sh ファイルのみで十分な場合はスコープを絞ってよい)
find . -name "*.sh" -type f -print0 | xargs -0 shellcheck -S warning -e SC1091

# plugin-lint ジョブ相当
bash scripts/plugin-lint.sh

# test ジョブ相当 (session-start.py の regression test)
bash scripts/test-session-start.sh
```

どれか 1 つでも失敗した場合は中断し、ログをユーザーに提示して修正判断を仰ぐ。本スキルから自動修正は行わない。

### 1. PR 作成

`create-pr` skill を起動する。本プロジェクトの規約に従い:

- タイトル / 本文は日本語、プレフィックス `[add]` / `[update]` / `[fix]` / `[refactoring]` / `[remove]` / `[docs]` / `[test]` のいずれか
- `.github/PULL_REQUEST_TEMPLATE.md` のセクション (概要 / 変更内容 / レビューの焦点 / テスト計画 / 参考資料) を埋める
- テスト計画のチェックリスト項目 (`jq` 構文チェック / `--plugin-dir` ローカルテスト / Markdown リンク整合性) は Step 0 相当の確認が済んでいれば `- [x]` にする
- 関連 Issue が判明していれば「参考資料」セクションに記載 (`Closes #<番号>` を含める)

PR 番号と URL を保持し、以降のステップで使用する。

### 2. CI 監視

`gh pr checks <PR番号>` で状態をポーリングする。本リポジトリの CI は validate / shellcheck (2 OS) / plugin-lint / test (2 OS) の複数ジョブ構成:

- **ポーリング間隔**: 30 秒
- **最大待機**: 10 分（超える場合は GitHub Actions 側で stuck している可能性が高いため、状況をユーザーに報告し中断）
- **無音で待たせない**: ポーリング中はステータスを 1 回ごとに要約してユーザーに見せる

CI 完了時の分岐:

- **全 check 成功** → 3 へ
- **1 件以上失敗** → `gh run view <run-id> --log-failed` で失敗ログを取得し、構造化してユーザーに提示。**自動修正は行わない**。ユーザー判断後に再 push が必要なら本スキルを再起動する想定で停止

### 3. レビュー対応

レビューコメント (Copilot / 人間) をすべて取得し、`review-pr` skill に委譲する。

- `gh pr view <PR番号> --json reviews,comments` で取得
- `[must]` 指摘は必ず対応、`[recommend]` は対応または明確な却下理由を返信、`[nits]` は判断に応じて対応 (PR テンプレの Copilot レビュールールに準拠)
- レビュアー別に分けず一括対応する。複数回ラウンドが発生した場合は 2 → 3 の往復を続ける
- すべてのコメントに「対応した / 対応見送る」の旨を返信する

対応後の push:

- 事前チェック (Step 0) のコマンド群を**再度すべて**実行してから push
- push 後は再度 Step 2 (CI 監視) に戻る

### 4. Merge 直前確認 (人間 go/no-go)

CI 緑 + 全レビューコメント対応済みを確認後、**必ず**ユーザーに確認プロンプトを出す:

> CI 全緑、レビューコメント N 件すべて対応済み。squash-merge してよろしいですか？

ユーザーが yes を返した場合のみ次へ進む。no または無応答の場合は merge せず停止。

### 5. Squash-Merge

```bash
gh pr merge <PR番号> --squash --delete-branch
```

`--delete-branch` でリモートブランチも同時削除。

merge 失敗時 (例: マージコンフリクト、required check 未満足) はエラー内容をユーザーに提示し停止。コンフリクト解消はユーザーに提案し、本スキルからは強制 merge しない。

### 6. ローカル cleanup 直前確認 + 実行

merge 成功後、もう一度ユーザーに確認:

> リモート merge 成功。ローカルブランチを削除して main を最新化してよろしいですか？

yes であれば:

```bash
git checkout main
git pull --ff-only origin main
git branch -d <出荷したブランチ名>     # -D ではなく -d で fully merged のみ削除
```

`git branch -d` が失敗する場合は意図しない未マージコミットが残っている可能性があるので、強制削除 (`-D`) せずユーザーに報告。

### 7. 完了レポート

最後に以下のサマリを 1 メッセージで提示:

- PR 番号 / URL
- merge コミット SHA
- CI 所要時間 (今後の調整用)
- レビュー往復回数 / 対応コメント数
- ローカルクリーンアップ結果

## 失敗ケースの扱い

| ステージ | 失敗 | 振る舞い |
|---|---|---|
| Step 0 | `git status` で未コミット変更 | commit / stash を促し停止。自動で commit や stash しない |
| Step 0 | validate / shellcheck / plugin-lint / test 失敗 | ログ提示し停止。自動修正はしない |
| Step 1 | gh pr create 失敗 | エラーログを提示し停止。認証状態 (`gh auth status`) の確認を促す。`github.com` に複数アカウントが紐づいている場合、意図しないアカウントが Active になっていると権限エラーになるため `gh auth switch --hostname github.com --user <対象アカウント>` での切り替えを提案する |
| Step 2 | CI 失敗 | `gh run view --log-failed` で抜粋を提示し停止 |
| Step 2 | 10 分超で stuck | GitHub Actions 状態をユーザーに報告し停止 |
| Step 3 | レビュー対応で新たな指摘発生 | Step 2 へ戻り再ループ。3 ラウンド超えたらユーザーに介入を促す |
| Step 5 | merge 失敗 (conflict) | コンフリクト解消をユーザーに提案。本スキルからは強制 merge しない |
| Step 6 | `git branch -d` が拒否 | 未 merge コミット残存の可能性。-D 強制削除せずユーザー確認 |

## やらないこと (out of scope)

- **CI 失敗の自動修正** (shellcheck / plugin-lint / test 含む) — 誤検知コストが高いため
- **強制 push** (`--force` / `--force-with-lease`) — 本スキル経由では実行しない
- **main への直接 push** — そもそも本リポジトリは PR 経由が必須
- **異なる文脈の PR の合流 (rebase squash の大幅履歴改変)** — 必要時はユーザー判断
- **複数 PR の並列ハンドリング** — 1 ブランチ 1 PR の単線で動かす（複数 issue の並列処理は `parallel-worktree` skill を使う）

## 関連スキル / 設定

- `create-pr` skill — Step 1 で委譲（git log / git diff から PR 本文を自動生成）
- `review-pr` skill — Step 3 で委譲（レビューコメント取得・分析・返信）
- `parallel-worktree` skill — 複数 issue の並列実装。本スキルとは別フロー（1 ブランチずつの出荷を担当）
- `.github/workflows/ci.yml` — Step 0 検証コマンドの整合性確認元
- `.github/PULL_REQUEST_TEMPLATE.md` — Step 1 で埋めるテンプレート
