# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援するClaude Codeプラグイン（日本語対応）のマーケットプレイスリポジトリ。Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現する。

## リポジトリ構成

```
ai-sdd-workflow-ja/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── plugins/
│   └── sdd-workflow-ja/           # sdd-workflow-ja プラグイン
│       ├── .claude-plugin/
│       │   └── plugin.json        # プラグインマニフェスト
│       ├── agents/
│       │   ├── sdd-workflow.md    # AI-SDD開発フローエージェント
│       │   └── spec-reviewer.md   # 仕様書レビューエージェント
│       ├── commands/
│       │   ├── generate_spec.md   # 仕様書・設計書生成
│       │   ├── generate_prd.md    # PRD生成
│       │   ├── check_spec.md      # 整合性チェック
│       │   ├── review_cleanup.md  # レビュークリーンアップ
│       │   └── task_breakdown.md  # タスク分解
│       ├── skills/
│       │   ├── vibe-detector.md   # Vibe Coding検出
│       │   └── doc-consistency-checker.md
│       ├── hooks/
│       │   ├── check-spec-exists.sh
│       │   ├── check-commit-prefix.sh
│       │   └── settings.example.json
│       └── LICENSE
├── CHANGELOG.md
├── CLAUDE.md
└── README.md
```

## AI-SDD 開発フロー

```
Specify（仕様化） → Plan（計画） → Tasks（タスク分解） → Implement & Review（実装と検証）
```

### ドキュメント構造

```
.docs/
├── requirement-diagram/          # PRD（要求仕様書）- 永続
├── specification/                # 永続的な知識資産
│   ├── {機能名}_spec.md         # 抽象仕様書
│   └── {機能名}_design.md       # 技術設計書
└── review/                       # 一時的な作業ログ（実装完了後に削除）
```

### ドキュメント永続性ルール

- `requirement-diagram/`, `specification/*_spec.md`, `specification/*_design.md`: **永続**
- `review/`: **一時的** - 実装完了後に削除。重要な設計判断は `*_design.md` に統合

## コミットメッセージ規約

| プレフィックス | 用途 |
|:---|:---|
| `[docs]` | ドキュメントの追加・更新 |
| `[spec]` | 仕様書の追加・更新（`*_spec.md`） |
| `[design]` | 設計書の追加・更新（`*_design.md`） |

## Vibe Coding防止

曖昧な指示（「いい感じに」「適当に」「前と同じように」など）を検出した場合、仕様の明確化を促す。仕様書なしでの実装は避け、最低限 `review/` に推測仕様を記録する。

## 新しいプラグインの追加

1. `plugins/{plugin-name}/` ディレクトリを作成
2. `.claude-plugin/plugin.json` にプラグインマニフェストを配置
3. agents, commands, skills, hooks を必要に応じて追加
4. `.claude-plugin/marketplace.json` の `plugins` 配列に追加
