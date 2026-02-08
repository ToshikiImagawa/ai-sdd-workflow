# 変更履歴

このプラグインの主な変更はこのファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
このプロジェクトは [セマンティックバージョニング](https://semver.org/lang/ja/) に準拠しています。

## [Unreleased]

## [3.0.2] - 2026-02-09

### 修正

- **`sdd-init`** - `.sdd-config.json` からの言語設定継承を修正
    - `update-claude-md.sh` が環境変数ではなく `.sdd-config.json` から直接 `SDD_LANG` を読み取るように変更
    - 以前は `.sdd-config.json` で `lang: "ja"` を設定していても、`CLAUDE.md` の `## AI-SDD Instructions` セクションが英語で生成されていた
    - 原因: `init-structure.sh` から `CLAUDE_ENV_FILE` への書き込みが、同一シェルセッション内で `update-claude-md.sh` 実行時に反映されていなかった

## [3.0.1] - 2026-02-09

### 追加

#### 新規スキル（PRD生成ワークフロー）

- **`/generate-usecase-diagram`** - ユースケース図生成スキル
    - ビジネス要件からMermaid flowchart形式のユースケース図を生成
    - `context: fork` でコンテキスト分離
    - Interactive と CI（`--ci`）モードをサポート
    - テキストのみ返却（ファイル書き込みなし）

- **`/analyze-requirements`** - 要求分析スキル
    - UR（ユーザー要求）、FR（機能要求）、NFR（非機能要求）を抽出
    - `context: fork` でコンテキスト分離
    - MoSCoW優先度付けとリスク評価をサポート
    - テキストのみ返却（ファイル書き込みなし）

- **`/generate-requirements-diagram`** - SysML要求図生成スキル
    - 要求分析からMermaid requirementDiagramを生成
    - `context: fork` でコンテキスト分離
    - 要求間関係（contains, derives, traces）をサポート
    - テキストのみ返却（ファイル書き込みなし）

- **`/finalize-prd`** - PRD統合スキル
    - ユースケース図、要求分析、要求図を統合して完全なPRDを作成
    - `context: fork` でコンテキスト分離
    - PRDテンプレート構造に従う
    - テキストのみ返却（ファイル書き込みなし）

#### スキル機能強化

- **`sdd-init`** - `.sdd-config.json` の `lang` フィールド自動管理機能を追加
    - 設定ファイルが存在しない場合: デフォルト設定（`lang: "en"` 含む）で新規作成
    - 設定ファイルに `lang` フィールドがない場合（v3.0.0マイグレーション）: `lang: "en"` を追加
    - 実行フローにステップ1.5「Manage Configuration File」を追加
    - シェルスクリプト追加: `init-structure.sh`, `update-claude-md.sh`

- **`check-spec`** - ファイルスキャン用シェルスクリプトを追加
    - `scripts/find-design-docs.sh` - ClaudeのGlob/Grepオーバーヘッドを削減するための設計ドキュメント事前スキャン

- **`constitution`** - 検証用シェルスクリプトを追加
    - `scripts/validate-files.sh` - 検証のためのrequirement/spec/designファイル事前スキャン

- **`generate-spec`** - 準備用シェルスクリプトを追加
    - `scripts/prepare-spec.sh` - 仕様生成のためのファイル前処理

#### ドキュメント

- **Mermaid記法ガイドに注意事項を追加**
    - `<` と `>` を含むラベル（`<<include>>` など）はHTMLエンティティでエスケープが必要
    - 例: `&lt;&lt;include&gt;&gt;` と記述して `<<include>>` を表示

- **Progressive Disclosure用参照ファイルを追加**
    - `clarify/references/nine_category_analysis.md` - 9カテゴリ分析の定義
    - `constitution/references/best_practices.md` - Constitutionベストプラクティス
    - `constitution/examples/validation_report.md` - 検証レポート例

### 変更

#### スキルアーキテクチャ

- **`generate-prd`** - オーケストレーターパターンにリファクタリング
    - 4つのサブスキルをオーケストレート: `/generate-usecase-diagram`, `/analyze-requirements`, `/generate-requirements-diagram`, `/finalize-prd`
    - サブスキルは `context: fork` でコンテキスト分離して実行
    - サブスキルはテキストのみ返却; `generate-prd` がファイル書き込みを担当
    - SKILL.mdを374行から140行に削減
    - ワークフロー追跡用のProgress Checklistを追加

- **全スキル** - Claude Code Skills Best Practices準拠
    - 全スキルに `$ARGUMENTS` プレースホルダーと `## Input` セクションを追加
    - 不足していた `allowed-tools` をフロントマターに追加
    - 出力前の `Quality Checks` セクションを追加
    - SKILL.mdファイルを500行以下に維持（Progressive Disclosureパターン）
    - 詳細コンテンツを `references/` と `examples/` ディレクトリに移動

- **`constitution`** - 558行から392行に削減
    - 検証レポート例を `examples/validation_report.md` に移動
    - ベストプラクティスを `references/best_practices.md` に移動

- **`clarify`** - 行数を削減
    - 9カテゴリ分析を `references/nine_category_analysis.md` に移動

#### 共有リファレンス

- **`usecase_diagram_guide.md`** - ユースケース図の関係表記をUML標準に修正
    - アソシエーション（関連）: `-->` → `---`（実線、双方向）
    - Include（包含）: `-. include .->` → `-.->|"<<include>>"|`（点線矢印＋ステレオタイプラベル）
    - Extend（拡張）: `-. extend .->` → `-.->|"<<extend>>"|`（点線矢印＋ステレオタイプラベル）
    - Common Mistakesテーブルを更新
    - すべてのMermaidコード例を新記法に更新

- **`mermaid_notation_rules.md`** - ユースケース図記法を更新
    - アソシエーション表記を `---` に修正
    - Include/Extendラベル形式を更新
    - Common Mistakesセクションを更新

#### テンプレート

- **`generate-prd`** - PRDテンプレートのユースケース図記法を修正
    - `templates/en/prd_template.md`: アソシエーション、Include、Extend表記を更新
    - `templates/ja/prd_template.md`: 同様の修正（日本語ラベル `<<包含>>`, `<<拡張>>` を維持）

## [3.0.0] - 2026-02-06

### 追加

#### 新規スキル

- **`/run-checklist`** - 自動品質検証スキル
    - `/checklist` で生成されたチェックリスト項目の検証コマンドを自動実行
    - テスト、リンター、セキュリティスキャナー、仕様整合性チェックを実行
    - カテゴリ（`--category`）と優先度（`--priority`）でフィルタリングをサポート
    - TaskList と連携した進捗追跡
    - タイムスタンプ付きで結果をチェックリストファイルに直接記録
    - `.sdd/task/{ticket}/verification_report.md` に検証レポートを生成

#### 共有リファレンス

- **`shared/references/`** - 集中リファレンスドキュメント
    - `mermaid_notation_rules.md` - 包括的な Mermaid 構文ガイド（1100行以上）
        - フローチャート、シーケンス、クラス、状態、ER、要件、ガントチャートの構文
        - エスケープルール、スタイリング、一般的な落とし穴
    - `usecase_diagram_guide.md` - Mermaid 用ユースケース図ガイド（750行以上）
        - アクター、ユースケース、システム境界の定義
        - 関係タイプ（association、include、extend、generalization）
        - スタイリングとレイアウトのベストプラクティス
    - `requirements_diagram_components.md` - SysML 要件図コンポーネント（800行以上）
        - 属性（id、text、risk、verifyMethod）を持つ要件要素定義
        - 関係タイプ（containment、derivation、refinement、satisfaction、verification）
        - Mermaid 構文の例とテンプレート
    - `document_dependencies.md` - ドキュメント依存関係チェーンリファレンス
    - `prerequisites_directory_paths.md` - SDD 環境変数リファレンス
    - `prerequisites_plugin_update.md` - プラグイン更新チェック手順
    - `prerequisites_principles.md` - AI-SDD 原則リファレンス

#### エージェント構造の改善

- **エージェント出力テンプレート** - 全エージェントの言語別テンプレート
    - `agents/templates/en/` - 英語出力テンプレート
    - `agents/templates/ja/` - 日本語出力テンプレート
    - テンプレート: `clarification_analysis_output.md`、`clarification_question_template.md`、`prd_review_output.md`、
      `requirement_analysis_output.md`、`spec_review_output.md`
- **エージェントリファレンス** - 再利用可能なリファレンスドキュメント
    - `agents/references/ambiguity_patterns.md` - 曖昧な表現パターン
    - `agents/references/document_link_convention.md` - Markdown リンク規約
    - `agents/references/sysml_requirements_theory.md` - SysML 要件理論
    - 共有リファレンスへのシンボリックリンク: `mermaid_notation_rules.md`、`requirements_diagram_components.md`、
      `usecase_diagram_guide.md`
- **エージェント例** - 使用例
    - `agents/examples/clarification_questions.md` - 明確化質問の例

#### スキル構造の改善

- **全スキルに `references/` ディレクトリを追加** - 共有リファレンスへのシンボリックリンク付き
    - スキル間で一貫した前提条件処理を実現
    - 前提条件ドキュメントの重複を削減
- **使用例付きの `examples/` ディレクトリをスキルに追加**
    - `check-spec/examples/` - scope_confirmation.md、serena_symbol_analysis.md
    - `checklist/examples/` - checklist_full_example.md
    - `constitution/examples/` - constitution_as_code.json、constitution_file_structure.md、principle_template.md
    - `generate-spec/examples/` - compliance_check_design.md、compliance_check_spec.md、prd_reference_section.md
    - `implement/examples/` - implementation_progress_log.md、input_format.md、option_* ファイル、output_* ファイル
    - `task-breakdown/examples/` - requirement_coverage.md、serena_analysis.md、task_list_format.md
    - `task-cleanup/examples/` - scope_confirmation.md

### 変更

#### スキル

- **全スキルをリファクタリング** - シンボリックリンク経由で共有リファレンスを使用
    - 前提条件は `references/prerequisites_*.md` シンボリックリンクを参照
    - メンテナンスオーバーヘッドを削減し、一貫性を確保
- **`implement` スキル** - 広範なリファレンスとテンプレートファイルを追加
    - `references/commit_strategy.md`、`five_phases_overview.md`、`tdd_principles.md` など
    - `templates/{en,ja}/phase_*.md` - フェーズ実行テンプレート
    - `templates/{en,ja}/tasklist_patterns.md` - TaskList 連携パターン
- **`generate-prd` スキル** - Mermaid ダイアグラムリファレンスを追加
    - `mermaid_notation_rules.md`、`usecase_diagram_guide.md`、`requirements_diagram_components.md` へのリンク
- **`doc-consistency-checker` スキル** - ドキュメント依存関係リファレンスを追加

#### エージェント

- **全エージェントを Progressive Disclosure パターンでリファクタリング**
    - エージェント Markdown ファイルで大規模コンテンツに `@reference` インポートを使用
    - 出力テンプレートを `templates/{en,ja}/` に外部化
- **`spec-reviewer`** - リファレンス使用により 566行から約200行に簡素化
- **`prd-reviewer`** - リファレンス使用により 328行から約150行に簡素化
- **`requirement-analyzer`** - リファレンス使用により 420行から約150行に簡素化
- **`clarification-assistant`** - リファレンス使用により 626行から約200行に簡素化

### 削除

#### スキル

- **`sdd-templates`** - 共有リファレンスと個別スキルテンプレートに統合
- **`output-templates`** - テンプレートを各スキルディレクトリに移動

#### レガシーコマンド

- **`commands/` ディレクトリを完全削除**
    - `commands/checklist.md` - `skills/checklist/SKILL.md` に移行
    - `commands/implement.md` - `skills/implement/SKILL.md` に移行
    - `commands/sdd_init.md` - `skills/sdd-init/SKILL.md` に移行

---

## [3.0.0-alpha] - 2026-02-03

### 破壊的変更

#### プラグイン統合

- **`sdd-workflow-ja` と `sdd-workflow` を単一の統合プラグインに統合**（`sdd-workflow`）
    - 言語選択は `SDD_LANG` 環境変数経由（`.sdd-config.json` の `lang` フィールドから、デフォルト: `en`）
    - テンプレートを言語別に分割: `templates/ja/` と `templates/en/`
    - SKILL.md とエージェントファイルは英語のみ
    - `sdd-workflow-ja` プラグインを完全に削除

#### コマンドをスキルに変換

- **11のコマンドすべてをスキルに移行** - `user-invocable: true` 付き
    - `commands/` ディレクトリを完全に削除
    - すべてのコマンドは `skills/{name}/SKILL.md` 配下に移動

#### コマンド名の変更（アンダースコア → ハイフン）

| 旧 (v2.x)          | 新 (v3.0.0)        |
|:------------------|:------------------|
| `/sdd_init`       | `/sdd-init`       |
| `/generate_spec`  | `/generate-spec`  |
| `/generate_prd`   | `/generate-prd`   |
| `/check_spec`     | `/check-spec`     |
| `/task_breakdown` | `/task-breakdown` |
| `/task_cleanup`   | `/task-cleanup`   |
| `/sdd_migrate`    | `/sdd-migrate`    |

### 追加

#### 多言語サポート

- **`SDD_LANG` 環境変数** - テンプレート言語選択を制御
    - `.sdd-config.json` の `lang` フィールドで設定
    - サポート値: `en`（デフォルト）、`ja`
    - `session-start.sh` が設定から `lang` を読み込み、`SDD_LANG` をエクスポート

#### 言語別テンプレート

- 既存の4つのスキルすべてに言語分離テンプレートを追加:
    - `sdd-templates/templates/{en,ja}/`
    - `vibe-detector/templates/{en,ja}/`
    - `doc-consistency-checker/templates/{en,ja}/`
    - `output-templates/templates/{en,ja}/`
- 日本語テンプレートは旧 `sdd-workflow-ja` プラグインからコピー

### 変更

#### スキル

- **旧コマンドから11の新規スキルを作成**:
    - `sdd-init`、`constitution`、`generate-spec`、`generate-prd`、`check-spec`
    - `task-breakdown`、`implement`、`clarify`、`task-cleanup`、`sdd-migrate`、`checklist`
    - 各スキルに適切な `allowed-tools`、`user-invocable: true`、オプションで `disable-model-invocation` を設定
- **既存の4スキルを v3.0.0 に更新** - 言語設定サポート付き
    - `## Language Configuration` セクションを追加し、動的な `SDD_LANG` コンテキスト注入
    - テンプレートパス参照を `templates/en/` 形式に更新

#### エージェント

- **spec-reviewer** - `skills` フィールドを追加:
  `["sdd-workflow:sdd-templates", "sdd-workflow:doc-consistency-checker"]`
- **prd-reviewer** - `skills` フィールドを追加: `["sdd-workflow:sdd-templates"]`
- 4つのエージェントすべてをハイフン区切りのコマンド名参照に更新
- すべてのエージェント説明を新しいコマンド名を参照するように更新

#### 設定

- **`.sdd-config.json`** - 言語設定用の `lang` フィールドを追加
- **`session-start.sh`** - `SDD_LANG` の読み込みとエクスポートを追加
- **`plugin.json`** - 統合プラグイン説明で v3.0.0 に更新
- **`marketplace.json`** - `sdd-workflow-ja` エントリを削除、`sdd-workflow` を v3.0.0 に更新

#### ドキュメント

- **`CLAUDE.md`** - リポジトリ構造をスキル付き単一プラグインに反映して更新
- **`README.md`** - v2.x からの移行ガイドを追加、すべてのコマンド参照を更新

### 削除

- **`plugins/sdd-workflow-ja/`** - 日本語プラグインディレクトリ全体（`sdd-workflow` に統合）
- **`plugins/sdd-workflow/commands/`** - コマンドディレクトリ全体（スキルに移行）

## [2.4.2] - 2026-01-26

### 修正

#### プラグインマニフェスト

- **plugin.json から skills フィールドを削除** - プラグインインストールエラーを修正
    - Claude Code の plugin.json スキーマでサポートされていない `skills` フィールドを削除
    - スキルは `skills/` ディレクトリから自動検出される
    - インストール時の "Invalid input" エラーを解決

## [2.4.1] - 2026-01-26

### 修正

#### コマンド

- **argument-hint の修正と引数説明** - 引数仕様を実際の使用法に合わせて修正
    - `argument-hint` 表現を統一（"file-path" → "feature-name" 修正）
    - 各コマンドに引数説明テーブルを追加（引数名、必須/オプション、説明）
    - 影響を受けるコマンド:
        - `task_breakdown`: `<design-doc-path>` → `<feature-name> [ticket-number]`
        - `check_spec`: `<design-doc-path>` → `[feature-name] [--full]`
        - `checklist`: `<file-path>` → `<feature-name> [ticket-number]`
        - `clarify`: `[spec-file-path]` → `<feature-name> [--interactive]`
        - `constitution`: `<init|update|check>` → `<subcommand> [arguments]`（サブコマンド詳細テーブルを追加）
        - `generate_prd`: `<feature-name> [requirements-description]` → `<requirements-description>`
        - `generate_spec`: `<feature-name> [prd-file-path]` → `<requirements-description>`
        - `implement`: `<task-file-path>` → `<feature-name> [ticket-number]`
        - `task_cleanup`: `<ticket-number>` → `[ticket-number]`（オプションに変更）
    - ユーザーがコマンド実行時に正しい引数形式を理解できるように

## [2.4.0] - 2026-01-25

### 追加

#### ドキュメント

- **PLUGIN.md** - Claude Code プラグインとマーケットプレイス作成の包括的ガイド
    - プラグイン基本構造（ディレクトリレイアウト、マーケットプレイス構造）
    - マニフェストファイル（plugin.json、marketplace.json の詳細）
    - コマンド、エージェント、スキルの実装（フロントマター、ベストプラクティス）
    - MCP サーバー連携（外部ツール統合）
    - フック実装（イベント駆動自動化）
    - マーケットプレイス公開プロセス（品質基準、配布モデル）
- **CLAUDE.md** - PLUGIN.md への参照を追加（AGENTS.md と同様の構造）

#### スキル

- すべてのスキルに `version: 2.3.1` と `license: MIT` フィールドを追加
    - vibe-detector
    - doc-consistency-checker
    - sdd-templates
- **output-templates** - コマンド出力フォーマットを提供する新規スキル
    - `init_output.md` - 初期化完了メッセージ
    - `prd_output.md` - PRD 生成完了メッセージ
    - `spec_output.md` - 仕様書・設計書生成完了メッセージ
    - `breakdown_output.md` - タスク分解結果
    - `cleanup_output.md` - クリーンアップ確認
    - `clarification_output.md` - 仕様明確化レポート
    - `check_spec_output.md` - 整合性チェック結果
    - `migrate_output.md` - 移行結果
    - `constitution_output.md` - 憲章管理結果

#### コマンド

- すべてのコマンドに `argument-hint` フィールドを追加して使いやすさを向上
    - generate_spec: `<feature-name> [prd-file-path]`
    - generate_prd: `<feature-name> [requirements-description]`
    - check_spec: `<design-doc-path>`
    - task_breakdown: `<design-doc-path> [ticket-number]`
    - task_cleanup: `<ticket-number>`
    - constitution: `<init|update|check>`
    - implement: `<task-file-path>`
    - clarify: `[spec-file-path]`
    - checklist: `<file-path>`

### 変更

#### アーキテクチャ

- **出力フォーマット分離** - コマンド出力フォーマットを `skills/output-templates/` に分離
    - コマンド md ファイルは Claude 向け指示のみを含む
    - 出力フォーマットは独立したテンプレートファイルとして管理
    - 新規スキル: `output-templates`（9つのテンプレートファイルを含む）
    - 既存の `sdd-templates` スキルはプロジェクトドキュメントテンプレート専用に

#### コマンド

- **implement** - TaskList ベースの進捗管理を追加
    - 各フェーズ開始時に TaskCreate でタスクを作成
    - フェーズ実行中に TaskUpdate でタスクステータスを更新（pending → in_progress → completed）
    - 依存関係を設定して前フェーズ完了後に次フェーズを開始
    - ユーザーは `/tasks` コマンドで実装進捗を確認可能
    - TaskList が利用できない場合は従来の markdown 進捗表示にフォールバック

#### マーケットプレイス

- **marketplace.json** の改善
    - `author.url` を追加（作成者帰属）
    - `category: "development"` を追加（マーケットプレイスフィルタリング）
    - `tags` 配列を追加（検索発見性）
        - "specification-driven-development"
        - "japanese" / "english"
        - "workflow"
        - "sysml"
        - "requirements"
        - "documentation"

#### エージェント

- すべてのエージェントの `description` をより明確な使用シナリオで改善
    - 機能説明スタイルから「いつ使用するか」スタイルに変更
    - 具体的なトリガーフレーズを追加（例: "review spec"、"check spec"）
    - コマンドとの関係を明示（例: /check_spec または /generate_spec 実行後）
    - 必要な入力情報を指定（例: 仕様ファイルパスが必要）
    - 自己参照的な「エージェント」用語を削除
    - 対象エージェント: spec-reviewer、requirement-analyzer、prd-reviewer、clarification-assistant

#### スキル

- すべてのスキルの `description` をより明確な実行コンテキストで改善
    - 実行タイミングを指定（例: 実装前に自動実行、コマンドで呼び出し）
    - 検出詳細を指定（例: 「いい感じに」「何とか」などの曖昧な表現）
    - トレーサビリティ保証を明示
    - フォールバック動作を詳細に説明
    - 対象スキル: vibe-detector、doc-consistency-checker、sdd-templates

### 修正

#### コマンド

- **プロンプト表現の統一** - ユーザー向け説明を削除し、明確な Claude 向け指示に統一
    - 「Next Steps」リスト項目を削除（「Post-Generation Actions」セクション内のプレーンテキストから）
    - 「Recommended Manual Verification」セクションを削除（出力テンプレートに移動）
    - 「手動で」表現を Claude 指示に変更（例: 「ユーザーに手動検証を推奨する」）
    - 出力フォーマット参照方法を統一（ファイルパスからスキル参照へ）
    - 影響を受けるコマンド: `sdd_init`、`generate_prd`、`generate_spec`、`task_breakdown`、`task_cleanup`、`clarify`、
      `check_spec`、`sdd_migrate`、`constitution`

#### エージェント

- **プロンプト表現の統一** - 「推奨」表現を指示形式に変更
    - spec-reviewer: 「追加を推奨」→「追加が必要」
    - clarification-assistant: 「補足を推奨」→「補足が必要」
    - clarification-assistant: 「推奨明確度スコア」→「明確度スコア評価基準」

## [2.3.1] - 2026-01-14

### 修正

#### フック

- `session-start.sh` - 一時ファイル存在チェックでエラーハンドリングを改善
    - sed コマンド失敗時の `mv: No such file or directory` エラーを修正
    - mv 実行前に一時ファイルの存在を確認する `&& [ -f "$TEMP_FILE" ]` を追加
    - フォールバックプロセスが正しく動作するように改善
    - 日本語版との一貫性のため英語版に警告ファイル削除プロセス（else 句）を追加

## [2.3.0] - 2026-01-09

### 変更

#### エージェント

- **役割分離**: `sdd-workflow` エージェントを `AI-SDD-PRINCIPLES.md` にリネーム
    - 原則定義を独立したドキュメントに分離
    - すべてのコマンド、エージェント、スキルを `../AI-SDD-PRINCIPLES.md` を参照するように更新
    - AI-SDD 原則を一元化してメンテナンス性を向上

- `spec-reviewer` - ドキュメントトレーサビリティチェック機能を追加
    - **PRD ↔ spec トレーサビリティチェック**: PRD 要件が仕様書で適切にカバーされているか検証
        - 要件 ID（UR/FR/NFR）マッピング検証
        - カバレッジ率計算（80%閾値チェック）
        - 部分的/欠落カバレッジの分類
    - **spec ↔ design 整合性チェック**: 仕様内容が設計書で適切に詳細化されているか検証
        - API 定義の詳細化チェック
        - 型定義の整合性チェック
        - 制約考慮チェック
    - `allowed-tools` に `Edit` を追加（自動修正サポート用）
    - 入力形式と出力形式を明確化（`--summary` オプションサポート）

#### コマンド

- `/check_spec` - **design ↔ implementation 整合性チェックに特化**
    - **[破壊的変更]** ドキュメント間整合性チェック（PRD↔spec、spec↔design）を `spec-reviewer` に委譲
        - **以前 (v2.2.0)**: すべての整合性チェックを実行（CONSTITUTION↔docs、PRD↔spec、spec↔design、design↔implementation）
        - **以後 (v2.3.0)**: design↔implementation 整合性チェックのみを実行（パフォーマンス向上）
        - **移行**:
            - ドキュメント間整合性チェックが必要な場合: `/check_spec --full` を使用
            - design↔implementation のみで十分な場合: `/check_spec` をそのまま使用
        - **影響**: CI/CD パイプラインで `/check_spec` を使用している場合、`--full` オプションの追加を検討
    - `--full` オプションを追加: 整合性チェックに加えて `spec-reviewer` による包括的レビューを実行
    - 対象ドキュメントを `*_design.md` に限定
    - 出力フォーマットを簡素化（design↔implementation に焦点）

- `/sdd_init` - 参照パスを更新
    - エージェント参照を `AI-SDD-PRINCIPLES.md` に変更

### 追加

#### ドキュメント

- `AI-SDD-PRINCIPLES.md` - AI-SDD 原則を定義する独立ドキュメント
    - 以前 `sdd-workflow` エージェントに含まれていた原則定義を分離
    - コマンド、エージェント、スキルから共通参照

#### README

- Windows プラットフォーム非互換性を文書化
    - プラットフォームサポートマトリックスを追加（macOS/Linux: ✅、Windows: ❌）
    - Windows ユーザー向けの代替案を文書化（WSL、Git Bash）
    - 今後のサポート予定（PowerShell 版、クロスプラットフォーム実装を検討中）

## [2.2.0] - 2026-01-06

### 追加

#### エージェント

- `prd-reviewer` - PRD（要求仕様書）レビューエージェント
    - CONSTITUTION.md 準拠チェック（最重要機能）
    - 原則カテゴリチェック（ビジネス、アーキテクチャ、開発、技術制約）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - SysML 要件図形式検証
    - 曖昧な表現の検出と改善提案

### 変更

#### エージェント

- `spec-reviewer` - CONSTITUTION.md 準拠チェック機能を追加
    - Read ツールを使用して CONSTITUTION.md を読み取る準備指示を追加
    - 仕様書に焦点を当てた原則カテゴリチェック（アーキテクチャ原則を強調）
    - 設計書に焦点を当てた原則カテゴリチェック（技術制約を強調）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - レビュー出力形式に CONSTITUTION.md 準拠チェック結果を追加

#### コマンド

- `/generate_prd` - CONSTITUTION.md 準拠生成フローを追加
    - 生成フローに CONSTITUTION.md 読み取りステップを追加（Step 2）
    - prd-reviewer 原則準拠チェックを必須化（Step 6）
    - PRD 用の原則カテゴリ影響テーブルを追加
    - チェック結果出力テンプレートを追加

- `/generate_spec` - CONSTITUTION.md 準拠生成フローを追加
    - 生成フローに CONSTITUTION.md 読み取りステップを追加（Step 2）
    - spec-reviewer 原則準拠チェックを必須化（Steps 6, 8）
    - 仕様書と設計書の両方にチェック結果出力テンプレートを追加

## [2.1.1] - 2025-12-23

### 変更

- すべてのコマンドとエージェントから自動 git コミット指示を削除
    - `task_cleanup` - クリーンアップワークフローからコミットステップを削除
    - `implement` - 継続的検証フローからコミット指示を削除
    - `generate_spec` - 生成フローからコミットステップを削除
    - `sdd-workflow` エージェント - ワークフローフェーズからコミットステップを削除
    - `clarify` - 統合モードからコミット指示を削除
    - `task_breakdown` - 生成後アクションからコミットステップを削除
    - `generate_prd` - 生成後アクションからコミットステップを削除
    - `sdd_migrate` - コミット指示とコミットメッセージ例を削除
    - `sdd_init` - 初期化フローからコミットステップを削除

## [2.1.0] - 2025-12-12

### 追加

#### コマンド

- `/clarify` - 仕様明確化コマンド
    - 9つのカテゴリで仕様をスキャン（機能スコープ、データモデル、フロー、非機能要件、
      統合、エッジケース、制約、用語、完了シグナル）
    - 不明確な項目を Clear/Partial/Missing に分類
    - 最大5つの高インパクト明確化質問を生成
    - 回答を `*_spec.md` にインクリメンタルに統合
    - `vibe-detector` スキルを補完
- `/implement` - TDD ベース実装実行コマンド
    - tasks.md のチェックリスト完了率を検証
    - 5つのフェーズを順番に実行（Setup→Tests→Core→Integration→Polish）
    - テストファースト（TDD）アプローチ
    - tasks.md に進捗を自動マーク
    - 完了検証（全タスク完了、テスト合格、仕様整合性）
- `/checklist` - 品質チェックリスト生成コマンド
    - 9つのカテゴリで仕様と計画からチェックリストを自動生成
    - CHK-{カテゴリ番号}{連番} 形式で ID を割り当て
    - 優先度レベル（P1/P2/P3）を自動設定
- `/constitution` - プロジェクト憲章管理コマンド
    - プロジェクトの非交渉可能な原則を定義（ビジネス、アーキテクチャ、開発方法論、技術制約）
    - セマンティックバージョニング（MAJOR/MINOR/PATCH）
    - 仕様書と設計書との同期検証

#### エージェント

- `clarification-assistant` - 仕様明確化アシスタントエージェント
    - 9つのカテゴリでユーザー要件を体系的に分析
    - 高インパクト明確化質問を生成
    - 回答を仕様書に統合
    - `/clarify` コマンドのバックエンド役割

#### テンプレート

- `checklist_template.md` - 品質チェックリストテンプレート
    - 9カテゴリの品質チェック項目
    - 優先度レベル（P1/P2/P3）
    - 各項目の検証方法
- `constitution_template.md` - プロジェクト憲章テンプレート
    - 原則階層（ビジネス → アーキテクチャ → 開発方法論 → 技術制約）
    - 各原則の検証方法、違反例、準拠例
    - バージョン履歴と改正プロセス
- `implementation_log_template.md` - 実装ログテンプレート
    - セッションベースの実装判断記録
    - 課題と解決策の追跡
    - 技術的発見とパフォーマンス指標

#### スキル

- `sdd-templates` - 新規テンプレートへの参照を追加

## [2.0.1] - 2025-12-12

### 追加

#### エージェント

- すべてのエージェントにドキュメントリンク規約を追加
    - `sdd-workflow` - ファイル/ディレクトリ用の markdown リンク形式を定義
    - `spec-reviewer` - リンク規約チェックポイントを追加
    - `requirement-analyzer` - 要件図用のリンク規約を追加
    - ファイルリンク: `[filename.md](path)` 形式
    - ディレクトリリンク: `[directory-name](path/index.md)` 形式

### 削除

#### エージェント

- `sdd-workflow` - コミットメッセージ規約セクションを削除
    - Claude Code の標準コミット規約に委譲するポリシーに変更

## [2.0.0] - 2025-12-09

### 破壊的変更

#### ディレクトリ構造の変更

- **ルートディレクトリ**: `.docs/` → `.sdd/`
- **要件ディレクトリ**: `requirement-diagram/` → `requirement/`
- **タスクログディレクトリ**: `review/` → `task/`

#### コマンドリネーム

- `/review_cleanup` → `/task_cleanup`

#### 移行

`/sdd_migrate` コマンドを使用してレガシーバージョン（v1.x）から移行:

- **オプション A**: ディレクトリをリネームして新構造に移行
- **オプション B**: `.sdd-config.json` を生成してレガシー構造を維持

### 追加

#### コマンド

- `/sdd_init` - AI-SDD ワークフロー初期化コマンド
    - プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
    - `.sdd/` ディレクトリ構造を作成（requirement/、specification/、task/）
    - `sdd-templates` スキルを使用してテンプレートファイルを生成
- `/sdd_migrate` - レガシーバージョンからの移行コマンド
    - レガシー構造（`.docs/`、`requirement-diagram/`、`review/`）を検出
    - 新構造への移行または互換設定の生成を選択

#### エージェント

- `requirement-analyzer` - 要件分析エージェント
    - SysML 要件図ベースの分析
    - 要件のトレーサビリティと検証

#### スキル

- `sdd-templates` - AI-SDD テンプレートスキル
    - PRD、仕様書、設計書のフォールバックテンプレートを提供
    - プロジェクトテンプレート優先ルールを明確化

#### フック

- `session-start` - セッション開始初期化フック
    - `.sdd-config.json` から設定を読み込み、環境変数を設定
    - レガシー構造を自動検出し、移行ガイダンスを表示

#### 設定ファイル

- `.sdd-config.json` - プロジェクト設定ファイルサポート
    - `root`: ルートディレクトリ（デフォルト: `.sdd`）
    - `directories.requirement`: 要件ディレクトリ（デフォルト: `requirement`）
    - `directories.specification`: 仕様ディレクトリ（デフォルト: `specification`）
    - `directories.task`: タスクログディレクトリ（デフォルト: `task`）

### 変更

#### プラグイン設定

- `plugin.json` - author フィールドを拡張
    - `author.url` フィールドを追加

#### コマンド

- すべてのコマンドに `allowed-tools` フィールドを追加
    - 各コマンドで利用可能なツールを明示的に指定
    - セキュリティと明確性を向上
- すべてのコマンドが `.sdd-config.json` 設定ファイルをサポート

#### スキル

- スキルディレクトリ構造を改善
    - `skill-name.md` から `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosure パターンを適用
    - テンプレートファイルを外部化し、SKILL.md を簡素化

### 削除

#### フック

- `check-spec-exists` - 削除
    - 仕様書の作成はオプションであり、非存在は一般的な有効なケース
- `check-commit-prefix` - 削除
    - コミットメッセージ規約はプラグイン機能で使用されないため削除

## [1.1.0] - 2025-12-06

### 追加

#### コマンド

- `/sdd_init` - AI-SDD ワークフロー初期化コマンド
    - プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
    - `.docs/` ディレクトリ構造を作成（requirement-diagram/、specification/、review/）
    - `sdd-templates` スキルを使用してテンプレートファイルを生成

#### スキル

- `sdd-templates` - AI-SDD テンプレートスキル
    - PRD、仕様書、設計書のフォールバックテンプレートを提供
    - プロジェクトテンプレート優先ルールを明確化

### 変更

#### プラグイン設定

- `plugin.json` - author フィールドを拡張
    - `author.url` フィールドを追加

#### コマンド

- すべてのコマンドに `allowed-tools` フィールドを追加
    - 各コマンドで利用可能なツールを明示的に指定
    - セキュリティと明確性を向上

#### スキル

- スキルディレクトリ構造を改善
    - `skill-name.md` から `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosure パターンを適用
    - テンプレートファイルを外部化し、SKILL.md を簡素化

## [1.0.1] - 2025-12-04

### 変更

#### エージェント

- `spec-reviewer` - 前提条件セクションを追加
    - 実行前に `sdd-workflow:sdd-workflow` エージェントコンテンツを読み取る指示を追加
    - AI-SDD 原則、ドキュメント構造、永続性ルール、Vibe Coding 防止の理解を促進

#### コマンド

- すべてのコマンドに前提条件セクションを追加
    - `generate_prd`、`generate_spec`、`check_spec`、`task_breakdown`、`review_cleanup`
    - 実行前に `sdd-workflow:sdd-workflow` エージェントコンテンツを読み取る指示を追加
    - sdd-workflow エージェント原則に従った一貫した動作を確保

#### スキル

- すべてのスキルに前提条件セクションを追加
    - `vibe-detector`、`doc-consistency-checker`
    - 実行前に `sdd-workflow:sdd-workflow` エージェントコンテンツを読み取る指示を追加

#### フック

- `check-spec-exists.sh` - パス解決を改善
    - `git rev-parse --show-toplevel` を使用してリポジトリルートを動的に取得
    - git リポジトリでない場合は現在のディレクトリにフォールバック
- `check-spec-exists.sh` - テストファイル除外パターンを拡張
    - Jest: `__tests__/`、`__mocks__/`
    - Storybook: `*.stories.*`
    - E2E: `/e2e/`、`/cypress/`
- `settings.example.json` - セットアップ手順をコメントとして追加
    - パスを `./hooks/` 形式に修正

#### スキル

- `vibe-detector` - `allowed-tools` に `AskUserQuestion` を追加
    - ユーザー確認フローをサポート
- `doc-consistency-checker` - `allowed-tools` に `Bash` を追加
    - ディレクトリ構造検証をサポート

## [1.0.0] - 2024-12-03

### 追加

#### エージェント

- `sdd-workflow` - AI-SDD 開発フロー管理エージェント
    - フェーズ判定（仕様化 → 計画 → タスク → 実装 & レビュー）
    - Vibe Coding 防止（曖昧な指示の検出と明確化の促進）
    - ドキュメント整合性チェック
- `spec-reviewer` - 仕様品質レビューエージェント
    - 曖昧な記述の検出
    - 欠落セクションの特定
    - SysML 準拠チェック

#### コマンド

- `/generate_prd` - ビジネス要件から SysML 要件図形式の PRD（要求仕様書）を生成
- `/generate_spec` - 入力から抽象仕様書と技術設計書を生成
    - PRD 整合性レビュー機能
- `/check_spec` - 実装コードと仕様書の整合性をチェック
    - 多層チェック: PRD ↔ spec ↔ design ↔ implementation
- `/task_breakdown` - 技術設計書からタスクを分解
    - 要件カバレッジ検証
- `/review_cleanup` - 実装後の review/ ディレクトリをクリーンアップ

#### スキル

- `vibe-detector` - Vibe Coding（曖昧な指示）の自動検出
- `doc-consistency-checker` - ドキュメント間の整合性自動チェック

#### 統合

- Serena MCP オプション統合
    - セマンティックコード分析による機能強化
    - 30以上のプログラミング言語をサポート
    - 設定されていない場合はテキストベース検索にフォールバック
