---
name: cli-integration-test
description: "sdd-cli と sdd-workflow プラグインの統合テスト。lint/index/search機能の動作確認を実施する。"
disable-model-invocation: true
context: fork
user-invocable: true
allowed-tools: Bash, Read
allowed-prompts:
  - tool: Bash
    prompt: "*"
---

# CLI Integration Test

sdd-cli と sdd-workflow プラグインの統合テストを実行し、CLI機能（lint/index/search）の動作を検証する。

## 実行ポリシー

**このスキルは自動実行モードで動作します:**
- plugin-integration-testで生成されたドキュメントを使用
- CLI有効なテストケースに対してのみテストを実行
- 全てのテスト完了後に結果を報告する

## 前提条件

- `uvx` がインストール済み（または `sdd-cli` がPATHに存在）
- plugin-integration-test が実行済みで、`/tmp/ai-sdd-plugin-test/` にテストケースが存在すること
- CLI有効なテストケース（`*-cli-enabled`）でドキュメントが生成されていること

## パス定義

```
REPO_ROOT = $(git rev-parse --show-toplevel)
SCRIPT = ${REPO_ROOT}/.claude/skills/cli-integration-test/scripts/cli-integration-test.sh
TEST_BASE = /tmp/ai-sdd-cli-integration-test
```

## 処理フロー

**IMPORTANT: 以下の Phase 1～3 を自動的に順番に実行してください。各フェーズの実行前にユーザーに確認を求めず、連続して実行してください。**

### Phase 1: 環境構築

スクリプトの `setup` コマンドでテスト環境を構築する。

```bash
bash "${SCRIPT}" setup
```

これにより `/tmp/ai-sdd-cli-integration-test/` ディレクトリが作成される。

### Phase 2: CLIテスト実行

plugin-integration-testで生成されたCLI有効なテストケースに対してテストを実行する。

以下のテストケースを対象とする:
- `/tmp/ai-sdd-plugin-test/en-cli-enabled`
- `/tmp/ai-sdd-plugin-test/ja-cli-enabled`

各テストケースに対して以下のコマンドを実行する（確認不要）:

```bash
bash "${SCRIPT}" test /tmp/ai-sdd-plugin-test/en-cli-enabled
bash "${SCRIPT}" test /tmp/ai-sdd-plugin-test/ja-cli-enabled
```

#### テスト内容

各テストケースで以下を検証:

1. **CLI検出確認**
   - `.sdd-config.json` の `cli.enabled` 設定確認
   - `uvx` または `sdd-cli` コマンドの存在確認

2. **sdd-cli lint --json**
   - 生成済みドキュメントのlint検証
   - JSON形式での出力確認
   - 終了コード確認

3. **sdd-cli index --quiet**
   - FTS5インデックス構築
   - 正常終了確認

4. **sdd-cli search --format json**
   - インデックス済みドキュメントの検索
   - JSON形式での結果出力確認
   - 終了コード確認

各コマンドの実行時間を `timing.log` に記録し、結果を `cli-test.log` に保存する。

### Phase 3: サマリーレポート生成

テスト結果のサマリーを生成する。

```bash
bash "${SCRIPT}" summary
```

生成された `/tmp/ai-sdd-cli-integration-test/CLI_TEST_SUMMARY.md` を読み取り、テスト結果をユーザーに報告する。

## 出力

**全てのPhase（1～3）を自動実行した後**、テスト完了メッセージとして以下を報告する:

1. 各テストケースの各CLI機能の PASS / FAIL
2. 全体の成功率（PASS数 / 全テスト数）
3. 各コマンドの実行時間
4. FAIL がある場合は該当ログの抜粋と原因の推定
5. `/tmp/ai-sdd-cli-integration-test/CLI_TEST_SUMMARY.md` のパス

### 判定基準

| テスト項目 | PASS 条件 |
|-----------|----------|
| CLI検出 | `uvx` または `sdd-cli` コマンドが利用可能 |
| lint --json | 終了コード 0、JSON出力あり |
| index --quiet | 終了コード 0 |
| search --format json | 終了コード 0、JSON出力あり |

### 実行時間の表示形式

各テストケースについて、以下の形式でタイミング情報を表示すること:

```markdown
### <test-case-name> 実行時間

| コマンド | 実行時間 |
|---------|----------|
| cli-lint | X秒 |
| cli-index | X秒 |
| cli-search | X秒 |
| **合計** | **X秒** |
```

**重要**: Phase 1～3の実行中にユーザーに進行確認を求めないこと。

## ログファイル

各テストケースについて以下のログファイルが生成される:

- `logs/<test_case>/cli-test.log` - テスト結果とメタデータ
- `logs/<test_case>/cli-lint.log` - lint コマンドの出力
- `logs/<test_case>/cli-index.log` - index コマンドの出力
- `logs/<test_case>/cli-search.log` - search コマンドの出力
- `logs/<test_case>/timing.log` - 実行時間記録

## スキップ条件

以下の場合、テストをスキップする:

- `.sdd-config.json` で `cli.enabled: false` が設定されている
- `uvx` も `sdd-cli` も利用不可能
- テストディレクトリが存在しない

スキップしたテストケースは SKIPPED として記録する。

## 使用例

### 手動実行

```bash
# 1. 環境構築
bash .claude/skills/cli-integration-test/scripts/cli-integration-test.sh setup

# 2. plugin-integration-testを実行してドキュメント生成
# (別途実施)

# 3. CLIテスト実行
bash .claude/skills/cli-integration-test/scripts/cli-integration-test.sh test /tmp/ai-sdd-plugin-test/en-cli-enabled

# 4. サマリー生成
bash .claude/skills/cli-integration-test/scripts/cli-integration-test.sh summary
```

### スキル実行（推奨）

```
/cli-integration-test
```

全フェーズが自動実行され、結果がレポートされる。
