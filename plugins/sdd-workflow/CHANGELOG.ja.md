# 変更履歴

このプラグインの重要な変更はすべてこのファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
このプロジェクトは [Semantic Versioning](https://semver.org/lang/ja/spec/v2.0.0.html) に準拠しています。

[English CHANGELOG](CHANGELOG.md)

## [Unreleased]

## [4.0.0] - 2026-07-16

### Added

#### Agents

- **`cross-prd-reviewer`** - 複数 PRD 間の整合性をレビューする新規エージェント
    - カテゴリ境界の整合（スコープ外の相互参照）、用語集間の用語統一、構成・記法スタイルの一貫性、
      CONSTITUTION.md 原則参照カバレッジ、front matter の付け方の整合を検査
    - 指摘は [must]/[recommend]/[nits] で分類。単一 PRD の品質レビューは従来どおり prd-reviewer が担当
    - 出力テンプレート `templates/{en,ja}/cross_prd_review_output.md` を追加

#### Configuration

- **`.sdd-config.json` の `index`** - セッション開始時に構築される `.sdd` ドキュメント圧縮インデックスを
  制御する真偽値の設定を追加。トークン消費を削減する
    - **デフォルトで有効**（`true`）。`"index": false` で無効化できる
    - 自動生成される `.sdd-config.json` にも発見性向上のため `"index": true` を明示的に含める
    - **インデックス抽出の拡充** - インデックスが SysML 要求図とデータモデルのフィールドまでカバー
      するようになり、従来は生 Read が必要だった SysML trace 軸もトークン削減インデックスの対象になった

### Changed

#### Configuration

- **`.sdd-config.json` の `index`** - 値の形式を**真偽値専用**（`true`/`false`）に統一。従来の文字列形式
  （`"on"`/`"off"`）は非対応となった。真偽値以外の値は警告を出して既定（on）にフォールバックする
    - デフォルトを **off から on** に変更。トークン削減インデックスが標準で構築される

#### Hooks

- **`PreToolUse`** - Write/Edit 対象が実装コードの場合に `.sdd/CONSTITUTION.md` の原則を
  `additionalContext` として注入
    - コンテキスト肥大化を防ぐため、注入はプロジェクト内のソースファイル編集に限定し、
      セッションごとに最大1回、3000文字で切り詰めて注入する
    - CONSTITUTION.md が存在しない場合は何も注入しない

#### Agents

- **`front-matter-reviewer`** - `model` を `sonnet` から `haiku` に変更
    - ルールベースのフォーマット検証は複雑な推論を必要としないため、軽量モデルによりコストとレイテンシを削減
    - 他のエージェント（prd-reviewer, spec-reviewer, requirement-analyzer, clarification-assistant）は
      ドキュメント横断の整合性推論が必要なため `sonnet` を維持

#### Skills

- **モデルティア** - 機械的・ルールベースのスキルのモデルを引き下げ、コストとレイテンシを削減
    - `generate-requirements-diagram` / `generate-usecase-diagram` - `agent` を `sonnet` から `haiku` に変更
    - `recommend-front-matter` / `run-checklist` / `sdd-init` / `task-cleanup` - `agent: haiku` を宣言
- **`sdd-init`** / **SessionStart フック** - 常時ロードされる `CLAUDE.md` から AI-SDD 詳細ガイドを
  パススコープ付きルール `.claude/rules/ai-sdd-instructions.md`（`.sdd/**` に触れたときのみロード）へ移行し、
  `.sdd/` 以外の作業時のコンテキスト消費を削減
    - `CLAUDE.md` には宣言・トリガー条件・ルールへのポインタのみを残し、約90行のディレクトリ構造・
      命名規則・リンク規約ブロックをルールファイルへ移動
    - ルールファイルは SessionStart フック（`session-start.py`）が自動生成・バージョン同期する。
      `/sdd-init`（`update-claude-md.sh`）は最小化された `CLAUDE.md` セクションのみを管理
    - ルールは `SDD_LANG` に関わらず英語の単一ファイル（人間向けではなく AI 向けガイダンス）とし、
      言語別ファイルが同時にロードされる問題を回避

#### Skills

- `arguments` frontmatter フィールドによる名前付きスキル引数を導入（Claude Code v2.1.199+）
    - 8スキル（`task-breakdown`, `implement`, `clarify`, `check-spec`, `checklist`, `run-checklist`,
      `task-cleanup`, `plan-refactor`）が `feature-name` / `ticket-number` を名前付き位置引数として宣言し、
      本文で `$name` 置換構文により参照するよう移行
    - 自由文入力のスキル（`generate-spec`, `generate-prd` 等）は従来どおり `$ARGUMENTS` 全体を解釈
    - 各スキル本文にフォールバックを明記: 値が空・未置換・位置的に捕捉されたフラグ（`--...`）の場合は
      引数文字列全体の解釈または対話的な確認にフォールバックし、v2.1.199 未満の挙動を維持

### Added

#### Hooks

- `hooks.json` を `SessionStart` 以外に拡張
    - **`UserPromptSubmit`** (`scripts/user-prompt-submit.py`) - ユーザープロンプト中の Vibe Coding 兆候
      （「いい感じに」等の曖昧な指示）を検知し、vibe-detector スタイルの明確化フローを促す追加コンテキストを注入
      （検知のみで、ブロックは行わない）
    - **`PreToolUse`** (`scripts/pre-tool-use.py`, matcher `Write|Edit|MultiEdit`) - `.sdd/` 配下への書き込み前に
      AI-SDD ファイル命名規則（requirement: サフィックスなし、specification: `_spec.md` / `_design.md` 必須）を
      検証し、違反する書き込みをブロック
    - **`PostToolUse`** (`scripts/post-tool-use.py`, matcher `Write|Edit|MultiEdit`) - ドキュメント更新漏れの
      可能性を検知: `.sdd/` ドキュメント編集後に整合性チェックの実行を促し、対応する `*_design.md` を持つ
      ソースファイル編集後に設計書の同期を促す

#### Agents

- **`requirement-analyzer`** - ID採番バリデーションを追加（`--validate-ids`、`--analyze` の一部としても実行）
    - 設定可能な正規表現パターン（`.sdd-config.json` の `id_conventions` セクション）による命名規約検証
    - ID順序の乱れに対する移動提案を含む昇順検証
    - 採番の欠番検出とリネーム後の旧ID残存検出
    - `requirement_analysis_output` テンプレート（en/ja）に「ID採番バリデーション」セクションを追加

#### Documentation

- **`AI-SDD-PRINCIPLES`** - `.sdd-config.json` のオプション `id_conventions` セクションを文書化

#### Skills

- **`check-spec`** (v3.1.0) - 整合性チェックをリテラル値まで拡張
    - 仕様書の「値域・閾値レジストリ」（Schema Registry）セクションが存在する場合はそれをパースし、ない場合は
      spec/design 本文からのリテラル値抽出にフォールバック
    - 実装側のリテラル値を設定ファイル、ORM の CHECK 制約、バリデーション制約（例: Pydantic）、
      言語固有の enum / 定数から抽出
    - spec / design / 実装間の値の乖離を検出し Warning として報告
      （例: spec `0.7` vs `config.py` `0.6`）
    - enum / CHECK 制約のメンバー集合の完全性と要求IDトレースの完全性（PRD <-> spec <-> design）を検証
    - 出力テンプレート（en/ja）に値乖離セクションを追加
- **`generate-spec`** - 設計書テンプレート（`templates/{en,ja}/design_template.md`）に「Pseudocode完全性ルール」セクションを追加
    - 設計書の擬似コードをそのままコピー可能に保つための言語別ガイダンス（Python 汎用 / Pydantic v2 / SQLAlchemy & alembic）
    - 追加言語（TypeScript / Go / Rust 等）向けに拡張可能なサブセクション構造

### Fixed

- **`.sdd-config.json` の `root`（およびディレクトリ名）のカスタム設定がプラグイン全体で尊重されるようになった。** 従来は多くのパスが既定の `.sdd/` にハードコードされており、カスタム root を使うプロジェクトで暗黙的に壊れていた。
    - `session-start.py` が生成するパススコープ付きルールの `paths:` グロブに設定 root を置換。カスタム root（例: `.ai-docs/`）配下でも `.claude/rules/ai-sdd-instructions.md` が自動ロードされる（グロブが `.sdd/**` 固定だったリグレッションも解消）
    - `update-claude-md.sh` が生成する `CLAUDE.md` セクションに設定 root を置換
    - skill/agent プロンプトと出力テンプレートは、リテラル `.sdd/...` ではなく `${SDD_ROOT}` / `${SDD_*_PATH}` で SDD パスを解決
    - `find-design-docs.sh` / `validate-files.sh` はキャッシュを設定 root 配下に出力。`pre-tool-use.py` の命名違反メッセージは設定ディレクトリパスを表示
- **`post-tool-use.py`** - `.sdd/requirement/` または `.sdd/specification/` 配下のファイル編集後に表示される
  advisory ヒントが、`doc-consistency-checker` スキルに加えて `/constitution validate` の実行も提案するよう
  になり、生成・編集後に CONSTITUTION.md の原則違反を検知しやすくなった
- **`doc-consistency-checker`** - `design ↔ 実装` チェック（旧 spec FR-004）を削除。`impl-spec-check`
  （`/check-spec`）と責務が重複しており、親 PRD が明示的にスコープ外と定義していた領域と矛盾していた。
  `design ↔ 実装` の整合性チェックは `/check-spec` に一本化される
- **生成成果物へのセクション必須度マーカー残留を防止** - 著者向けのセクション必須度マーカー
  （`<MUST>` / `<RECOMMENDED>` / `<OPTIONAL>`）が生成ドキュメントに残らないようにした。`generate-spec` は
  最終出力の見出しからこれらを除去し、`prd-reviewer` / `spec-reviewer` に残留マーカーを検出する
  「No Marker Residue」チェックを追加

## [3.3.0] - 2026-03-02

### Changed

#### Hooks

- **`session-start`** - `session-start.sh`（Bash）を `session-start.py`（Python 3.7+）に移行
    - Python 標準の `json` モジュールの使用により `jq` 依存を排除
    - `--default-lang` 引数により `sdd-workflow` と `sdd-workflow-ja` でスクリプトを統一
    - `sdd-workflow-ja/scripts/` は `sdd-workflow/scripts/` へのシンボリックリンクに変更（重複排除）
    - 不正な `.sdd-config.json` に対するエラーハンドリングを追加（デフォルト値への graceful fallback）
    - Python 3.7+ が必要（`dataclasses` と `subprocess.run(capture_output=True)` のため）

#### Documentation

- `sdd-workflow` プラグインの日本語 README として `README.ja.md` を追加
- 独立した `sdd-workflow-ja/README.md` を削除（現在は `sdd-workflow/README.ja.md` へのシンボリックリンク）
- ルート `README.md` に CI バッジとライセンスバッジを追加

## [3.2.1] - 2026-02-26

### Fixed

#### Hooks

- **`hooks.json`** - Claude Code Issue [#24529](https://github.com/anthropics/claude-code/issues/24529) のワークアラウンド
    - フック実行時に `CLAUDE_PLUGIN_ROOT` が環境変数として設定されない問題
    - フックコマンド内で `CLAUDE_PLUGIN_ROOT` を明示的に設定し、`session-start.sh` 内で利用可能に
    - 変更前: `source ${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh`
    - 変更後: `CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT} source ${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh`

## [3.2.0] - 2026-02-25

### Added

#### Skills

- **`recommend-front-matter`** - 既存ドキュメントへの YAML front matter 追加を推奨する新スキル
    - すべての AI-SDD ドキュメント（PRD, spec, design, task）の front matter 有無をスキャン
    - 推定メタデータ（id, title, type, status, depends-on, tags, category）付きの推奨を生成
    - ユーザー確認後の `--apply` オプションによる自動適用をサポート
    - バイリンガルのレポートテンプレート（en/ja）を提供
    - ドキュメントスキャンスクリプト（`scan-documents.sh`）を同梱

#### Agents

- **`front-matter-reviewer`** - AI-SDD ドキュメントの YAML front matter を検証する新エージェント
    - フィールド形式、依存方向、ステータス値、種別固有フィールドをチェック
    - 相互参照の整合性と id の一意性を検証
    - ドキュメント生成後や整合性チェック時に使用

#### Shared References

- **`shared/references/`** - YAML front matter リファレンスドキュメントを追加
    - `front_matter_reference.md` - front matter フィールドの包括的リファレンス
    - `front_matter_prd.md` - PRD 固有の front matter ガイド
    - `front_matter_spec_design.md` - spec/design 固有の front matter ガイド
    - `front_matter_task.md` - タスク固有の front matter ガイド
    - `front_matter_impl.md` - 実装ログ固有の front matter ガイド

### Removed

#### Skills

- **`sdd-migrate`** - レガシーマイグレーションスキルを削除（v1.x → v2.0.0 ディレクトリ構造移行用）
    - 現在のユーザーにはマイグレーション機能が不要になったため
    - メンテナンスコストとコードの複雑さを削減

#### Hooks

- **`session-start.sh`** - レガシーディレクトリ構造の検出と自動マイグレーションロジックを削除
    - `.sdd-config.json` の生成をデフォルト値のみに簡素化
    - 29〜82行目（レガシー検出とマイグレーション警告）を削除

#### Documentation

- **`sdd-init/SKILL.md`** - v3.0.0 マイグレーション（`lang` フィールド追加）への参照を削除

## [3.1.1] - 2026-02-23

### Changed

#### Hooks

- **`session-start.sh`** - POSIX 互換性と堅牢性を改善
    - スクリプト冒頭に `CLAUDE_PLUGIN_ROOT` のガードチェックを追加
    - `&> /dev/null` を POSIX 互換の `>/dev/null 2>&1` に置換
    - echo 文から不要な `>&2` リダイレクトを削除
    - principles コピー時の `CLAUDE_PLUGIN_ROOT` 存在チェックを簡素化

#### Skills

- **`plan-refactor`** - テンプレート/リファレンスファイルのパス参照を snake_case に修正
    - `refactor-plan-section.md` → `refactor_plan_section.md`
    - `reverse-design-template.md` → `reverse_design_template.md`
    - `reverse-spec-template.md` → `reverse_spec_template.md`
    - `design-doc-integration.md` → `design_doc_integration.md`
    - `templates/` と `references/` の実ファイル名も一致するようにリネーム

## [3.1.0] - 2026-02-15

### Added

- **plan-refactor スキル** - 既存機能のリファクタリング計画を支援する新スキル
    - 現在の実装を分析し、リファクタリング計画を含む設計書を作成・更新
    - 2つのシナリオをサポート: ケースA（既存ドキュメントあり）とケースB（ドキュメントなし）
    - 日英両言語のテンプレート、サンプル、リファレンスドキュメントを提供
    - リファクタリングパターンのリファレンス（Extract Interface, Dependency Injection 等）を同梱
    - 実装ファイル検索スクリプト（`find-implementation-files.sh`）
    - 既存ドキュメントスキャンスクリプト（`scan-existing-docs.sh`）
- **エージェントのサンプルとリファレンスドキュメント** - 使いやすさを改善
    - `clarification-assistant`: 使用例と明確化ワークフローのリファレンスを追加
    - `prd-reviewer`: 使用例を追加
    - `requirement-analyzer`: 使用例を追加
    - `spec-reviewer`: 使用例を追加
    - 全エージェント向けに stop report フォーマットテンプレート（en/ja）を追加
    - ディレクトリ構造リファレンスと修正提案フローリファレンスを追加
- **SKILL.md の argument-hint** - 全スキルに `argument-hint` フィールドを追加し引数仕様を明確化

### Changed

- **/constitution init** - 非対話モード初期化用のコンテキスト引数を追加
    - `[context]` 引数を指定すると、対話なしでプロジェクトコンテキストに基づく原則を生成
    - 引数なしの場合は従来どおり対話モードで実行
- **エージェント設定ファイル** - コードブロック抽出精度を高めるため Markdown 形式を改善
    - clarification-assistant: 冗長な説明を削減しより簡潔な構造に（103行削減）
    - prd-reviewer: ワークフロー説明を整理
    - requirement-analyzer: 分析フロー説明を改善
    - spec-reviewer: レビュープロセス説明を整理

### Fixed

- **plan-refactor テンプレートの言語中立化** - 特定技術への依存を排除
    - `reverse-design-template.md`: TypeScript, React, PostgreSQL 等の具体例を削除
    - `reverse-design-template.md`: 言語固有のコードブロック（typescript, sql）を削除
    - API エンドポイントセクション: サンプル行を削除しテーブルヘッダーのみに簡素化
    - データベーススキーマセクション: 実装からの逆生成が不可能なため完全に削除
    - 関数シグネチャセクション: TypeScript 固有の内容のため完全に削除
    - プレースホルダーを説明的なガイダンス形式に変更（例: `{e.g., TypeScript}` →
      `{Programming language used in the project}`）

## [3.0.2] - 2026-02-09

### Fixed

- **`sdd-init`** - `.sdd-config.json` からの言語設定継承を修正
    - `update-claude-md.sh` が環境変数に依存せず `.sdd-config.json` から直接 `SDD_LANG` を読み取るように変更
    - 従来、`.sdd-config.json` に `lang: "ja"` が設定されていても、`CLAUDE.md` の `## AI-SDD Instructions`
      セクションが誤って英語で生成されていた
    - 根本原因: `init-structure.sh` による `CLAUDE_ENV_FILE` への書き込みが、同一シェルセッション内で
      `update-claude-md.sh` 実行時に反映されていなかった

## [3.0.1] - 2026-02-09

### Added

#### 新スキル（PRD 生成ワークフロー）

- **`/generate-usecase-diagram`** - ユースケース図生成スキル
    - ビジネス要求から Mermaid flowchart ベースのユースケース図を生成
    - コンテキスト分離のための `context: fork`
    - 対話モードと CI（`--ci`）モードをサポート
    - テキストのみを返す（ファイル書き込みなし）

- **`/analyze-requirements`** - 要求分析スキル
    - UR（ユーザー要求）、FR（機能要求）、NFR（非機能要求）を抽出
    - コンテキスト分離のための `context: fork`
    - MoSCoW 優先度付けとリスク評価をサポート
    - テキストのみを返す（ファイル書き込みなし）

- **`/generate-requirements-diagram`** - SysML 要求図生成スキル
    - 要求分析から Mermaid requirementDiagram を生成
    - コンテキスト分離のための `context: fork`
    - 要求間関係（contains, derives, traces）をサポート
    - テキストのみを返す（ファイル書き込みなし）

- **`/finalize-prd`** - PRD 統合スキル
    - ユースケース図、要求分析、要求図を統合して完全な PRD を生成
    - コンテキスト分離のための `context: fork`
    - PRD テンプレート構造に準拠
    - テキストのみを返す（ファイル書き込みなし）

#### スキル強化

- **`sdd-init`** - `.sdd-config.json` の `lang` フィールドの自動管理を追加
    - 設定ファイルが存在しない場合: デフォルト設定（`lang: "en"` を含む）で作成
    - 設定ファイルが存在するが `lang` フィールドがない場合（v3.0.0 からの移行）: `lang: "en"` を追加
    - 実行フローにステップ 1.5「設定ファイルの管理」を追加
    - シェルスクリプトを追加: `init-structure.sh`, `update-claude-md.sh`

- **`check-spec`** - ファイルスキャン用シェルスクリプトを追加
    - `scripts/find-design-docs.sh` - 設計書を事前スキャンし Claude の Glob/Grep オーバーヘッドを削減

- **`constitution`** - 検証用シェルスクリプトを追加
    - `scripts/validate-files.sh` - 検証用に requirement/spec/design ファイルを事前スキャン

- **`generate-spec`** - 準備用シェルスクリプトを追加
    - `scripts/prepare-spec.sh` - 仕様書生成用にファイルを前処理

#### Documentation

- **Mermaid 記法ガイドに注記を追加**
    - `<` と `>` を含むラベル（`<<include>>` 等）は HTML エンティティでエスケープが必要
    - 例: `<<include>>` を表示するには `&lt;&lt;include&gt;&gt;` と記述する

- **Progressive Disclosure 用のリファレンスファイルを追加**
    - `clarify/references/nine_category_analysis.md` - 9カテゴリ分析の定義
    - `constitution/references/best_practices.md` - Constitution のベストプラクティス
    - `constitution/examples/validation_report.md` - 検証レポートの例

### Changed

#### スキルアーキテクチャ

- **`generate-prd`** - オーケストレーターパターンにリファクタリング
    - 4つのサブスキルをオーケストレート: `/generate-usecase-diagram`, `/analyze-requirements`,
      `/generate-requirements-diagram`, `/finalize-prd`
    - サブスキルはコンテキスト分離のため `context: fork` で実行
    - サブスキルはテキストのみを返し、ファイル書き込みは `generate-prd` が担当
    - SKILL.md を 374 行から 140 行に削減
    - ワークフロー追跡用の Progress Checklist を追加

- **全スキル** - Claude Code Skills ベストプラクティスへの準拠
    - 全スキルに `$ARGUMENTS` プレースホルダーと `## Input` セクションを追加
    - `allowed-tools` が未設定のフロントマターに追加
    - 出力前の `Quality Checks` セクションを追加
    - SKILL.md ファイルを 500 行以下に維持（Progressive Disclosure パターン）
    - 詳細な内容を `references/` および `examples/` ディレクトリに移動

- **`constitution`** - 558 行から 392 行に削減
    - 検証レポートの例を `examples/validation_report.md` に移動
    - ベストプラクティスを `references/best_practices.md` に移動

- **`clarify`** - 行数を削減
    - 9カテゴリ分析を `references/nine_category_analysis.md` に移動

#### Shared References

- **`usecase_diagram_guide.md`** - ユースケース図の関係記法を UML 標準に修正
    - 関連（Association）: `-->` → `---`（実線・双方向）
    - 包含（Include）: `-. include .->` → `-.->|"<<include>>"|`（ステレオタイプラベル付き点線矢印）
    - 拡張（Extend）: `-. extend .->` → `-.->|"<<extend>>"|`（ステレオタイプラベル付き点線矢印）
    - Common Mistakes テーブルを更新
    - すべての Mermaid コード例を新記法に更新

- **`mermaid_notation_rules.md`** - ユースケース図記法を更新
    - 関連の記法を `---` に修正
    - Include/Extend のラベル形式を更新
    - Common Mistakes セクションを更新

#### Templates

- **`generate-prd`** - PRD テンプレートのユースケース図記法を修正
    - `templates/en/prd_template.md`: 関連、Include、Extend の記法を更新
    - `templates/ja/prd_template.md`: 同様の修正（日本語ラベル `<<包含>>`、`<<拡張>>` を維持）

## [3.0.0] - 2026-02-06

### Added

#### 新スキル

- **`/run-checklist`** - 品質検証自動化スキル
    - `/checklist` で生成されたチェックリスト項目の検証コマンドを自動実行
    - テスト、リンター、セキュリティスキャナー、仕様整合性チェックを実行
    - カテゴリ（`--category`）と優先度（`--priority`）によるフィルタリングをサポート
    - 進捗追跡のための TaskList 統合
    - チェックリストファイルに結果をタイムスタンプ付きで直接記録
    - `.sdd/task/{ticket}/verification_report.md` に検証レポートを生成

#### Shared References

- **`shared/references/`** - リファレンスドキュメントの一元化
    - `mermaid_notation_rules.md` - 包括的な Mermaid 構文ガイド（1100行以上）
        - フローチャート、シーケンス図、クラス図、状態遷移図、ER図、要求図、ガント図の構文
        - エスケープルール、スタイリング、よくある落とし穴
    - `usecase_diagram_guide.md` - Mermaid 用ユースケース図ガイド（750行以上）
        - アクター、ユースケース、システム境界の定義
        - 関係の種類（関連、包含、拡張、汎化）
        - スタイリングとレイアウトのベストプラクティス
    - `requirements_diagram_components.md` - SysML 要求図コンポーネント（800行以上）
        - 属性付き要求要素の定義（id, text, risk, verifyMethod）
        - 関係の種類（containment, derivation, refinement, satisfaction, verification）
        - Mermaid 構文の例とテンプレート
    - `document_dependencies.md` - ドキュメント依存チェーンのリファレンス
    - `prerequisites_directory_paths.md` - SDD 環境変数リファレンス
    - `prerequisites_plugin_update.md` - プラグイン更新チェック手順
    - `prerequisites_principles.md` - AI-SDD 原則リファレンス

#### エージェント構造の改善

- **エージェント出力テンプレート** - 全エージェント向けの言語別テンプレート
    - `agents/templates/en/` - 英語出力テンプレート
    - `agents/templates/ja/` - 日本語出力テンプレート
    - テンプレート: `clarification_analysis_output.md`, `clarification_question_template.md`, `prd_review_output.md`,
      `requirement_analysis_output.md`, `spec_review_output.md`
- **エージェントリファレンス** - 再利用可能なリファレンスドキュメント
    - `agents/references/ambiguity_patterns.md` - 曖昧表現パターン
    - `agents/references/document_link_convention.md` - Markdown リンク規約
    - `agents/references/sysml_requirements_theory.md` - SysML 要求理論
    - 共有リファレンスへのシンボリックリンク: `mermaid_notation_rules.md`, `requirements_diagram_components.md`,
      `usecase_diagram_guide.md`
- **エージェント使用例** - 使用例の追加
    - `agents/examples/clarification_questions.md` - 明確化質問の例

#### スキル構造の改善

- 全スキルに共有リファレンスへのシンボリックリンクを持つ **`references/` ディレクトリを追加**
    - スキル間で一貫した前提条件の取り扱いを実現
    - 前提条件ドキュメントの重複を削減
- 使用例を持つスキルに **`examples/` ディレクトリを追加**
    - `check-spec/examples/` - scope_confirmation.md, serena_symbol_analysis.md
    - `checklist/examples/` - checklist_full_example.md
    - `constitution/examples/` - constitution_as_code.json, constitution_file_structure.md, principle_template.md
    - `generate-spec/examples/` - compliance_check_design.md, compliance_check_spec.md, prd_reference_section.md
    - `implement/examples/` - implementation_progress_log.md, input_format.md, option_* ファイル, output_* ファイル
    - `task-breakdown/examples/` - requirement_coverage.md, serena_analysis.md, task_list_format.md
    - `task-cleanup/examples/` - scope_confirmation.md

### Changed

#### Skills

- **全スキルをリファクタリング** し、シンボリックリンク経由で共有リファレンスを使用
    - 前提条件は `references/prerequisites_*.md` シンボリックリンクを参照
    - メンテナンスコストを削減し一貫性を確保
- **`implement` スキル** - リファレンスとテンプレートファイルを大幅追加
    - `references/commit_strategy.md`, `five_phases_overview.md`, `tdd_principles.md` 等
    - `templates/{en,ja}/phase_*.md` - フェーズ実行テンプレート
    - `templates/{en,ja}/tasklist_patterns.md` - TaskList 統合パターン
- **`generate-prd` スキル** - Mermaid 図のリファレンスを追加
    - `mermaid_notation_rules.md`, `usecase_diagram_guide.md`, `requirements_diagram_components.md` へのリンク
- **`doc-consistency-checker` スキル** - ドキュメント依存関係リファレンスを追加

#### Agents

- **全エージェントを Progressive Disclosure パターンでリファクタリング**
    - エージェント Markdown ファイルは大きなコンテンツに `@reference` インポートを使用
    - 出力テンプレートを `templates/{en,ja}/` に外部化
- **`spec-reviewer`** - リファレンス活用により 566 行から約 200 行に簡素化
- **`prd-reviewer`** - リファレンス活用により 328 行から約 150 行に簡素化
- **`requirement-analyzer`** - リファレンス活用により 420 行から約 150 行に簡素化
- **`clarification-assistant`** - リファレンス活用により 626 行から約 200 行に簡素化

### Removed

#### Skills

- **`sdd-templates`** - 共有リファレンスと各スキルのテンプレートに統合
- **`output-templates`** - テンプレートを各スキルディレクトリに移動

#### レガシーコマンド

- **`commands/` ディレクトリを完全削除**
    - `commands/checklist.md` - `skills/checklist/SKILL.md` に移行
    - `commands/implement.md` - `skills/implement/SKILL.md` に移行
    - `commands/sdd_init.md` - `skills/sdd-init/SKILL.md` に移行

---

## [3.0.0-alpha] - 2026-02-03

### Breaking Changes

#### プラグイン統合

- **`sdd-workflow-ja` と `sdd-workflow` を単一の統合プラグイン（`sdd-workflow`）にマージ**
    - `SDD_LANG` 環境変数による言語選択（`.sdd-config.json` の `lang` フィールドから、デフォルト: `en`）
    - テンプレートを言語別に分割: `templates/ja/` と `templates/en/`
    - SKILL.md とエージェントファイルは英語のみ
    - `sdd-workflow-ja` プラグインを完全に削除

#### コマンドのスキル化

- **全 11 コマンドを `user-invocable: true` のスキルに移行**
    - `commands/` ディレクトリを完全に削除
    - すべてのコマンドは `skills/{name}/SKILL.md` 配下に配置

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

### Added

#### 多言語対応

- **`SDD_LANG` 環境変数** - テンプレート言語の選択を制御
    - `.sdd-config.json` の `lang` フィールドで設定
    - サポート値: `en`（デフォルト）、`ja`
    - `session-start.sh` が設定から `lang` を読み取り `SDD_LANG` をエクスポート

#### 言語別テンプレート

- 既存 4 スキルすべてに言語別テンプレートを追加:
    - `sdd-templates/templates/{en,ja}/`
    - `vibe-detector/templates/{en,ja}/`
    - `doc-consistency-checker/templates/{en,ja}/`
    - `output-templates/templates/{en,ja}/`
- 日本語テンプレートは旧 `sdd-workflow-ja` プラグインからコピー

### Changed

#### Skills

- **旧コマンドから 11 の新スキルを作成**:
    - `sdd-init`, `constitution`, `generate-spec`, `generate-prd`, `check-spec`
    - `task-breakdown`, `implement`, `clarify`, `task-cleanup`, `sdd-migrate`, `checklist`
    - 各スキルに適切な `allowed-tools`、`user-invocable: true`、必要に応じて `disable-model-invocation` を設定
- **既存 4 スキルを言語設定対応の v3.0.0 に更新**
    - 動的な `SDD_LANG` コンテキスト注入を行う `## Language Configuration` セクションを追加
    - テンプレートパス参照を `templates/en/` 形式に更新

#### Agents

- **spec-reviewer** - `skills` フィールドを追加: `["sdd-workflow:sdd-templates", "sdd-workflow:doc-consistency-checker"]`
- **prd-reviewer** - `skills` フィールドを追加: `["sdd-workflow:sdd-templates"]`
- 全 4 エージェントをハイフン形式のコマンド名参照に更新
- 全エージェントの説明を新コマンド名参照に更新

#### Configuration

- **`.sdd-config.json`** - 言語設定用の `lang` フィールドを追加
- **`session-start.sh`** - `SDD_LANG` の読み取りとエクスポートを追加
- **`plugin.json`** - 統合プラグインの説明とともに v3.0.0 に更新
- **`marketplace.json`** - `sdd-workflow-ja` エントリを削除、`sdd-workflow` を v3.0.0 に更新

#### Documentation

- **`CLAUDE.md`** - スキルを持つ単一プラグインを反映するようリポジトリ構成を更新
- **`README.md`** - v2.x からの移行ガイドを追加、全コマンド参照を更新

### Removed

- **`plugins/sdd-workflow-ja/`** - 日本語プラグインディレクトリ全体（`sdd-workflow` に統合）
- **`plugins/sdd-workflow/commands/`** - commands ディレクトリ全体（スキルに移行）

## [2.4.2] - 2026-01-26

### Fixed

#### プラグインマニフェスト

- **plugin.json から skills フィールドを削除** - プラグインインストールエラーを修正
    - Claude Code の plugin.json スキーマでサポートされていない `skills` フィールドを削除
    - スキルは `skills/` ディレクトリから自動検出される
    - インストール時の「Invalid input」エラーを解消

## [2.4.1] - 2026-01-26

### Fixed

#### Commands

- **argument-hint の修正と引数説明の追加** - 引数仕様を実際の使い方に合わせて修正
    - `argument-hint` の表現を統一（"file-path" → "feature-name" の修正）
    - 各コマンドに引数説明テーブルを追加（引数名、必須/任意、説明）
    - 対象コマンド:
        - `task_breakdown`: `<design-doc-path>` → `<feature-name> [ticket-number]`
        - `check_spec`: `<design-doc-path>` → `[feature-name] [--full]`
        - `checklist`: `<file-path>` → `<feature-name> [ticket-number]`
        - `clarify`: `[spec-file-path]` → `<feature-name> [--interactive]`
        - `constitution`: `<init|update|check>` → `<subcommand> [arguments]`（サブコマンド詳細テーブルを追加）
        - `generate_prd`: `<feature-name> [requirements-description]` → `<requirements-description>`
        - `generate_spec`: `<feature-name> [prd-file-path]` → `<requirements-description>`
        - `implement`: `<task-file-path>` → `<feature-name> [ticket-number]`
        - `task_cleanup`: `<ticket-number>` → `[ticket-number]`（任意に変更）
    - コマンド実行時に正しい引数形式を把握できるように

## [2.4.0] - 2026-01-25

### Added

#### Documentation

- **PLUGIN.md** - Claude Code プラグインとマーケットプレイス作成の包括的ガイド
    - プラグイン基本構造（ディレクトリレイアウト、マーケットプレイス構成）
    - マニフェストファイル（plugin.json, marketplace.json の詳細）
    - コマンド、エージェント、スキルの実装（フロントマター、ベストプラクティス）
    - MCP サーバー統合（外部ツール連携）
    - フック実装（イベント駆動の自動化）
    - マーケットプレイス公開プロセス（品質基準、配布モデル）
- **CLAUDE.md** - PLUGIN.md への参照を追加（PLUGIN_AGENTS.md と同様の構成）

#### Skills

- 全スキルに `version: 2.3.1` と `license: MIT` フィールドを追加
    - vibe-detector
    - doc-consistency-checker
    - sdd-templates
- **output-templates** - コマンド出力フォーマットを提供する新スキル
    - `init_output.md` - 初期化完了メッセージ
    - `prd_output.md` - PRD 生成完了メッセージ
    - `spec_output.md` - 仕様書・設計書生成完了メッセージ
    - `breakdown_output.md` - タスク分解結果
    - `cleanup_output.md` - クリーンアップ確認
    - `clarification_output.md` - 仕様明確化レポート
    - `check_spec_output.md` - 整合性チェック結果
    - `migrate_output.md` - マイグレーション結果
    - `constitution_output.md` - Constitution 管理結果

#### Commands

- 全コマンドに `argument-hint` フィールドを追加し使いやすさを改善
    - generate_spec: `<feature-name> [prd-file-path]`
    - generate_prd: `<feature-name> [requirements-description]`
    - check_spec: `<design-doc-path>`
    - task_breakdown: `<design-doc-path> [ticket-number]`
    - task_cleanup: `<ticket-number>`
    - constitution: `<init|update|check>`
    - implement: `<task-file-path>`
    - clarify: `[spec-file-path]`
    - checklist: `<file-path>`

### Changed

#### アーキテクチャ

- **出力フォーマットの分離** - コマンド出力フォーマットを `skills/output-templates/` に分離
    - コマンド md ファイルは Claude 向けの指示のみを含む
    - 出力フォーマットは独立したテンプレートファイルとして管理
    - 新スキル: `output-templates`（9 テンプレートファイルを含む）
    - 既存の `sdd-templates` スキルはプロジェクトドキュメントテンプレート専用に

#### Commands

- **implement** - TaskList ベースの進捗管理を追加
    - 各フェーズ開始時に TaskCreate でタスクを作成
    - フェーズ実行中に TaskUpdate でタスクステータスを更新（pending → in_progress → completed）
    - 依存関係を設定し、前フェーズ完了後にのみ次フェーズを開始
    - `/tasks` コマンドで実装進捗を確認可能
    - TaskList が利用できない場合は従来の Markdown 進捗表示にフォールバック

#### Marketplace

- **marketplace.json** の改善
    - `author.url` を追加（作成者の帰属表示）
    - `category: "development"` を追加（マーケットプレイスのフィルタリング）
    - `tags` 配列を追加（検索での発見性向上）
        - "specification-driven-development"
        - "japanese" / "english"
        - "workflow"
        - "sysml"
        - "requirements"
        - "documentation"

#### Agents

- 全エージェントの `description` を使用シナリオが明確になるよう改善
    - 機能説明スタイルから「いつ使うか」スタイルに変更
    - 具体的なトリガーフレーズを追加（例: "review spec", "check spec"）
    - コマンドとの関係を明示（例: /check_spec や /generate_spec 実行後）
    - 必要な入力情報を明記（例: 仕様書ファイルパスが必要）
    - 自己言及的な「agent」という表現を削除
    - 対象エージェント: spec-reviewer, requirement-analyzer, prd-reviewer, clarification-assistant

#### Skills

- 全スキルの `description` を実行コンテキストが明確になるよう改善
    - 実行タイミングを明記（例: 実装前に自動実行、コマンドから呼び出し）
    - 検知内容の詳細を明記（例: 「いい感じに」「なんとなく」等の曖昧表現）
    - トレーサビリティ保証を明示
    - フォールバック動作の詳細な説明
    - 対象スキル: vibe-detector, doc-consistency-checker, sdd-templates

### Fixed

#### Commands

- **プロンプト表現の統一** - ユーザー向け説明を削除し、Claude 向けの明確な指示に統一
    - 「Next Steps」リスト項目を削除（「Post-Generation Actions」セクション内のプレーンテキストから）
    - 「Recommended Manual Verification」セクションを削除（出力テンプレートに移動）
    - 「manually」表現を Claude 向けの指示に変更（例: 「ユーザーに手動検証を推奨する」）
    - 出力フォーマット参照方法を統一（ファイルパスからスキル参照へ）
    - 対象コマンド: `sdd_init`, `generate_prd`, `generate_spec`, `task_breakdown`, `task_cleanup`, `clarify`,
      `check_spec`, `sdd_migrate`, `constitution`

#### Agents

- **プロンプト表現の統一** - 「recommended」表現を指示形に変更
    - spec-reviewer: "recommended to be added" → "need to be added"
    - clarification-assistant: "Supplementation recommended" → "Supplementation needed"
    - clarification-assistant: "Recommended Clarity Scores" → "Clarity Score Evaluation Criteria"

## [2.3.1] - 2026-01-14

### Fixed

#### Hooks

- `session-start.sh` - 一時ファイル存在チェックによるエラーハンドリングの改善
    - sed コマンド失敗時の `mv: No such file or directory` エラーを修正
    - mv 実行前に一時ファイルの存在を確認する `&& [ -f "$TEMP_FILE" ]` を追加
    - フォールバック処理が正しく動作するよう改善
    - 日本語版との一貫性のため、英語版に警告ファイル削除処理（else 節）を追加

## [2.3.0] - 2026-01-09

### Changed

#### Agents

- **役割分離**: `sdd-workflow` エージェントを `AI-SDD-PRINCIPLES.md` にリネーム
    - 原則定義を独立したドキュメントに分離
    - 全コマンド、エージェント、スキルの参照を `../AI-SDD-PRINCIPLES.md` に更新
    - AI-SDD 原則を一元化しメンテナンス性を向上

- `spec-reviewer` - ドキュメントトレーサビリティチェック機能を追加
    - **PRD ↔ spec トレーサビリティチェック**: PRD の要求が spec で適切にカバーされているかを検証
        - 要求 ID（UR/FR/NFR）のマッピング検証
        - カバレッジ率の計算（80% 閾値チェック）
        - 部分的/未カバーの分類
    - **spec ↔ design 整合性チェック**: spec の内容が design で適切に詳細化されているかを検証
        - API 定義の詳細化チェック
        - 型定義の整合性チェック
        - 制約の考慮チェック
    - `allowed-tools` に `Edit` を追加（自動修正サポート用）
    - 入力フォーマットと出力フォーマットを明確化（`--summary` オプションをサポート）

#### Commands

- `/check_spec` - **design ↔ 実装の整合性チェックに特化**
    - **[BREAKING]** ドキュメント間の整合性チェック（PRD↔spec, spec↔design）を `spec-reviewer` に委譲
        - **変更前 (v2.2.0)**: すべての整合性チェックを実行（CONSTITUTION↔docs, PRD↔spec, spec↔design,
          design↔実装）
        - **変更後 (v2.3.0)**: design↔実装の整合性チェックのみ実行（パフォーマンス改善）
        - **移行方法**:
            - ドキュメント間の整合性チェックが必要な場合: `/check_spec --full` を使用
            - design↔実装のみで十分な場合: 従来どおり `/check_spec` を使用（コマンドは同じ）
        - **影響**: CI/CD パイプラインで `/check_spec` を使用している場合は `--full` オプションの追加を検討
    - `--full` オプションを追加: 整合性チェックに加えて `spec-reviewer` による包括的レビューを実行
    - 対象ドキュメントを `*_design.md` に限定
    - 出力フォーマットを簡素化（design↔実装に焦点）

- `/sdd_init` - 参照パスを更新
    - エージェント参照を `AI-SDD-PRINCIPLES.md` に変更

### Added

#### Documentation

- `AI-SDD-PRINCIPLES.md` - AI-SDD 原則を定義する独立ドキュメント
    - 従来 `sdd-workflow` エージェントに含まれていた原則定義を分離
    - コマンド、エージェント、スキルから共通で参照

#### README

- Windows プラットフォーム非対応を文書化
    - プラットフォームサポートマトリクスを追加（macOS/Linux: ✅、Windows: ❌）
    - Windows ユーザー向けの代替案を記載（WSL, Git Bash）
    - 今後のサポート計画（PowerShell 版、クロスプラットフォーム実装を検討中）

## [2.2.0] - 2026-01-06

### Added

#### Agents

- `prd-reviewer` - PRD（要求仕様書）レビューエージェント
    - CONSTITUTION.md 準拠チェック（最重要機能）
    - 原則カテゴリのチェック（ビジネス、アーキテクチャ、開発、技術的制約）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - SysML 要求図フォーマットの検証
    - 曖昧表現の検出と改善提案

### Changed

#### Agents

- `spec-reviewer` - CONSTITUTION.md 準拠チェック機能を追加
    - Read ツールで CONSTITUTION.md を読み込む準備手順を追加
    - spec 向けの原則カテゴリチェック（アーキテクチャ原則を重視）
    - design 向けの原則カテゴリチェック（技術的制約を重視）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - レビュー出力フォーマットに CONSTITUTION.md 準拠チェック結果を追加

#### Commands

- `/generate_prd` - CONSTITUTION.md 準拠の生成フローを追加
    - 生成フローに CONSTITUTION.md 読み込みステップを追加（Step 2）
    - prd-reviewer による原則準拠チェックを必須化（Step 6）
    - PRD 向けの原則カテゴリ影響テーブルを追加
    - チェック結果の出力テンプレートを追加

- `/generate_spec` - CONSTITUTION.md 準拠の生成フローを追加
    - 生成フローに CONSTITUTION.md 読み込みステップを追加（Step 2）
    - spec-reviewer による原則準拠チェックを必須化（Steps 6, 8）
    - spec と design doc 両方のチェック結果出力テンプレートを追加

## [2.1.1] - 2025-12-23

### Changed

- 全コマンドとエージェントから自動 git commit の指示を削除
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

### Added

#### Commands

- `/clarify` - 仕様明確化コマンド
    - 9 カテゴリ（機能スコープ、データモデル、フロー、非機能要件、連携、
      エッジケース、制約、用語、完了基準）で仕様をスキャン
    - 不明確な項目を Clear/Partial/Missing に分類
    - 影響度の高い明確化質問を最大 5 件生成
    - 回答を段階的に `*_spec.md` に統合
    - `vibe-detector` スキルと補完関係
- `/implement` - TDD ベースの実装実行コマンド
    - tasks.md のチェックリスト完了率を検証
    - 5 フェーズを順番に実行（Setup→Tests→Core→Integration→Polish）
    - テストファースト（TDD）アプローチ
    - tasks.md の進捗を自動マーキング
    - 完了検証（全タスク完了、テスト合格、仕様整合性）
- `/checklist` - 品質チェックリスト生成コマンド
    - 仕様書と計画から 9 カテゴリのチェックリストを自動生成
    - CHK-{カテゴリ番号}{連番} 形式で ID を採番
    - 優先度レベル（P1/P2/P3）を自動設定
- `/constitution` - プロジェクト憲法管理コマンド
    - プロジェクトの交渉不可能な原則を定義（ビジネス、アーキテクチャ、開発方法論、技術的制約）
    - セマンティックバージョニング（MAJOR/MINOR/PATCH）
    - 仕様書・設計書との同期検証

#### Agents

- `clarification-assistant` - 仕様明確化アシスタントエージェント
    - 9 カテゴリでユーザー要求を体系的に分析
    - 影響度の高い明確化質問を生成
    - 回答を仕様書に統合
    - `/clarify` コマンドのバックエンド役

#### Templates

- `checklist_template.md` - 品質チェックリストテンプレート
    - 9 カテゴリの品質チェック項目
    - 優先度レベル（P1/P2/P3）
    - 各項目の検証方法
- `constitution_template.md` - プロジェクト憲法テンプレート
    - 原則の階層（ビジネス → アーキテクチャ → 開発方法論 → 技術的制約）
    - 各原則の検証方法、違反例、準拠例
    - バージョン履歴と改定プロセス
- `implementation_log_template.md` - 実装ログテンプレート
    - セッション単位の実装判断記録
    - 課題と解決策の追跡
    - 技術的発見とパフォーマンス指標

#### Skills

- `sdd-templates` - 新テンプレートへの参照を追加

## [2.0.1] - 2025-12-12

### Added

#### Agents

- 全エージェントにドキュメントリンク規約を追加
    - `sdd-workflow` - ファイル/ディレクトリの Markdown リンク形式を定義
    - `spec-reviewer` - リンク規約のチェックポイントを追加
    - `requirement-analyzer` - 要求図向けのリンク規約を追加
    - ファイルリンク: `[filename.md](path)` 形式
    - ディレクトリリンク: `[directory-name](path/index.md)` 形式

### Removed

#### Agents

- `sdd-workflow` - コミットメッセージ規約セクションを削除
    - Claude Code 標準のコミット規約に委ねる方針に変更

## [2.0.0] - 2025-12-09

### Breaking Changes

#### ディレクトリ構造の変更

- **ルートディレクトリ**: `.docs/` → `.sdd/`
- **要求ディレクトリ**: `requirement-diagram/` → `requirement/`
- **タスクログディレクトリ**: `review/` → `task/`

#### コマンドのリネーム

- `/review_cleanup` → `/task_cleanup`

#### マイグレーション

レガシーバージョン（v1.x）からの移行には `/sdd_migrate` コマンドを使用:

- **オプション A**: ディレクトリをリネームして新構造に移行
- **オプション B**: `.sdd-config.json` を生成してレガシー構造を維持

### Added

#### Commands

- `/sdd_init` - AI-SDD ワークフロー初期化コマンド
    - プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
    - `.sdd/` ディレクトリ構造（requirement/, specification/, task/）を作成
    - `sdd-templates` スキルでテンプレートファイルを生成
- `/sdd_migrate` - レガシーバージョンからのマイグレーションコマンド
    - レガシー構造（`.docs/`, `requirement-diagram/`, `review/`）を検出
    - 新構造への移行か互換設定の生成かを選択可能

#### Agents

- `requirement-analyzer` - 要求分析エージェント
    - SysML 要求図ベースの分析
    - 要求の追跡と検証

#### Skills

- `sdd-templates` - AI-SDD テンプレートスキル
    - PRD、仕様書、設計書のフォールバックテンプレートを提供
    - プロジェクトテンプレートの優先ルールを明確化

#### Hooks

- `session-start` - セッション開始時の初期化フック
    - `.sdd-config.json` から設定を読み込み環境変数を設定
    - レガシー構造を自動検出しマイグレーションガイダンスを表示

#### 設定ファイル

- `.sdd-config.json` - プロジェクト設定ファイルのサポート
    - `root`: ルートディレクトリ（デフォルト: `.sdd`）
    - `directories.requirement`: 要求ディレクトリ（デフォルト: `requirement`）
    - `directories.specification`: 仕様ディレクトリ（デフォルト: `specification`）
    - `directories.task`: タスクログディレクトリ（デフォルト: `task`）

### Changed

#### プラグイン設定

- `plugin.json` - author フィールドを強化
    - `author.url` フィールドを追加

#### Commands

- 全コマンドに `allowed-tools` フィールドを追加
    - 各コマンドで利用可能なツールを明示
    - セキュリティと明確性を向上
- 全コマンドが `.sdd-config.json` 設定ファイルをサポート

#### Skills

- スキルディレクトリ構造を改善
    - `skill-name.md` から `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosure パターンを適用
    - テンプレートファイルを外部化し SKILL.md を簡素化

### Removed

#### Hooks

- `check-spec-exists` - 削除
    - 仕様書の作成は任意であり、存在しないことは一般的な正常ケースのため
- `check-commit-prefix` - 削除
    - コミットメッセージ規約はプラグイン機能で使用されないため

## [1.1.0] - 2025-12-06

### Added

#### Commands

- `/sdd_init` - AI-SDD ワークフロー初期化コマンド
    - プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
    - `.docs/` ディレクトリ構造（requirement-diagram/, specification/, review/）を作成
    - `sdd-templates` スキルでテンプレートファイルを生成

#### Skills

- `sdd-templates` - AI-SDD テンプレートスキル
    - PRD、仕様書、設計書のフォールバックテンプレートを提供
    - プロジェクトテンプレートの優先ルールを明確化

### Changed

#### プラグイン設定

- `plugin.json` - author フィールドを強化
    - `author.url` フィールドを追加

#### Commands

- 全コマンドに `allowed-tools` フィールドを追加
    - 各コマンドで利用可能なツールを明示
    - セキュリティと明確性を向上

#### Skills

- スキルディレクトリ構造を改善
    - `skill-name.md` から `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosure パターンを適用
    - テンプレートファイルを外部化し SKILL.md を簡素化

## [1.0.1] - 2025-12-04

### Changed

#### Agents

- `spec-reviewer` - 前提条件セクションを追加
    - 実行前に `sdd-workflow:sdd-workflow` エージェントの内容を読む指示を追加
    - AI-SDD 原則、ドキュメント構造、永続化ルール、Vibe Coding 防止の理解を促進

#### Commands

- 全コマンドに前提条件セクションを追加
    - `generate_prd`, `generate_spec`, `check_spec`, `task_breakdown`, `review_cleanup`
    - 実行前に `sdd-workflow:sdd-workflow` エージェントの内容を読む指示を追加
    - sdd-workflow エージェントの原則に従う一貫した動作を保証

#### Skills

- 全スキルに前提条件セクションを追加
    - `vibe-detector`, `doc-consistency-checker`
    - 実行前に `sdd-workflow:sdd-workflow` エージェントの内容を読む指示を追加

#### Hooks

- `check-spec-exists.sh` - パス解決を改善
    - `git rev-parse --show-toplevel` でリポジトリルートを動的に取得
    - git リポジトリでない場合はカレントディレクトリにフォールバック
- `check-spec-exists.sh` - テストファイル除外パターンを拡張
    - Jest: `__tests__/`, `__mocks__/`
    - Storybook: `*.stories.*`
    - E2E: `/e2e/`, `/cypress/`
- `settings.example.json` - セットアップ手順をコメントとして追加
    - パスを `./hooks/` 形式に修正

#### Skills

- `vibe-detector` - `allowed-tools` に `AskUserQuestion` を追加
    - ユーザー確認フローをサポート
- `doc-consistency-checker` - `allowed-tools` に `Bash` を追加
    - ディレクトリ構造の検証をサポート

## [1.0.0] - 2024-12-03

### Added

#### Agents

- `sdd-workflow` - AI-SDD 開発フロー管理エージェント
    - フェーズ判定（Specify → Plan → Tasks → Implement & Review）
    - Vibe Coding 防止（曖昧な指示の検出と明確化の促進）
    - ドキュメント整合性チェック
- `spec-reviewer` - 仕様書品質レビューエージェント
    - 曖昧な記述の検出
    - 不足セクションの特定
    - SysML 準拠チェック

#### Commands

- `/generate_prd` - ビジネス要求から SysML 要求図形式の PRD（要求仕様書）を生成
- `/generate_spec` - 入力から抽象仕様書と技術設計書を生成
    - PRD 整合性レビュー機能
- `/check_spec` - 実装コードと仕様書の整合性をチェック
    - 多層チェック: PRD ↔ spec ↔ design ↔ 実装
- `/task_breakdown` - 技術設計書からタスクを分解
    - 要求カバレッジの検証
- `/review_cleanup` - 実装後に review/ ディレクトリをクリーンアップ

#### Skills

- `vibe-detector` - Vibe Coding（曖昧な指示）の自動検出
- `doc-consistency-checker` - ドキュメント間の整合性自動チェック

#### Integration

- Serena MCP のオプション統合
    - セマンティックコード解析による機能強化
    - 30 以上のプログラミング言語をサポート
    - 未設定時はテキストベース検索にフォールバック
