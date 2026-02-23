<!-- I want to review in Japanese. -->
## 概要

<!-- 変更の目的を簡潔に記述 -->

## 変更内容

<!-- 主な変更点を箇条書きで記述 -->

-

## レビューの焦点

<!-- レビュープロセス中にレビュアーが注目すべき特定の領域を強調します。 -->

## テスト計画

<!-- 動作確認の方法を記述 -->

- [ ] `cat plugins/*/.claude-plugin/*.json | jq .` JSON構文チェック通過
- [ ] `claude --plugin-dir ./plugins/sdd-workflow` でローカルテスト確認
- [ ] Markdownリンクの整合性確認

## 参考資料

-


<!-- for GitHub Copilot review rule -->

<details>
<summary>for GitHub Copilot review rule</summary>

## お願い

- 日本語で回答してください
- 簡潔で分かりやすい説明を心がけてください
- ベストプラクティスの具体例を提示してください
- 指摘の根拠となる情報源や学習リソースの提案を積極的に行ってください

## レビュールール

以下のプレフィックスを使用してレビューコメントを分類してください：

- `[must]` - 必須修正項目（セキュリティ、バグ、重大な設計問題）
- `[recommend]` - 推奨修正項目（パフォーマンス、可読性の大幅改善）
- `[nits]` - 軽微な指摘（コードスタイル、タイポ等）

## レビューステップ

1. コードの差分よりPRの概要を作成する

2. 実際にコードを確認し、以下の観点でレビューを行う
  - コードの正確性
  - パフォーマンス
  - セキュリティ
  - 可読性
  - 保守性
  - コーディング規約の遵守

3. 必要に応じて、具体的な改善点を指摘する

</details>

<!-- for GitHub Copilot review rule -->

<!-- I want to review in Japanese. -->