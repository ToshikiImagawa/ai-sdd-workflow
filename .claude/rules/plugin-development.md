---
paths:
  - "plugins/**"
---

# プラグイン開発

## 開発時の注意

- プラグイン修正時は `plugins/sdd-workflow/` に限定して作業
- 「調査して」と依頼された場合は、まずスコープを確認してから探索

## プラグインエージェント設計ガイド

AI-SDDワークフロープラグインのサブエージェント設計・実装に関する原則とベストプラクティスは、
[PLUGIN_AGENTS.md](../../PLUGIN_AGENTS.md) を参照してください。

このガイドでは以下の内容を定義しています：

1. **サブエージェントの基本概念**（コンテキスト独立性、トークン効率化）
2. **エージェント設計原則**（役割、入出力、allowed-tools/tools/skills/hooks、前提条件）
3. **委任すべきタスク vs メインで実行すべきタスク**
4. **エージェント間連携パターン**（スキル連携、フック連携を含む）
5. **実践Tips**（デバッグ方法、`claude --debug` の活用）

## プラグイン開発ガイド

Claude Codeプラグインとマーケットプレイスの作成に関する包括的なガイドは、[PLUGIN.md](../../PLUGIN.md) を参照してください。

このガイドでは以下の内容を定義しています：

1. **プラグイン基本構造**（ディレクトリレイアウト、マーケットプレイス構成）
2. **マニフェストファイル**（plugin.json のコンポーネントパスフィールド、`${CLAUDE_PLUGIN_ROOT}` 環境変数）
3. **コマンド（legacy）、エージェント、スキルの実装**（フロントマター、`context: fork`、動的コンテキスト注入）
4. **MCP / LSP サーバー連携**（外部ツール統合、Language Server Protocol 統合）
5. **フック実装**（JSON形式の `hooks.json`、イベント一覧、フックタイプ: command/prompt/agent）
6. **プラグインキャッシュとインストールスコープ**（user/project/local/managed）
7. **マーケットプレイス公開プロセス**（品質基準、配布モデル）
8. **CLI コマンドリファレンス / デバッグ**

## 新しいプラグインの追加

1. `plugins/{plugin-name}/` ディレクトリを作成
2. `.claude-plugin/plugin.json` にプラグインマニフェストを配置
3. agents, skills, hooks を必要に応じて追加（新規コマンドは `skills/` を推奨）
4. `.claude-plugin/marketplace.json` の `plugins` 配列に追加
