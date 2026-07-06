あなたは並列 git worktree 上で起動された Claude Code セッションです。
このセッションは下記の単一 GitHub Issue を実装するために起動されました。

---

# 担当 Issue

- **Issue 番号**: #${ISSUE_NUMBER}
- **Issue 参照キー**: ${ISSUE_ID}
- **タイトル**: ${ISSUE_TITLE}
- **ブランチ**: `${BRANCH}`
- **worktree**: `${WORKTREE_PATH}`

# 実行ステップ

## 1. コンテキスト取得

```bash
gh issue view ${ISSUE_NUMBER}
```

issue 本文の背景・対象ファイル・受け入れ基準を熟読してください。
本文中で `.sdd/` 配下のドキュメントや `.claude/rules/` 配下のルールへの参照があれば、それも Read してください。

## 2. 実装方針の確認

この Issue は**既にユーザー承認済みのタスク**として扱ってよく、`/plan` モードに入る必要はありません。
ただし以下のケースでは **AskUserQuestion で確認**してください。

- Issue 本文に記載されていない設計判断を伴う場合
- issue が触れていないファイル・プラグイン・スキルへの影響が発生する場合
- 受け入れ基準が満たせない別アプローチを取りたい場合
- 影響範囲が予想より大きい (10 ファイル以上等)

逆に Issue 本文どおりに機械的に実装できる場合は即着手してよいです。

## 3. 実装

CLAUDE.md (グローバル + プロジェクト) と `.claude/rules/` 配下のルールを厳守してください。

- シンプルさ優先 / YAGNI / 既存パターン踏襲
- 不要なコメント / 過剰な抽象化を避ける
- 設計的に正しい判断をする (実装量で妥協しない)
- ドキュメントの記述 (ステータス、実装済みフラグ等) を根拠に変更する前に、必ず Glob/Grep/Read で実態を確認する
- 新規エージェント/スキル追加時は対象プラグインの `plugin.json` への登録を忘れない
- `.sdd/` 配下を操作する場合は `.sdd/AI-SDD-PRINCIPLES.md` に準拠する

## 4. 品質保証

PR を出す前に以下を**必ず**通過させてください。失敗時は修正してから次へ進んでください。

```bash
# プラグインJSON構文チェック (対象プラグインを変更した場合)
cat plugins/*/.claude-plugin/*.json | jq .

# プラグイン構造 lint
claude --plugin-dir ./plugins/sdd-workflow  # 手動確認、または /plugin-lint skill
```

Markdown ドキュメントを変更した場合は、相対リンクが有効かも確認してください。

## 5. コミット

CLAUDE.md のコミット規約に従ってください。

- 日本語で記述する
- プレフィックスを付ける: `[add]`, `[update]`, `[fix]`, `[refactoring]`, `[remove]`, `[docs]`, `[test]`
- 簡潔に変更内容を説明する

```bash
git add <変更ファイル>
git commit -m "<メッセージ>"
```

## 6. push & PR 作成

```bash
git push -u origin ${BRANCH}
```

その後、`/create-pr` skill で PR を作成してください。PR 本文には必ず `Closes #${ISSUE_NUMBER}` を含めること。

## 7. 完了報告

PR 作成後、user に以下を短く報告してください。

- PR の URL
- 変更ファイル数 / 追加削除行数
- lint (plugin-lint 等) の確認結果
- 受け入れ基準のうち手動検証が必要な項目があれば明示

---

# 注意事項

- **他の並列 worktree セッションが同時稼働中**の可能性があります。push 時の rejected → fetch → rebase を順守してください。
- **lint が通らない場合は push しない**でください。修正不可能と判断した場合は AskUserQuestion で報告してください。

それでは、上記ステップに従って実装を進めてください。
