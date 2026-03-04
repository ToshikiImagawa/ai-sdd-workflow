---
name: plugin-integration-test
description: "sdd-workflowプラグインの成果物生成確認テスト。言語別・CLI有無別の4ケースで、session-start、/sdd-init、生成系スキルの動作を検証する。"
disable-model-invocation: true
context: fork
user-invocable: true
allowed-tools: Bash, Read
allowed-prompts:
  - tool: Bash
    prompt: "*"
---

# Plugin Integration Test

sdd-workflowプラグインの成果物生成確認テストを実行し、4ケース（言語別×CLI有無別）でドキュメント生成機能を検証する。

## 実行ポリシー

**このスキルは自動実行モードで動作します:**

- Phase 1～5を順番に自動実行する
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

**IMPORTANT: 以下の Phase 1～5 を自動的に順番に実行してください。各フェーズの実行前にユーザーに確認を求めず、連続して実行してください。
**

以下の Phase を順番に実行する。

### Phase 1: 環境構築

スクリプトの `setup` コマンドでテスト環境を構築する。

```bash
bash "${SCRIPT}" setup
```

これにより `/tmp/ai-sdd-plugin-test/` 以下に4ケースのテストディレクトリが作成される（git init + 空 CLAUDE.md +
.sdd-config.json のコミット済み）:

- `en-cli-disabled`: lang=en, cli.enabled=false
- `en-cli-enabled`: lang=en, cli.enabled=true
- `ja-cli-disabled`: lang=ja, cli.enabled=false
- `ja-cli-enabled`: lang=ja, cli.enabled=true

### Phase 2: session-start テスト

各テストケースに対して `run` コマンドを実行する。以下の4つのコマンドを順番に実行する（確認不要）。

```bash
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" en-cli-disabled
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" en-cli-enabled
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" ja-cli-disabled
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow" ja-cli-enabled
```

内部で `claude --plugin-dir <plugin_dir> --print -p` によるサブセッションを起動し、session-start フックを実行させる。
フックが生成する以下のファイルを直接検証する（環境変数は `CLAUDE_ENV_FILE` 経由で設定されるため、サブセッション内の `echo`
では取得できない）:

- `.sdd-config.json` の生成と `lang` フィールドの値（`SDD_LANG` の代替検証）
- `.sdd/` ディレクトリと `AI-SDD-PRINCIPLES.md` の配置

### Phase 3: /sdd-init テスト

各テストケースに対して `sdd-init` コマンドを実行する。以下の4つのコマンドを順番に実行する（確認不要）。

```bash
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" en-cli-disabled
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" en-cli-enabled
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" ja-cli-disabled
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow" ja-cli-enabled
```

**前提条件チェック**: `/sdd-init` 実行前に `session-start.sh` が正しく実行されたかを検証する。以下のファイルが存在するかチェックし、結果を
`session-start-check.log` に記録する:

- `.sdd-config.json`
- `.sdd/` ディレクトリ
- `.sdd/AI-SDD-PRINCIPLES.md`

内部で `claude --plugin-dir <plugin_dir> --print -p "/sdd-init --ci"` を実行し、以下を検証する（`--ci`
フラグで非対話モード実行）:

- `/sdd-init` スキルの正常実行
- `.sdd/` 配下のディレクトリ構造生成
- `CLAUDE.md` への AI-SDD セクション追記

### Phase 3b: 生成系スキルテスト

各テストケースに対して `gen-skills` コマンドを実行する。Phase 3（`/sdd-init`
）の完了後に、以下の4つのコマンドを順番に実行する（確認不要、timeout=300000）。

```bash
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" en-cli-disabled
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" en-cli-enabled
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" ja-cli-disabled
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow" ja-cli-enabled
```

内部で以下のスキルをサブセッションで実行し、生成ファイルと言語を検証する:

- `/constitution init <コンテキスト>` - CONSTITUTION.md の生成と言語検証（コンテキスト引数で非対話モード実行）
- `/generate-prd --ci <ダミー要件>` - PRD ファイルの生成と言語検証（`--ci` フラグで非対話モード実行）
- `/generate-spec --ci <ダミー要件>` - 仕様書ファイルの生成と言語検証（`--ci` フラグで非対話モード実行）

`--ci` フラグにより、Vibe Coding リスク評価・上書き確認・レビューエージェント呼び出しがスキップされ、`claude --print -p`
での非対話実行が可能になる。

生成されたファイルはログディレクトリにコピーされる。

### Phase 4: ログ収集

各テストケースのログを収集する。以下のコマンドを1つのBash呼び出しで実行する（確認不要）。

```bash
bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" en-cli-disabled && bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" en-cli-enabled && bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" ja-cli-disabled && bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow" ja-cli-enabled
```

### Phase 5: ログ読み取りとテスト結果判定

収集した各ログファイルを `Read` ツールで読み取り、テスト結果を判定する。複数のログファイルを並列に読み取る（確認不要）。

読み取るログファイル（各テストケースについて）:

1. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/config.json`** - `.sdd-config.json` が正しく生成されたか（`lang`
   フィールドで言語設定を検証）
2. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/session-start.log`** - session-start サブセッションの実行ログ
3. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/sdd-structure-after-session.log`** - session-start 後の `.sdd/` 配下のファイル構造
4. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/AI-SDD-PRINCIPLES.md`** - 配置された AI-SDD-PRINCIPLES.md の内容
5. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/session-start-check.log`** - `/sdd-init` 実行前の session-start.sh 実行確認結果
6. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/sdd-init.log`** - `/sdd-init` が正常に実行されたか
7. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/sdd-structure.log`** - `/sdd-init` 後の `.sdd/` 配下のファイル構造
8. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/CLAUDE.md.after-init`** - AI-SDD セクションが追記されたか
9. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/constitution-init.log`** - `/constitution init` の実行ログ
10. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/CONSTITUTION.md`** - 生成された CONSTITUTION.md の内容と言語
11. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/generate-prd.log`** - `/generate-prd` の実行ログ
12. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/prd-*.md`** - 生成された PRD ファイルの内容と言語
13. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/generate-spec.log`** - `/generate-spec` の実行ログ
14. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/spec-*.md`** - 生成された仕様書ファイルの内容と言語
15. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/sdd-structure-after-gen.log`** - 生成系スキル実行後のファイル構造
16. **`/tmp/ai-sdd-plugin-test/logs/<test_case>/timing.log`** - 各コマンドの実行時間（`<phase>:<seconds>` 形式）

#### 判定基準

各テスト項目について PASS / FAIL を判定（14項目/ケース）:

| テスト項目                   | PASS 条件                                                                           |
|-------------------------|-----------------------------------------------------------------------------------|
| session-start.sh 実行     | session-start.log にエラーなし                                                          |
| .sdd-config.json 生成     | config.json が存在し、`root`/`lang`/`directories`/`cli` を含む                            |
| 言語設定                    | config.json の `lang` フィールドが期待値と一致（en系: `"en"`, ja系: `"ja"`）                       |
| .sdd ディレクトリ作成           | sdd-structure-after-session.log にファイルが記録されている                                     |
| AI-SDD-PRINCIPLES.md 配置 | AI-SDD-PRINCIPLES.md が存在し、frontmatter に `version` が含まれる                           |
| /sdd-init 前提条件          | session-start-check.log の全チェックが `exists`                                          |
| /sdd-init 実行            | sdd-init.log にエラーなし                                                               |
| CLAUDE.md AI-SDD セクション  | CLAUDE.md.after-init に `## AI-SDD Instructions` が含まれる                             |
| CLAUDE.md 言語検証          | CLAUDE.md.after-init が期待言語で生成されていること（en: `This project follows`, ja: `このプロジェクトは`） |
| /constitution init 実行   | constitution-init.log にエラーなし、CONSTITUTION.md が生成されている                             |
| CONSTITUTION.md 言語検証    | CONSTITUTION.md の内容が期待言語で記述されていること                                                |
| /generate-prd 実行        | generate-prd.log にエラーなし、`.sdd/requirement/` 配下に PRD ファイルが生成されている                  |
| PRD 言語検証                | 生成された PRD ファイル（prd-*.md）が期待言語で記述されていること                                           |
| /generate-spec 実行       | generate-spec.log にエラーなし、`.sdd/specification/` 配下に仕様書ファイルが生成されている                 |
| 仕様書 言語検証                | 生成された仕様書ファイル（spec-*.md）が期待言語で記述されていること                                            |

#### テストケースと期待言語の対応

| テストケース          | 期待 lang | CLI設定   | CLAUDE.md 言語マーカー              |
|-----------------|---------|---------|-------------------------------|
| en-cli-disabled | `en`    | `false` | `This project follows AI-SDD` |
| en-cli-enabled  | `en`    | `true`  | `This project follows AI-SDD` |
| ja-cli-disabled | `ja`    | `false` | `このプロジェクトは AI-SDD`            |
| ja-cli-enabled  | `ja`    | `true`  | `このプロジェクトは AI-SDD`            |

4ケースで以下を検証：

- **言語別動作**: en系とja系でテンプレートが正しく切り替わるか
- **CLI設定の影響**: CLI有効/無効でも成果物生成に影響しないか（パフォーマンス測定はcli-ab-testスキルで実施）

### Phase 5: TEST_SUMMARY.md 生成

サマリーテンプレートを生成する。

```bash
bash "${SCRIPT}" summary
```

生成された `/tmp/ai-sdd-plugin-test/TEST_SUMMARY.md` を読み取り、Phase 5 の判定結果で各テスト項目の「結果」列を PASS / FAIL
で埋めて、最終的なテスト結果をユーザーに報告する。

## 出力

**全てのPhase（1～5）を自動実行した後**、テスト完了メッセージとして以下を報告する:

1. 各テストケースの各テスト項目の PASS / FAIL（14項目×4ケース = 56項目）
2. 全体の成功率（PASS数 / 全テスト数）
3. **各コマンドの実行時間集計**（`timing.log` から読み取り、テーブル形式で表示）
4. FAIL がある場合は該当ログの抜粋と原因の推定
5. `/tmp/ai-sdd-plugin-test/TEST_SUMMARY.md` のパス

### 実行時間の表示形式

各テストケースについて、以下の形式でタイミング情報を表示すること:

```markdown
### <test-case-name> 実行時間

| フェーズ | 実行時間 |
|---------|----------|
| session-start | X秒 |
| sdd-init | X秒 |
| constitution-init | X秒 |
| generate-prd | X秒 |
| generate-spec | X秒 |
| **合計** | **X分Y秒 (Z秒)** |
```

**重要**: Phase 1～5の実行中にユーザーに進行確認を求めないこと。
