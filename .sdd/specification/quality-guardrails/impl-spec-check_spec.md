---
id: "spec-quality-guardrails-impl-spec-check"
title: "実装と設計の整合性チェック"
type: "spec"
status: "draft"
sdd-phase: "specify"
created: "2026-07-07"
updated: "2026-07-07"
depends-on: ["prd-quality-guardrails-impl-spec-check"]
tags: ["consistency-check", "design-sync", "quality-gate"]
category: "quality-guardrails"
priority: "high"
risk: "high"
---

# 実装と設計の整合性チェック `<MUST>`

**関連 Design Doc:** [impl-spec-check_design.md](impl-spec-check_design.md)
**関連 PRD:** [impl-spec-check.md](../../requirement/quality-guardrails/impl-spec-check.md)
**準拠する原則:** [CONSTITUTION.md](../../CONSTITUTION.md) の B-001, A-002, B-002, D-002

---

# 1. 背景 `<MUST>`

技術設計書（`*_design.md`）は「どのように実現するか」の真実の源だが、実装が進むにつれて設計書との
乖離が発生し得る。API シグネチャの変更、型定義の不一致、閾値・列挙値などのリテラル値の書き換え、
設計書に記載された機能の未実装といった乖離は、放置すると設計判断の透明性を損ない、仕様駆動の開発
サイクルを破綻させる。

本機能は、開発者が任意のタイミングで実装コードと技術設計書を比較し、乖離を検出・報告することで、
親 PRD [quality-guardrails](../../requirement/quality-guardrails/index.md) の UR_003（PRD・仕様書・
設計書・実装の整合性維持）を満たす品質ガードレールを提供する。子 PRD
[impl-spec-check.md](../../requirement/quality-guardrails/impl-spec-check.md) の FR_001 を実現する。

# 2. 概要 `<MUST>`

本機能は、Claude Code プラグイン `sdd-workflow` の `check-spec` スキル（`/check-spec`）として提供する。
開発者が明示的に呼び出す**手動トリガー方式**の品質ゲートであり、実装コードと技術設計書の乖離を検出・
報告する。

主要な設計原則：

- **手動トリガー**: フックによる自動発火ではなく、開発者が `/check-spec` で任意のタイミングに起動する
  （実装完了時・PR 作成前・定期チェック等）。
- **検出・報告に専念**: 乖離の検出と報告までを責務とし、**自動修正は行わない**。修正の判断は開発者と
  AI の対話に委ねる（読み取り専用スキル）。
- **責務の分離**: 本スキルは **design ↔ 実装**の整合性チェックに特化する。ドキュメント間整合性
  （PRD ↔ spec ↔ design）と品質レビューは `--full` オプション指定時に `spec-reviewer` エージェントへ
  委譲する。
- **多言語対応**: 出力は `SDD_LANG` 環境変数に応じて EN / JA を切り替える。
- **段階的検出**: リテラル値（閾値・列挙値・CHECK 制約値）を spec → design → 実装の 3 層で比較し、
  値ドリフトを検出する。

**「何を実現するか」に焦点を当て、具体的なスクリプト構成・処理アルゴリズムの詳細は
[impl-spec-check_design.md](impl-spec-check_design.md) に委ねる。**

# 3. 要求定義 `<RECOMMENDED>`

## 3.1. 機能要件 (Functional Requirements)

各要件は子 PRD [impl-spec-check.md](../../requirement/quality-guardrails/impl-spec-check.md) の
FR_001（実装コードと技術設計書の乖離を検出する）から派生する。

| ID     | 要件                                                                                  | 優先度 | 根拠（上流要求）                       |
|--------|-------------------------------------------------------------------------------------|-----|--------------------------------|
| FR-001 | 開発者の手動呼び出し（`/check-spec [feature-name] [--full]`）で整合性チェックを起動する               | 必須  | PRD FR_001（手動トリガー方式）           |
| FR-002 | チェック対象の技術設計書（`*_design.md`）と対応する抽象仕様書を特定する（フラット構造・階層構造の両方に対応）         | 必須  | PRD FR_001 / 前提条件（`.sdd/` 構造）  |
| FR-003 | design と実装コードを比較し、API シグネチャ・型定義・モジュール構成・機能実装・技術スタックの乖離を検出する            | 必須  | PRD FR_001（乖離の検出）              |
| FR-004 | リテラル値（閾値・列挙値・CHECK 制約値）を spec → design → 実装の 3 層で比較し、値ドリフトを検出する            | 必須  | PRD FR_001（乖離の検出）              |
| FR-005 | 検出した乖離を重大度（Critical / Warning / Info）で分類し、未実装機能・未文書化実装とともに報告する            | 必須  | PRD FR_001（乖離の報告）              |
| FR-006 | front matter を持つ対象ドキュメントについて `front-matter-reviewer` エージェントで検証し、`impl-status` の指摘を統合する | 必須  | PRD FR_001（乖離の検出を補強する連携。親 PRD の front-matter-validation 機能を再利用） |
| FR-007 | `--full` オプション指定時に `spec-reviewer` エージェントを呼び出し、ドキュメント間整合性・品質レビューを実施する      | 推奨  | PRD FR_001（乖離の報告を拡張する連携。親 PRD の doc-consistency 機能を再利用） |
| FR-008 | 引数なし実行時は対象ファイル一覧を提示し、開発者に実行範囲を確認する                                          | 推奨  | PRD FR_001（誤操作防止）              |

## 3.2. 非機能要件 (Non-Functional Requirements) `<OPTIONAL>`

| ID      | カテゴリ  | 要件                                                                       | 目標値                              |
|---------|-------|--------------------------------------------------------------------------|----------------------------------|
| NFR-001 | 安全性   | 本スキルは読み取り専用とし、実装コード・ドキュメントを一切変更しない                          | `Write` / `Edit` ツールを禁止        |
| NFR-002 | 多言語対応 | 出力メッセージ・レポートは `SDD_LANG` に応じて EN / JA を切り替える（親 PRD B-002 準拠）    | `templates/{en,ja}/` の両方を提供     |
| NFR-003 | 移植性   | macOS / Linux の両方で動作する（親 PRD DC_004 準拠）                            | POSIX 準拠（bash 3.2 / dash）       |
| NFR-004 | 効率性   | 決定的なファイル走査を Claude のツール呼び出しではなくスクリプトに委譲し、トークン消費を抑制する（A-002） | 走査は Shell スクリプトの 1 回実行に集約 |

# 4. 提供コンポーネント `<MUST>`

| 種別（skill/agent/hook/template） | 配置場所                                                          | 名前                       | 概要                                                            |
|------------------------------|---------------------------------------------------------------|--------------------------|---------------------------------------------------------------|
| skill                        | `skills/check-spec/SKILL.md`                                  | `check-spec`             | 実装と技術設計書の整合性チェック（`/check-spec`）。`user-invocable: true` |
| script                       | `skills/check-spec/scripts/find-design-docs.sh`               | `find-design-docs.sh`    | design/spec ファイルの走査・マッピング生成・環境変数エクスポート（Phase 1） |
| template                     | `skills/check-spec/templates/{en,ja}/check_spec_output.md`    | `check_spec_output.md`   | チェック結果レポートの出力フォーマット（EN / JA）                       |
| agent（連携）                  | `agents/front-matter-reviewer.md`                             | `front-matter-reviewer`  | front matter 検証（`impl-status` 等）を委譲                    |
| agent（連携・`--full`）        | `agents/spec-reviewer.md`                                     | `spec-reviewer`          | ドキュメント間整合性・品質レビューを委譲                            |

## 4.1. 入出力定義 `<OPTIONAL>`

### 入力

| 項目           | 種別   | 説明                                                                                       |
|--------------|------|------------------------------------------------------------------------------------------|
| `feature-name` | 引数（任意） | 対象機能名またはパス（例: `user-auth`、`auth/user-login`）。省略時は全 design 文書が対象           |
| `--full`     | オプション | 整合性チェックに加えて `spec-reviewer` による品質レビューを実施する                              |
| `SDD_LANG`   | 環境変数 | 出力言語（`en` / `ja`）。既定値は `en`                                                        |
| `SDD_SPECIFICATION_PATH` 等 | 環境変数 | ディレクトリパス解決（未設定時は `.sdd-config.json` → 既定値の順に解決）                        |

`find-design-docs.sh` が `$CLAUDE_ENV_FILE` へエクスポートする環境変数（後続の Claude フェーズが参照）：

```bash
export CHECK_SPEC_CACHE_DIR=".sdd/.cache/check-spec"        # キャッシュ出力先
export CHECK_SPEC_DESIGN_FILES=".../design_files.txt"      # design 文書一覧
export CHECK_SPEC_SPEC_FILES=".../spec_files.txt"          # spec 文書一覧
export CHECK_SPEC_MAPPING=".../file_mapping.json"          # design → spec → feature の対応
```

### 出力

`templates/${SDD_LANG:-en}/check_spec_output.md` に従うレポート。主要構成要素：

- チェック結果サマリー表（design ↔ 実装 / リテラル値の整合状況）
- 🔴 Critical（即座に対応が必要）
- 🟡 Warning（対応推奨、値ドリフトを含む）
- 🟢 Info（参考情報）
- 未実装機能 / 仕様書に未記載の実装
- 品質レビュー結果（`--full` オプション指定時のみ）

# 5. 用語集 `<OPTIONAL>`

| 用語             | 説明                                                                                          |
|----------------|---------------------------------------------------------------------------------------------|
| 乖離（drift）      | 技術設計書の記述と実装コードの実態が一致しない状態                                                    |
| リテラル値ドリフト  | 閾値・列挙値・CHECK 制約値が spec / design / 実装のいずれかの層で食い違う状態                        |
| 手動トリガー       | フックによる自動発火ではなく、開発者が明示的にスキルを呼び出す起動方式                                 |
| Schema Registry | `*_spec.md` 内の「値域・閾値レジストリ」表。リテラル値の権威的定義（`{value-id, value, unit, source-requirement-id, section}`） |
| 2 フェーズ実行     | 決定的なファイル走査を Shell スクリプトが担い（Phase 1）、判断・比較・報告を Claude が担う（Phase 2）構成（A-002） |
| Serena MCP     | シンボル解析による高精度な整合性チェックを可能にする任意の MCP 連携                                    |

# 6. 使用例 `<RECOMMENDED>`

```
/check-spec user-auth                # 特定機能の整合性チェックのみ（既定）
/check-spec auth/user-login          # 階層構造: auth ドメイン配下の user-login 機能
/check-spec auth                     # 階層構造: auth ドメイン全体
/check-spec task-management --full   # 整合性チェック + 品質レビュー
/check-spec --full                   # 全仕様書を対象に包括チェック
/check-spec                          # 引数なし: 全 design を対象（実行前に範囲確認）
```

# 7. 振る舞い図 `<OPTIONAL>`

```mermaid
sequenceDiagram
    participant Dev as 開発者
    participant Skill as check-spec スキル
    participant Script as find-design-docs.sh
    participant Claude
    participant FMR as front-matter-reviewer
    participant SR as spec-reviewer

    Dev ->> Skill: /check-spec [feature-name] [--full]
    Skill ->> Script: Phase 1: design/spec 走査
    Script -->> Skill: 環境変数（DESIGN_FILES / SPEC_FILES / MAPPING）
    Note over Skill,Claude: 引数なしの場合は範囲確認を挟む
    Skill ->> Claude: Phase 2: 整合性チェック開始
    Claude ->> Claude: design/spec からAPI・型・リテラル値を抽出
    Claude ->> Claude: 実装コードを検索し 3 層で比較
    Claude ->> FMR: front matter 検証を委譲
    FMR -->> Claude: impl-status 等の指摘
    opt --full 指定時
        Claude ->> SR: ドキュメント間整合性・品質レビュー
        SR -->> Claude: PRD↔spec↔design の指摘
    end
    Claude -->> Dev: 乖離レポート（Critical / Warning / Info）
```

# 8. 制約事項 `<OPTIONAL>`

- 本スキルは前提として、対象プロジェクトで `sdd-workflow` プラグインが有効化され、`.sdd/` ディレクトリ
  構造（sdd-init による初期化）が存在し、チェック対象の `*_design.md` が存在することを要する。
- 乖離の**検出・報告までを責務**とし、自動修正は行わない（子 PRD スコープ外）。
- ドキュメント間（PRD ↔ spec ↔ design）の整合性チェックは本スキル単体では行わず、`--full` 指定時に
  `spec-reviewer` へ委譲する（責務の分離）。
- Serena MCP が未設定の場合でも Grep / Glob によるテキストベース検索で動作するが、シンボル解析による
  高精度チェックは利用できない。

# 9. 原則との整合性 `<RECOMMENDED>`

| 原則ID | 原則名                          | 本仕様への適用内容                                                                        |
|-------|-------------------------------|------------------------------------------------------------------------------------|
| B-001 | Vibe Coding 防止                | 設計書を真実の源とし、実装との乖離を検出することで仕様駆動の開発サイクルを維持する               |
| A-002 | フックとスクリプトの責務分離        | ファイル走査を `find-design-docs.sh`（Phase 1）に委譲し、Claude は判断・比較・報告に専念（Phase 2） |
| B-002 | 多言語対応（EN/JA）の一貫性        | 出力テンプレートを `templates/{en,ja}/` の両方で提供し、`SDD_LANG` で切り替える              |
| D-002 | ファイル命名規則の厳守             | `_spec.md` / `_design.md` サフィックスを前提に対象文書を特定する                            |
