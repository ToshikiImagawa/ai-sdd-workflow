# AGENTS.md

このファイルは、AI-SDDワークフロープラグインのサブエージェント設計・実装に関する原則とベストプラクティスを定義します。

Claude Code (claude.ai/code) がこのリポジトリのプラグインエージェントを開発・レビューする際の指針となります。

---

## プラグインエージェント設計ガイド

このセクションでは、AI-SDDワークフロープラグインのサブエージェントを設計・実装する際の原則とベストプラクティスを定義します。

### 1. サブエージェントの基本概念

#### 1.1 コンテキストの独立性

サブエージェントは **独立したコンテキストウィンドウ** を使用します。これは以下を意味します：

**重要な特性**:

- サブエージェントは独立したコンテキストウィンドウ (200,000トークン) を使用
- タスク委任時に毎回コンテキスト断裂が発生
- 毎回新しいセッションで起動

**設計の前提**:

```
メインコンテキスト (200,000トークン)
  ↓ 必要十分なコンテキストを渡す
サブエージェント (独立した200,000トークン)
  ↓ 要約結果を返す
メインコンテキスト
```

#### 1.2 トークン効率化の仕組み

サブエージェントを使用することで、メインコンテキストをクリーンに保ちながら、重い処理（レビュー、分析）を隔離できます。

**AI-SDDワークフローでの具体例**:

```
【メインコンテキスト】
- ユーザー要求: "PRDを生成してください"
- コンテキスト: ビジネス要求テキスト (2,000トークン消費)

↓ 委任プロンプト
  "対象PRDファイルパス: .sdd/requirement/user-auth.md"

【prd-reviewer サブエージェント (独立コンテキスト)】
- CONSTITUTION.md 読み込み (3,000トークン)
- PRD読み込み (2,000トークン)
- 原則準拠チェック (5,000トークン)
- 自動修正試行

↓ 要約結果 (500トークンのみ)
  "【CONSTITUTION準拠: 🟢】
   自動修正: 2件
   手動修正が必要: 0件"

【メインコンテキスト】
- レビュー結果(500トークン)を受け取る
- 次のステップ（spec生成）へ
- 合計消費: 2,000(既存) + 500(結果) = 2,500トークン
  ※ 10,000トークンのレビュープロセスはサブエージェントで隔離
```

**コンテキスト保護の効果**:

| タスク             | サブエージェント未使用 | サブエージェント使用 | 削減量     |
|:----------------|:------------|:-----------|:--------|
| PRDレビュー         | 12,000トークン  | 2,500トークン  | -9,500  |
| spec/designレビュー | 18,000トークン  | 3,500トークン  | -14,500 |
| 仕様明確化分析         | 15,000トークン  | 4,000トークン  | -11,000 |

サブエージェントはレビュー・分析の重い処理を隔離し、メインには要約のみを返すことで、メインコンテキストを開発作業に温存します。

### 2. エージェント設計原則

#### 2.1 役割と責務の明確化

各エージェントは **単一の明確な責務** を持つべきです。

**AI-SDDワークフローの役割分担**:

| エージェント                    | 責務                 | スコープ                                  |
|:--------------------------|:-------------------|:--------------------------------------|
| `sdd-workflow`            | AI-SDD開発フロー全体の管理   | フェーズ判定、Vibe Coding防止、知識資産管理           |
| `prd-reviewer`            | PRDの品質レビュー         | CONSTITUTION.md準拠チェック、SysML要求図形式検証    |
| `spec-reviewer`           | spec/designの品質レビュー | CONSTITUTION.md準拠チェック、ドキュメント間トレーサビリティ |
| `requirement-analyzer`    | 要求分析・追跡・検証         | SysML要求図分析、実装とのトレーサビリティ確認             |
| `clarification-assistant` | 仕様明確化支援            | 9カテゴリ分析、不明点の洗い出し、質問生成                 |

**descriptionの書き方**:

```markdown
# ❌ Bad: 曖昧

description: "仕様書をレビューする"

# ✅ Good: 明確で具体的

description: "
仕様書の品質レビューとCONSTITUTION.md準拠チェックを行うエージェント。曖昧な記述、不足セクション、SysMLとしての妥当性をチェックし、違反時は自動修正を試行します。"
```

**Good descriptionの条件**:

- 何をするか（動詞）
- どのドキュメントを対象とするか
- どのような観点でチェックするか
- 結果としてどうなるか（自動修正等）

#### 2.2 入出力インターフェース

すべてのエージェントは明確な入出力インターフェースを定義します。

**標準フォーマット**:

```markdown
## 入力

$ARGUMENTS

### 入力形式

```

対象ファイルパス（必須）: .sdd/specification/{機能名}_spec.md
オプション: --summary （簡易出力モード）

```

### 入力例

```

sdd-workflow-ja:spec-reviewer .sdd/specification/user-auth_spec.md
sdd-workflow-ja:spec-reviewer .sdd/specification/user-auth_spec.md --summary

```

## 前提条件

**実行前に必ず `sdd-workflow-ja:sdd-workflow` エージェントの内容を読み込み、AI-SDDの原則を理解してください。**

## 出力

レビュー結果レポート（評価サマリー、要修正項目、改善推奨項目、自動修正サマリー）
```

**入出力設計のポイント**:

- `$ARGUMENTS` で引数を受け取る
- 入力形式を明示（必須/オプション）
- 入力例を複数示す
- 前提条件を明記（sdd-workflow参照、環境変数等）
- 出力フォーマットを定義

#### 2.3 allowed-toolsの設計方針

`allowed-tools` は **タスクの性質に応じて最小限** に設定します。

**AI-SDDワークフローの設計パターン**:

| エージェントタイプ                                               | allowed-tools                           | 理由                         |
|:--------------------------------------------------------|:----------------------------------------|:---------------------------|
| **レビュー系** (prd-reviewer, spec-reviewer)                 | Read, Glob, Grep, Edit, AskUserQuestion | コンテキスト効率化のため、Taskツールを使用しない |
| **分析系** (requirement-analyzer, clarification-assistant) | 全ツール                                    | 柔軟な分析・探索が必要                |
| **フロー管理系** (sdd-workflow)                               | 全ツール                                    | 全体フローを管理するため、すべてのツールが必要    |

**重要な制約**: **spec-reviewer は Task ツールを使用不可**

理由:

- ドキュメント間トレーサビリティチェック（PRD↔spec、spec↔design）を行う
- 大量のファイル読み込みが発生する可能性がある
- Taskツールで再帰的に探索すると、コンテキストが爆発的に増加
- Read, Glob, Grep で必要なファイルを特定し、効率的に読み込む設計

**allowed-tools設計のベストプラクティス**:

```markdown
# ❌ Bad: すべてのツールを許可

allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion

# ✅ Good: 必要最小限のツールのみ許可

allowed-tools: Read, Glob, Grep, Edit, AskUserQuestion
```

理由: 不要なツールを許可すると、エージェントが非効率な実装を選択する可能性がある。

#### 2.4 前提条件の記述

すべてのエージェントは **共通の理解基盤** を持つ必要があります。

**標準テンプレート**:

```markdown
## 前提条件

**実行前に必ず `sdd-workflow-ja:sdd-workflow` エージェントの内容を読み込み、AI-SDDの原則・ドキュメント構成・永続性ルール・Vibe
Coding防止の詳細を理解してください。**

このエージェントはsdd-workflowエージェントの原則に基づいて{タスク名}を行います。

### ディレクトリパスの解決

**環境変数 `SDD_*` を使用してディレクトリパスを解決します。**

| 環境変数                     | デフォルト値               | 説明              |
|:-------------------------|:---------------------|:----------------|
| `SDD_ROOT`               | `.sdd`               | ルートディレクトリ       |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | PRD/要求仕様書ディレクトリ |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | 仕様書・設計書ディレクトリ   |
| `SDD_TASK_PATH`          | `.sdd/task`          | タスクログディレクトリ     |

**パス解決の優先順位:**

1. 環境変数 `SDD_*` が設定されている場合はそれを使用
2. 環境変数がない場合は `.sdd-config.json` を確認
3. どちらもない場合はデフォルト値を使用
```

### 3. 委任すべきタスク vs メインで実行すべきタスク

#### 3.1 基本原則: READ系はサブエージェント、WRITE系は慎重に

**✅ サブエージェントに委任すべきタスク (READ系)**:

| タスク          | 理由                    | AI-SDDワークフローでの例                  |
|:-------------|:----------------------|:---------------------------------|
| **レビュー・分析**  | コンテキスト汚染を避けたい、結果のみが重要 | prd-reviewer, spec-reviewer      |
| **複数ソースの探索** | 並列で行いたい検索、独立した視点で評価   | requirement-analyzer（トレーサビリティ確認） |
| **仕様明確化分析**  | 9カテゴリの体系的分析、質問生成      | clarification-assistant          |

**⚠️ 慎重に行うべきタスク (WRITE系)**:

| タスク          | 問題点                      | 対策                                           |
|:-------------|:-------------------------|:---------------------------------------------|
| **ドキュメント生成** | 重複したコンテキスト読み込みで無駄なトークン消費 | 基本的にメインエージェント（コマンド）で実行                       |
| **ドキュメント修正** | コンテキスト損失が品質に影響           | **例外**: 自動修正（spec-reviewer, prd-reviewer）は許可 |

**AI-SDDワークフローにおけるWRITE系の扱い**:

```
メインエージェント（コマンド）でドキュメント生成:
  /generate_prd → PRD生成 (Write)
  /generate_spec → spec/design生成 (Write)

サブエージェント（レビュー）で自動修正:
  prd-reviewer → PRD自動修正 (Edit)
  spec-reviewer → spec/design自動修正 (Edit)
  clarification-assistant → ユーザー回答を仕様書に統合 (Edit/Write)
```

**例外**: `clarification-assistant` は仕様明確化後にユーザー回答を仕様書に統合するため、Writeツールを使用します。
これは標準化されたセクションへの追記であり、コンテキスト損失の影響が小さいためです。

#### 3.2 委譲判断フロー

```
タスクを受け取る
  ↓
READ系タスク? (レビュー、分析、検証)
  ↓ YES
サブエージェントに委任
  - PRDレビュー → prd-reviewer
  - spec/designレビュー → spec-reviewer
  - 要求分析 → requirement-analyzer
  - 仕様明確化 → clarification-assistant
  ↓ NO
  ↓
WRITE系タスク? (ドキュメント生成、修正)
  ↓ YES
メインエージェント（コマンド）で実行
  - PRD生成 → /generate_prd
  - spec/design生成 → /generate_spec

  例外: 自動修正
    - prd-reviewer (Edit)
    - spec-reviewer (Edit)
    - clarification-assistant (Edit/Write)
```

### 4. エージェント間連携パターン

#### 4.1 コマンド → エージェント呼び出し

**標準パターン**: コマンドがドキュメントを生成した後、自動的にレビューエージェントを呼び出します。

```
/generate_prd
  ↓
1. PRD生成 (Write)
  ↓
2. prd-reviewer 自動実行
  ├─ CONSTITUTION.md 準拠チェック
  ├─ 自動修正試行
  └─ レビュー結果出力
  ↓
3. ユーザーに結果を返す
```

```
/generate_spec
  ↓
1. spec生成 (Write)
  ↓
2. spec-reviewer 自動実行 (spec)
  ├─ CONSTITUTION.md 準拠チェック
  ├─ PRD↔spec トレーサビリティチェック
  └─ 自動修正試行
  ↓
3. design生成 (Write)
  ↓
4. spec-reviewer 自動実行 (design)
  ├─ CONSTITUTION.md 準拠チェック
  ├─ spec↔design 整合性チェック
  └─ 自動修正試行
  ↓
5. ユーザーに結果を返す
```

**オプション呼び出しパターン**: `--full` オプションで包括的チェックを実行します。

```
/check_spec --full
  ↓
1. design↔実装の整合性チェック (メイン処理)
  ↓
2. spec-reviewer 呼び出し (--full オプション)
  ├─ PRD↔spec↔design 包括的トレーサビリティ
  ├─ CONSTITUTION.md 準拠チェック
  └─ 品質レビュー
  ↓
3. 統合結果を返す
```

#### 4.2 エージェント間データフロー

エージェント間でデータを受け渡す方法:

| 送信元      | 受信先             | 受け渡しデータ | 方法                    |
|:---------|:----------------|:--------|:----------------------|
| コマンド     | サブエージェント        | ファイルパス  | コマンド引数（`$ARGUMENTS`）  |
| サブエージェント | CONSTITUTION.md | -       | Read ツールで読み込み         |
| サブエージェント | PRD/spec/design | -       | Read ツールで読み込み         |
| サブエージェント | PRD/spec/design | 自動修正内容  | Edit ツールで書き込み         |
| サブエージェント | コマンド            | レビュー結果  | 要約結果を返す（500〜1000トークン） |

**コンテキスト継承**:

各エージェントは **sdd-workflowエージェントの原則を参照** することで、共通の理解基盤を持ちます：

1. **実行前に sdd-workflow エージェントの内容を読み込む**（全エージェントの前提条件）
2. **CONSTITUTION.md の原則を理解する**（レビューエージェントの前提）
3. **環境変数 `SDD_*` を使用してディレクトリパスを解決**（全エージェント共通）

#### 4.3 再委譲の禁止

**重要な制約**: サブエージェントは自分自身または他のサブエージェントに再委譲してはいけません。

**理由**:

- 無限ループ防止
- コンテキスト効率化の意図を損なう
- デバッグの困難性増加

**禁止パターン**:

```markdown
# ❌ Bad: spec-reviewerが自分自身に再委譲

spec-reviewer
↓
Task tool で spec-reviewer を呼び出す (禁止)
```

```markdown
# ❌ Bad: spec-reviewerが他のサブエージェントに委譲

spec-reviewer
↓
Task tool で prd-reviewer を呼び出す (禁止)
```

**許可パターン**:

```markdown
# ✅ Good: spec-reviewerが Read, Glob, Grep で必要な情報を取得

spec-reviewer
├─ Read: CONSTITUTION.md
├─ Read: PRD
├─ Read: spec
└─ Grep: 要求ID検索
```

**エージェントマニフェストでの制約表明**:

```markdown
allowed-tools: Read, Glob, Grep, Edit, AskUserQuestion

**注意**: このエージェントは Task ツールを使用しません。再委譲を避け、コンテキスト効率化を優先します。
```

### 5. 実践Tips

#### 5.1 descriptionを明確にする

**Good descriptionの要件**:

- 1行で役割を表現
- 対象ドキュメントを明示
- 主要な機能を列挙
- 設計意図を示す

```markdown
# ❌ Bad: 曖昧

description: "仕様書をレビューする"

# ✅ Good: 明確で具体的

description: "
仕様書の品質レビューとCONSTITUTION.md準拠チェックを行うエージェント。曖昧な記述、不足セクション、SysMLとしての妥当性をチェックし、違反時は自動修正を試行します。"
```

#### 5.2 allowed-toolsを最小限にする

**設計ルール**:

1. タスクの性質を分析（READ系 or WRITE系）
2. 必要最小限のツールを選択
3. 特にTaskツールは慎重に判断（コンテキスト効率化）

```markdown
# ❌ Bad: すべてのツールを許可

allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion

# ✅ Good: レビュー系エージェント（READ系）

allowed-tools: Read, Glob, Grep, Edit, AskUserQuestion
```

#### 5.3 大きなコンテキストはファイルで委任

**問題**: プロンプトに全データを貼り付けるとトークンエラー

**解決策**: ファイルパスで委任

```markdown
# ❌ Bad: プロンプトに全PRDを貼り付け

prompt: "[5,000行のPRD内容]をレビューしてください"

# ✅ Good: ファイルパスで委任

prompt: "対象PRDファイルパス: .sdd/requirement/user-auth.md"
```

**メリット**:

- コンテキスト汚染防止
- トークン制限エラー回避
- サブエージェントが必要な情報のみ読み取り

#### 5.4 デバッグ方法

**ログの場所**:

```
~/.claude/projects/<project-name>/
  ├── conversation.jsonl  # メイン会話
  └── sidechains/         # サブエージェントログ
```

**確認内容**:

- 委任プロンプト（何を伝えたか）
- 実行ログ（何をしたか）
- 返却結果（何を返したか）

**デバッグ例**:

```bash
cd ~/.claude/projects/ai-sdd-workflow/
grep -r "spec-reviewer" sidechains/
```
