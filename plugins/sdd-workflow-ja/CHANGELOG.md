# 変更履歴

このプラグインに対するすべての重要な変更はこのファイルに記録されます。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づき、
[Semantic Versioning](https://semver.org/lang/ja/) に準拠しています。

## [1.0.1] - 2025-12-03

### Changed

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

#### フック

- `check-spec-exists` - 実装前に仕様書の存在を確認
- `check-commit-prefix` - コミットメッセージ規約（[docs], [spec], [design]）のチェック

#### 統合

- Serena MCP オプショナル統合
  - セマンティックコード分析による機能強化
  - 30以上のプログラミング言語に対応
  - 未設定時もテキストベース検索で動作
