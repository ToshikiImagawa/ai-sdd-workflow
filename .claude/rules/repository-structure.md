# リポジトリ構成

```
ai-sdd-workflow/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイスメタデータ
├── .agents/skills/                # Codex向け開発スキル
├── .claude/skills/                # Claude Code向け開発スキル
├── plugins/
│   └── sdd-workflow/              # 統合プラグイン（多言語対応）
│       ├── .claude-plugin/
│       │   └── plugin.json        # プラグインマニフェスト
│       ├── agents/
│       │   ├── spec-reviewer.md   # 仕様書レビューエージェント
│       │   ├── prd-reviewer.md    # PRDレビューエージェント
│       │   ├── requirement-analyzer.md  # 要求仕様分析エージェント
│       │   ├── clarification-assistant.md  # 仕様明確化アシスタント
│       │   ├── front-matter-reviewer.md  # front matter検証エージェント
│       │   ├── cross-prd-reviewer.md  # PRD横断整合レビューエージェント
│       │   ├── examples/          # エージェント利用例
│       │   ├── references/        # エージェント参照資料
│       │   └── templates/{en,ja}/ # エージェント出力テンプレート
│       ├── skills/                # 19スキル
│       │   ├── analyze-requirements/       # 要求分析（UR/FR/NFR抽出）
│       │   ├── check-spec/                 # 実装とdesignの整合性チェック
│       │   │   └── templates/{en,ja}/
│       │   ├── checklist/                  # 品質チェックリスト生成
│       │   │   └── templates/{en,ja}/
│       │   ├── clarify/                    # 仕様明確化
│       │   │   └── templates/{en,ja}/
│       │   ├── constitution/               # プロジェクト原則管理
│       │   │   └── templates/{en,ja}/
│       │   ├── doc-consistency-checker/    # ドキュメント整合性チェッカー
│       │   │   └── templates/{en,ja}/
│       │   ├── finalize-prd/               # PRD統合・完成
│       │   │   └── templates/{en,ja}/
│       │   ├── generate-prd/               # PRD生成
│       │   │   └── templates/{en,ja}/
│       │   ├── generate-requirements-diagram/  # SysML要求図生成
│       │   ├── generate-spec/              # 仕様書・設計書生成
│       │   │   └── templates/{en,ja}/
│       │   ├── generate-usecase-diagram/   # ユースケース図生成
│       │   ├── implement/                  # TDD実装
│       │   │   └── templates/{en,ja}/
│       │   ├── plan-refactor/              # リファクタリング計画
│       │   │   └── templates/{en,ja}/
│       │   ├── recommend-front-matter/     # front matter推奨
│       │   │   └── templates/{en,ja}/
│       │   ├── run-checklist/              # チェックリスト自動検証
│       │   │   └── templates/{en,ja}/
│       │   ├── sdd-init/                   # AI-SDDワークフロー初期化
│       │   │   └── templates/{en,ja}/
│       │   ├── task-breakdown/             # タスク分解
│       │   │   └── templates/{en,ja}/
│       │   ├── task-cleanup/               # タスククリーンアップ
│       │   │   └── templates/{en,ja}/
│       │   └── vibe-detector/              # Vibe Coding検出
│       │       └── templates/{en,ja}/
│       ├── hooks/
│       │   └── hooks.json         # フック設定（JSON形式）
│       ├── scripts/
│       │   ├── session-start.py   # セッション開始時の初期化
│       │   ├── hook_common.py     # フックスクリプト共通ヘルパー
│       │   ├── user-prompt-submit.py  # Vibe Coding兆候検知
│       │   ├── pre-tool-use.py    # .sdd/ ファイル命名規則検証・CONSTITUTION原則注入
│       │   └── post-tool-use.py   # ドキュメント更新漏れ検知
│       ├── AI-SDD-PRINCIPLES.source.md
│       ├── LICENSE
│       ├── README.md
│       ├── CHANGELOG.md
│       └── CHANGELOG.ja.md
├── CLAUDE.md                       # 共通プロジェクト指示（正本）
├── PLUGIN_AGENTS.md                # プラグインエージェント設計ガイド
├── PLUGIN.md
└── README.md
```
