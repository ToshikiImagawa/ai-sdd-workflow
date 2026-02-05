---
name: plugin-integration-test
description: "sdd-workflow / sdd-workflow-ja プラグインの統合テストを実行する。session-start.sh、環境変数、/sdd-init を検証しログを記録する。"
disable-model-invocation: true
allowed-tools: Bash(bash:*), Read
---

# Plugin Integration Test

sdd-workflow / sdd-workflow-ja プラグインの統合テストを実行し、session-start.sh のフック動作・環境変数設定・`/sdd-init` スキルの動作を検証する。

## 前提条件

- `claude` CLI がインストール済み
- リポジトリルートに `plugins/sdd-workflow/` と `plugins/sdd-workflow-ja/` が存在すること

## パス定義

```
REPO_ROOT = $(git rev-parse --show-toplevel)
SCRIPT = ${REPO_ROOT}/.claude/skills/plugin-integration-test/scripts/plugin-integration-test.sh
PLUGINS_DIR = ${REPO_ROOT}/plugins
TEST_BASE = /tmp/ai-sdd-plugin-test
```

## 処理フロー

以下の Phase を順番に実行する。

### Phase 1: 環境構築

スクリプトの `setup` コマンドでテスト環境を構築する。

```bash
bash "${SCRIPT}" setup
```

これにより `/tmp/ai-sdd-plugin-test/` 以下にプラグインごとのテストディレクトリが作成される（git init + 空 CLAUDE.md のコミット済み）。

### Phase 2: session-start テスト

各プラグインに対して `run` コマンドを実行する。`${PLUGINS_DIR}` 内の各プラグインディレクトリに対して順番に実行すること。

```bash
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow"
bash "${SCRIPT}" run "${PLUGINS_DIR}/sdd-workflow-ja"
```

内部で `claude --plugin-dir <plugin_dir> --print -p` によるサブセッションを起動し、session-start フックを実行させる。
フックが生成する以下のファイルを直接検証する（環境変数は `CLAUDE_ENV_FILE` 経由で設定されるため、サブセッション内の `echo` では取得できない）:
- `.sdd-config.json` の生成と `lang` フィールドの値（`SDD_LANG` の代替検証）
- `.sdd/` ディレクトリと `AI-SDD-PRINCIPLES.md` の配置

### Phase 3: /sdd-init テスト

各プラグインに対して `sdd-init` コマンドを実行する。

```bash
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow"
bash "${SCRIPT}" sdd-init "${PLUGINS_DIR}/sdd-workflow-ja"
```

**前提条件チェック**: `/sdd-init` 実行前に `session-start.sh` が正しく実行されたかを検証する。以下のファイルが存在するかチェックし、結果を `session-start-check.log` に記録する:
- `.sdd-config.json`
- `.sdd/` ディレクトリ
- `.sdd/AI-SDD-PRINCIPLES.md`

内部で `claude --plugin-dir <plugin_dir> --print -p "/sdd-init"` を実行し、以下を検証する:
- `/sdd-init` スキルの正常実行
- `.sdd/` 配下のディレクトリ構造生成
- `CLAUDE.md` への AI-SDD セクション追記

### Phase 3b: 生成系スキルテスト

各プラグインに対して `gen-skills` コマンドを実行する。Phase 3（`/sdd-init`）の完了後に実行すること。

```bash
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow"
bash "${SCRIPT}" gen-skills "${PLUGINS_DIR}/sdd-workflow-ja"
```

内部で以下のスキルをサブセッションで実行し、生成ファイルと言語を検証する:
- `/constitution init` - CONSTITUTION.md の生成と言語検証
- `/generate-prd --ci <ダミー要件>` - PRD ファイルの生成と言語検証（`--ci` フラグで非対話モード実行）
- `/generate-spec --ci <ダミー要件>` - 仕様書ファイルの生成と言語検証（`--ci` フラグで非対話モード実行）

`--ci` フラグにより、Vibe Coding リスク評価・上書き確認・レビューエージェント呼び出しがスキップされ、`claude --print -p` での非対話実行が可能になる。

生成されたファイルはログディレクトリにコピーされる。

### Phase 4: ログ収集

各プラグインのログを収集する。

```bash
bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow"
bash "${SCRIPT}" collect "${PLUGINS_DIR}/sdd-workflow-ja"
```

### Phase 5: ログ読み取りとテスト結果判定

収集した各ログファイルを `Read` ツールで読み取り、テスト結果を判定する。

読み取るログファイル（各プラグインについて）:

1. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/config.json`** - `.sdd-config.json` が正しく生成されたか（`lang` フィールドで言語設定を検証）
2. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/session-start.log`** - session-start サブセッションの実行ログ
3. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/sdd-structure-after-session.log`** - session-start 後の `.sdd/` 配下のファイル構造
4. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/AI-SDD-PRINCIPLES.md`** - 配置された AI-SDD-PRINCIPLES.md の内容
5. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/session-start-check.log`** - `/sdd-init` 実行前の session-start.sh 実行確認結果
6. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/sdd-init.log`** - `/sdd-init` が正常に実行されたか
7. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/sdd-structure.log`** - `/sdd-init` 後の `.sdd/` 配下のファイル構造
8. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/CLAUDE.md.after-init`** - AI-SDD セクションが追記されたか
9. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/constitution-init.log`** - `/constitution init` の実行ログ
10. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/CONSTITUTION.md`** - 生成された CONSTITUTION.md の内容と言語
11. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/generate-prd.log`** - `/generate-prd` の実行ログ
12. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/prd-*.md`** - 生成された PRD ファイルの内容と言語
13. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/generate-spec.log`** - `/generate-spec` の実行ログ
14. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/spec-*.md`** - 生成された仕様書ファイルの内容と言語
15. **`/tmp/ai-sdd-plugin-test/logs/<plugin>/sdd-structure-after-gen.log`** - 生成系スキル実行後のファイル構造

#### 判定基準

各テスト項目について PASS / FAIL を判定:

| テスト項目 | PASS 条件 |
|-----------|----------|
| session-start.sh 実行 | session-start.log にエラーなし |
| .sdd-config.json 生成 | config.json が存在し、`root`/`lang`/`directories` を含む |
| SDD_LANG 言語設定 | config.json の `lang` フィールドが期待値と一致（sdd-workflow: `"en"`, sdd-workflow-ja: `"ja"`） |
| .sdd ディレクトリ作成 | sdd-structure-after-session.log にファイルが記録されている |
| AI-SDD-PRINCIPLES.md 配置 | AI-SDD-PRINCIPLES.md が存在し、frontmatter に `version` が含まれる |
| session-start 前提条件チェック | session-start-check.log の `session_start_executed` が `true` |
| /sdd-init 実行 | sdd-init.log にエラーなし |
| CLAUDE.md AI-SDD セクション | CLAUDE.md.after-init に `## AI-SDD Instructions` が含まれる |
| CLAUDE.md 言語検証 | CLAUDE.md.after-init の AI-SDD セクションが正しい言語で生成されていること。sdd-workflow: 英語（`This project follows`を含む）、sdd-workflow-ja: 日本語（`このプロジェクトは`を含む） |
| /constitution init 実行 | constitution-init.log にエラーなし、CONSTITUTION.md が生成されている |
| CONSTITUTION.md 言語検証 | CONSTITUTION.md の内容がプラグインの期待言語で記述されていること |
| /generate-prd 実行 | generate-prd.log にエラーなし、`.sdd/requirement/` 配下に PRD ファイルが生成されている |
| PRD 言語検証 | 生成された PRD ファイル（prd-*.md）の内容がプラグインの期待言語で記述されていること |
| /generate-spec 実行 | generate-spec.log にエラーなし、`.sdd/specification/` 配下に仕様書ファイルが生成されている |
| 仕様書 言語検証 | 生成された仕様書ファイル（spec-*.md）の内容がプラグインの期待言語で記述されていること |

#### プラグインと期待言語の対応

| プラグイン | 期待 SDD_LANG | CLAUDE.md 言語マーカー |
|-----------|-------------|---------------------|
| sdd-workflow | `en` | `This project follows AI-SDD` |
| sdd-workflow-ja | `ja` | `このプロジェクトは AI-SDD` |

### Phase 6: TEST_SUMMARY.md 生成

サマリーテンプレートを生成する。

```bash
bash "${SCRIPT}" summary
```

生成された `/tmp/ai-sdd-plugin-test/TEST_SUMMARY.md` を読み取り、Phase 5 の判定結果で各テスト項目の「結果」列を PASS / FAIL で埋めて、最終的なテスト結果をユーザーに報告する。

## 出力

テスト完了後、以下を報告する:

1. 各プラグインの各テスト項目の PASS / FAIL
2. 全体の成功率（PASS数 / 全テスト数）
3. FAIL がある場合は該当ログの抜粋と原因の推定
4. `/tmp/ai-sdd-plugin-test/TEST_SUMMARY.md` のパス
