# PRD（要求仕様書）テンプレート

このドキュメントは `.sdd/requirement/` 配下のPRD（要求仕様書）を作成する際のテンプレートです。
ファイル名は `{機能名}.md` となります。

> **注意**: このテンプレートはプラグインのフォールバック用です。
> プロジェクトで使用する際は、プロジェクト構成に合わせてカスタマイズし、
> `.sdd/PRD_TEMPLATE.md` として保存してください。

## 仕様書・設計書との違い

| ドキュメント             | SDDフェーズ          | 役割と焦点                                               | 抽象度      |
|--------------------|------------------|-----------------------------------------------------|----------|
| `requirement/*.md` | **Specify（仕様化）** | **「何を作るか」「なぜ作るか」** - ビジネス要求を定義。技術詳細は含めない            | 最高（抽象的）  |
| `xxx_spec.md`      | **Specify（仕様化）** | **「何を作るか」** - システムの抽象的な構造と振る舞いを定義。技術的詳細は含めない        | 高（抽象的）   |
| `xxx_design.md`    | **Plan（計画/設計）**  | **「どのように実現するか」** - 抽象仕様を実現するための具体的な技術設計。設計判断の透明性を確保 | 中〜低（具体的） |

---

# {機能名} 要求仕様書 `<MUST>`

## 概要 `<MUST>`

このドキュメントの目的と対象範囲を簡潔に説明します。

---

# 1. 要求図の読み方 `<RECOMMENDED>`

## 1.1. 要求タイプ

- **requirement**: 一般的な要求
- **functionalRequirement**: 機能要求
- **performanceRequirement**: パフォーマンス要求
- **interfaceRequirement**: インターフェース要求
- **designConstraint**: 設計制約

## 1.2. リスクレベル

- **High**: 高リスク（ビジネスクリティカル、実装困難）
- **Medium**: 中リスク（重要だが代替可能）
- **Low**: 低リスク（Nice to have）

## 1.3. 検証方法

- **Analysis**: 分析による検証
- **Test**: テストによる検証
- **Demonstration**: デモンストレーションによる検証
- **Inspection**: インスペクション（レビュー）による検証

## 1.4. 関係タイプ

- **contains**: 包含関係（親要求が子要求を含む）
- **derives**: 派生関係（要求から別の要求が導出される）
- **satisfies**: 満足関係（要素が要求を満たす）
- **verifies**: 検証関係（テストケースが要求を検証する）
- **refines**: 詳細化関係（要求をより詳細に定義する）
- **traces**: トレース関係（要求間の追跡可能性）

---

# 2. 要求一覧 `<MUST>`

## 2.1. ユースケース図（概要） `<RECOMMENDED>`

主要機能とアクターの関係を示す概要図です。

```mermaid
graph TB
    subgraph "システム名"
        Actor1((アクター1))
        Actor2((アクター2))
        Func1[機能1]
        Func2[機能2]
        Func3[機能3]
    end

    Actor1 --- Func1
    Actor1 --- Func2
    Actor2 --- Func3
    Func1 -.->|"&lt;&lt;包含&gt;&gt;"| Func3
```

## 2.2. ユースケース図（詳細） `<OPTIONAL>`

### {機能カテゴリ1}

```mermaid
graph TB
    subgraph "機能カテゴリ1"
        Actor((アクター))
        UseCase1[ユースケース1]
        UseCase2[ユースケース2]

        subgraph "詳細"
            Detail1[詳細1]
            Detail2[詳細2]
        end
    end

    Actor --- UseCase1
    Actor --- UseCase2
    Detail1 -.->|"&lt;&lt;拡張&gt;&gt;"| UseCase1
    Detail2 -.->|"&lt;&lt;拡張&gt;&gt;"| UseCase1
```

## 2.3. 機能一覧（テキスト形式） `<MUST>`

- 機能カテゴリ1
    - サブ機能1-1
        - 詳細1-1-1
        - 詳細1-1-2
    - サブ機能1-2
- 機能カテゴリ2
    - サブ機能2-1

---

# 3. 要求図（SysML Requirements Diagram） `<MUST>`

## 3.1. 全体要求図

```mermaid
requirementDiagram
    requirement SystemRequirement {
        id: REQ_001
        text: "システム全体の要求"
        risk: high
        verifymethod: demonstration
    }

    requirement CoreFunctionality {
        id: REQ_002
        text: "コア機能要求"
        risk: high
        verifymethod: demonstration
    }

    requirement Architecture {
        id: REQ_003
        text: "アーキテクチャ要求"
        risk: high
        verifymethod: inspection
    }

    requirement Quality {
        id: REQ_004
        text: "品質要求（非機能要求）"
        risk: high
        verifymethod: test
    }

    functionalRequirement Function1 {
        id: FR_001
        text: "機能要求1の説明"
        risk: high
        verifymethod: test
    }

    functionalRequirement Function2 {
        id: FR_002
        text: "機能要求2の説明"
        risk: medium
        verifymethod: test
    }

    performanceRequirement Performance1 {
        id: PR_001
        text: "パフォーマンス要求1"
        risk: high
        verifymethod: test
    }

    interfaceRequirement Interface1 {
        id: IR_001
        text: "インターフェース要求1"
        risk: high
        verifymethod: inspection
    }

    designConstraint Constraint1 {
        id: DC_001
        text: "設計制約1"
        risk: high
        verifymethod: inspection
    }

    SystemRequirement - contains -> CoreFunctionality
    SystemRequirement - contains -> Architecture
    SystemRequirement - contains -> Quality
    CoreFunctionality - contains -> Function1
    CoreFunctionality - contains -> Function2
    Quality - contains -> Performance1
    Architecture - contains -> Interface1
    Architecture - contains -> Constraint1
    Function1 - traces -> Interface1
    Performance1 - traces -> Function1
```

## 3.2. 主要サブシステム詳細図 `<OPTIONAL>`

### {サブシステム名}

```mermaid
requirementDiagram
    requirement Subsystem {
        id: REQ_002
        text: "サブシステムの要求"
        risk: high
        verifymethod: demonstration
    }

    functionalRequirement SubFunction1 {
        id: FR_001_01
        text: "サブ機能1"
        risk: high
        verifymethod: test
    }

    functionalRequirement SubFunction2 {
        id: FR_001_02
        text: "サブ機能2"
        risk: medium
        verifymethod: test
    }

    Subsystem - contains -> SubFunction1
    Subsystem - contains -> SubFunction2
```

---

# 4. 要求の詳細説明 `<MUST>`

## 4.1. 機能要求

### FR_001: {機能要求名}

{機能の詳細な説明}

**含まれる機能:**

- FR_001_01: {サブ機能1}
- FR_001_02: {サブ機能2}

**検証方法:** テストによる検証

### FR_002: {機能要求名}

{機能の詳細な説明}

**検証方法:** テストによる検証

## 4.2. パフォーマンス要求 `<OPTIONAL>`

### PR_001: {パフォーマンス要求名}

{パフォーマンス要求の詳細な説明と目標値}

**検証方法:** テストによる検証

## 4.3. インターフェース要求 `<OPTIONAL>`

### IR_001: {インターフェース要求名}

{インターフェース要求の詳細な説明}

**検証方法:** インスペクションによる検証

## 4.4. 設計制約 `<OPTIONAL>`

### DC_001: {設計制約名}

{設計制約の詳細な説明}

**検証方法:** インスペクションによる検証

---

# 5. 制約事項 `<OPTIONAL>`

## 5.1. 技術的制約

- 技術的な制約

## 5.2. ビジネス的制約

- ビジネス的な制約（スケジュール、予算など）

---

# 6. 前提条件 `<OPTIONAL>`

- この機能が動作するための前提
- 依存する他システム・機能

---

# 7. スコープ外 `<OPTIONAL>`

以下は本PRDのスコープ外とします：

- この機能に含まれないこと
- 将来的に検討する可能性があるが、今回は対象外

---

# 8. 用語集 `<RECOMMENDED>`

> **注意**: 用語集が大きくなる場合は、別ファイル（`glossary.md`）として管理することを推奨します。

| 用語   | 定義   |
|------|------|
| [用語] | [定義] |

---

# セクション必須度の凡例

| マーク             | 意味 | 説明                 |
|-----------------|----|--------------------|
| `<MUST>`        | 必須 | すべてのPRDで必ず記載してください |
| `<RECOMMENDED>` | 推奨 | 可能な限り記載することを推奨します  |
| `<OPTIONAL>`    | 任意 | 必要に応じて記載してください     |

---

# ガイドライン

## 含めるべき内容

- ✅ 概要と目的
- ✅ ユースケース図（概要・詳細）
- ✅ SysML要求図（requirementDiagram構文）
- ✅ 要求の詳細説明（機能要求、パフォーマンス要求、インターフェース要求、設計制約）
- ✅ 要求間の関係（contains, derives, satisfies, verifies, refines, traces）
- ✅ 制約事項・前提条件
- ✅ スコープ外の明示
- ✅ 用語集

## 含めないべき内容（→ Spec / Design Doc へ）

- ❌ 技術的な実装詳細
- ❌ アーキテクチャ・モジュール構成
- ❌ 技術スタックの選定
- ❌ API定義・型定義
- ❌ データベーススキーマ

---

# プロジェクトへのカスタマイズ指針

このテンプレートをプロジェクト用にカスタマイズする際は、以下の項目を更新してください：

1. **要求IDの命名規則**: プロジェクトの規約に合わせる（REQ/FR/PR/IR/DC以外のプレフィックスを使う場合）
2. **リスクレベルの分類**: プロジェクトのリスク評価基準に合わせる
3. **検証方法の分類**: プロジェクトの検証プロセスに合わせる
4. **ユースケース図のスタイル**: プロジェクトのアクター・機能構成に合わせる
5. **用語集の管理方法**: 別ファイル管理にするか、PRD内に含めるか決定する

---

**このPRDは、AIエージェントが仕様化（Specify）フェーズで参照する、ビジネス要求の真実の源となります。**
