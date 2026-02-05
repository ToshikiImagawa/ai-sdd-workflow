#!/bin/bash
set -e

# マーケットプレイスとプラグイン構造の検証スクリプト
# GitHub Actionsと同じ検証をローカルで実行できます

echo "🔍 Validating Anthony Claude Marketplace"
echo "========================================"
echo ""

# 1. JSON構文検証
echo "📝 Step 1: Validating JSON syntax..."
if jq empty .claude-plugin/marketplace.json 2>/dev/null; then
    echo "✅ marketplace.json is valid JSON"
else
    echo "❌ marketplace.json has invalid JSON syntax"
    exit 1
fi
echo ""

# 2. マーケットプレイス構造チェック
echo "📋 Step 2: Checking marketplace.json structure..."
jq -e '.name' .claude-plugin/marketplace.json > /dev/null || (echo "❌ 'name' field is missing" && exit 1)
jq -e '.metadata' .claude-plugin/marketplace.json > /dev/null || (echo "❌ 'metadata' field is missing" && exit 1)
jq -e '.plugins' .claude-plugin/marketplace.json > /dev/null || (echo "❌ 'plugins' field is missing" && exit 1)

PLUGIN_COUNT=$(jq '.plugins | length' .claude-plugin/marketplace.json)
echo "✅ Found $PLUGIN_COUNT plugins in marketplace"
echo ""

# 3. プラグイン必須フィールドチェック
echo "🔌 Step 3: Checking plugin required fields..."
jq -r '.plugins[] | .name' .claude-plugin/marketplace.json | while read plugin_name; do
    echo "  - Checking plugin: $plugin_name"
    jq -e ".plugins[] | select(.name == \"$plugin_name\") | .source" .claude-plugin/marketplace.json > /dev/null || (echo "❌ Plugin $plugin_name is missing 'source' field" && exit 1)
    jq -e ".plugins[] | select(.name == \"$plugin_name\") | .version" .claude-plugin/marketplace.json > /dev/null || (echo "❌ Plugin $plugin_name is missing 'version' field" && exit 1)
done
echo "✅ All plugins have required fields"
echo ""

# 4. plugin.json ファイル検証
echo "📦 Step 4: Validating plugin.json files..."
find plugins -name "plugin.json" -type f | while read plugin_file; do
    echo "  - Validating: $plugin_file"
    jq empty "$plugin_file" || (echo "❌ Invalid JSON: $plugin_file" && exit 1)

    jq -e '.name' "$plugin_file" > /dev/null || (echo "❌ 'name' field is missing in $plugin_file" && exit 1)
    jq -e '.version' "$plugin_file" > /dev/null || (echo "❌ 'version' field is missing in $plugin_file" && exit 1)
done
echo "✅ All plugin.json files are valid"
echo ""

# 5. バージョン整合性チェック
echo "🔄 Step 5: Checking version consistency..."
jq -r '.plugins[] | "\(.name)|\(.version)|\(.source)"' .claude-plugin/marketplace.json | while IFS='|' read name marketplace_version source; do
    plugin_json="${source}/.claude-plugin/plugin.json"

    if [ -f "$plugin_json" ]; then
        plugin_version=$(jq -r '.version' "$plugin_json")

        if [ "$marketplace_version" != "$plugin_version" ]; then
            echo "❌ Version mismatch for plugin '$name':"
            echo "   marketplace.json: $marketplace_version"
            echo "   plugin.json: $plugin_version"
            exit 1
        else
            echo "  ✅ Plugin '$name': version $marketplace_version (consistent)"
        fi
    else
        echo "  ⚠️  Plugin '$name': plugin.json not found at $plugin_json"
    fi
done
echo ""

# 6. Claude CLI検証
echo "🤖 Step 6: Validating with Claude CLI..."
if command -v claude &> /dev/null; then
    claude plugin validate .
    echo "✅ Claude CLI validation passed"
else
    echo "⚠️  Claude CLI not found. Skipping claude plugin validate."
    echo "   Install Claude CLI: https://claude.ai/code"
fi
echo ""

# 7. スキルとエージェントファイルチェック
echo "📚 Step 7: Checking skill and agent files..."
SKILL_COUNT=$(find plugins -name "SKILL.md" -type f | wc -l)
echo "  ✅ Found $SKILL_COUNT skill files"

AGENT_COUNT=$(find plugins -path "*/agents/*.md" -type f | wc -l)
echo "  ✅ Found $AGENT_COUNT agent files"

# スキルファイルのフロントマター検証
find plugins -name "SKILL.md" -type f | while read skill_file; do
    if ! grep -q "^---$" "$skill_file"; then
        echo "  ⚠️  Warning: $skill_file may be missing frontmatter"
    fi
done
echo ""

# サマリー
echo "========================================"
echo "✅ All validation checks passed!"
echo "========================================"
