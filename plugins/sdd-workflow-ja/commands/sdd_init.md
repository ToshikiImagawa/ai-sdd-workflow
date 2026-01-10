---
description: "現在のプロジェクトにAI-SDDワークフローを初期化する。CLAUDE.mdの設定とドキュメントテンプレートの生成を行う。"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# SDD Init - AI-SDDワークフロー初期化

現在のプロジェクトにAI-SDD（AI駆動仕様駆動開発）ワークフローを初期化します。

## このコマンドの機能

1. **CLAUDE.md設定**: プロジェクトの `CLAUDE.md` にAI-SDD指示を追加
2. **プロジェクト原則生成**: `.sdd/CONSTITUTION.md` を作成（存在しない場合）
3. **テンプレート生成**: `.sdd/` ディレクトリにドキュメントテンプレートを作成（存在しない場合）

## 前提条件

**実行前に必ず AI-SDD原則ドキュメントを読み込んでください。**

AI-SDD原則ドキュメントのパス（以下の順序で検索し、最初に見つかったファイルを使用）：
1. `.sdd/AI-SDD-PRINCIPLES.md`（プロジェクトルートから - プラグイン利用者向け）
2. `../AI-SDD-PRINCIPLES.md`（このファイルからの相対パス - プラグイン開発者向け）
3. `plugins/sdd-workflow-ja/AI-SDD-PRINCIPLES.md`（プロジェクトルートから - プラグイン開発者向け）

AI-SDDの原則を理解してください。

このコマンドはAI-SDD原則に従ってプロジェクトを初期化します。

### 設定ファイル（オプション）

プロジェクトルートに `.sdd-config.json` を作成することで、ディレクトリ名をカスタマイズできます。

設定ファイルの詳細は AI-SDD原則ドキュメントの「プロジェクト設定ファイル」セクションを参照してください。

**注意**: 初期化時にカスタムディレクトリ名を使用する場合は、先に `.sdd-config.json`
を作成してください。初期化後にディレクトリ構造とCLAUDE.mdの記載が設定値に基づいて生成されます。

### 使用するスキル

このコマンドは以下のスキルを使用します：

| スキル                             | 用途                                           |
|:--------------------------------|:---------------------------------------------|
| `sdd-workflow-ja:sdd-templates` | プロジェクト原則およびPRD、仕様書、設計書テンプレートを生成 |

## 実行フロー

```
1. 現在のプロジェクト状態を確認
   ├─ CLAUDE.md が存在するか？
   ├─ .sdd/ ディレクトリが存在するか？
   └─ .sdd/CONSTITUTION.md が存在するか？
   ↓
2. CLAUDE.md を設定
   ├─ CLAUDE.md が存在する場合: AI-SDD Instructionsセクションを追加
   └─ 存在しない場合: AI-SDD Instructionsを含む新規CLAUDE.mdを作成
   ↓
3. .sdd/ ディレクトリ構造を作成
   ├─ .sdd/requirement/
   ├─ .sdd/specification/
   └─ .sdd/task/
   ↓
4. AI-SDD原則ドキュメントをコピー
   ├─ プラグインルートのAI-SDD-PRINCIPLES.mdを読み込み（Read tool）
   └─ .sdd/AI-SDD-PRINCIPLES.md として保存（Write tool）
   ↓
5. プロジェクト原則を生成（存在しない場合）
   ├─ .sdd/CONSTITUTION.md が存在するか確認
   └─ 存在しない場合: sdd-workflow-ja:sdd-templates スキルを使用して生成
   ↓
6. 既存テンプレートを確認
   ├─ .sdd/PRD_TEMPLATE.md
   ├─ .sdd/SPECIFICATION_TEMPLATE.md
   └─ .sdd/DESIGN_DOC_TEMPLATE.md
   ↓
7. 不足しているテンプレートを生成
   └─ sdd-workflow-ja:sdd-templates スキルを使用して生成
```

## CLAUDE.md設定

### AI-SDD Instructionsセクション

`CLAUDE.md` に以下のセクションを追加します：

````markdown
## AI-SDD Instructions

このプロジェクトはAI-SDD（AI駆動仕様駆動開発）ワークフローに従います。

### ドキュメント操作

`.sdd/` ディレクトリ配下のファイルを操作する際は、`.sdd/AI-SDD-PRINCIPLES.md` を参照して、適切なAI-SDDワークフローへの準拠を確保してください。

**トリガー条件**:

- `.sdd/` 配下のファイルの読み込みまたは変更
- 新しい仕様書、設計書、要求仕様書の作成
- `.sdd/` のドキュメントを参照する機能の実装

### ディレクトリ構造

フラット構造と階層構造の両方をサポートします。

**フラット構造（小〜中規模プロジェクト向け）**:

    .sdd/
    ├── CONSTITUTION.md               # プロジェクト原則（最上位）
    ├── PRD_TEMPLATE.md               # このプロジェクト用のPRDテンプレート
    ├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート
    ├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート
    ├── requirement/                  # PRD（要求仕様書）
    │   └── {機能名}.md
    ├── specification/                # 仕様書と設計書
    │   ├── {機能名}_spec.md          # 抽象仕様書
    │   └── {機能名}_design.md        # 技術設計書
    └── task/                         # 一時的なタスクログ
        └── {チケット番号}/

**階層構造（中〜大規模プロジェクト向け）**:

    .sdd/
    ├── CONSTITUTION.md               # プロジェクト原則（最上位）
    ├── PRD_TEMPLATE.md               # このプロジェクト用のPRDテンプレート
    ├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート
    ├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート
    ├── requirement/                  # PRD（要求仕様書）
    │   ├── {機能名}.md               # トップレベル機能
    │   └── {親機能名}/               # 親機能ディレクトリ
    │       ├── index.md              # 親機能の概要・要求一覧
    │       └── {子機能名}.md         # 子機能の要求仕様
    ├── specification/                # 仕様書と設計書
    │   ├── {機能名}_spec.md          # トップレベル機能
    │   ├── {機能名}_design.md
    │   └── {親機能名}/               # 親機能ディレクトリ
    │       ├── index_spec.md         # 親機能の抽象仕様書
    │       ├── index_design.md       # 親機能の技術設計書
    │       ├── {子機能名}_spec.md    # 子機能の抽象仕様書
    │       └── {子機能名}_design.md  # 子機能の技術設計書
    └── task/                         # 一時的なタスクログ
        └── {チケット番号}/

### ファイル命名規則（重要）

**⚠️ requirement と specification でサフィックスの有無が異なります。混同しないでください。**

| ディレクトリ            | ファイル種別 | 命名パターン                               | 例                                         |
|:------------------|:-------|:-------------------------------------|:------------------------------------------|
| **requirement**   | 全ファイル  | `{名前}.md`（サフィックスなし）                  | `user-login.md`, `index.md`               |
| **specification** | 抽象仕様書  | `{名前}_spec.md`（`_spec` サフィックス必須）     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | 技術設計書  | `{名前}_design.md`（`_design` サフィックス必須） | `user-login_design.md`, `index_design.md` |

#### 命名パターン早見表

```
# ✅ 正しい命名
requirement/auth/index.md              # 親機能の概要（サフィックスなし）
requirement/auth/user-login.md         # 子機能の要求仕様（サフィックスなし）
specification/auth/index_spec.md       # 親機能の抽象仕様書（_spec 必須）
specification/auth/index_design.md     # 親機能の技術設計書（_design 必須）
specification/auth/user-login_spec.md  # 子機能の抽象仕様書（_spec 必須）
specification/auth/user-login_design.md # 子機能の技術設計書（_design 必須）

# ❌ 誤った命名（絶対に使用しないこと）
requirement/auth/index_spec.md         # requirement に _spec は不要
specification/auth/user-login.md       # specification には _spec/_design が必須
specification/auth/index.md            # specification には _spec/_design が必須
```

### ドキュメントリンク規約

ドキュメント内でのマークダウンリンクは以下の形式に従ってください：

| リンク先       | 形式                             | リンクテキスト   | 例                                                    |
|:-----------|:-------------------------------|:----------|:-----------------------------------------------------|
| **ファイル**   | `[ファイル名.md](パスまたはURL)`         | ファイル名を含める | `[user-login.md](../requirement/auth/user-login.md)` |
| **ディレクトリ** | `[ディレクトリ名](パスまたはURL/index.md)` | ディレクトリ名のみ | `[auth](../requirement/auth/index.md)`               |

この規約により、リンク先がファイルかディレクトリかが視覚的に判別しやすくなります。

````

### 配置ルール

1. **CLAUDE.md に既に "AI-SDD" セクションがある場合**: スキップ（初期化済み）
2. **CLAUDE.md が存在するが AI-SDD セクションがない場合**: セクションを末尾に追加
3. **CLAUDE.md が存在しない場合**: セクションを含む新規ファイルを作成

## プロジェクト原則生成

### プロジェクト原則とは

プロジェクト原則（CONSTITUTION.md）は、**すべての設計判断の基盤となる非交渉原則**を定義します。

| 特徴       | 説明                       |
|:---------|:-------------------------|
| **非交渉**  | 議論の余地がない。変更には慎重な検討が必要    |
| **永続的**  | プロジェクト全体で一貫して適用される       |
| **階層的**  | 上位原則が下位原則に優先する           |
| **検証可能** | 仕様書・設計書が原則に従っているか自動検証できる |

### 生成プロセス

1. `.sdd/CONSTITUTION.md` が存在するか確認
2. 存在しない場合、`sdd-workflow-ja:sdd-templates` スキルを使用して生成
3. プロジェクトコンテキスト（言語、フレームワーク、ドメイン）に基づいてカスタマイズ

### 原則の管理

初期化後の原則管理には `/constitution` コマンドを使用：

| サブコマンド     | 用途                   |
|:-----------|:---------------------|
| `validate` | 仕様書・設計書が原則に準拠しているか検証 |
| `add`      | 新しい原則を追加             |
| `sync`     | テンプレートを原則と同期         |

## テンプレート生成

### 生成するファイル

| ファイル               | パス                               | 用途            |
|:-------------------|:---------------------------------|:--------------|
| **プロジェクト原則**       | `.sdd/CONSTITUTION.md`           | 非交渉原則の定義      |
| **PRDテンプレート**      | `.sdd/PRD_TEMPLATE.md`           | SysML形式の要求仕様書 |
| **仕様書テンプレート**      | `.sdd/SPECIFICATION_TEMPLATE.md` | 抽象的なシステム仕様    |
| **設計書テンプレート**      | `.sdd/DESIGN_DOC_TEMPLATE.md`    | 技術設計書         |

### 生成プロセス

1. **既存テンプレートを確認**: テンプレートが既に存在する場合はスキップ
2. **プロジェクトコンテキストを分析**:
    - 使用されているプログラミング言語を検出
    - プロジェクト構造と規約を特定
    - 既存のドキュメントパターンを確認
3. **カスタマイズされたテンプレートを生成**:
    - `sdd-workflow-ja:sdd-templates` スキルを使用
    - プロジェクトの言語に合わせて型構文をカスタマイズ（TypeScript、Python、Goなど）
    - プロジェクトのドメインに合わせて例を調整

### テンプレートカスタマイズポイント

テンプレート生成時、プロジェクト分析に基づいてカスタマイズ：

| 項目           | カスタマイズ内容                                          |
|:-------------|:--------------------------------------------------|
| **型構文**      | プロジェクトの主要言語に合わせる（例：TypeScriptインターフェース、Python型ヒント） |
| **ディレクトリパス** | 例にプロジェクトの実際の構造を反映                                 |
| **ドメイン例**    | プロジェクトタイプに基づいた関連例を使用（Webアプリ、CLI、ライブラリなど）          |

## 初期化後の検証

初期化後、以下を検証：

1. **CLAUDE.md**: AI-SDD Instructionsセクションが含まれている
2. **ディレクトリ構造**:
    - `.sdd/requirement/` が存在する
    - `.sdd/specification/` が存在する
    - `.sdd/task/` が存在する
3. **プロジェクト原則**: `.sdd/CONSTITUTION.md` が存在する
4. **テンプレート**: 3つのテンプレートファイルすべてが `.sdd/` に存在する

## 出力

初期化成功時、以下を表示：

````markdown
## AI-SDD初期化完了

### CLAUDE.md

- [x] AI-SDD Instructionsセクションを追加

### ディレクトリ構造

- [x] .sdd/requirement/ を作成
- [x] .sdd/specification/ を作成
- [x] .sdd/task/ を作成

### プロジェクト原則

- [x] .sdd/CONSTITUTION.md を作成

### 生成されたテンプレート

- [x] .sdd/PRD_TEMPLATE.md
- [x] .sdd/SPECIFICATION_TEMPLATE.md
- [x] .sdd/DESIGN_DOC_TEMPLATE.md

### 次のステップ

1. `.sdd/CONSTITUTION.md` を確認し、プロジェクトの原則をカスタマイズ
2. 生成されたテンプレートを確認し、必要に応じてカスタマイズ
3. `/generate_prd` を使用して最初のPRDを作成
4. `/generate_spec` を使用してPRDから仕様書を作成
5. `/constitution validate` で原則準拠を検証
````
