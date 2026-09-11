# SDD Workflow

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)]()

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する統合 Claude Code プラグイン（多言語対応）。

[English README](README.md)

## 概要

このプラグインは Vibe Coding 問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのツールを提供します。`SDD_LANG`
設定による多言語対応。

## 対応環境

| 要件      | バージョン | 備考                        |
|:--------|:-----:|:--------------------------|
| macOS   |   ✅   | 完全サポート                    |
| Linux   |   ✅   | 完全サポート                    |
| Windows |   ❌   | 非対応（下記の代替案を参照）            |
| Python  | 3.7+  | フックスクリプトの実行に必要            |
| Claude Code | 2.1.199+ | 名前付きスキル引数（`arguments` frontmatter / `$name` 置換）に必要。旧バージョンでは `$name` は置換されず、スキルは引数文字列全体の解釈にフォールバックする |

### Windows の制限事項

このプラグインのフックは `python3` コマンドを bash 経由で実行しており、Windows のネイティブ環境では動作しません。

### Windows ユーザー向けの代替案

1. **WSL (Windows Subsystem for Linux) の使用**（推奨）
    - WSL2 をインストールし、Linux 環境内で Claude Code を実行
    - [WSL インストールガイド](https://learn.microsoft.com/ja-jp/windows/wsl/install)

2. **Git Bash の使用**
    - Git for Windows に含まれる Git Bash で実行可能な場合があります
    - [Git for Windows](https://gitforwindows.org/)

### Vibe Coding とは？

Vibe Coding は、曖昧な指示によって AI が数千もの未定義の要件を推測しなければならない状況で発生します。
このプラグインは、仕様を中心とした開発フローを提供することでこの問題を解決します。

## インストール

### 方法 1: マーケットプレイスからインストール（推奨）

Claude Code で以下を実行:

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

次にプラグインをインストール:

```
/plugin install sdd-workflow@ToshikiImagawa/ai-sdd-workflow
```

### 方法 2: GitHub からクローン

```bash
git clone https://github.com/ToshikiImagawa/ai-sdd-workflow.git ~/.claude/plugins/sdd-workflow
```

インストール後、Claude Code を再起動してください。

### 確認

Claude Code で `/plugin` コマンドを実行し、`sdd-workflow` が表示されることを確認してください。

## 言語設定

`.sdd-config.json` で言語を設定:

```json
{
  "lang": "ja"
}
```

対応言語: `en`（デフォルト）, `ja`

セッション開始時に、この設定から `SDD_LANG` 環境変数が自動的に設定されます。

## クイックスタート

### 1. プロジェクト初期化

**このプラグインを初めて使用するプロジェクトでは、`/sdd-init` を実行してください。**

```
/sdd-init
```

このコマンドは自動的に:

- プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
- `.sdd/` ルートディレクトリを作成。`requirement/`・`specification/`・`adr/`・`task/` の各サブディレクトリは
  事前には作成**されず**、最初のファイルが書き込まれた時点で自動的に作成されます
- PRD、仕様書、設計書、決定ログ（ADR）のテンプレートファイルを生成
- プロジェクトの `.gitignore` に `.sdd/.cache/`（カスタム root の場合は `${SDD_ROOT}/.cache/`）を追加。
  このディレクトリは生成物のためです。既存の行は書き換えられず、エントリが末尾に1回だけ追記されます
  （`.gitignore` が無い場合はこのエントリだけで新規作成）。再実行しても追加されず、無視されるのは
  `.cache/` のみで、`.sdd/` 配下のドキュメントは追跡対象のまま残ります

`/sdd-init` の再実行はいつでも安全です。既存のテンプレートファイルは上書きされずスキップされ、
`.gitignore` のエントリも重複しません。

`CONSTITUTION.md` は `/sdd-init` では生成**されません**。汎用テンプレートのコピーではなくプロジェクトに
合わせて作成するため、`/constitution init` を実行してください。

## 含まれるコンポーネント

### エージェント

| エージェント                    | 説明                                                            |
|:--------------------------|:--------------------------------------------------------------|
| `prd-reviewer`            | PRD の品質と CONSTITUTION.md 準拠をレビュー。違反に対する修正提案を生成                |
| `spec-reviewer`           | 仕様書・設計ドラフトの品質、CONSTITUTION.md 準拠、spec ↔ adr の決定整合をレビュー。違反に対する修正提案を生成 |
| `requirement-analyzer`    | SysML 要件図ベースの分析、要件のトレーサビリティと検証                                |
| `clarification-assistant` | 仕様明確化支援。9つのカテゴリで要件を分析し、統合提案を出力                                |
| `front-matter-reviewer`   | AI-SDD ドキュメントの YAML front matter を検証。フィールド形式、依存方向、ADR のファイル単位 supersede ポインタ、ID 一意性をチェック |
| `cross-prd-reviewer`      | 複数 PRD 間の整合性をレビュー。カテゴリ境界、用語、スタイル、原則参照網羅性をチェック                 |

### スキル（ユーザー起動可能）

| スキル                              | 説明                                                           |
|:---------------------------------|:-------------------------------------------------------------|
| `/sdd-init`                      | AI-SDD ワークフロー初期化。CLAUDE.md セットアップとテンプレート生成                   |
| `/generate-spec`                 | 入力から抽象仕様書と技術設計書を生成                                           |
| `/generate-prd`                  | ビジネス要件から完全な PRD（要求仕様書）を生成。ユースケース図・UR/FR/NFR 分析・SysML 要件図を含む   |
| `/check-spec`                    | 実装コードと抽象仕様書（spec）の整合性をチェックし、不整合を検出                            |
| `/task-cleanup`                  | 実装完了後の task/ ディレクトリをクリーンアップし、設計判断と却下した代替案を削除前に `adr/{feature-name}.md` へ統合 |
| `/render-adr-review`             | ADR決定ログを決定・理由・却下した代替案の軸で構造化した一時レビューHTMLとしてレンダリング              |
| `/task-breakdown`                | 技術設計ドラフトからタスクを独立にテスト可能な小タスクのリストに分解                          |
| `/clarify`                       | 仕様を9つのカテゴリでスキャンし、曖昧さを明確化するための質問を生成                           |
| `/implement`                     | TDD ベースの5フェーズ実装。TaskList で進捗を追跡し、tasks.md に自動マーク             |
| `/checklist`                     | 仕様書と計画から9カテゴリの品質チェックリストを構造化IDつきで自動生成                         |
| `/run-checklist`                 | チェックリスト項目をテスト、リンター、セキュリティスキャンで自動検証                           |
| `/constitution`                  | プロジェクトの非交渉可能な原則（constitution）を定義・管理                          |
| `/recommend-front-matter`        | 既存の AI-SDD ドキュメント（ADR決定ログを含む）をスキャンし、構造化メタデータのための YAML front matter 追加を推奨 |
| `/plan-refactor`                 | 既存機能のリファクタリング計画。実装を分析し、計画をチケット単位の設計ドラフトに記録                    |
| `/generate-usecase-diagram`      | ビジネス要件から Mermaid 形式のユースケース図を生成                               |
| `/analyze-requirements`          | ユースケース図やビジネス要件から UR/FR/NFR を抽出                               |
| `/generate-requirements-diagram` | 要求分析から Mermaid 形式の SysML 要件図を生成                              |
| `/finalize-prd`                  | ユースケース図、要求分析、要件図を統合して完全な PRD を作成                             |

### スキル（自動）

| スキル                       | 説明                                 |
|:--------------------------|:-----------------------------------|
| `vibe-detector`           | ユーザー入力を分析し、Vibe Coding（曖昧な指示）を自動検出 |
| `doc-consistency-checker` | ドキュメント間（PRD ↔ 仕様書 ↔ adr）の整合性を自動チェック   |

### フック

| フック             | トリガー         | 説明                                     |
|:----------------|:-------------|:---------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json` から設定を読み込み、環境変数を自動設定 |
| `user-prompt-submit` | UserPromptSubmit | ユーザープロンプト内の Vibe Coding 兆候（曖昧な指示）を検知し、明確化リマインダーを注入 |
| `pre-tool-use`  | PreToolUse (Write/Edit) | ファイル命名規則に違反する `.sdd/` ドキュメントへの書き込みを拒否し、実装ソースコード編集時に `CONSTITUTION.md` の原則を注入（セッションごとに1回） |
| `post-tool-use` | PostToolUse (Write/Edit) | `.sdd/` ドキュメントや対応する仕様書を持つソースファイルを編集した後、ドキュメント整合性チェックを促す（v4 の design doc しか対応しない場合は `adr/` への移行を案内する） |

**注**: フックはプラグインインストール時に自動的に有効化されます。追加の設定は不要です。

## 使用方法

### チケット番号について

v5.0.0 以降、技術設計ドラフトとタスクログは `task/{ticket-number}/` 配下に置かれるため、いくつかのスキルは
チケット番号を必要とします。渡し方はスキルごとに異なります:

| スキル                                       | チケット番号の渡し方      | 必須か                                          |
|:------------------------------------------|:----------------|:---------------------------------------------|
| `/generate-spec`                          | オプションのみ         | 必須 — 省略時は対話的に解決。`--ci` モードでは指定必須              |
| `/plan-refactor`                          | オプションのみ         | 必須 — 省略時は対話的に解決。`--ci` モードでは指定必須              |
| `/task-breakdown`                         | 第2位置引数、またはオプション | 必須 — フォールバックなし                               |
| `/implement`・`/checklist`・`/run-checklist` | 第2位置引数、またはオプション | 任意 — 省略時は feature 名がタスクディレクトリ名として使われる         |
| `/clarify`                                | 第2位置引数、またはオプション | 任意 — 省略時は PRD・spec・v4.x の設計書（あれば）で分析する      |
| `/task-cleanup`                           | 第1位置引数、またはオプション | 任意 — 省略時は `task/` 全体が対象                       |
| `/check-spec`                             | オプションのみ         | 任意 — 補助入力にする設計ドラフトを絞り込む（「整合性チェック」も参照）         |
| `/render-adr-review`                      | 第2位置引数、またはオプション | 任意 — 出力ファイル名に使う。省略時はソースファイルの機能名を使う           |

チケット番号をオプションで渡す箇所では、`--ticket <番号>`（スペース）と `--ticket=<番号>`（イコール）の
**どちらの書式も受理**されます。位置引数でも渡せるスキルでは、フラグ形式は位置引数のスロットを消費しないため、
`/task-breakdown user-auth --ticket=123` でも feature 名は `user-auth` に解決されます。

#### チケットトラッカーを使っていない場合

チケット番号は `task/` 配下の**ディレクトリ名**と front matter の `ticket` フィールドの値としてのみ使われます。
GitHub や JIRA などのトラッカーに対して検証されることはないため、安定した識別子であれば何でも使えます:

```
/generate-spec ユーザー認証機能 --ticket user-auth
/task-breakdown user-auth user-auth
/implement user-auth
```

最も簡単な運用は**feature 名をチケット番号として渡す**ことです。`/implement`・`/checklist`・`/run-checklist`
は省略時に feature 名を使うため、その機能の `task/` 配下のファイルが1つのディレクトリにまとまります。
ブランチ名や日付付きのスラッグ（`2026-09-10-user-auth`）でも同様に機能します。

実際のトラッカーを必要とするのは `/task-cleanup` の完了コメント投稿だけです。トラッカーを特定できない場合、
この手順は失敗せずスキップされたことが報告され、チケットと機能の対応は `adr/{feature-name}.md` の `ticket`
フィールドに残ります。

### コマンド使用例

#### PRD 生成

```
/generate-prd ユーザーがタスクを管理する機能。
ログインユーザーのみ利用可能。
```

#### 仕様書/設計書生成

```
/generate-spec ユーザー認証機能。メールアドレスとパスワードでのログイン・ログアウトをサポート。
```

#### 整合性チェック

```
/check-spec user-auth
/check-spec user-auth --ticket TICKET-123   # 補助入力にする設計ドラフトを1チケットに絞る
/check-spec user-auth --ticket=TICKET-123   # 同じ意味
/check-spec user-auth --full                # PRD <-> spec <-> adr と品質レビューも実施
```

`--ticket` は**どの** `task/{ticket-number}/design-draft.md` を補助入力として読むかを決めます。省略した場合も、
対応が一意に定まる範囲ではヘルパースクリプトが自分でドラフトを選び、他チケットの設計を混ぜるくらいなら
何も読まずに諦めます:

| 状況                                                        | 読み込まれるもの                                        |
|:----------------------------------------------------------|:------------------------------------------------|
| ドラフトが存在しない（実装完了後の正常な状態）                                   | 何も読まない。設計チェックは報告されない                            |
| `--ticket <番号>` を指定                                       | そのチケットのドラフトのみ                                   |
| ドラフトの front matter `depends-on` が対象 spec の ID（`spec-*`）を参照 | そのドラフト（他チケットが並行していても選ばれる）                        |
| プロジェクト全体でドラフトが1つだけ                                        | そのドラフト                                          |
| 複数のドラフトがあり、どれもこの実行に紐付けられない                                | **どれも読まない**。スキップしたドラフトが報告されるので `--ticket` で再実行する |

つまり `--ticket` が必須なのは最後の行のケースだけです。各ドラフトの front matter に
`depends-on: ["spec-{feature}"]` を書いておけば、この場合も回避できます。

`--full` を付けると追加で `spec-reviewer` エージェントによる**ドキュメントレベル**のレビューが走ります。
内容は PRD ↔ 仕様書のトレーサビリティ、spec ↔ adr の決定整合（現行＝最新かつ未覆の決定が仕様書と一致するか、
仕様書が覆された決定に依拠していないか、仕様書の振る舞いの背後にある決定がそもそも記録されているか）、
CONSTITUTION.md 準拠、必須セクションの網羅性、曖昧な記述の検出、SysML 要求 ID の妥当性です。
決定ログがまだ無い機能は**該当なし**として報告され、これは指摘でもなく「整合」でもありません。
`adr/` は追記専用なので、修正は仕様書側か、`Supersedes` を持つ新規エントリの追記のどちらかで行い、
既存エントリを編集することはありません。

#### タスク分解

```
/task-breakdown task-management TICKET-123
```

#### タスククリーンアップ

```
/task-cleanup TICKET-123
```

#### ADRレビューHTMLレンダリング

```
/render-adr-review adr/user-auth.md
```

決定ログを `.sdd/.cache/render-adr-review/` 配下の一時HTMLとして、決定・理由・却下した代替案の軸で
構造化してレンダリングする。生成物はスクラッチファイルであり、コミットされない。

#### 仕様明確化

```
/clarify user-auth
```

9つのカテゴリで仕様をスキャンし、最大5つの明確化質問を生成します。

#### TDD ベース実装

```
/implement user-auth TICKET-123
```

5つのフェーズ（Setup→Tests→Core→Integration→Polish）で実装を実行し、tasks.md に進捗を自動マークします。

#### 品質チェックリスト生成

```
/checklist user-auth TICKET-123
```

仕様書と設計書から9カテゴリの品質チェックリストを自動生成します。

#### 自動チェックリスト検証

```
/run-checklist user-auth TICKET-123
/run-checklist user-auth TICKET-123 --priority P1  # P1 項目のみ実行
/run-checklist user-auth TICKET-123 --category testing  # テストカテゴリのみ実行
```

検証コマンド（テスト、リンター、セキュリティスキャン）を自動実行し、結果をチェックリストに記録します。

#### プロジェクト憲章管理

```
/constitution show                    # 現在の憲章を表示
/constitution add "Library-First"     # 新しい原則を追加
/constitution validate                # 仕様/設計が憲章に準拠しているか検証
```

プロジェクトの非交渉可能な原則を定義・管理します。最初に `/constitution init` で憲章ファイルを作成してください。

### 完全なワークフロー例

新しい「ユーザー認証」機能を実装する完全なワークフローです。

#### Step 1: プロジェクト初期化（初回のみ）

```
/sdd-init
```

`.sdd/` ルートとドキュメントテンプレートを作成します。プロジェクト憲章（`CONSTITUTION.md`）は `/sdd-init` では
作成されないため、続けて `/constitution init` を実行してください。

#### Step 2: 要求仕様書（PRD）の作成

```
/generate-prd ユーザー認証機能。メールアドレスとパスワードでのログイン・ログアウト。
セッション管理とパスワードリセット機能を含む。
```

→ `.sdd/requirement/user-auth.md` が生成されます。

#### Step 3: 仕様書と設計書の生成

```
/generate-spec user-auth --ticket TICKET-123
```

→ `.sdd/specification/user-auth_spec.md` が生成され、`.sdd/task/TICKET-123/design-draft.md` に
一時的な設計ドラフトも生成されます。

#### Step 4: 仕様の明確化

```
/clarify user-auth
```

9つのカテゴリで仕様をスキャンし、不明確な点について質問を生成します。回答は仕様書に自動統合されます。

#### Step 5: タスク分解

```
/task-breakdown user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/tasks.md` にタスクリストが生成されます。

#### Step 6: 品質チェックリスト生成

```
/checklist user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/checklist.md` に9カテゴリの品質チェックリストが生成されます。

#### Step 7: TDD ベース実装

```
/implement user-auth TICKET-123
```

5つのフェーズ（Setup→Tests→Core→Integration→Polish）で進行し、進捗を自動マークします。

#### Step 8: チェックリスト項目の検証

```
/run-checklist user-auth TICKET-123
```

テスト、リンター、セキュリティスキャンを自動実行し、チェックリスト項目を検証します。検証レポートを生成します。

#### Step 9: 整合性チェック

```
/check-spec user-auth
```

実装と仕様書の整合性を検証し、不整合を報告します。

#### Step 10: タスククリーンアップ

```
/task-cleanup TICKET-123
```

`task/` 配下の一時ファイル（`design-draft.md` を含む）をクリーンアップし、重要な設計判断を
`adr/{feature-name}.md`（追記専用）に統合してから削除します。

## v2.x からの移行

### v3.0.0 の破壊的変更

1. **2つのプラグインを1つに統合**: `sdd-workflow-ja` と `sdd-workflow` は `SDD_LANG` による多言語対応を持つ単一の
   `sdd-workflow` プラグインに統合
2. **コマンドをスキルに変換**: 11のコマンドすべてがハイフン区切りの名前を持つスキルに移行
3. **コマンド名の変更**: アンダースコアをハイフンに置換（例: `/sdd_init` → `/sdd-init`）

### コマンド名の移行

| 旧 (v2.x)          | 新 (v3.0.0)        |
|:------------------|:------------------|
| `/sdd_init`       | `/sdd-init`       |
| `/generate_spec`  | `/generate-spec`  |
| `/generate_prd`   | `/generate-prd`   |
| `/check_spec`     | `/check-spec`     |
| `/task_breakdown` | `/task-breakdown` |
| `/task_cleanup`   | `/task-cleanup`   |
| `/sdd_migrate`    | `/sdd-migrate`    |
| `/implement`      | `/implement`      |
| `/clarify`        | `/clarify`        |
| `/constitution`   | `/constitution`   |
| `/checklist`      | `/checklist`      |

### 移行手順

1. `sdd-workflow-ja` を使用している場合、アンインストールして `sdd-workflow` をインストール
2. 日本語サポートのために `.sdd-config.json` に `"lang": "ja"` を設定
3. 自動化スクリプトを新しいコマンド名（アンダースコアからハイフン）に更新

## v4.x からの移行

### v5.0.0 の破壊的変更

1. **`specification/{feature-name}_design.md` は永続ドキュメントではなくなりました。** 技術設計書はまず
   `task/{ticket-number}/design-draft.md` の一時ドラフトとして作成され、`task/` の他のファイルと同様、
   実装完了後に削除されます
2. **新しい `adr/` ディレクトリを追加。** 決定・その理由・却下した代替案のみが `adr/{feature-name}.md`
   （追記専用）に永続化されます
3. **`/generate-spec` にチケット番号が必要になりました。** 設計ドラフトのパスが `specification/` ではなく
   `task/{ticket-number}/` 配下になったため、`--ticket <番号>`（または `--ticket=<番号>`）を指定するか、
   対話的に解決してください
4. **`/check-spec` の比較基準が設計書から仕様書に変わりました。** `specification/` 配下の仕様書が第一級の
   比較基準となり、設計ドラフトは仕様書で表現できない情報（モジュール構成・技術スタック）を補う**任意の
   補助入力**としてのみ使われます。実装完了後にドラフトが存在しないのは正常な状態であり、不整合として
   報告されることはありません
5. **`/plan-refactor` の Case A / Case B 判定が仕様書基準になり、計画は設計ドラフトに書かれます。**
   以前は `specification/{feature-name}_design.md` の有無で判定していましたが、**仕様書**の有無
   （`_spec` サフィックスの有無どちらでも照合）で判定するようになりました。リファクタリング計画は
   `task/{ticket-number}/design-draft.md` に書かれ、リバースエンジニアリングした仕様書は従来どおり
   `specification/` 配下に永続化されます
6. **`/plan-refactor` にチケット番号を渡すようになりました**（`--ticket <番号>` または `--ticket=<番号>`。
   省略時は対話的に解決、`--ci` モードでは指定必須）。設計ドラフトのパスがチケット単位になったためです
7. **`/task-breakdown` にチケット番号が必須になりました。** 読み込む設計ドラフトと書き出す `tasks.md` の
   どちらも `task/{ticket-number}/` 配下にあるためです。`tasks.md` は常に
   `task/{ticket-number}/tasks.md` に書かれ、従来の `task/{feature}/tasks.md` へのフォールバックは
   廃止されました
8. **`doc-consistency-checker` の対象が PRD ↔ spec ↔ design から PRD ↔ spec ↔ adr に変わりました**

### 既存の `*_design.md` を `adr/` へ抜粋する手順

この変更より前に永続化された `specification/{feature-name}_design.md` がある場合、決定履歴を
`adr/{feature-name}.md` へ抜粋してください。

**この移行は急ぐ必要はありません。** 既存の `specification/*_design.md` は**引き続き有効**です。命名規則
フックはこれらを受理し、技術設計を読むスキルはこれらを**補助入力**として読み取ります
（不在であることも同様に正常です）。違反として報告されることも、削除を促されることもありません。
新規に作成しないことだけを守ってください — 新しい技術設計は `task/{ticket-number}/design-draft.md` に置きます。

該当ファイルが存在する場合、`session-start` フックが `.sdd/MIGRATION_PENDING.md` を書き出し、対象ファイル
（パス順に先頭10件と、残りの件数）を一覧化してこの節を参照するよう案内します。この一覧は
**`.sdd/UPDATE_REQUIRED.md` とは独立**しています。`UPDATE_REQUIRED.md` は `CLAUDE.md` が古いことだけを
報告するファイルで、`/sdd-init` を実行すると削除されますが、`MIGRATION_PENDING.md` はそのまま残ります。
該当ファイルが1件でも残っている限りセッション開始ごとに書き直され、0件になると自動的に削除されるため、
一覧が消えることなく自分のペースで移行を進められます。生成ファイルなので、直接編集しても次のセッションで
上書きされます。

1. `.sdd-config.json` で `directories.adr` にカスタム名を使用する場合は移行前に設定する
   （デフォルトは `adr`）。その後 `/sdd-init` を再実行して、追記専用のエントリ形式を説明する
   `ADR_TEMPLATE.md` を取得する（既存ファイルは上書きされないため、再実行はいつでも安全）。
   ただし `/sdd-init` は `adr/` ディレクトリ自体を作成**しません** — `requirement/`・`specification/`・
   `task/` と同様に、最初のファイルが書き込まれた時点で作成されます
2. **各 `*_design.md` から設計判断を特定する** — 技術・アーキテクチャ・アプローチをなぜ選んだかを説明している節
3. **`adr/{feature-name}.md` を作成する**（`specification/` 配下のパスに対応させる。例:
   `specification/auth/user-login_design.md` → `adr/auth/user-login.md`）。
   `shared/references/front_matter_reference.md` に定義された `type: "adr"` の front matter
   フィールド（`id`、`type`、`title`、`status`、`created`、`updated`、`sdd-phase`、`depends-on`、
   分かる場合は `ticket`）を設定する。決定は事後に記録するものなので `status` は `"approved"` とする。
   front matter の `supersedes`/`superseded-by` は書かない — これらは決定ログ**ファイル全体**の引退
   （機能のリネーム・分割・統合）を表すもので、エントリ間の覆しを表すものではない
4. **決定ごとに1エントリを**ファイル末尾に `##` ブロックとして追記する。エントリの形式は固定:
   - 見出し `## YYYY-MM-DD {決定のタイトル}` — 決定が確定した日付
   - `- **Decision**:` 決めたこと
   - `- **Rationale**:` なぜそれを選んだか。選択を強制した制約を含める
   - `- **Rejected alternatives**:` 検討して却下した代替案とその理由。無い場合は `None considered`
     と書く（捏造しない）
   - `- **Supersedes**:` **同一ファイル内**の過去エントリを覆すときのみ記載。対象エントリ見出しへの
     リンクと、何が変わったかを1行。覆された旧エントリは編集しない（`adr/` は追記専用）
5. **持ち込まないもの**: 実装手順、理由付けのない技術スタックの列挙、現在のコードに既に反映されている内容 —
   *why* のみを残し、*how* / *what* は持ち込まない
6. **決定を `adr/` に取り込んだ後に旧 `*_design.md` を削除する場合**は、先に残存参照を自分で洗い出す。
   `/check-spec` も `doc-consistency-checker` も Markdown リンクの健全性は検査しないため、
   リンク切れは**報告されません**。検索は2本必要です。本文中のリンクは**パス**を保持しますが、
   front matter の `depends-on` はドキュメントの **`id`** を保持するため、同じファイルが両者で
   同じ書き方で現れることはありません:

   ```bash
   # 1. パス参照: 本文中のリンク・散文・コードブロック
   grep -rn "_design\.md" .sdd/ --exclude-dir=.cache --exclude=AI-SDD-PRINCIPLES.md

   # 2. ID 参照: `depends-on` のエントリと、そのドキュメント自身の `id`
   #    フラット: design-{feature-name}   階層: design-{parent-feature}-{feature-name}
   grep -rn "design-user-auth" .sdd/ --exclude-dir=.cache --exclude=AI-SDD-PRINCIPLES.md
   ```

   root をカスタマイズしている場合は `.sdd` を、移行対象の機能名に応じて `user-auth` をそれぞれ
   置き換える。除外指定は2つとも必要です。`.sdd/.cache/` はセッション開始ごとに再生成され、
   `.sdd/AI-SDD-PRINCIPLES.md` は `session-start` フックがインストール済みプラグインから上書き同期する
   ためで、どちらも編集しても無意味であり、ヒットするのはプラグイン自身の説明文であってあなたの
   ドキュメントへの参照ではありません。

   残ったヒットのうち、削除したファイルを指しているものを更新する。本文中のリンクは
   `adr/{feature-name}.md` へのリンクに、`depends-on` のエントリはその ADR の `id`
   （`adr-{feature-name}`）または現行ドラフトの `id`（`design-{ticket-number}`）に、その依存が実際に
   何を意味していたかに応じて書き換える。意味を失った参照は削除する。`*_design.md` という規約を散文で
   言及しているだけのヒットは参照ではないので何もしなくてよい。旧ファイルをそのまま残すことも妥当な
   選択で（上記の注記を参照）、その場合はどちらの検索結果にも対応は不要です

完成した決定ログは `/render-adr-review adr/{feature-name}.md` で決定 / 理由 / 却下した代替案の軸に構造化して
読み返せます。

`adr/` のフィールド・フォーマットの全体は `AI-SDD-PRINCIPLES.md` の「Architecture Decision Record」節を
参照してください。

## 既知の制約

- **`adr/` と実装の乖離は自動検出されません。** `/check-spec` は実装を抽象仕様と突き合わせ、`--full` は
  さらに文書レベルの `PRD ↔ spec ↔ adr` レビューを行いますが、`adr/` のエントリを読んでコードが依然その決定に
  従っているかを検査するチェックはありません。記録済みの決定を実装が変えたときは決定ログを人手でレビューし
  （`/render-adr-review adr/{feature-name}.md` が役立ちます）、覆しは旧エントリを編集せず `Supersedes` 付きの
  **新規エントリ**として記録してください。
- **Markdown リンクの健全性は検証されません。** `/check-spec` も `doc-consistency-checker` もリンク切れを
  報告しないため、ドキュメントを削除・改名した後は自分で残存参照を探してください
  （「既存の `*_design.md` を `adr/` へ抜粋する手順」の `grep` を参照）。

## フックについて

このプラグインはセッション開始時に `.sdd-config.json` を自動的に読み込み、環境変数を設定します。
**フックはプラグインインストール時に自動的に有効化されます。追加の設定は不要です。**

### フックの動作

| フック             | トリガー         | 説明                                   |
|:----------------|:-------------|:-------------------------------------|
| `session-start` | SessionStart | `.sdd-config.json` から設定を読み込み、環境変数を設定 |
| `user-prompt-submit` | UserPromptSubmit | ユーザープロンプト内の Vibe Coding 兆候（曖昧な指示）を検知し、明確化リマインダーを注入 |
| `pre-tool-use`  | PreToolUse (Write/Edit) | ファイル命名規則に違反する `.sdd/` ドキュメントへの書き込みを拒否し、実装ソースコード編集時に `CONSTITUTION.md` の原則を注入（セッションごとに1回） |
| `post-tool-use` | PostToolUse (Write/Edit) | `.sdd/` ドキュメントや対応する仕様書を持つソースファイルを編集した後、ドキュメント整合性チェックを促す（v4 の design doc しか対応しない場合は `adr/` への移行を案内する） |

### 設定される環境変数

セッション開始時に以下の環境変数が自動的に設定されます:

| 環境変数                     | デフォルト                | 説明            |
|:-------------------------|:---------------------|:--------------|
| `SDD_ROOT`               | `.sdd`               | ルートディレクトリ     |
| `SDD_LANG`               | `en`                 | 言語設定          |
| `SDD_REQUIREMENT_DIR`    | `requirement`        | 要求仕様書ディレクトリ   |
| `SDD_SPECIFICATION_DIR`  | `specification`      | 仕様書ディレクトリ     |
| `SDD_ADR_DIR`            | `adr`                | 決定ログ（ADR）ディレクトリ |
| `SDD_TASK_DIR`           | `task`               | タスクログディレクトリ   |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | 要求仕様書フルパス     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書フルパス       |
| `SDD_ADR_PATH`           | `.sdd/adr`           | 決定ログ（ADR）フルパス |
| `SDD_TASK_PATH`          | `.sdd/task`          | タスクログフルパス     |
| `SDD_INDEX`              | `on`                 | ドキュメントインデックスが有効（`index: true`、デフォルト）な間は `on` に設定される。`index` が `false` の場合は設定されず、スキルはこれによりインデックス高速パスが使えないことを判定する |

### フックのデバッグ

フックの登録状態を確認するには:

```bash
claude --debug
```

## ツール権限

このプラグインの各スキルは front matter に `allowed-tools` を宣言しています。このフィールドは
**ツール権限の事前承認**、つまり「スキルがユーザーに尋ねずに実行できるツール呼び出し」の宣言です。**制限ではありません** —
すべてのツールは引き続き呼び出し可能で、事前承認されていない操作は通常の権限確認にフォールバックするだけです。

このプラグインは事前承認の範囲を意図的に狭く保っています。ベアな `Bash` を事前承認しているスキルは1つも無いため、
任意のシェルコマンドを無確認で実行することはできず、書き込みの事前承認もドキュメントと決まったセットアップファイルの
範囲に限られます:

| 操作                                                                             | 事前承認される範囲                                                          | 挙動                       |
|:---------------------------------------------------------------------------------|:----------------------------------------------------------------------------|:---------------------------|
| AI-SDD ドキュメントへの書き込み                                                  | `Edit(.sdd/**)`                                                             | 確認なしで適用             |
| `/sdd-init` / `/constitution` / `/recommend-front-matter` のセットアップファイル | `Edit(CLAUDE.md)`, `Edit(.sdd-config.json)`, `Edit(.claude/rules/**)`       | 確認なしで適用             |
| 同梱ヘルパースクリプトの実行（スクリプトごとに固定パス1本。下記の注意点を参照）   | `Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/<script>.py" *)` | 確認なしで適用             |
| それ以外すべて                                                                   | 事前承認しない                                                              | Claude Code が確認を求める |

「それ以外すべて」には、上記パス外への書き込み、任意のシェルコマンド、削除コマンド `git rm` / `rm`、
直接実行するテスト・リンターが含まれます。`/implement` と `/task-cleanup` は `Bash` を**一切事前承認していません**。
そのため `/task-cleanup` の `git ls-files` と `git rm` / `rm` による削除を含め、実行するコマンドごとに確認が入ります。

### プロジェクト側のコマンドを実行する事前承認済みスクリプト

「同梱ヘルパースクリプトの実行」の行には注意が必要です。これらのスクリプトのうち1本は自己完結していません。
`/run-checklist` は次を事前承認しています:

```
Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" *)
```

そしてこのスクリプトは、**プロジェクト側のテスト・リンター・型チェック・監査コマンド**を `subprocess` で
自分で実行します。追加の確認は入りません。マニフェストファイル（`package.json`・`pyproject.toml`・
`Cargo.toml`・`go.mod`・`setup.py`・`requirements.txt`・`Gemfile`、またはマニフェストが1つも無い場合は
`test_*.py` / `*_test.py` を含む `tests/`・`test/` ディレクトリ）から
プロジェクト種別を判定し、固定表の中から利用可能な最初のコマンドを実行します:

| プロジェクト種別 | 実行されうるコマンド                                                                       |
|:----------|:---------------------------------------------------------------------------------|
| Node      | `npm test`、`npx eslint .` / `eslint .`、`npx tsc --noEmit` / `tsc --noEmit`、`npm audit` |
| Python    | `pytest`、`ruff check .`、`mypy .`、`pip-audit` / `safety check`                     |
| Rust      | `cargo test`、`cargo clippy`、`cargo audit`                                        |
| Go        | `go test ./...`、`golangci-lint run`、`govulncheck ./...`                           |
| Ruby      | `bundle exec rspec`、`bundle exec rubocop`、`bundle exec bundler-audit`             |

したがってラッパーを一度承認すると、その実行の間はこれらのコマンドが動きます。歯止めは2点です。コマンドの出所は
上の表**だけ**であり、`checklist.md` の項目に書かれた検証コマンドは実行されず手動検証の指示として記録される
（`allowed-tools` が承認しているのはスクリプトであってベアな `Bash` ではないため）こと、そして各コマンドは
300秒で打ち切られることです。

コマンドごとに確認したい場合は `/run-checklist` を使わず、テスト・リンター・監査コマンドを自分で実行して
`task/{ticket-number}/checklist.md` の項目を手でチェックしてください。

同梱ヘルパースクリプト10本（`find-spec-docs.py`・`validate-files.py`・`prepare-prd.py`・`prepare-spec.py`・
`find-implementation-files.py`・`scan-existing-docs.py`・`scan-documents.py`・`run-verification.py`・
`init-structure.py`・`update-claude-md.py`）のうち、別プロセスを起動するのは `run-verification.py` だけです。

### 権限確認を減らす

確認を減らしたい場合は、プロジェクトの `.claude/settings.json`（またはユーザーの `~/.claude/settings.json`）で
自分で権限を付与してください:

```json
{
  "permissions": {
    "allow": [
      "Edit(.sdd/**)",
      "Bash(npm test:*)",
      "Bash(git ls-files:*)",
      "Bash(git rm:*)",
      "Bash(rm:*)"
    ]
  }
}
```

最後の3つは `/task-cleanup` の step 9 に対応します。step 9 は `git ls-files` で追跡状態を判定し、追跡されて
いれば `git rm`、未追跡なら `rm` で削除します。`Bash(rm:*)` は**あらゆる** `rm` を許可するため、それが許容
できる場合にのみ追加してください。

**`Write(<path>)` ではなく `Edit(<path>)` を使ってください。** `Write(<path>)` はファイル権限チェックにマッチしません。
`Edit(<path>)` ルールは Write を含む**すべてのファイル編集ツール**をカバーします。

### カスタム SDD root の場合

`.sdd-config.json` の `root` を `.sdd` 以外に設定している場合、プラグインの `Edit(.sdd/**)`
事前承認はドキュメントにマッチしないため、書き込みのたびに権限確認が入ります。`allowed-tools` では `${SDD_ROOT}`
を参照できないため（展開されるのは `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PROJECT_DIR}` のみ）、
自分の root に合わせたルールを `.claude/settings.json` に追加してください:

```json
{
  "permissions": {
    "allow": [
      "Edit(docs/sdd/**)"
    ]
  }
}
```

## Serena MCP 連携（オプション）

[Serena](https://github.com/oraios/serena) MCP を設定すると、セマンティックコード分析による機能強化が可能です。

### Serena とは？

Serena は LSP（Language Server Protocol）ベースのセマンティックコード分析ツールで、30以上のプログラミング言語をサポートしています。
シンボルレベルのコード検索と分析が可能です。

### 設定

プロジェクトの `.mcp.json` に以下を追加:

```json
{
  "mcpServers": {
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        ".",
        "--enable-web-dashboard",
        "false"
      ]
    }
  }
}
```

### 強化される機能

| スキル               | Serena 連携時の強化内容                 |
|:------------------|:--------------------------------|
| `/generate-spec`  | 既存コードの API/型定義を参照して一貫性のある仕様生成   |
| `/check-spec`     | シンボルベース検索による高精度な API 実装とシグネチャ検証 |
| `/task-breakdown` | 変更影響範囲を分析して正確なタスク依存関係をマッピング     |

### Serena なしの場合

すべての機能は Serena なしでも動作します。分析にはテキストベース検索（Grep/Glob）が使用され、言語に依存しません。

## AI-SDD 開発フロー

```
仕様化 → 計画 → タスク → 実装 & レビュー
```

### 推奨ディレクトリ構造

フラット構造と階層構造の両方をサポートしています。

#### フラット構造（小〜中規模プロジェクト向け）

```
.sdd/
├── CONSTITUTION.md               # プロジェクト憲章（最上位）
├── PRD_TEMPLATE.md               # PRD テンプレート（オプション）
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（オプション）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（オプション）
├── ADR_TEMPLATE.md               # 決定ログ（ADR）テンプレート（オプション）
├── requirement/                  # PRD（要求仕様書）
│   └── {feature-name}.md
├── specification/                # 永続的な知識資産
│   └── {feature-name}_spec.md    # 抽象仕様書
├── adr/                          # 永続的な決定ログ
│   └── {feature-name}.md         # 決定と理由（追記専用）
└── task/                         # 一時的なタスクログ（実装後に削除）
    └── {ticket-number}/
        └── design-draft.md       # 技術設計ドラフト（実装後に削除）
```

#### 階層構造（中〜大規模プロジェクト向け）

```
.sdd/
├── CONSTITUTION.md               # プロジェクト憲章（最上位）
├── PRD_TEMPLATE.md               # PRD テンプレート（オプション）
├── SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート（オプション）
├── DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート（オプション）
├── ADR_TEMPLATE.md               # 決定ログ（ADR）テンプレート（オプション）
├── requirement/                  # PRD（要求仕様書）
│   ├── {feature-name}.md         # トップレベル機能（フラット構造と下位互換）
│   └── {parent-feature}/         # 親機能ディレクトリ
│       ├── index.md              # 親機能の概要と要件リスト
│       └── {child-feature}.md    # 子機能の要件
├── specification/                # 永続的な知識資産
│   ├── {feature-name}_spec.md    # トップレベル機能（フラット構造と下位互換）
│   └── {parent-feature}/         # 親機能ディレクトリ
│       ├── index_spec.md         # 親機能の抽象仕様書
│       └── {child-feature}_spec.md   # 子機能の抽象仕様書
├── adr/                          # 永続的な決定ログ
│   ├── {feature-name}.md         # トップレベル機能（フラット構造と下位互換）
│   └── {parent-feature}/         # 親機能ディレクトリ
│       ├── index.md              # 親機能の決定ログ
│       └── {child-feature}.md    # 子機能の決定ログ
└── task/                         # 一時的なタスクログ（実装後に削除）
    └── {ticket-number}/
        └── design-draft.md       # 技術設計ドラフト（実装後に削除）
```

#### ドキュメント依存関係

```
CONSTITUTION.md → requirement/ → *_spec.md → task/{ticket-number}/design-draft.md → 実装
```

`adr/{feature-name}.md` は、`design-draft.md` が削除される前に抜粋された決定・理由・却下した
代替案を永続化します（追記専用。既存の `*_design.md` を移行する場合は
[v4.x からの移行](#v4x-からの移行) を参照）。

すべてのドキュメントは `CONSTITUTION.md` のプロジェクト原則に従って作成されます。

**階層構造の使用例**:

```
/generate-prd auth/user-login   # auth ドメイン下に user-login PRD を生成
/generate-spec auth/user-login  # auth ドメイン下に仕様を生成
/check-spec auth                # auth ドメイン全体の整合性をチェック
```

### プロジェクト設定ファイル

プロジェクトルートに `.sdd-config.json` を配置して、ディレクトリ名と言語をカスタマイズできます。

```json
{
  "root": ".sdd",
  "lang": "en",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "adr": "adr",
    "task": "task"
  },
  "index": true,
  "naming": {
    "ignore_patterns": ["*_test.md"]
  }
}
```

| 設定                          | デフォルト           | 説明                                                                          |
|:----------------------------|:----------------|:----------------------------------------------------------------------------|
| `root`                      | `.sdd`          | ルートディレクトリ                                                                   |
| `lang`                      | `en`            | 言語（`en` または `ja`）                                                           |
| `directories.requirement`   | `requirement`   | PRD（要求仕様書）ディレクトリ                                                            |
| `directories.specification` | `specification` | 仕様書/設計書ディレクトリ                                                               |
| `directories.adr`           | `adr`           | ADR（決定ログ）ディレクトリ                                                            |
| `directories.task`          | `task`          | 一時タスクログディレクトリ                                                               |
| `index`                     | `true`          | 真偽値。セッション開始時に `.sdd` ドキュメントの圧縮インデックス（SQLite → `index.md`）を構築しトークンを削減する。`false` で無効化。 |
| `naming.ignore_patterns`    | `[]`            | ファイル名（basename）に対して照合する glob パターン（`fnmatch` 形式）。マッチしたファイルは `requirement`/`specification` の命名規則チェックをスキップする（例: テスト用ファイルの `*_test.md`）。 |

**注**:

- 設定ファイルが存在しない場合、デフォルト値が使用されます
- 部分的な設定もサポートされています（未指定の項目はデフォルト値を使用）

## プラグイン構造

```
sdd-workflow/
├── .claude-plugin/
│   └── plugin.json                # プラグインマニフェスト
├── agents/
│   ├── prd-reviewer.md            # PRDレビュー・CONSTITUTION準拠チェックエージェント
│   ├── spec-reviewer.md           # 仕様書レビューエージェント
│   ├── requirement-analyzer.md    # 要求分析エージェント
│   ├── clarification-assistant.md # 仕様明確化アシスタント
│   ├── front-matter-reviewer.md   # YAML front matter検証エージェント
│   └── cross-prd-reviewer.md      # PRD横断整合レビューエージェント
├── shared/                        # スキル・エージェント共通のサポートファイル
│   ├── references/                # 共通参照ドキュメント
│   │   ├── mermaid_notation_rules.md          # Mermaid記法ガイド
│   │   ├── usecase_diagram_guide.md           # ユースケース図ガイド
│   │   ├── requirements_diagram_components.md # SysML要求図
│   │   ├── document_dependencies.md           # ドキュメント依存関係チェーン
│   │   ├── front_matter_*.md                  # YAML front matter 参照資料
│   │   └── prerequisites_*.md                 # 前提条件参照資料
│   ├── examples/                  # エージェント使用例
│   └── templates/{en,ja}/         # エージェント出力テンプレート（言語別）
├── skills/
│   ├── sdd-init/                  # AI-SDDワークフロー初期化
│   ├── constitution/              # プロジェクト憲章管理
│   ├── generate-spec/             # 仕様書/設計書生成
│   ├── generate-prd/              # PRD生成
│   ├── check-spec/                # 整合性チェック
│   ├── task-breakdown/            # タスク分解
│   ├── implement/                 # TDDベース実装の実行
│   ├── clarify/                   # 仕様明確化
│   ├── task-cleanup/              # タスククリーンアップ
│   ├── render-adr-review/         # ADR軸レビューHTMLレンダリング
│   ├── checklist/                 # 品質チェックリスト生成
│   ├── run-checklist/             # チェックリスト自動検証
│   ├── recommend-front-matter/    # YAML front matter推奨
│   ├── plan-refactor/             # リファクタリング計画
│   ├── generate-usecase-diagram/  # ユースケース図生成（サブスキル）
│   ├── analyze-requirements/      # 要求分析（サブスキル）
│   ├── generate-requirements-diagram/ # 要求図生成（サブスキル）
│   ├── finalize-prd/              # PRD統合・完成（サブスキル）
│   ├── vibe-detector/             # Vibe Coding検出スキル
│   └── doc-consistency-checker/   # ドキュメント整合性チェッカー
│   # 各スキルの構成:
│   # ├── SKILL.md                 # スキル定義
│   # ├── templates/{en,ja}/       # 言語別テンプレート
│   # ├── references/              # shared参照へのsymlink
│   # └── examples/                # 使用例（オプション）
├── hooks/
│   └── hooks.json                 # フック設定
├── scripts/
│   ├── session-start.py           # セッション開始時の初期化スクリプト
│   ├── user-prompt-submit.py      # Vibe Coding兆候検知
│   ├── pre-tool-use.py            # .sdd/ ファイル命名規則検証・CONSTITUTION原則注入
│   ├── post-tool-use.py           # ドキュメント更新漏れ検知
│   ├── sdd_index.py               # .sdd/ ドキュメントの構造化インデックス生成
│   ├── hook_common.py             # 共有: stdin/stdout・パス解決・.sdd-config読込
│   ├── fm_parser.py               # 共有: front matter 検出・パース
│   ├── naming.py                  # 共有: 命名規則検証・ドキュメント種別判定
│   ├── doc_walker.py              # 共有: 対象ドキュメント走査・design doc探索
│   └── env_export.py              # 共有: CLAUDE_ENV_FILE への export 書き出し
├── AI-SDD-PRINCIPLES.source.md
├── LICENSE
├── README.md
├── README.ja.md
├── CHANGELOG.md
└── CHANGELOG.ja.md
```

## ライセンス

MIT License
