> **これはサンプルです。** parallel-worktree skill を AI-SDD ワークフロー（本リポジトリ）の
> spec/design 生成に使う場合の**プロジェクト固有テンプレートの例**です。別プロジェクトでは
> そのまま使わず、コピーして自プロジェクトの規約・スキル体系に合わせて編集し、`spawn.sh` に
> `--prompt-template <あなたのテンプレへのパス>` で渡してください。書き方は同ディレクトリの
> `README.md` を参照。

---

あなたは並列 git worktree 上で起動された Claude Code セッションです。
このセッションは下記の単一 GitHub Issue（spec 生成タスク）を遂行するために起動されました。

---

# 担当 Issue

- **Issue 番号**: #${ISSUE_NUMBER}
- **Issue 参照キー**: ${ISSUE_ID}
- **タイトル**: ${ISSUE_TITLE}
- **ブランチ**: `${BRANCH}`
- **worktree**: `${WORKTREE_PATH}`

このタスクは**既にユーザー承認済み**として扱ってよく、`/plan` モードに入る必要はありません。

# 実行ステップ

## 1. コンテキスト取得

```bash
gh issue view ${ISSUE_NUMBER}
```

issue 本文には、対象PRD・出力先パス・front matter の id/depends-on・既存実装の参照先・受け入れ基準が記載されています。**熟読してください**。

続けて、issue 本文が指す以下を Read してください。

- 対象の子PRD（issue 本文「対象PRD」節のパス）
- 親PRD（同カテゴリの `index.md`）の UR・NFR・DC・IR
- 既存実装（issue 本文の「既存実装」節に列挙されたスクリプト/スキル）— **これが真実の源**
- `.sdd/AI-SDD-PRINCIPLES.md`（AI-SDD ワークフロー正典）
- `.sdd/CONSTITUTION.md`、`.sdd/SPECIFICATION_TEMPLATE.md`、`.sdd/DESIGN_DOC_TEMPLATE.md`

## 2. spec / design の生成

`/sdd-workflow:generate-spec` skill を使い、対象の子PRD から抽象仕様書と技術設計書を生成してください。

- 出力先は issue 本文の「出力先」節のパスに厳密に従う（階層構造: `.sdd/specification/<category>/` 配下）
- front matter の id / depends-on は issue 本文の指定どおりに設定する
- 命名規則（`_spec.md` / `_design.md` サフィックス必須）を厳守する
- トレーサビリティ表に PRD の要求ID（UR/FR/NFR 等）を必ず記載し、上流（親PRD）→ 子PRD → spec → design の依存方向を保つ
- 既存実装の挙動（トリガー方式・定量基準・判定ロジック）を**逆算して** design に正確に反映する。ドキュメントの記述ではなくコードの実態を真実とする

生成中に仕様上の重大な曖昧さに気付いた場合は AskUserQuestion で確認してください。

## 3. レビューと指摘適用

生成後、以下のエージェントでレビューし、指摘を適用してください。

```
spec-reviewer          # spec/design の CONSTITUTION 準拠・曖昧記述・SysML妥当性・トレーサビリティ
front-matter-reviewer  # front matter の形式・依存方向・id 一意性・相互参照整合
```

対象は生成した `_spec.md` と `_design.md` の両方。[must] 指摘は必ず修正、[recommend]/[nits] は妥当なものを適用してください。

## 4. コミット

CLAUDE.md のコミット規約に従ってください。

- 日本語 / プレフィックス（`[add]` 等）/ 簡潔に
- 末尾に `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` を付ける

```bash
git add .sdd/specification/<category>/
git commit -m "[add] <feat> の抽象仕様書・技術設計書を追加"
```

## 5. push & PR 作成

```bash
git push -u origin ${BRANCH}
```

その後 `/create-pr` skill で PR を作成してください。PR 本文には必ず `Closes #${ISSUE_NUMBER}` を含めること。

## 6. 完了報告

PR 作成後、user に以下を短く報告してください。

- PR の URL
- 生成した spec/design のパス
- spec-reviewer / front-matter-reviewer の確認結果（残指摘があれば明示）

---

# 注意事項

- **他の並列 worktree セッションが同時稼働中**です。各セッションは別々の子PRD → 別々の出力ファイルを触るためファイル衝突はありませんが、push 時の rejected → fetch → rebase は順守してください。
- **設計的に正しい判断をする**。実装量の推定で仕様の粒度を妥協しない。
- 日本語出力の品質（文字化け・U+FFFD 混入なし）を確認してから出力すること。

それでは、上記ステップに従って spec 生成を進めてください。
