---
id: "prd-task-implementation-task-cleanup"
title: "タスククリーンアップ"
type: "prd"
status: "draft"
created: "2026-07-07"
updated: "2026-07-07"
depends-on: ["prd-task-implementation"]
tags: ["task-cleanup", "knowledge-persistence"]
category: "task-implementation"
priority: "medium"
risk: "medium"
---

# タスククリーンアップ 要求仕様書

## 概要

本ドキュメントは、タスク・実装機能群（親 PRD: [index.md](index.md)）のうち、
実装完了後にタスクログを整理する「タスククリーンアップ」機能に対する要求仕様書である。

タスククリーンアップは、タスクログ内の重要な設計決定を技術設計書（`*_design.md`）へ統合したうえで
task ディレクトリを削除し、実装中の設計知見が失われずに永続化される状態を保証する。

SysML 要求図の記法（要求タイプ・リスクレベル・検証方法・関係タイプ）の凡例は
[PRD_TEMPLATE.md](../../PRD_TEMPLATE.md) のセクション 1 を参照。

---

# 1. 要求一覧

## 1.1. ユースケース図

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    Developer((開発者))

    subgraph TaskCleanup["タスククリーンアップ"]
        ExtractDecisions([重要な設計決定を抽出する])
        MergeToDesign([技術設計書へ統合する])
        DeleteTaskDir([taskディレクトリを削除する])
    end

    Developer --- ExtractDecisions
    ExtractDecisions --> MergeToDesign --> DeleteTaskDir
```

## 1.2. 機能一覧（テキスト形式）

- タスククリーンアップ
    - 重要な設計決定の技術設計書への統合
    - 統合後の task ディレクトリ削除

---

# 2. 要求図（SysML Requirements Diagram）

要求 ID は本ファイル内スコープで採番する。本ファイルの FR_001 は、
[index.md](index.md) の UR_004（設計知見の永続化）から派生し、
同 DC_002（統合前削除の禁止）にトレースされる
（親 PRD の全体要求図を参照。本図には自ファイル内のノードのみを定義する）。

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram
    functionalRequirement TaskCleanup {
        id: FR_001
        text: "設計決定を設計書へ統合してからタスクログを削除する"
        risk: medium
        verifymethod: demonstration
    }
```

---

# 3. 要求の詳細説明

## 3.1. 機能要求

### FR_001: タスククリーンアップ

実装完了後、タスクログ内の重要な設計決定を対応する技術設計書（`*_design.md`）へ統合したうえで、
task ディレクトリを削除する。
[index.md](index.md) の UR_004 から派生。

**トリガー方式:** 手動（開発者による `/task-cleanup` スキル呼び出し）

**関連する親制約:**

- [index.md](index.md) の DC_002（統合前削除の禁止）: task ディレクトリの削除は、重要な設計決定の
  技術設計書への統合が完了した後にのみ許可すること。
  根拠は D-003 原則（ドキュメント永続性ルール）であり、task/ は一時ログとして扱い、
  設計知見は永続ドキュメントである `*_design.md` に集約する

**検証方法:** デモンストレーションによる検証

---

# 4. 前提条件

- 対象チケットの実装が完了しており、`task/{ticket-number}/` 配下にタスクログが存在すること
- 統合先となる技術設計書（`*_design.md`）が存在すること
- 対象プロジェクトで sdd-workflow プラグインが有効化され、`.sdd/` ディレクトリが初期化済みであること

---

# 5. スコープ外

以下は本 PRD のスコープ外とします：

- タスク分解・TDD 実装・チェックリスト検証そのもの（[task-breakdown.md](task-breakdown.md) /
  [implement.md](implement.md) / [run-checklist.md](run-checklist.md) で扱う）
- 技術設計書の新規生成（spec-design カテゴリで扱う。本機能は既存設計書への統合のみを行う）
- バージョン管理操作（コミット・PR 作成等はプロジェクト運用・他ツールに委ねる）
