---
name: cli-ab-test
description: "CLI有効/無効のA/Bテストを実行し、トークン使用量を比較する。CLI分岐スキル（task-breakdown, constitution validate, check-spec）に特化してCLI有効時のトークン削減効果を測定する。"
disable-model-invocation: true
context: fork
user-invocable: true
allowed-tools: Bash, Read
allowed-prompts:
  - tool: Bash
    prompt: "*"
---

# CLI A/B Test

CLI有効/無効の2パターンでCLI分岐スキル（`SDD_CLI_AVAILABLE` で処理が変わるスキル）を実行し、トークン使用量を比較するA/Bテスト。

## 実行ポリシー

**このスキルは自動実行モードで動作します:**
- Phase 1～4を順番に自動実行する
- 各フェーズの実行前にユーザーに確認を求めない
- 全てのフェーズ完了後に結果を報告する

## 前提条件

- `claude` CLI がインストール済み
- リポジトリルートに `plugins/sdd-workflow/` が存在すること

## パス定義

```
REPO_ROOT = $(git rev-parse --show-toplevel)
SCRIPT = ${REPO_ROOT}/.claude/skills/cli-ab-test/scripts/cli-ab-test.sh
PLUGINS_DIR = ${REPO_ROOT}/plugins
TEST_BASE = /tmp/ai-sdd-cli-ab-test
```

## 処理フロー

**IMPORTANT: 以下の Phase 1～4 を自動的に順番に実行してください。各フェーズの実行前にユーザーに確認を求めず、連続して実行してください。**

### Phase 1: 環境構築

スクリプトの `setup` コマンドでテスト環境を構築する。

```bash
bash "${SCRIPT}" setup
```

これにより `/tmp/ai-sdd-cli-ab-test/` 以下に2つのテストディレクトリが作成される:
- `sdd-workflow` — ベースライン（CLI無効）
- `sdd-workflow-with-cli` — CLI有効設定

### Phase 2: 前提条件構築（メトリクス比較対象外）

> これらのスキルはCLI分岐しないため、メトリクス比較の対象としない。
> Phase 3 のCLI分岐スキルを実行するための前提ファイル（CONSTITUTION.md, PRD, spec, design）を生成する。

両テストケースに対して session-start → sdd-init → gen-skills を順次実行する。

```bash
# ベースライン (CLI無効)
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow"
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow"
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow"

# CLI有効
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-cli
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-cli
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-cli
```

### Phase 3: CLI分岐スキル実行（メトリクス比較対象）

CLI分岐スキル（`SDD_CLI_AVAILABLE` で処理が変わるスキル）を実行し、メトリクスを収集する。

```bash
# ベースライン (CLI無効)
bash "${SCRIPT}" cli-skills "${PLUGINS_DIR}/sdd-workflow"

# CLI有効
bash "${SCRIPT}" cli-skills "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-cli
```

### Phase 4: ログ収集・テスト結果判定・トークン比較

ログ収集とサマリーテンプレートを生成する。

```bash
bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" && bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-cli
bash "${SCRIPT}" summary
```

生成された `/tmp/ai-sdd-cli-ab-test/TEST_SUMMARY.md` を読み取り、以下を判定する:

1. 各テストケースのCLI分岐スキルテスト項目（PASS / FAIL）
2. トークン比較テーブルの内容確認

#### 判定基準

CLI分岐スキルの各テスト項目について PASS / FAIL を判定:

| テスト項目 | PASS 条件 |
|-----------|----------|
| /task-breakdown 実行 | ログにエラーなし、`.sdd/task/` 配下にタスクファイル生成 |
| /constitution validate 実行 | ログにエラーなし、検証レポート出力 |
| /check-spec 実行 | ログにエラーなし、整合性チェック結果出力 |

読み取るログファイル（各テストケースについて）:

**前提条件構築フェーズ:**
1. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/config.json`**
2. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/session-start.jsonl`**
3. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/sdd-init.jsonl`**
4. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/constitution-init.jsonl`**
5. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/generate-prd.jsonl`**
6. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/generate-spec.jsonl`**

**CLI分岐スキルフェーズ:**
7. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/task-breakdown.jsonl`**
8. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/task-files.log`**
9. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/constitution-validate.jsonl`**
10. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/check-spec.jsonl`**
11. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/sdd-structure-after-cli-skills.log`**
12. **`/tmp/ai-sdd-cli-ab-test/logs/<test_case>/timing.log`**

## 出力

**全てのPhase（1～4）を自動実行した後**、テスト完了メッセージとして以下を報告する:

1. 各テストケースのCLI分岐スキルテスト項目の PASS / FAIL
2. **トークン使用量比較テーブル**（CLI分岐スキルごとの CLI無効 vs CLI有効 のトークン数・コスト・削減率）
3. **各コマンドの実行時間集計**（`timing.log` から読み取り、テーブル形式で表示）
4. FAIL がある場合は該当ログの抜粋と原因の推定
5. `/tmp/ai-sdd-cli-ab-test/TEST_SUMMARY.md` のパス

**重要**: Phase 1～4の実行中にユーザーに進行確認を求めないこと。
