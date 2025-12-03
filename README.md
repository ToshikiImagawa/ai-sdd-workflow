# sdd-workflow-ja

AI駆動仕様駆動開発（AI-SDD）ワークフローを支援する日本語 Claude Code プラグインです。

## 概要

このプラグインは、Vibe Coding問題を防ぎ、仕様書を真実の源として高品質な実装を実現するためのツール群を提供します。

### Vibe Codingとは？

曖昧な指示によりAIが数千の未定義要件を推測せざるを得ない問題のことです。
このプラグインは、仕様書を中心とした開発フローを提供することで、この問題を解決します。

## インストール

### 方法1: マーケットプレイスからインストール（推奨）

Claude Codeで以下を実行：

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow-ja
```

その後、プラグインをインストール：

```
/plugin install sdd-workflow-ja@ToshikiImagawa/ai-sdd-workflow-ja
```

### 方法2: GitHubからクローン

```bash
git clone https://github.com/ToshikiImagawa/ai-sdd-workflow-ja.git ~/.claude/plugins/sdd-workflow-ja
```

インストール後、Claude Codeを再起動してください。

### 確認

Claude Codeで `/plugin` コマンドを実行し、`sdd-workflow-ja` が表示されることを確認してください。

## ライセンス

MIT License
