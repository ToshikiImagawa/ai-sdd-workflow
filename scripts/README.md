# Scripts

このディレクトリには、マーケットプレイスの管理・検証スクリプトが含まれています。

## validate-marketplace.sh

マーケットプレイスとプラグイン構造の包括的な検証を行うスクリプトです。

### 使用方法

```bash
./scripts/validate-marketplace.sh
```

### 検証内容

1. **JSON構文検証**
   - `marketplace.json` の JSON 構文をチェック

2. **マーケットプレイス構造チェック**
   - 必須フィールド（`name`, `metadata`, `plugins`）の存在確認
   - プラグイン数の表示

3. **プラグイン必須フィールドチェック**
   - 各プラグインの `source`, `version` フィールドの確認

4. **plugin.json ファイル検証**
   - すべての `plugin.json` ファイルの JSON 構文チェック
   - 必須フィールド（`name`, `version`）の確認

5. **バージョン整合性チェック**
   - `marketplace.json` と各プラグインの `plugin.json` でバージョンが一致するか確認

6. **Claude CLI検証**
   - `claude plugin validate .` による公式検証
   - Claude CLI がインストールされていない場合はスキップ

7. **スキルとエージェントファイルチェック**
   - スキルファイル（`SKILL.md`）の数を表示
   - エージェントファイル（`agents/*.md`）の数を表示
   - フロントマターの存在確認

### 出力例

```
🔍 Validating Anthony Claude Marketplace
========================================

📝 Step 1: Validating JSON syntax...
✅ marketplace.json is valid JSON

📋 Step 2: Checking marketplace.json structure...
✅ Found 4 plugins in marketplace

🔌 Step 3: Checking plugin required fields...
  - Checking plugin: pr-workflow
  - Checking plugin: venue-layout-plan
  - Checking plugin: jira-workflow
  - Checking plugin: plugin-development
✅ All plugins have required fields

📦 Step 4: Validating plugin.json files...
  - Validating: plugins/shared/pr-workflow/.claude-plugin/plugin.json
  ...
✅ All plugin.json files are valid

🔄 Step 5: Checking version consistency...
  ✅ Plugin 'pr-workflow': version 1.3.0 (consistent)
  ...

🤖 Step 6: Validating with Claude CLI...
✅ Claude CLI validation passed

📚 Step 7: Checking skill and agent files...
  ✅ Found 14 skill files
  ✅ Found 8 agent files

========================================
✅ All validation checks passed!
========================================
```

### エラーが発生した場合

エラーが発生すると、スクリプトは即座に終了し（`set -e`）、エラーメッセージが表示されます。

- **JSON構文エラー**: `jq` でパースエラーの詳細が表示されます
- **必須フィールドエラー**: どのフィールドが欠けているか表示されます
- **バージョン不一致**: どのプラグインでバージョンが異なるか表示されます

### CI/CD統合

このスクリプトと同じ検証が GitHub Actions でも実行されます。
詳細は `.github/workflows/validate-marketplace.yml` を参照してください。
