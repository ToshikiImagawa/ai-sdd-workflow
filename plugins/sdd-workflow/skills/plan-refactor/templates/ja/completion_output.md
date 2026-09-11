# 完了出力テンプレート

## Phase 5: 次のステップの要約

```
✅ リファクタリング計画が完了しました

**生成/更新されたファイル:**
- {spec_path} (Case B のみ — 実装から逆生成した永続仕様書)
- {design_draft_path} (一時ドラフト。実装完了後に削除される)

**リファクタリング計画の場所:**
{design_draft_path} - "Refactoring Plan" セクション

**逆生成した分析結果（Case B のみ）— 永続する範囲:**
- {spec_path} へ引き継いだ内容: {パブリックAPI | 内部インターフェース | データモデル |
  振る舞いとデータフロー | アーキテクチャパターン — 実際に書いたセクションを列挙}
- 意図的にドラフトとともに破棄する内容: コンポーネントの内訳、ディレクトリ構成、コンポーネント間の
  依存関係、内部の呼び出し順序、主要アルゴリズム、状態管理の内部、テストカバレッジの数値。
  いずれもコードから再導出できるため、再度必要になったら `/plan-refactor` を再実行する

**技術的負債の観測事項 — 永続的な退避先:**
| 観測事項 | 退避先 |
|:--|:--|
| {負債項目} | {クリーンアップ時の `adr/` エントリ | チケット {id / 要作成} | Spec 修正の提案} |

退避先が未定の観測事項: {なし | 一覧} — 実装開始前に割り当てる。未定のままではドラフト削除時に失われる。

**次のステップ:**
1. リファクタリング計画をレビュー: {design_draft_path}
2. 上記で見送りとした技術的負債のチケットを作成する
3. `/task-breakdown {feature-name} {ticket-number}` を実行してリファクタリングを実行可能なタスクに分解
4. TDDアプローチで `/implement {feature-name} {ticket-number}` を実行（`tasks.md` と設計ドラフトは
   どちらも `task/{ticket-number}/` 配下にあるため、同じチケット番号を渡す）
5. 実装完了後に `/task-cleanup {ticket-number}` を実行し、確定した決定を
   ${SDD_ADR_PATH}/{feature-name}.md へ追記する。この時点でドラフト（本計画を含む）は削除されるため、
   決定ログが唯一の恒久的な記録になる
```

## 出力フォーマット

```
File: {file_path}
Persistence: {永続 (specification/) | 一時ドラフト (task/{ticket-number}/)}
Status: {Created/Updated}
Sections Added: Refactoring Plan
```
