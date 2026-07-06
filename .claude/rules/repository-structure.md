# リポジトリ構成

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── plugins/
│   └── sdd-workflow/              # 統合プラグイン（多言語対応）
│       ├── .claude-plugin/
│       │   └── plugin.json        # プラグインマニフェスト
│       ├── agents/
│       │   ├── spec-reviewer.md   # 仕様書レビューエージェント
│       │   ├── prd-reviewer.md    # PRDレビューエージェント
│       │   ├── requirement-analyzer.md  # 要求仕様分析エージェント
│       │   └── clarification-assistant.md  # 仕様明確化アシスタント
│       ├── skills/                # 11スキル（旧commands）+ 4スキル（既存）
│       │   ├── sdd-init/          # AI-SDDワークフロー初期化
│       │   ├── constitution/      # プロジェクト原則管理
│       │   ├── generate-spec/     # 仕様書・設計書生成
│       │   ├── generate-prd/      # PRD生成
│       │   ├── check-spec/        # 整合性チェック
│       │   ├── task-breakdown/    # タスク分解
│       │   ├── implement/         # TDD実装
│       │   ├── clarify/           # 仕様明確化
│       │   ├── task-cleanup/      # タスククリーンアップ
│       │   ├── sdd-migrate/       # マイグレーション
│       │   ├── checklist/         # 品質チェックリスト
│       │   ├── vibe-detector/     # Vibe Coding検出
│       │   │   └── templates/{en,ja}/
│       │   ├── sdd-templates/     # AI-SDDテンプレート
│       │   │   └── templates/{en,ja}/
│       │   ├── doc-consistency-checker/  # ドキュメント整合性チェッカー
│       │   │   └── templates/{en,ja}/
│       │   └── output-templates/  # 出力テンプレート
│       │       └── templates/{en,ja}/
│       ├── hooks/
│       │   └── hooks.json         # フック設定（JSON形式）
│       ├── scripts/
│       │   ├── session-start.py   # セッション開始時の初期化
│       │   ├── hook_common.py     # フックスクリプト共通ヘルパー
│       │   ├── user-prompt-submit.py  # Vibe Coding兆候検知
│       │   ├── pre-tool-use.py    # .sdd/ ファイル命名規則検証
│       │   └── post-tool-use.py   # ドキュメント更新漏れ検知
│       ├── AI-SDD-PRINCIPLES.source.md
│       ├── LICENSE
│       ├── README.md
│       ├── CHANGELOG.md
│       └── CHANGELOG.ja.md
├── CLAUDE.md
├── AGENTS.md
├── PLUGIN.md
└── README.md
```
