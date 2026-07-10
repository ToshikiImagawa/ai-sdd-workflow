# Contributing Guide

ai-sdd-workflow へのコントリビューションに興味を持っていただきありがとうございます。
このドキュメントでは、コントリビューションの手順と規約を説明します。

Thank you for your interest in contributing to ai-sdd-workflow.
This document describes the contribution process and conventions (Japanese first, English summary at the end).

## Issue の報告

バグ報告・機能提案は [GitHub Issues](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues) で受け付けています。

- 再現手順・期待する動作・実際の動作を具体的に記載してください
- 脆弱性の報告は Issue ではなく [SECURITY.md](./SECURITY.md) の手順に従ってください

## 開発の流れ

1. リポジトリを Fork し、`main` からブランチを作成する
2. 変更を実装する
3. [検証](#検証) の各チェックを通過させる
4. Pull Request を作成する

## 新しいプラグインの追加

1. `plugins/{plugin-name}/` ディレクトリを作成する
2. `plugins/{plugin-name}/.claude-plugin/plugin.json` にプラグインマニフェストを配置する
3. agents / skills / hooks を必要に応じて追加する（新規コマンドは `skills/` を推奨）
4. `.claude-plugin/marketplace.json` の `plugins` 配列にプラグインを登録する
5. 新規エージェント / スキルは `plugin.json` のコンポーネントパスに登録する

プラグインとマーケットプレイスの詳細な構造は [PLUGIN.md](./PLUGIN.md) を、
サブエージェントの設計原則は [PLUGIN_AGENTS.md](./PLUGIN_AGENTS.md) を参照してください。

CodexとClaude Codeは共通のプロジェクト指示として `CLAUDE.md` を使用します。
Codexで開発する場合は `~/.codex/config.toml` に
`project_doc_fallback_filenames = ["CLAUDE.md"]` を設定し、`.agents/skills/` を使用してください。
Claude Codeでは `.claude/skills/` を使用します。

## 検証

Pull Request を作成する前に、以下のチェックを通過させてください（CI でも同じチェックが実行されます）。

```bash
# プラグイン JSON 構文チェック
cat plugins/*/.claude-plugin/*.json | jq .

# マーケットプレイス構成の検証
bash scripts/validate-marketplace.sh

# プラグイン構造の lint
bash scripts/plugin-lint.sh

# シェルスクリプトの静的解析
find . -name "*.sh" -type f -print0 | xargs -0 shellcheck -S warning -e SC1091

# フックスクリプトの回帰テスト
bash scripts/test-session-start.sh
bash scripts/test-hook-scripts.sh
```

ローカルでプラグインの動作確認をする場合:

```bash
claude --plugin-dir ./plugins/sdd-workflow
```

Markdown ドキュメントを変更した場合は、相対リンクが有効であることも確認してください。

## コミットメッセージ規約

- 日本語で記述する
- 以下のプレフィックスを付ける: `[add]`, `[update]`, `[fix]`, `[refactoring]`, `[remove]`, `[docs]`, `[test]`
- 簡潔に変更内容を説明する

```
[add] spec-reviewer にトレーサビリティ検証を追加
[fix] session-start.py の SDD_LANG 未設定時のフォールバックを修正
```

## Pull Request 規約

- [PR テンプレート](./.github/PULL_REQUEST_TEMPLATE.md) に従い、概要・変更内容・テスト計画を記載する
- 対応する Issue がある場合は `Closes #<番号>` で紐付ける
- CI（validate / shellcheck / plugin-lint / test）がすべて通過していることを確認する

---

## English Summary

- **Issues**: Report bugs and feature requests via GitHub Issues. For vulnerabilities, follow [SECURITY.md](./SECURITY.md) instead.
- **Adding a plugin**: Create `plugins/{plugin-name}/` with a `.claude-plugin/plugin.json` manifest, add agents/skills/hooks as needed, and register the plugin in `.claude-plugin/marketplace.json`. See [PLUGIN.md](./PLUGIN.md) and [PLUGIN_AGENTS.md](./PLUGIN_AGENTS.md) for details.
- **Verification**: Before opening a PR, run the checks above (JSON syntax, `scripts/validate-marketplace.sh`, `scripts/plugin-lint.sh`, shellcheck, and hook script regression tests). The same checks run in CI.
- **Commit messages**: Written in Japanese with a prefix such as `[add]`, `[update]`, `[fix]`, `[refactoring]`, `[remove]`, `[docs]`, or `[test]`.
- **Pull requests**: Follow the PR template, link related issues with `Closes #<number>`, and make sure CI passes.
