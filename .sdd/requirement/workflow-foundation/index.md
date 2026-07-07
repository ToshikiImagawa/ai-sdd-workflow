---
id: "prd-workflow-foundation"
title: "ワークフロー基盤"
type: "prd"
status: "draft"
created: "2026-07-07"
updated: "2026-07-07"
depends-on: []
tags: ["initialization", "constitution", "session-config", "front-matter"]
category: "workflow-foundation"
priority: "high"
risk: "medium"
---

# ワークフロー基盤 要求仕様書

## 概要

本ドキュメントは、Claude Code プラグイン「sdd-workflow」のワークフロー基盤機能群に対する要求仕様書である。

AI-SDD ワークフロー（Specify → Plan → Tasks → Implement & Review）が機能するためには、
対象プロジェクトへの導入（ディレクトリ構造・テンプレート・原則の整備）と、
セッションごとの一貫した設定（パス解決・言語設定）が前提となる。
本機能群は、ワークフロー導入の初期化、プロジェクト原則の定義・管理、セッション設定の自動ロード、
既存ドキュメントへの構造化メタデータ付与という、他のすべての機能カテゴリが依存する土台を提供する。

**対象範囲:**

- プロジェクト初期化（`.sdd/` 構造・テンプレート・CLAUDE.md 設定）
- プロジェクト原則（CONSTITUTION）の定義・管理・同期検証
- セッション開始時の設定ロードと環境変数初期化
- 既存ドキュメントへの YAML front matter 推奨・適用

---

# 1. 要求図の読み方

SysML 要求図の記法（要求タイプ・リスクレベル・検証方法・関係タイプ）の凡例は
[PRD_TEMPLATE.md](../../PRD_TEMPLATE.md) のセクション 1 を参照。

---

# 2. 要求一覧

## 2.1. ユースケース図（概要）

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    Developer((開発者))
    HookRuntime((フックランタイム))

    subgraph WorkflowFoundation["ワークフロー基盤"]
        InitProject([プロジェクトを初期化する])
        ManagePrinciples([プロジェクト原則を定義・管理する])
        LoadConfig([セッション設定をロードする])
        RecommendFM([front matter を推奨・適用する])
    end

    Developer --- InitProject
    Developer --- ManagePrinciples
    Developer --- RecommendFM
    HookRuntime -.->|"セッション開始時"| LoadConfig
    InitProject -.->|"<<包含>>"| ManagePrinciples
```

## 2.2. 機能一覧（子 PRD）

各機能の要求詳細は以下の子 PRD を参照。

| 機能 | 子 PRD | 元要求 ID |
|:-----|:-------|:----------|
| プロジェクト初期化 | [sdd-init.md](sdd-init.md) | FR_001 |
| プロジェクト原則管理 | [constitution-management.md](constitution-management.md) | FR_002 |
| セッション設定初期化 | [session-config.md](session-config.md) | FR_003（FR_003_01〜03） |
| front matter 推奨 | [front-matter-recommend.md](front-matter-recommend.md) | FR_004 |

---

# 3. 要求図（SysML Requirements Diagram）

## 3.1. 全体要求図

FR ノード（FR_001〜FR_004）の詳細説明・トリガー方式・検証方法は各子 PRD を参照。

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram
    requirement WorkflowFoundation {
        id: UR_001
        text: "AI-SDDワークフローを対象プロジェクトへ容易に導入できる"
        risk: medium
        verifymethod: demonstration
    }

    requirement PrincipleGovernance {
        id: UR_002
        text: "プロジェクト原則を定義し全ドキュメントと同期を保てる"
        risk: high
        verifymethod: inspection
    }

    requirement ConsistentSession {
        id: UR_003
        text: "全スキルが一貫したパスと言語設定で動作する"
        risk: high
        verifymethod: test
    }

    requirement MetadataReadiness {
        id: UR_004
        text: "既存ドキュメントを構造化メタデータで検索・検証可能にできる"
        risk: low
        verifymethod: inspection
    }

    functionalRequirement ProjectInit {
        id: FR_001
        text: "ディレクトリ構造とテンプレートとCLAUDE.md設定を初期化する"
        risk: medium
        verifymethod: demonstration
    }

    functionalRequirement ConstitutionMgmt {
        id: FR_002
        text: "プロジェクト原則を作成し更新し同期を検証する"
        risk: medium
        verifymethod: demonstration
    }

    functionalRequirement SessionInit {
        id: FR_003
        text: "セッション開始時に設定をロードし環境変数を初期化する"
        risk: high
        verifymethod: test
    }

    functionalRequirement FrontMatterRecommend {
        id: FR_004
        text: "既存ドキュメントをスキャンしfront matter付与を推奨する"
        risk: low
        verifymethod: demonstration
    }

    requirement BackwardCompatibility {
        id: NFR_001
        text: "front matterのない既存ドキュメントも引き続き有効である"
        risk: medium
        verifymethod: test
    }

    interfaceRequirement ConfigSchema {
        id: IR_001
        text: "設定ファイルスキーマと環境変数名は全機能カテゴリ共通の契約とする"
        risk: high
        verifymethod: inspection
    }

    designConstraint StructureSupport {
        id: DC_001
        text: "フラット構造と階層構造の両方をサポートする"
        risk: medium
        verifymethod: test
    }

    designConstraint DefaultFallback {
        id: DC_002
        text: "設定が欠落しても既定値で動作を継続する"
        risk: medium
        verifymethod: test
    }

    designConstraint LanguageSupport {
        id: DC_003
        text: "言語設定により日英のテンプレートと出力を切り替える"
        risk: medium
        verifymethod: test
    }

    ProjectInit - derives -> WorkflowFoundation
    ConstitutionMgmt - derives -> PrincipleGovernance
    SessionInit - derives -> ConsistentSession
    FrontMatterRecommend - derives -> MetadataReadiness
    BackwardCompatibility - derives -> MetadataReadiness
    WorkflowFoundation - contains -> PrincipleGovernance
    WorkflowFoundation - contains -> ConsistentSession
    WorkflowFoundation - contains -> MetadataReadiness
    SessionInit - traces -> ConfigSchema
    ProjectInit - traces -> ConfigSchema
    StructureSupport - traces -> ProjectInit
    DefaultFallback - traces -> SessionInit
    LanguageSupport - traces -> SessionInit
```

---

# 4. 要求の詳細説明

## 4.1. ユーザー要求

### UR_001: ワークフローの容易な導入

開発者は、最小限の操作（初期化スキルの 1 回の実行）で、対象プロジェクトに AI-SDD ワークフローの
前提となるディレクトリ構造・テンプレート・設定を導入できること。

**検証方法:** デモンストレーションによる検証

### UR_002: プロジェクト原則のガバナンス

開発者は、プロジェクトの譲れない原則（Constitution）を定義・更新でき、
原則と他ドキュメント（PRD / 仕様書 / 設計書）との同期状態を検証できること。

**検証方法:** インスペクションによる検証

### UR_003: セッションの一貫性

すべてのスキル・エージェント・フックが、同一セッション内で一貫したディレクトリパスと言語設定を
参照して動作すること。設定の解決が個々の機能に分散せず、単一の初期化に集約されること。

**検証方法:** テストによる検証

### UR_004: メタデータによる検索・検証可能性

開発者は、front matter を持たない既存の AI-SDD ドキュメントに対して、構造化メタデータの付与を
推奨・適用でき、機械的な検索・フィルタリング・整合性検証を可能にできること。

**検証方法:** インスペクションによる検証

## 4.2. 非機能要求

### NFR_001: 後方互換性

front matter を持たない既存ドキュメントも引き続き有効として扱い、front matter の導入が
既存ワークフローを破壊しないこと。

**検証方法:** テストによる検証

## 4.3. インターフェース要求

### IR_001: 設定スキーマ・環境変数の共通契約

`.sdd-config.json` のスキーマおよび `SDD_*` 環境変数の名称・意味は、全機能カテゴリ
（PRD 生成・仕様設計・タスク実装・品質ガードレール）が参照する共通契約であり、
変更時は参照側との互換性を維持すること。

**検証方法:** インスペクションによる検証

## 4.4. 設計制約

### DC_001: フラット構造と階層構造の両サポート

`.sdd/` 配下のドキュメント配置は、フラット構造（小〜中規模）と階層構造（親機能ディレクトリ +
index / 子機能、中〜大規模）の両方をサポートすること。

**検証方法:** テストによる検証

### DC_002: 既定値へのフォールバック

設定ファイルの欠落・不正（不正 JSON・空値等）があっても、既定値にフォールバックして
セッション初期化を継続すること。設定不備がワークフロー全体を停止させてはならない。

**検証方法:** テストによる検証

### DC_003: 言語設定による切り替え

`SDD_LANG` 設定（en / ja）により、生成されるテンプレート・出力の言語を切り替えること。

**検証方法:** テストによる検証

---

# 5. 制約事項

## 5.1. 技術的制約

- セッション設定初期化は Claude Code の SessionStart フックとして実装され、フックランタイムの
  提供するインターフェース（環境変数エクスポート等）に依存する
- CLAUDE.md への設定はプロジェクト側の既存記述と共存する必要があり、既存内容を破壊してはならない

## 5.2. ビジネス的制約

- B-002 原則（多言語対応の一貫性）に従い、テンプレートは EN/JA で同等の構成を維持すること
- D-002 原則（ファイル命名規則の厳守）に従い、初期化で生成する構造・テンプレートは命名規則に準拠すること

---

# 6. 前提条件

- Claude Code のプラグイン機構・フックイベントシステムが利用可能であること
- 対象プロジェクトのルートに書き込み権限があること

---

# 7. スコープ外

以下は本 PRD のスコープ外とします：

- ドキュメントの生成そのもの（PRD 生成は prd-generation、仕様・設計は spec-design カテゴリで扱う）
- front matter の検証（quality-guardrails カテゴリの front-matter-reviewer が扱う。本カテゴリは推奨・適用まで）
- プラグイン自体の配布・バージョン管理（distribution カテゴリで扱う）

---

# 8. 用語集

| 用語               | 定義                                                            |
|------------------|-----------------------------------------------------------------|
| Constitution     | プロジェクトの譲れない最上位原則を定義するドキュメント（CONSTITUTION.md）      |
| .sdd-config.json | プロジェクトルートに置く AI-SDD 設定ファイル（ルート・言語・ディレクトリ名等）      |
| SDD_* 環境変数       | セッション初期化が設定する共通環境変数群（SDD_ROOT / SDD_LANG / SDD_*_PATH 等） |
| フラット構造 / 階層構造    | `.sdd/` 配下のドキュメント配置方式。規模に応じて選択する                        |
| front matter     | ドキュメント冒頭の YAML メタデータ（id / type / status / depends-on 等）     |
