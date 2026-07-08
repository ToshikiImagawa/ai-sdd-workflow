---
id: "design-spec-design-plan-refactor"
title: "リファクタリング計画"
type: "design"
status: "draft"
sdd-phase: "plan"
impl-status: "implemented"
created: "2026-07-08"
updated: "2026-07-08"
depends-on: ["spec-spec-design-plan-refactor"]
tags: ["refactoring", "reverse-engineering", "skill-implementation"]
category: "spec-design"
priority: "medium"
risk: "medium"
---

# リファクタリング計画 - 技術設計書

**関連 Spec:** [plan-refactor_spec.md](plan-refactor_spec.md)
**関連 PRD:** [../requirement/spec-design/plan-refactor.md](../requirement/spec-design/plan-refactor.md)
**実装参照:** `plugins/sdd-workflow/skills/plan-refactor/SKILL.md`

---

# 1. 設計概要

## 1.1. 現在のアーキテクチャ

`/plan-refactor` スキルは Claude Code プラグイン内でエージェント実行される。
実装の核は以下の2つのユースケースに分かれている：

- **Case A**: 既存設計書がある場合、実装と設計の比較から改善ポイントを特定し、リファクタリング計画を追加
- **Case B**: 設計書がない場合、実装から設計書を逆生成してから計画を作成

## 1.2. 技術スタック

- **言語**: Markdown（ドキュメント生成）/ Bash（ファイル検索）
- **実行環境**: Claude Code エージェント実行時
- **出力形式**: Markdown（front matter 付き）
- **テンプレートエンジン**: 環境変数置換 + プリミティブなテンプレート処理

---

# 2. アーキテクチャ

## 2.1. コンポーネント構造

```
plugins/sdd-workflow/skills/plan-refactor/
├── SKILL.md                      # スキル定義書（入出力・フロー・ルール）
├── scripts/
│   ├── scan-existing-docs.sh    # Phase 1: 既存ドキュメント検索
│   └── find-implementation-files.sh  # Phase 2: 実装ファイル検索
├── templates/{en,ja}/
│   ├── reverse_spec_template.md    # Case B: 逆生成仕様書テンプレート
│   ├── reverse_design_template.md  # Case B: 逆生成設計書テンプレート
│   ├── refactor_plan_section.md    # Both: リファクタリング計画テンプレート
│   └── completion_output.md        # 出力フォーマット
├── examples/
│   ├── cli_usage.md             # 使用例
│   ├── case_a_existing_docs.md  # Case A のワークスルー
│   └── case_b_no_docs.md        # Case B のワークスルー
└── references/
    ├── front_matter_spec_design.md     # front matter スキーマ定義
    ├── design_doc_integration.md       # 設計書統合ガイド
    └── refactor_patterns.md            # リファクタリングパターン集
```

## 2.2. データフロー

```
ユーザー入力
  ↓
[フェーズ 1: 事前チェック]
  - scan-existing-docs.sh → .sdd/.cache/plan-refactor/existing-docs.json
  - Case A / Case B 判定
  ↓
[フェーズ 1.5: ユーザー意図の解析]
  - context パラメータを解析（オプション）
  ↓
[フェーズ 2: 実装ファイル検出]
  - find-implementation-files.sh → implementation-files.json
  - ファイル数チェック（20+ の場合、ユーザー確認）
  - 実装ファイルを読み込む
  ↓
[フェーズ 3: 処理分岐]
  ├─ Case A:
  │   - 既存設計書を読み込む
  │   - 実装と設計書の比較分析
  │   - リファクタリング計画を生成・追記
  │
  └─ Case B:
      - 仕様書テンプレートから逆生成
      - 設計書テンプレートから逆生成
      - リファクタリング計画を生成・追記
  ↓
[フェーズ 4: 検証]
  - 必須セクション確認
  ↓
[フェーズ 5: 次のステップ]
  - レビューエージェント推奨
  ↓
出力: 設計書 + リファクタリング計画
```

---

# 3. 実装詳細

## 3.1. Phase 1: Pre-flight Checks

### Step 1.1: Scan for Existing Documents

**実装ファイル**: `scripts/scan-existing-docs.sh`

**処理**:
1. `.sdd/requirement/{feature-name}.md` → PRD を検索
2. `.sdd/specification/{feature-name}_spec.md` → 仕様書を検索
3. `.sdd/specification/{feature-name}_design.md` → 設計書を検索
4. 階層構造対応：親機能ディレクトリ内のファイルも検索
5. 結果を `.sdd/.cache/plan-refactor/existing-docs.json` に出力

**出力例**:
```json
{
  "prd_exists": true,
  "prd_path": ".sdd/requirement/auth.md",
  "spec_exists": false,
  "spec_path": null,
  "design_exists": true,
  "design_path": ".sdd/specification/auth_design.md"
}
```

### Step 1.3: Determine Processing Case

- `design_exists == true` → **Case A** (設計書更新)
- `design_exists == false` → **Case B** (逆生成)

## 3.2. Phase 1.5: Parse User Intent (Optional)

**入力**: `context` パラメータ（例: "無限スクロール化してパフォーマンス改善"）

**処理**:
- パラメータがある場合、プロンプトで Claude に解析させる
- 抽出項目:
  - Primary Goal: 達成したい主要な改善
  - Motivation: なぜそれが必要か
  - Approach: 使用する技術・パターン（オプション）

**利用先**:
- リファクタリング計画の "Purpose and Background" セクションで優先度付け
- "Refactoring Strategy" で指定の手法を採用
- "Business/Technical Drivers" で motivation を記載

## 3.3. Phase 2: Implementation Discovery

### Step 2.1: Find Implementation Files

**実装ファイル**: `scripts/find-implementation-files.sh`

**処理**:
1. `feature-name` をパターンマッチング
   - ファイル名に `{feature-name}` を含む
   - ファイル内容に `{feature-name}` を含む（grep）
2. `--scope=<dir>` で検索範囲を限定（指定時）
3. 除外パターン: `node_modules/`, `.git/`, `dist/`, `build/`, `*.test.*`
4. 結果を `.sdd/.cache/plan-refactor/implementation-files.json` に出力

**出力例**:
```json
{
  "feature": "auth",
  "file_count": 12,
  "files": [
    {
      "path": "src/services/auth.ts",
      "relevance": "high",
      "matches": ["function authenticate", "class AuthService"]
    }
  ]
}
```

### Step 2.3: Validate File Count

- ファイル数 > 20 かつ `--ci` フラグなし → ユーザー確認ダイアログ
- 選択肢: Yes / No / Adjust Scope
- Adjust Scope 選択時 → 新しいスコープを入力させる

### Step 2.4: Read Implementation Files

- `implementation-files.json` から最大10ファイルを優先度順に読み込む
- 優先度: ファイル名の関連度 > ファイルサイズ
- テストファイルは除外（初期読み込み時）

## 3.4. Phase 3A: Case A - Existing Design Document

### Step 3A.2: Analyze Implementation vs. Specification

**比較観点**:
1. 設計書に記載されているコンポーネントが実装に存在するか
2. 実装がコンポーネント設計に従っているか
3. 実装に存在するが設計書に記載されていない部分があるか

**抽出内容**:
- **一致度**: ✓ 完全一致 / ⚠ 部分一致 / ✗ 乖離
- **乖離内容**: 技術スタック・API・データフロー・エラー処理
- **技術的負債**: コード重複・密結合・テストカバレッジ不足

### Step 3A.4: Generate Refactoring Plan

**テンプレート**: `templates/${SDD_LANG}/refactor_plan_section.md`

**セクション構成**:

| セクション | 内容 | 必須 |
|----------|------|------|
| Purpose and Background | リファクタリングの目的・背景。context がある場合は優先度付け | ✓ |
| Current State Analysis | 現状の問題点・メトリクス・根本原因。context に関連する項目を強調 | ✓ |
| Refactoring Strategy | 目標・アプローチ・トレードオフ。context の approach を採用すれば記載 | ✓ |
| Migration Plan | 段階的タスク・見積もり・依存関係 | ✓ |
| Impact Analysis | 破壊的変更・影響コンポーネント・ロールバック計画 | ✓ |
| Testing Strategy | ユニットテスト・統合テスト・E2E テスト計画 | ✓ |
| Success Criteria | メトリクス・受け入れ基準 | ✓ |
| Risks and Mitigations | リスク・軽減策 | ✓ |
| Timeline and Milestones | スケジュール・マイルストーン | - |

**例（context: "無限スクロール化してパフォーマンス改善"）**:

このコンテクストを使用した場合、生成される リファクタリング計画は以下のようになります（SDD_LANG=JA の場合）：

```markdown
## リファクタリング計画

### 目的と背景
現在のリスト表示は全アイテムを一度に DOM にレンダリングしているため、
1000+ アイテムで レンダリング時間が 3 秒以上かかる。
これを無限スクロール実装により 500ms 以下に改善する。

### 現状分析
- 全アイテムのデータを メモリに保持（20MB+）
- 初期ロード時に全 DOM を作成（実装: UserList.tsx:45）
- スクロールイベントの処理なし

### リファクタリング戦略
**アプローチ**: react-window による仮想化
- 動的にビューポート内のアイテムのみレンダリング
- メモリ使用量を 2MB 以下に削減
- 初期ロードを 200ms 以下に短縮

...
```

### Step 3A.5: Update Design Document

**処理**: `Edit {design_path}` で既存設計書の末尾に "## Refactoring Plan" セクションを追記

**前提**: 設計書に "## References" などの最終セクションがない場合のみ末尾に追記。
既に "## Refactoring Plan" が存在する場合は置換。

## 3.5. Phase 3B: Case B - No Documents (Reverse Engineering)

### Step 3B.1: Reverse-Engineer Specification

**テンプレート**: `templates/${SDD_LANG}/reverse_spec_template.md`

**抽出内容**:

| 項目 | 説明 | 実装参考箇所 |
|-----|------|-----------|
| **Feature Name** | 機能の識別子 | パラメータから |
| **Background** | なぜこの機能が必要か | コミットメッセージ / issue / コード内コメント |
| **Purpose** | 機能の目的 | 実装の主要 API / エクスポート |
| **Functional Requirements** | 何ができるのか | 公開 API / インターフェース定義 |
| **Data Model** | データ型・エンティティ | 型定義 / データベーススキーマ |
| **Behavior** | 主要なユースケース・フロー | 実装の核となるアルゴリズム |

**生成規則**:
```markdown
---
id: "spec-{feature-name}"
title: "{FEATURE_NAME}"
type: "spec"
status: "review"           # 逆生成は review 状態
sdd-phase: "specify"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
depends-on: ["prd-{feature-name}"]  # PRD があれば指定
tags: ["reverse-engineered"]
---

> **⚠️ 注意**: この仕様書は{DATE}時点の実装から逆生成されたものです。
> 元々の設計ではなく、現在の実装の文書化です。内容を確認の上、
> 必要に応じて更新してください。
```

### Step 3B.3: Reverse-Engineer Design Document

**テンプレート**: `templates/${SDD_LANG}/reverse_design_template.md`

**抽出内容**:

| 項目 | 説明 | 実装参考箇所 |
|-----|------|-----------|
| **Architecture Overview** | 高レベルアーキテクチャ | ディレクトリ構造 / モジュール設計 |
| **Component Structure** | コンポーネント一覧 | ファイル / クラス / 関数構成 |
| **Data Flow** | データの流れ | 呼び出し関係 / イベントハンドリング |
| **Key Algorithms** | 重要なアルゴリズム | 複雑な処理・計算ロジック |
| **API Design** | インターフェース設計 | 公開関数・エンドポイント・型定義 |
| **Error Handling** | エラー処理戦略 | 例外処理 / エラーコード |
| **Testing Strategy** | テスト構成 | テストファイル有無・カバレッジ |
| **Technical Debt** | 観測された負債項目 | コード重複・硬い結合・古いパターン |

**生成規則**:
```markdown
---
id: "design-{feature-name}"
title: "{FEATURE_NAME}"
type: "design"
status: "review"            # 逆生成は review 状態
sdd-phase: "plan"
impl-status: "implemented"  # 既に実装済み
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
depends-on: ["spec-{feature-name}"]
tags: ["reverse-engineered"]
---

> **⚠️ 注意**: この設計書は{DATE}時点の実装から逆生成されたものです。
> 現在の状態を文書化したものであり、元々の設計ではありません。
> 内容を確認の上、必要に応じて更新してください。
```

### Step 3B.5: Generate Refactoring Plan

Case A と同じ流れで「## Refactoring Plan」セクションを作成・追記

---

# 4. テンプレート管理

## 4.1. テンプレートの場所と優先度

### テンプレート検索順序

1. **プロジェクト定義テンプレート** (最優先)
   - `.sdd/SPECIFICATION_TEMPLATE.md`
   - `.sdd/DESIGN_DOC_TEMPLATE.md`

2. **プラグイン言語別テンプレート**
   - `plugins/sdd-workflow/skills/plan-refactor/templates/${SDD_LANG:-en}/`

3. **フォールバック** (推奨されない)
   - プラグイン EN テンプレート

### front matter スキーマ

**Spec front matter**:
```yaml
id: "spec-{feature-name}"
type: "spec"
status: "draft" or "review"
sdd-phase: "specify"
depends-on: ["prd-{feature-name}"] or []
tags: ["reverse-engineered"] (if Case B)
```

**Design front matter**:
```yaml
id: "design-{feature-name}"
type: "design"
status: "draft" or "review"
sdd-phase: "plan"
impl-status: "implemented" or "not-implemented"
depends-on: ["spec-{feature-name}"]
tags: ["reverse-engineered"] (if Case B)
```

---

# 5. エラーハンドリング

| 状況 | 対応 |
|-----|------|
| 実装ファイルが見つからない | ユーザーに feature-name を確認。`--scope` の指定を推奨 |
| 20+ ファイル検出 | CI モードでない場合、確認ダイアログ表示。スコープ調整を提案 |
| context が曖昧 | `AskUserQuestion` で Primary Goal / Motivation を確認 |
| PRD / 既存設計書が複数存在 | 最新の mtime を持つものを採用 |
| テンプレートが見つからない | プラグイン EN テンプレートにフォールバック |

---

# 6. テスト戦略

## 6.1. ユニットテスト

- `tests/skills/plan-refactor/` 配下
- scan-existing-docs.sh の正確性（複数構造・ファイル名パターン）
- find-implementation-files.sh のマッチング精度

## 6.2. 統合テスト

- Case A: 既存設計書がある機能で実行 → 設計書更新を確認
- Case B: 設計書がない機能で実行 → spec / design 生成を確認
- context パラメータ付き実行 → 計画に反映されたか確認

## 6.3. マニュアルテスト

- 実際のプロジェクトで実行
- レビューエージェントで品質確認

---

# 7. 言語対応（SDD_LANG）

- **EN**: 英語テンプレート・出力
- **JA**: 日本語テンプレート・出力

テンプレートパス: `templates/${SDD_LANG:-en}/`

---

# 8. デプロイ・リリース

- プラグイン `sdd-workflow` の一部として配布
- スキル `.claude-plugin/plugin.json` に登録
- ドキュメント: `SKILL.md`, テンプレート, examples, references

---

# 9. 設計判断の記録

### Decision 1: Case A/B の分岐設計

**判断**: 既存設計書の有無で異なる処理流を採用

**理由**:
- 既存設計書がある場合、逆生成より既存設計の更新が効率的
- 設計書がない場合、テンプレートから逆生成して明確な文書を作成

**代替案**:
- 常に逆生成 → 既存設計書を上書きしてしまいデータ喪失のリスク
- 常に既存ドキュメント参照 → 新規機能に対応不可

**トレードオフ**:
- ロジック複雑性 ↑ / 安全性・柔軟性 ↑

### Decision 2: context パラメータのオプション化

**判断**: context は必須でなくオプション

**理由**:
- 自動分析で一般的な改善提案も可能
- context を指定することでより焦点を絞った計画が作成可能
- ユーザーの使い勝手が向上

**実装上の複雑性**: context 有無で異なるプロンプトを用意

### Decision 3: 20+ ファイルチェック

**判断**: 実装ファイルが多い場合、ユーザー確認を必須に

**理由**:
- 分析時間の増加を予防
- 不要なファイル読み込みを避ける（--scope で最適化可能）

**代替案**:
- 固定値でフィルタリング → ユーザー意図を反映できない
- 常にすべて読む → スケール問題

---

# 10. 今後の拡張

- **実行時挙動分析**: コードカバレッジツールとの連携で動的情報を補完
- **差分レポート生成**: 設計書と実装の差分を図示
- **マイグレーション支援**: リファクタリング計画の自動タスク化・実装テンプレート生成

---

# 参照

- **親 PRD**: [../requirement/spec-design/index.md](../requirement/spec-design/index.md)
- **AI-SDD 原則**: [../../AI-SDD-PRINCIPLES.md](../../AI-SDD-PRINCIPLES.md)
- **スキル SKILL.md**: [../../../plugins/sdd-workflow/skills/plan-refactor/SKILL.md](../../../plugins/sdd-workflow/skills/plan-refactor/SKILL.md)
- **テンプレート**: [../../../plugins/sdd-workflow/skills/plan-refactor/templates/](../../../plugins/sdd-workflow/skills/plan-refactor/templates/)
