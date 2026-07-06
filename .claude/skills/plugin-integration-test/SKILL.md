---
name: plugin-integration-test
description: "sdd-workflow プラグインの統合テストを実行する。session-start.py、環境変数、/sdd-init を検証しログを記録する。"
version: 1.0.0
license: MIT
argument-hint: "[none]"
disable-model-invocation: true
context: fork
user-invocable: true
allowed-tools: Bash, Read
allowed-prompts:
  - tool: Bash
    prompt: "*"
---

# Plugin Integration Test

sdd-workflow プラグインの統合テストを実行し、session-start.py のフック動作・環境変数設定・`/sdd-init` スキルの動作を検証する。

## 実行ポリシー

**このスキルは自動実行モードで動作します:**
- Phase 1～6を順番に自動実行する
- 各フェーズの実行前にユーザーに確認を求めない
- 全てのフェーズ完了後に結果を報告する

## 前提条件

- `claude` CLI がインストール済み
- リポジトリルートに `plugins/sdd-workflow/` が存在すること

## パス定義

```
REPO_ROOT = $(git rev-parse --show-toplevel)
SCRIPT = ${REPO_ROOT}/.claude/skills/plugin-integration-test/scripts/plugin-integration-test.sh
PLUGINS_DIR = ${REPO_ROOT}/plugins
TEST_BASE = /tmp/ai-sdd-plugin-test
```

## 処理フロー

**IMPORTANT: 以下の Phase 1～6 を自動的に順番に実行してください。各フェーズの実行前にユーザーに確認を求めず、連続して実行してください。**

以下の Phase を順番に実行する。

### Phase 1: 環境構築

スクリプトの `setup` コマンドでテスト環境を構築する。

```bash
bash "${SCRIPT}" setup
```

これにより `/tmp/ai-sdd-plugin-test/` 以下にプラグインごとのテストディレクトリが作成される（git init + 空 CLAUDE.md のコミット済み）。

**追加テストケース**: `sdd-workflow-with-ja-config` ディレクトリも作成され、事前に `lang: "ja"` の `.sdd-config.json` が配置される。このテストケースは、既存の設定ファイルの言語設定がスキルに正しく継承されるかを検証する。

### Phase 2: session-start テスト

2つのテストケース（sdd-workflow / sdd-workflow-with-ja-config）を **1つの Bash 呼び出し**で直列実行する（確認不要）。

```bash
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" && \
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-ja-config
```

`sdd-workflow-with-ja-config` は、既存の `.sdd-config.json` (lang: ja) がある状態で sdd-workflow プラグインを使うケース。

内部で `claude --plugin-dir <plugin_dir> --print -p` によるサブセッションを起動し、session-start フックを実行させる。
フックが生成する以下のファイルを直接検証する（環境変数は `CLAUDE_ENV_FILE` 経由で設定されるため、サブセッション内の `echo` では取得できない）:
- `.sdd-config.json` の生成と `lang` フィールドの値（`SDD_LANG` の代替検証）
- `.sdd/` ディレクトリと `AI-SDD-PRINCIPLES.md` の配置
- **既存設定継承テスト**: 既存の `.sdd-config.json` が上書きされず、`lang: ja` が維持されること

### Phase 3: /sdd-init テスト

2つのテストケースを **1つの Bash 呼び出し**で直列実行する（確認不要）。

```bash
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" && \
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-ja-config
```

**前提条件チェック**: `/sdd-init` 実行前に `session-start.py` が正しく実行されたかを検証する。以下のファイルが存在するかチェックし、結果を `session-start-check.log` に記録する:
- `.sdd-config.json`
- `.sdd/` ディレクトリ
- `.sdd/AI-SDD-PRINCIPLES.md`

内部で `claude --plugin-dir <plugin_dir> --print -p "/sdd-init --ci"` を実行し、以下を検証する（`--ci` フラグで非対話モード実行）:
- `/sdd-init` スキルの正常実行
- `.sdd/` 配下のディレクトリ構造生成
- `CLAUDE.md` への AI-SDD セクション追記

### Phase 3b: 生成系スキルテスト

Phase 3（`/sdd-init`）の完了後に、2つのテストケースを **1つの Bash 呼び出し**で直列実行する（確認不要、timeout=600000）。

```bash
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" && \
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-ja-config
```

内部で以下のスキルをサブセッションで実行し、生成ファイルと言語を検証する:
- `/constitution init <コンテキスト>` - CONSTITUTION.md の生成と言語検証（コンテキスト引数で非対話モード実行）
- `/generate-prd --ci <ダミー要件>` - PRD ファイルの生成と言語検証（`--ci` フラグで非対話モード実行）
- `/generate-spec --ci <ダミー要件>` - 仕様書ファイルの生成と言語検証（`--ci` フラグで非対話モード実行）

`--ci` フラグにより、Vibe Coding リスク評価・上書き確認・レビューエージェント呼び出しがスキップされ、`claude --print -p` での非対話実行が可能になる。

生成されたファイルはログディレクトリにコピーされる。

### Phase 4: ログ収集

各プラグインのログを収集する。以下のコマンドを1つのBash呼び出しで実行する（確認不要）。

```bash
bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" && bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" sdd-workflow-with-ja-config
```

### Phase 5: テスト結果判定

判定は2段階で行う。

#### 5a: 決定論的判定（judge コマンド）

ファイル存在・設定値一致・マーカー含有などの機械的な判定は、スクリプトの `judge` コマンドで実行する（1つの Bash 呼び出し、確認不要）:

```bash
bash "${SCRIPT}" judge sdd-workflow en && \
bash "${SCRIPT}" judge sdd-workflow-with-ja-config ja
```

出力は項目ごとに `PASS: <項目>` / `FAIL: <項目> (<理由>)` の形式。判定ロジックの詳細はスクリプトを参照。

#### 5b: 言語内容の検証（LLM 判定）

生成文書の**内容言語**はスクリプトでは判定できないため、以下を Read で読み取り、期待言語（sdd-workflow: 英語 / sdd-workflow-with-ja-config: 日本語）で記述されているかを判定する:

1. **`/tmp/ai-sdd-plugin-test/logs/<test-case>/CONSTITUTION.md`** - CONSTITUTION.md の言語検証
2. **`/tmp/ai-sdd-plugin-test/logs/<test-case>/prd-*.md`** - PRD の言語検証
3. **`/tmp/ai-sdd-plugin-test/logs/<test-case>/spec-*.md`** - 仕様書の言語検証

FAIL があった場合のみ、原因分析のため該当する実行ログ（`session-start.log`, `sdd-init.log`, `constitution-init.log`, `generate-prd.log`, `generate-spec.log`）を Read で読み取る。

#### プラグインと期待言語の対応

| プラグイン | 期待 SDD_LANG | CLAUDE.md 言語マーカー |
|-----------|-------------|---------------------|
| sdd-workflow | `en` | `This project follows AI-SDD` |
| sdd-workflow-with-ja-config | `ja` | `このプロジェクトは AI-SDD` |

**sdd-workflow-with-ja-config** は、`sdd-workflow` プラグインを使用しているが、既存の `.sdd-config.json` で `lang: "ja"` が設定されているケース。このテストにより、既存設定がスキル実行時に正しく継承されるかを検証する。

### Phase 6: TEST_SUMMARY.md 生成

サマリーテンプレートを生成する。

```bash
bash "${SCRIPT}" summary
```

生成された `/tmp/ai-sdd-plugin-test/TEST_SUMMARY.md` を読み取り、Phase 5 の判定結果で各テスト項目の「結果」列を PASS / FAIL で埋めて、最終的なテスト結果をユーザーに報告する。

## 出力

**全てのPhase（1～6）を自動実行した後**、テスト完了メッセージとして以下を報告する:

1. 各プラグインの各テスト項目の PASS / FAIL
2. 全体の成功率（PASS数 / 全テスト数）
3. **各コマンドの実行時間集計**（`timing.log` から読み取り、テーブル形式で表示）
4. FAIL がある場合は該当ログの抜粋と原因の推定
5. `/tmp/ai-sdd-plugin-test/TEST_SUMMARY.md` のパス

### 実行時間の表示形式

各プラグインについて、以下の形式でタイミング情報を表示すること:

```markdown
### <plugin-name> 実行時間

| フェーズ | 実行時間 |
|---------|----------|
| session-start | X秒 |
| sdd-init | X秒 |
| constitution-init | X秒 |
| generate-prd | X秒 |
| generate-spec | X秒 |
| **合計** | **X分Y秒 (Z秒)** |
```

**重要**: Phase 1～6の実行中にユーザーに進行確認を求めないこと。
