---
id: "design-{ticket-number}"
title: "{FEATURE_NAME}"
type: "design"
status: "review"
sdd-phase: "plan"
impl-status: "implemented"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
depends-on: []
tags: ["reverse-engineered"]
category: ""
priority: "medium"
risk: "medium"
---

# {FEATURE_NAME} - 技術設計ドラフト（既存実装からの逆生成）

> **⚠️ 注意**: この設計ドラフトは{DATE}時点の既存実装から逆生成されたものです。
> 現在の状態を文書化したものであり、元々の設計ではありません。内容を確認の上、必要に応じて更新してください。
>
> **これは一時ドラフト**（`${SDD_TASK_PATH}/{ticket-number}/design-draft.md`）です。実装完了後、
> 確定した決定が `/task-cleanup` により `${SDD_ADR_PATH}/{feature-name}.md` へ追記されたうえで削除されます。

## 設計概要

**現在のアーキテクチャ:**

{HIGH_LEVEL_ARCHITECTURE_DESCRIPTION}

**技術スタック:**

- 言語: {プロジェクトで使用されているプログラミング言語}
- フレームワーク: {使用されているフレームワーク}
- データベース: {使用されているデータベース}
- ライブラリ: {主要なライブラリ}

## アーキテクチャ

> **これはこのチケット限りの作業用記述である。** 以下のうち永続する spec
> （`{feature-name}_spec.md` の「振る舞いとデータフロー」「内部インターフェース」）へ引き継がれるのは、
> 外部から観測できるデータフローと、他のコードが依存しているモジュール境界だけである。
> コンポーネントの内訳・ディレクトリ構成・コンポーネント間の依存関係はこのドラフトとともに破棄される。
> コードから再導出できる派生情報であるため、これは意図した設計である。`plan-refactor` スキルの
> "Reverse-Engineered Analysis — What Persists and What Does Not" を参照。

### コンポーネント構造

```
{CURRENT_DIRECTORY_STRUCTURE}
```

**コンポーネント:**

1. **{コンポーネント1名}** (`{file_path}`)
    - 責務: {何をするか}
    - 依存関係: {何に依存しているか}

2. **{コンポーネント2名}** (`{file_path}`)
    - 責務: ...
    - 依存関係: ...

### データフロー

```
{DATA_FLOW_DIAGRAM_OR_DESCRIPTION}
```

## 実装詳細

### 主要アルゴリズム

**{アルゴリズム名}** ({file_path}:{line_number})

```
{PSEUDOCODE_OR_DESCRIPTION}
```

### 状態管理

{状態の管理方法 - Redux、Context、データベースなど}

### エラー処理

{現在のエラー処理パターン}

## API設計

### エンドポイント（該当する場合）

| メソッド | パス | 説明 | 実装箇所 |
|:-----|:-----|:---|:-------|

## テスト戦略

**現在のテストカバレッジ:**

- ユニットテスト: {ファイルパス}
- 統合テスト: {ファイルパス}
- カバレッジ: {分かる場合はパーセンテージ}

**ギャップ:**
{テストが不足している領域}

## デプロイ

{観測可能な現在のデプロイプロセス}

## 技術的負債の観測事項

このドラフトは `/task-cleanup` で削除されるため、各項目に永続的な退避先を明記する。

1. **{負債項目1}**: {説明}
    - 深刻度: {高/中/低}
    - 場所: `{file_path}`
    - 退避先: {今回のリファクタで解消 → `/task-cleanup` が `${SDD_ADR_PATH}/{feature-name}.md` へ追記する
      エントリの Rationale に含める | 今回は見送り → チケット `{issue/ticket id、未作成なら「要作成」}` |
      Spec の記述と矛盾 → `{feature-name}_spec.md` の修正提案（人間の承認が必要）}

2. **{負債項目2}**: ...

---

**次のステップ:**

1. この設計が実際の実装と一致するか確認
2. 技術的負債項目に対処する、または見送る項目のチケットを作成する
3. リファクタリングを計画（以下にリファクタリング計画セクションを追加）
4. 実装完了後に `/task-cleanup` を実行し、確定した決定を
   `${SDD_ADR_PATH}/{feature-name}.md` へ追記してからドラフトを削除する
