# 変更履歴

このプラグインに対するすべての重要な変更はこのファイルに記録されます。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づき、
[Semantic Versioning](https://semver.org/lang/ja/) に準拠しています。

## [Unreleased]

### Added

#### ドキュメント

- **PLUGIN.md** - Claude Codeプラグインとマーケットプレイス作成の包括的ガイド
    - プラグイン基本構造（ディレクトリレイアウト、マーケットプレイス構成）
    - マニフェストファイル（plugin.json, marketplace.json の詳細）
    - コマンド、エージェント、スキルの実装（フロントマター、ベストプラクティス）
    - MCP サーバー連携（外部ツール統合）
    - フック実装（イベント駆動型自動化）
    - マーケットプレイス公開プロセス（品質基準、配布モデル）
- **CLAUDE.md** - PLUGIN.md への参照を追加（AGENTS.md と同様の構造）

#### スキル

- 全スキルに `version: 2.3.1` と `license: MIT` フィールドを追加
    - vibe-detector
    - doc-consistency-checker
    - sdd-templates

#### コマンド

- 全コマンドに `argument-hint` フィールドを追加してユーザビリティ向上
    - generate_spec: `<機能名> [PRDファイルパス]`
    - generate_prd: `<機能名> [要件説明]`
    - check_spec: `<設計書ファイルパス>`
    - task_breakdown: `<設計書ファイルパス> [チケット番号]`
    - task_cleanup: `<チケット番号>`
    - constitution: `<init|update|check>`
    - implement: `<タスクファイルパス>`
    - clarify: `[仕様書ファイルパス]`
    - checklist: `<ファイルパス>`

### Changed

#### マーケットプレイス

- **marketplace.json** の改善
    - `author.url` を追加（作成者への帰属）
    - `category: "development"` を追加（マーケットプレイスフィルタリング）
    - `tags` 配列を追加（検索の発見性向上）
        - "specification-driven-development"
        - "japanese" / "english"
        - "workflow"
        - "sysml"
        - "requirements"
        - "documentation"

#### エージェント

- 全エージェントの `description` をより明確に改善
    - 機能説明スタイルから「いつ使うか」スタイルに変更
    - 具体的なトリガーフレーズを追加（例: 「仕様書をレビュー」「specをチェック」）
    - コマンドとの関係を明示（例: /check_spec や /generate_spec コマンド実行後）
    - 必要な入力情報を明記（例: 仕様書ファイルパスが必要）
    - 自己参照的な「エージェント」表現を削除
    - 対象エージェント: spec-reviewer, requirement-analyzer, prd-reviewer, clarification-assistant

#### スキル

- 全スキルの `description` をより明確に改善
    - 実行タイミングを明示（例: 実装開始前に自動実行、コマンドから自動呼び出し）
    - 検出内容の具体化（例: 「いい感じに」「適当に」などの曖昧表現）
    - トレーサビリティ保証の明記
    - フォールバック動作の詳細説明
    - 対象スキル: vibe-detector, doc-consistency-checker, sdd-templates

## [2.3.1] - 2026-01-14

### Fixed

#### Hooks

- `session-start.sh` - 一時ファイル存在確認によるエラーハンドリング改善
    - sedコマンド失敗時の `mv: No such file or directory` エラーを修正
    - `&& [ -f "$TEMP_FILE" ]` を追加して一時ファイルの存在を確認してから mv を実行
    - フォールバック処理が適切に動作するように改善
    - 英語版に警告ファイル削除処理（else節）を追加して日本語版と統一

## [2.3.0] - 2026-01-09

### Changed

#### エージェント

- **役割分離**: `sdd-workflow` エージェントを `AI-SDD-PRINCIPLES.md` に変更
    - エージェントの原則定義部分を独立したドキュメントとして分離
    - 全コマンド・エージェント・スキルの参照先を `../AI-SDD-PRINCIPLES.md` に更新
    - AI-SDD原則の一元管理と保守性の向上

- `spec-reviewer` - ドキュメント間トレーサビリティチェック機能を追加
    - **PRD ↔ spec トレーサビリティチェック**: PRDの要求がspecで適切にカバーされているか確認
        - 要求ID（UR/FR/NFR）のマッピング検証
        - カバレッジ率の計算（80%閾値チェック）
        - 部分対応・未対応の分類
    - **spec ↔ design 整合性チェック**: specの内容がdesignで適切に詳細化されているか確認
        - API定義の詳細化確認
        - 型定義の一致確認
        - 制約事項の考慮確認
    - `allowed-tools` に `Edit` を追加（自動修正対応）
    - 入力形式と出力フォーマットの明確化（`--summary` オプション対応）

#### コマンド

- `/check_spec` - **設計書（design）↔ 実装の整合性チェックに特化**
    - **[BREAKING]** ドキュメント間整合性チェック（PRD↔spec、spec↔design）を `spec-reviewer` に委譲
        - **変更前（v2.2.0）**: すべての整合性チェック（CONSTITUTION↔docs、PRD↔spec、spec↔design、design↔実装）を実行
        - **変更後（v2.3.0）**: design↔実装の整合性チェックのみ実行（高速化）
        - **移行方法**:
            - ドキュメント間整合性も含む包括的チェックが必要な場合: `/check_spec --full` を使用
            - design↔実装のみで十分な場合: `/check_spec` のまま（既存と同じコマンド）
        - **影響**: CI/CDパイプラインで `/check_spec` を使用している場合、`--full` オプションの追加を検討してください
    - `--full` オプションの追加: 整合性チェックに加えて `spec-reviewer` による包括的レビューを実行
    - 対象ドキュメントを `*_design.md` に限定
    - 出力フォーマットの簡素化（design↔実装に集中）

- `/sdd_init` - 参照先の更新
    - エージェント参照を `AI-SDD-PRINCIPLES.md` に変更

### Added

#### ドキュメント

- `AI-SDD-PRINCIPLES.md` - AI-SDD原則を定義する独立ドキュメント
    - 従来 `sdd-workflow` エージェントに含まれていた原則定義を分離
    - コマンド・エージェント・スキルから共通参照される設計

#### README

- Windows 環境非対応の明記
    - 対応環境マトリックスを追加（macOS/Linux: ✅、Windows: ❌）
    - Windowsユーザー向け代替手段を記載（WSL、Git Bash）
    - 将来的な対応方針（PowerShell版、クロスプラットフォーム実装の検討）

## [2.2.0] - 2026-01-06

### Added

#### エージェント

- `prd-reviewer` - PRD（要求仕様書）専用のレビューエージェント
    - CONSTITUTION.md準拠チェック（最重要機能）
    - 原則カテゴリ別チェック（ビジネス原則、アーキテクチャ原則、開発手法原則、技術制約）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - SysML 要求図形式の妥当性検証
    - 曖昧な表現の検出と改善提案

### Changed

#### エージェント

- `spec-reviewer` - CONSTITUTION.md準拠チェック機能を追加
    - 事前準備としてRead ツールでCONSTITUTION.mdを読み込む指示を追加
    - spec向け原則カテゴリ別チェック（アーキテクチャ原則を重視）
    - design向け原則カテゴリ別チェック（技術制約を重視）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - レビュー出力フォーマットにCONSTITUTION.md準拠チェック結果を追加

#### コマンド

- `/generate_prd` - CONSTITUTION.md準拠の生成フローを追加
    - 生成フローにCONSTITUTION.md読み込みステップを追加（ステップ2）
    - prd-reviewerによる原則準拠チェックを必須化（ステップ6）
    - 原則カテゴリ別のPRDへの影響表を追加
    - チェック結果の出力テンプレートを追加

- `/generate_spec` - CONSTITUTION.md準拠の生成フローを追加
    - 生成フローにCONSTITUTION.md読み込みステップを追加（ステップ2）
    - spec-reviewerによる原則準拠チェックを必須化（ステップ6, 8）
    - 抽象仕様書・技術設計書それぞれのチェック結果出力テンプレートを追加

## [2.1.1] - 2025-12-23

### Changed

- すべてのコマンドとエージェントから自動git commit指示を削除
    - `task_cleanup` - クリーンアップワークフローからコミットステップを削除
    - `implement` - 継続的な検証フローからコミット指示を削除
    - `generate_spec` - 生成フローからコミットステップを削除
    - `sdd-workflow` エージェント - ワークフローフェーズからコミットステップを削除
    - `clarify` - 統合モードからコミット指示を削除
    - `task_breakdown` - 生成後アクションからコミットステップを削除
    - `generate_prd` - 生成後アクションからコミットステップを削除
    - `sdd_migrate` - コミット指示とコミットメッセージ例を削除
    - `sdd_init` - 初期化フローからコミットステップを削除

## [2.1.0] - 2025-12-12

### Added

#### コマンド

- `/clarify` - 仕様明確化支援コマンド
    - 仕様書の不明点を9カテゴリ（機能範囲、データモデル、フロー、非機能要件、統合、エッジケース、制約、用語、完了条件）でスキャン
    - 不明確な箇所をClear/Partial/Missingで分類
    - 最大5つの高インパクト質問を生成
    - 回答を仕様書（`*_spec.md`）に段階的に統合
    - `vibe-detector` スキルと補完関係
- `/implement` - TDDベース実装実行コマンド
    - tasks.mdのチェックリスト完了率を検証
    - 5フェーズ順実行（Setup→Tests→Core→Integration→Polish）
    - テスト優先（TDD）で実装
    - 進捗をtasks.mdに自動マーク
    - 完了検証（全タスク完了、テスト合格、仕様との整合性）
- `/checklist` - 品質チェックリスト生成コマンド
    - 仕様書・設計書から9カテゴリのチェックリストを自動生成
    - CHK-{カテゴリ番号}{連番} 形式でID付与
    - 優先度（P1/P2/P3）を自動設定
- `/constitution` - プロジェクト原則管理コマンド
    - プロジェクトの非交渉原則を定義（ビジネス原則、アーキテクチャ原則、開発手法原則、技術制約）
    - セマンティックバージョニング（MAJOR/MINOR/PATCH）
    - 仕様書・設計書との同期検証機能

#### エージェント

- `clarification-assistant` - 仕様明確化支援エージェント
    - ユーザーからの要件を9カテゴリで体系的に分析
    - 不明点について高インパクト質問を生成
    - 回答を仕様書に統合
    - `/clarify` コマンドのバックエンド的役割

#### テンプレート

- `checklist_template.md` - 品質チェックリストテンプレート
    - 9カテゴリの品質チェック項目
    - 優先度（P1/P2/P3）設定
    - 検証方法・完了条件を含む
- `constitution_template.md` - プロジェクト原則テンプレート
    - 原則階層（ビジネス原則→アーキテクチャ原則→開発手法原則→技術制約）
    - 各原則の検証方法・違反例・準拠例
    - 変更履歴のバージョン管理
- `implementation_log_template.md` - 実装ログテンプレート
    - セッション単位の実装判断記録
    - 問題と解決策の記録
    - 技術的発見・パフォーマンス計測

#### スキル

- `sdd-templates` - 新しいテンプレートへの参照を追加

## [2.0.1] - 2025-12-12

### Added

#### エージェント

- 全エージェントにドキュメントリンク規約を追加
    - `sdd-workflow` - ファイル/ディレクトリへのマークダウンリンク形式を規定
    - `spec-reviewer` - リンク規約のチェックポイントを追加
    - `requirement-analyzer` - 要求図内でのリンク規約を追加
    - ファイルへのリンク: `[ファイル名.md](パス)` 形式
    - ディレクトリへのリンク: `[ディレクトリ名](パス/index.md)` 形式

### Removed

#### エージェント

- `sdd-workflow` - コミットメッセージ規約セクションを削除
    - Claude Codeの標準的なコミット規約に委ねる方針に変更

## [2.0.0] - 2025-12-09

### Breaking Changes

#### ディレクトリ構造の変更

- **ルートディレクトリ**: `.docs/` → `.sdd/` に変更
- **要求仕様ディレクトリ**: `requirement-diagram/` → `requirement/` に変更
- **タスクログディレクトリ**: `review/` → `task/` に変更

#### コマンド名の変更

- `/review_cleanup` → `/task_cleanup` に変更

#### マイグレーション

旧バージョン（v1.x）からの移行は `/sdd_migrate` コマンドを使用してください:

- **オプションA**: ディレクトリをリネームして新構成に移行
- **オプションB**: `.sdd-config.json` を生成して旧構成を維持

### Added

#### コマンド

- `/sdd_migrate` - 旧バージョンからのマイグレーションコマンド
    - 旧構成（`.docs/`, `requirement-diagram/`, `review/`）を検出
    - 新構成への移行または互換性設定の生成を選択可能

#### エージェント

- `requirement-analyzer` - 要求仕様分析エージェント
    - SysML要求図に基づく要求分析
    - 要求のトラッキングと検証

#### フック

- `session-start` - セッション開始時の初期化フック
    - `.sdd-config.json` から設定を読み込み環境変数を設定
    - 旧構成を自動検出し、マイグレーション案内を表示

#### 設定ファイル

- `.sdd-config.json` - プロジェクト設定ファイルのサポート
    - `root`: ルートディレクトリ（デフォルト: `.sdd`）
    - `directories.requirement`: 要求仕様ディレクトリ（デフォルト: `requirement`）
    - `directories.specification`: 仕様書ディレクトリ（デフォルト: `specification`）
    - `directories.task`: タスクログディレクトリ（デフォルト: `task`）

### Removed

#### フック

- `check-spec-exists` - 削除
    - 仕様書作成はオプショナルなため、存在しないケースが正常系として多い
- `check-commit-prefix` - 削除
    - コミットメッセージ規約がプラグインの機能で使用されていないため削除

## [1.1.0] - 2025-12-06

### Added

#### コマンド

- `/sdd_init` - AI-SDDワークフロー初期化コマンドを追加
    - プロジェクトの `CLAUDE.md` にAI-SDD Instructionsセクションを追加
    - `.docs/` ディレクトリ構造を作成（requirement-diagram/, specification/, review/）
    - `sdd-templates` スキルを使用してテンプレートファイルを生成

#### スキル

- `sdd-templates` - AI-SDDテンプレートスキルを追加
    - PRD、仕様書、設計書テンプレートのフォールバック提供
    - プロジェクトテンプレート優先のルールを明確化

### Changed

#### プラグイン設定

- `plugin.json` - authorフィールドを強化
    - `author.url` フィールドを追加

#### コマンド

- 全コマンドに `allowed-tools` フィールドを追加
    - 各コマンドで使用可能なツールを明示化
    - セキュリティと明確性の向上

#### スキル

- スキルのディレクトリ構造を改善
    - `skill-name.md` → `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosureパターンを適用
    - テンプレートファイルを外部化し、SKILL.md をシンプル化

## [1.0.1] - 2025-12-04

### Changed

#### エージェント

- `spec-reviewer` - 前提条件セクションを追加
    - 実行前に `sdd-workflow-ja:sdd-workflow` エージェントの内容を読み込む指示を追加
    - AI-SDDの原則・ドキュメント構成・永続性ルール・Vibe Coding防止の理解を促進

#### コマンド

- 全コマンドに前提条件セクションを追加
    - `generate_prd`, `generate_spec`, `check_spec`, `task_breakdown`, `review_cleanup`
    - 実行前に `sdd-workflow-ja:sdd-workflow` エージェントの内容を読み込む指示を追加
    - sdd-workflowエージェントの原則に従った一貫した動作を保証

#### スキル

- 全スキルに前提条件セクションを追加
    - `vibe-detector`, `doc-consistency-checker`
    - 実行前に `sdd-workflow-ja:sdd-workflow` エージェントの内容を読み込む指示を追加

#### フック

- `check-spec-exists.sh` - パス解決の改善
    - `git rev-parse --show-toplevel` でリポジトリルートを動的に取得
    - gitリポジトリでない場合はカレントディレクトリにフォールバック
- `check-spec-exists.sh` - テストファイル除外パターンを拡張
    - Jest: `__tests__/`, `__mocks__/`
    - Storybook: `*.stories.*`
    - E2E: `/e2e/`, `/cypress/`
- `settings.example.json` - セットアップ手順をコメントとして追加
    - パスを `./hooks/` 形式に修正

#### スキル

- `vibe-detector` - `allowed-tools` に `AskUserQuestion` を追加
    - ユーザーへの確認フローをサポート
- `doc-consistency-checker` - `allowed-tools` に `Bash` を追加
    - ディレクトリ構造の確認をサポート

## [1.0.0] - 2024-12-03

### Added

#### エージェント

- `sdd-workflow` - AI-SDD開発フローの管理エージェント
    - フェーズ判定（Specify → Plan → Tasks → Implement & Review）
    - Vibe Coding防止（曖昧な指示の検出と明確化促進）
    - ドキュメント整合性チェック
- `spec-reviewer` - 仕様書の品質レビューエージェント
    - 曖昧な記述の検出
    - 不足セクションの指摘
    - SysML準拠のチェック

#### コマンド

- `/generate_prd` - ビジネス要求からPRD（要求仕様書）をSysML要求図形式で生成
- `/generate_spec` - 入力から抽象仕様書と技術設計書を生成
    - PRDとの整合性レビュー機能
- `/check_spec` - 実装コードと仕様書の整合性チェック
    - PRD ↔ spec ↔ design ↔ 実装 の多層チェック
- `/task_breakdown` - 技術設計書からタスクを分解
    - 要求カバレッジの確認機能
- `/review_cleanup` - 実装完了後のreview/ディレクトリ整理

#### スキル

- `vibe-detector` - Vibe Coding（曖昧な指示）の自動検出
- `doc-consistency-checker` - ドキュメント間整合性の自動チェック

#### 統合

- Serena MCP オプショナル統合
    - セマンティックコード分析による機能強化
    - 30以上のプログラミング言語に対応
    - 未設定時もテキストベース検索で動作
