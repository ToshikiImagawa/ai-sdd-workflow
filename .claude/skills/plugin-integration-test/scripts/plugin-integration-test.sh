#!/bin/bash
# plugin-integration-test.sh
# sdd-workflow / sdd-workflow-ja プラグインの統合テスト実行スクリプト
#
# Usage:
#   plugin-integration-test.sh setup              - テスト環境を構築
#   plugin-integration-test.sh run <plugin_dir>   - サブセッションでテスト実行
#   plugin-integration-test.sh sdd-init <plugin_dir> - /sdd-init テスト実行
#   plugin-integration-test.sh gen-skills <plugin_dir> - 生成系スキルテスト実行
#   plugin-integration-test.sh collect <plugin_dir>  - ログ収集
#   plugin-integration-test.sh summary            - TEST_SUMMARY.md テンプレート生成

set -euo pipefail

TEST_BASE="/tmp/ai-sdd-plugin-test"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
PLUGINS_DIR="${REPO_ROOT}/plugins"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# --- Phase 1: Setup ---
setup() {
    echo "=== Phase 1: テスト環境構築 ==="

    # クリーンアップ
    if [ -d "$TEST_BASE" ]; then
        rm -rf "$TEST_BASE"
        echo "既存のテストディレクトリを削除しました"
    fi

    mkdir -p "$TEST_BASE"
    echo "テストベースディレクトリ作成: $TEST_BASE"

    # プラグインごとのテストディレクトリを作成
    for plugin_dir in "$PLUGINS_DIR"/*/; do
        plugin_name="$(basename "$plugin_dir")"
        test_dir="${TEST_BASE}/${plugin_name}"

        mkdir -p "$test_dir"
        cd "$test_dir"

        # git init + 空 CLAUDE.md をコミット
        git init -q
        echo "" > CLAUDE.md
        git add CLAUDE.md
        git commit -q -m "initial commit"

        echo "テストディレクトリ作成: ${test_dir} (git initialized)"
    done

    # ログディレクトリ
    mkdir -p "${TEST_BASE}/logs"
    echo "ログディレクトリ作成: ${TEST_BASE}/logs"

    echo ""
    echo "=== セットアップ完了 ==="
    echo "テストディレクトリ: $TEST_BASE"
    echo "検出プラグイン:"
    for plugin_dir in "$PLUGINS_DIR"/*/; do
        echo "  - $(basename "$plugin_dir")"
    done
}

# --- Phase 2: サブセッション実行 (session-start + 基本検証) ---
run_test() {
    local plugin_dir="$1"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"
    local test_dir="${TEST_BASE}/${plugin_name}"
    local log_dir="${TEST_BASE}/logs/${plugin_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 2: session-start テスト [${plugin_name}] ==="

    # claude サブセッションを起動して session-start フックを実行させる
    # session-start.sh は CLAUDE_ENV_FILE 経由で環境変数を設定するため、
    # echo による環境変数確認はサンドボックス制限で動作しない。
    # 代わりに、フックが生成するファイル（.sdd-config.json, .sdd/ ディレクトリ）を直接検証する。
    cd "$test_dir"
    claude --plugin-dir "$plugin_dir" --print -p "session-start フックが実行されました。このメッセージが表示されれば正常です。" > "$log_dir/session-start.log" 2>&1 || true

    echo "ログ保存: $log_dir/session-start.log"

    # .sdd-config.json を保存（session-start.sh が自動生成）
    if [ -f "$test_dir/.sdd-config.json" ]; then
        cp "$test_dir/.sdd-config.json" "$log_dir/config.json"
        echo "config.json 保存完了"
    else
        echo "WARNING: .sdd-config.json が生成されていません"
    fi

    # .sdd ディレクトリ構造を記録
    if [ -d "$test_dir/.sdd" ]; then
        find "$test_dir/.sdd" -type f | sort > "$log_dir/sdd-structure-after-session.log" 2>&1 || true
        echo "sdd-structure-after-session.log 保存完了"
    else
        echo "WARNING: .sdd ディレクトリが作成されていません"
    fi

    # AI-SDD-PRINCIPLES.md を保存
    if [ -f "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" ]; then
        cp "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" "$log_dir/AI-SDD-PRINCIPLES.md"
        echo "AI-SDD-PRINCIPLES.md 保存完了"
    fi

    echo ""
}

# --- Phase 3: /sdd-init テスト ---
run_sdd_init_test() {
    local plugin_dir="$1"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"
    local test_dir="${TEST_BASE}/${plugin_name}"
    local log_dir="${TEST_BASE}/logs/${plugin_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 3: /sdd-init テスト [${plugin_name}] ==="

    # 前提条件チェック: session-start.sh が実行されたか確認
    echo "--- session-start 実行確認 ---"
    local session_start_ok=true

    if [ ! -f "$test_dir/.sdd-config.json" ]; then
        echo "ERROR: .sdd-config.json が存在しません（session-start.sh が実行されていない可能性）"
        session_start_ok=false
    fi

    if [ ! -d "$test_dir/.sdd" ]; then
        echo "ERROR: .sdd ディレクトリが存在しません（session-start.sh が実行されていない可能性）"
        session_start_ok=false
    fi

    if [ ! -f "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" ]; then
        echo "ERROR: AI-SDD-PRINCIPLES.md が存在しません（session-start.sh が実行されていない可能性）"
        session_start_ok=false
    fi

    if [ "$session_start_ok" = true ]; then
        echo "OK: session-start.sh の実行を確認（.sdd-config.json, .sdd/, AI-SDD-PRINCIPLES.md が存在）"
    else
        echo "WARNING: session-start.sh が正しく実行されていない可能性があります"
        echo "  -> Phase 2 (run) を先に実行してください"
    fi

    # session-start 実行確認結果をログに保存
    echo "session_start_executed: $session_start_ok" > "$log_dir/session-start-check.log"
    echo "checked_files:" >> "$log_dir/session-start-check.log"
    echo "  .sdd-config.json: $([ -f "$test_dir/.sdd-config.json" ] && echo 'exists' || echo 'missing')" >> "$log_dir/session-start-check.log"
    echo "  .sdd/: $([ -d "$test_dir/.sdd" ] && echo 'exists' || echo 'missing')" >> "$log_dir/session-start-check.log"
    echo "  .sdd/AI-SDD-PRINCIPLES.md: $([ -f "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" ] && echo 'exists' || echo 'missing')" >> "$log_dir/session-start-check.log"
    echo "session-start-check.log 保存完了"

    echo "--- /sdd-init 実行 ---"
    cd "$test_dir"
    claude --plugin-dir "$plugin_dir" --print -p "/sdd-init" > "$log_dir/sdd-init.log" 2>&1 || true

    echo "ログ保存: $log_dir/sdd-init.log"

    # /sdd-init 後のディレクトリ構造を記録
    cd "$test_dir"
    if [ -d ".sdd" ]; then
        find .sdd -type f | sort > "$log_dir/sdd-structure.log" 2>&1 || true
        echo "sdd-structure.log 保存完了"
    fi

    # CLAUDE.md の AI-SDD セクション確認
    if [ -f "CLAUDE.md" ]; then
        cp "CLAUDE.md" "$log_dir/CLAUDE.md.after-init"
        echo "CLAUDE.md 保存完了"
    fi

    echo ""
}

# --- Phase 3b: 生成系スキルテスト ---
run_gen_skills_test() {
    local plugin_dir="$1"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"
    local test_dir="${TEST_BASE}/${plugin_name}"
    local log_dir="${TEST_BASE}/logs/${plugin_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 3b: 生成系スキルテスト [${plugin_name}] ==="

    # /constitution init テスト
    echo "--- /constitution init テスト ---"
    cd "$test_dir"
    claude --plugin-dir "$plugin_dir" --print -p "/constitution init" > "$log_dir/constitution-init.log" 2>&1 || true
    echo "ログ保存: $log_dir/constitution-init.log"

    # CONSTITUTION.md を保存
    if [ -f "$test_dir/.sdd/CONSTITUTION.md" ]; then
        cp "$test_dir/.sdd/CONSTITUTION.md" "$log_dir/CONSTITUTION.md"
        echo "CONSTITUTION.md 保存完了"
    fi

    # /generate-prd テスト（ダミー要件）
    echo "--- /generate-prd テスト ---"
    cd "$test_dir"
    claude --plugin-dir "$plugin_dir" --print -p "/generate-prd --ci A sample task management feature. Users can create, edit, and delete tasks." > "$log_dir/generate-prd.log" 2>&1 || true
    echo "ログ保存: $log_dir/generate-prd.log"

    # 生成された PRD ファイルを保存
    if [ -d "$test_dir/.sdd/requirement" ]; then
        for f in "$test_dir/.sdd/requirement"/*.md; do
            if [ -f "$f" ]; then
                local basename_f
                basename_f="$(basename "$f")"
                cp "$f" "$log_dir/prd-${basename_f}"
                echo "PRD 保存完了: prd-${basename_f}"
            fi
        done
    fi

    # /generate-spec テスト（ダミー要件）
    echo "--- /generate-spec テスト ---"
    cd "$test_dir"
    claude --plugin-dir "$plugin_dir" --print -p "/generate-spec --ci User authentication feature. Supports login and logout with email and password." > "$log_dir/generate-spec.log" 2>&1 || true
    echo "ログ保存: $log_dir/generate-spec.log"

    # 生成された仕様書ファイルを保存
    if [ -d "$test_dir/.sdd/specification" ]; then
        for f in "$test_dir/.sdd/specification"/*.md; do
            if [ -f "$f" ]; then
                local basename_f
                basename_f="$(basename "$f")"
                cp "$f" "$log_dir/spec-${basename_f}"
                echo "Spec 保存完了: spec-${basename_f}"
            fi
        done
    fi

    # /sdd-init 後のディレクトリ構造を再記録（生成スキル実行後）
    cd "$test_dir"
    if [ -d ".sdd" ]; then
        find .sdd -type f | sort > "$log_dir/sdd-structure-after-gen.log" 2>&1 || true
        echo "sdd-structure-after-gen.log 保存完了"
    fi

    echo ""
}

# --- Phase 4: ログ収集 ---
collect_logs() {
    local plugin_dir="$1"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"
    local log_dir="${TEST_BASE}/logs/${plugin_name}"

    echo "=== Phase 4: ログ収集 [${plugin_name}] ==="

    if [ ! -d "$log_dir" ]; then
        echo "ログディレクトリが見つかりません: $log_dir"
        return 1
    fi

    echo "収集済みログファイル:"
    for f in "$log_dir"/*; do
        if [ -f "$f" ]; then
            local size
            size=$(wc -c < "$f" | tr -d ' ')
            echo "  - $(basename "$f") (${size} bytes)"
        fi
    done
    echo ""
}

# --- Summary 生成 ---
generate_summary() {
    local summary_file="${TEST_BASE}/TEST_SUMMARY.md"

    cat > "$summary_file" << 'SUMMARY_EOF'
# Plugin Integration Test Summary

> 自動生成テンプレート - テスト結果を記入してください

## テスト実行情報

| 項目 | 値 |
|------|-----|
| 実行日時 | TIMESTAMP_PLACEHOLDER |
| テストベース | /tmp/ai-sdd-plugin-test |

## テスト結果

### sdd-workflow (期待言語: en)

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| session-start.sh 実行 | - | |
| .sdd-config.json 生成 | - | |
| SDD_LANG 言語設定 (config.json) | - | 期待値: en |
| .sdd ディレクトリ作成 | - | |
| AI-SDD-PRINCIPLES.md 配置 | - | |
| /sdd-init 実行 | - | |
| CLAUDE.md AI-SDD セクション | - | |
| CLAUDE.md 言語検証 | - | 英語テンプレートで生成されていること |
| /constitution init 実行 | - | |
| CONSTITUTION.md 言語検証 | - | 英語で生成されていること |
| /generate-prd 実行 | - | |
| PRD 言語検証 | - | 英語で生成されていること |
| /generate-spec 実行 | - | |
| 仕様書 言語検証 | - | 英語で生成されていること |

### sdd-workflow-ja (期待言語: ja)

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| session-start.sh 実行 | - | |
| .sdd-config.json 生成 | - | |
| SDD_LANG 言語設定 (config.json) | - | 期待値: ja |
| .sdd ディレクトリ作成 | - | |
| AI-SDD-PRINCIPLES.md 配置 | - | |
| /sdd-init 実行 | - | |
| CLAUDE.md AI-SDD セクション | - | |
| CLAUDE.md 言語検証 | - | 日本語テンプレートで生成されていること |
| /constitution init 実行 | - | |
| CONSTITUTION.md 言語検証 | - | 日本語で生成されていること |
| /generate-prd 実行 | - | |
| PRD 言語検証 | - | 日本語で生成されていること |
| /generate-spec 実行 | - | |
| 仕様書 言語検証 | - | 日本語で生成されていること |

## ログファイル

SUMMARY_EOF

    # ログファイル一覧を追加
    for plugin_dir in "$PLUGINS_DIR"/*/; do
        local plugin_name
        plugin_name="$(basename "$plugin_dir")"
        local log_dir="${TEST_BASE}/logs/${plugin_name}"

        echo "### ${plugin_name}" >> "$summary_file"
        echo "" >> "$summary_file"

        if [ -d "$log_dir" ]; then
            for f in "$log_dir"/*; do
                if [ -f "$f" ]; then
                    echo "- \`logs/${plugin_name}/$(basename "$f")\`" >> "$summary_file"
                fi
            done
        else
            echo "- ログなし" >> "$summary_file"
        fi
        echo "" >> "$summary_file"
    done

    # タイムスタンプを置換
    sed -i '' "s/TIMESTAMP_PLACEHOLDER/${TIMESTAMP}/" "$summary_file" 2>/dev/null || \
    sed -i "s/TIMESTAMP_PLACEHOLDER/${TIMESTAMP}/" "$summary_file" 2>/dev/null || true

    echo "TEST_SUMMARY.md 生成: $summary_file"
}

# --- メイン ---
case "${1:-help}" in
    setup)
        setup
        ;;
    run)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 run <plugin_dir>"
            exit 1
        fi
        run_test "$2"
        ;;
    sdd-init)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 sdd-init <plugin_dir>"
            exit 1
        fi
        run_sdd_init_test "$2"
        ;;
    gen-skills)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 gen-skills <plugin_dir>"
            exit 1
        fi
        run_gen_skills_test "$2"
        ;;
    collect)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 collect <plugin_dir>"
            exit 1
        fi
        collect_logs "$2"
        ;;
    summary)
        generate_summary
        ;;
    help|*)
        echo "Usage: $0 {setup|run|sdd-init|gen-skills|collect|summary} [plugin_dir]"
        echo ""
        echo "Commands:"
        echo "  setup                  テスト環境を構築"
        echo "  run <plugin_dir>       session-start テスト実行"
        echo "  sdd-init <plugin_dir>  /sdd-init テスト実行"
        echo "  gen-skills <plugin_dir>  生成系スキルテスト実行"
        echo "  collect <plugin_dir>   ログ収集"
        echo "  summary                TEST_SUMMARY.md 生成"
        exit 1
        ;;
esac
