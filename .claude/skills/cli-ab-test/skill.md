---
name: cli-ab-test
description: "CLI連携有効/無効の実行時間・トークン使用量・コストを比較する A/B テスト"
disable-model-invocation: true
context: fork
user-invocable: true
allowed-tools: Bash, Read
allowed-prompts:
  - tool: Bash
    prompt: "*"
---

# CLI A/B テストスキル

このスキルは、CLI連携機能（`sdd-cli`）の有効/無効による実行時間・トークン使用量・APIコストへの影響を定量的に測定します。

## 測定対象メトリクス

- **実行時間**: 各スキル・合計の実行時間（秒）
- **トークン使用量**: input/output/cache creation/cache read
- **APIコスト**: USD
- **ターン数**: Claude API への往復回数

## テスト対象スキル

1. `/sdd-init` - セッション開始時の初期化
2. `/constitution init` - プロジェクト原則の初期化
3. `/generate-prd` - PRD生成
4. `/generate-spec` - 仕様書生成

## 比較ケース

- **CLI有効**: `cli.enabled: true` → 通常のスキル（`constitution`, `generate-prd`, `generate-spec`）を使用
- **CLI無効**: `cli.enabled: false` → CLI-fallbackスキル（`constitution-cli-fallback`, `generate-prd-cli-fallback`, `generate-spec-cli-fallback`）を使用

## 実行フロー

このスキルは自動実行モードで動作し、以下の6つのPhaseを順番に実行します。

---

## Phase 1: 環境構築

テスト用のディレクトリとgitリポジトリを作成します。

<bash description="テスト環境を構築">
SCRIPT=".claude/skills/cli-ab-test/scripts/cli-ab-test.sh"
bash "${SCRIPT}" setup
</bash>

---

## Phase 2: CLI有効ケース実行

CLI連携が有効な状態でスキルを実行し、メトリクスを記録します。

<bash description="CLI有効ケースを実行" timeout="600000">
SCRIPT=".claude/skills/cli-ab-test/scripts/cli-ab-test.sh"
bash "${SCRIPT}" run cli-enabled
</bash>

---

## Phase 3: CLI無効ケース実行

CLI連携が無効な状態でスキルを実行し、メトリクスを記録します。

<bash description="CLI無効ケースを実行" timeout="600000">
SCRIPT=".claude/skills/cli-ab-test/scripts/cli-ab-test.sh"
bash "${SCRIPT}" run cli-disabled
</bash>

---

## Phase 4: ログ収集

両ケースのログを収集して確認します。

<bash description="ログを収集">
SCRIPT=".claude/skills/cli-ab-test/scripts/cli-ab-test.sh"
bash "${SCRIPT}" collect
</bash>

---

## Phase 5: 比較レポート生成

実行時間・トークン使用量・コストの比較レポートを生成します。

<bash description="比較レポートを生成">
SCRIPT=".claude/skills/cli-ab-test/scripts/cli-ab-test.sh"
bash "${SCRIPT}" report
</bash>

---

## Phase 6: レポート読み取りと表示

生成された比較レポートを読み取り、ユーザーに表示します。

<read file_path="/tmp/cli-ab-test/COMPARISON_REPORT.md" />

---

## 期待される出力

- `/tmp/cli-ab-test/logs/cli-enabled/` - CLI有効ケースのログ
- `/tmp/cli-ab-test/logs/cli-disabled/` - CLI無効ケースのログ
- `/tmp/cli-ab-test/COMPARISON_REPORT.md` - 比較レポート

## 制約事項

- テストは非対話モード（`--ci` フラグ）で実行
- ダミーの要件を使用（実際のプロジェクトコンテキストは不要）
- テスト時間は約15分（各ケース7-8分想定）

## CI/CD統合（将来）

GitHub Actionsで定期的に実行し、CLI連携のパフォーマンス影響をトラッキング可能。

```yaml
- name: Run CLI A/B Test
  run: |
    claude --print -p "/cli-ab-test"
    cat /tmp/cli-ab-test/COMPARISON_REPORT.md
```
