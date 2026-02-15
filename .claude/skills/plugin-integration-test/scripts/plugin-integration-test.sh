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

    # 追加テストケース: sdd-workflow + 既存 .sdd-config.json (lang: ja)
    # このテストは、既存の設定ファイルの言語設定がスキルに正しく引き継がれるかを検証する
    local ja_config_test_dir="${TEST_BASE}/sdd-workflow-with-ja-config"
    mkdir -p "$ja_config_test_dir"
    cd "$ja_config_test_dir"

    # git init + 空 CLAUDE.md をコミット
    git init -q
    echo "" > CLAUDE.md
    git add CLAUDE.md
    git commit -q -m "initial commit"

    # 事前に lang: "ja" の .sdd-config.json を配置
    cat > ".sdd-config.json" << 'EOF'
{
  "root": ".sdd",
  "lang": "ja",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
EOF
    git add .sdd-config.json
    git commit -q -m "add .sdd-config.json with lang: ja"

    echo "テストディレクトリ作成: ${ja_config_test_dir} (git initialized, .sdd-config.json with lang: ja)"

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
    echo "追加テストケース:"
    echo "  - sdd-workflow-with-ja-config (sdd-workflow + 既存 lang: ja 設定)"
}

# --- Phase 2: サブセッション実行 (session-start + 基本検証) ---
run_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"  # オプショナル: テストケース名（省略時はプラグイン名を使用）
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    # テストケース名が指定されていればそれを使用、なければプラグイン名を使用
    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 2: session-start テスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local start_time
    start_time=$(date +%s)

    # claude サブセッションを起動して session-start フックを実行させる
    # session-start.sh は CLAUDE_ENV_FILE 経由で環境変数を設定するため、
    # echo による環境変数確認はサンドボックス制限で動作しない。
    # 代わりに、フックが生成するファイル（.sdd-config.json, .sdd/ ディレクトリ）を直接検証する。
    cd "$test_dir"
    echo "session-start フックが実行されました。このメッセージが表示されれば正常です。" | claude --plugin-dir "$plugin_dir" --print > "$log_dir/session-start.log" 2>&1 || true

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

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo "session-start:${elapsed}" >> "$log_dir/timing.log"
    echo "実行時間: ${elapsed}秒"

    echo ""
}

# --- Phase 3: /sdd-init テスト ---
run_sdd_init_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"  # オプショナル: テストケース名（省略時はプラグイン名を使用）
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    # テストケース名が指定されていればそれを使用、なければプラグイン名を使用
    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 3: /sdd-init テスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local start_time
    start_time=$(date +%s)

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

    echo "--- /sdd-init --ci 実行 ---"
    cd "$test_dir"
    echo "/sdd-init --ci" | claude --plugin-dir "$plugin_dir" --print > "$log_dir/sdd-init.log" 2>&1 || true

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

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo "sdd-init:${elapsed}" >> "$log_dir/timing.log"
    echo "実行時間: ${elapsed}秒"

    echo ""
}

# --- Phase 3b: 生成系スキルテスト ---
run_gen_skills_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"  # オプショナル: テストケース名（省略時はプラグイン名を使用）
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    # テストケース名が指定されていればそれを使用、なければプラグイン名を使用
    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 3b: 生成系スキルテスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local phase_start
    phase_start=$(date +%s)

    # /constitution init テスト
    echo "--- /constitution init テスト ---"
    cd "$test_dir"
    local start_time
    start_time=$(date +%s)
    echo '/constitution init A sample CLI tool project using TypeScript.' | claude --plugin-dir "$plugin_dir" --print > "$log_dir/constitution-init.log" 2>&1 || true
    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo "constitution-init:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/constitution-init.log (${elapsed}秒)"

    # CONSTITUTION.md を保存
    if [ -f "$test_dir/.sdd/CONSTITUTION.md" ]; then
        cp "$test_dir/.sdd/CONSTITUTION.md" "$log_dir/CONSTITUTION.md"
        echo "CONSTITUTION.md 保存完了"
    fi

    # /generate-prd テスト（ダミー要件）
    echo "--- /generate-prd テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    echo "/generate-prd --ci A sample task management feature. Users can create, edit, and delete tasks." | claude --plugin-dir "$plugin_dir" --print > "$log_dir/generate-prd.log" 2>&1 || true
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "generate-prd:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/generate-prd.log (${elapsed}秒)"

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
    start_time=$(date +%s)
    echo "/generate-spec --ci User authentication feature. Supports login and logout with email and password." | claude --plugin-dir "$plugin_dir" --print > "$log_dir/generate-spec.log" 2>&1 || true
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "generate-spec:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/generate-spec.log (${elapsed}秒)"

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

    local phase_end
    phase_end=$(date +%s)
    local phase_elapsed=$((phase_end - phase_start))
    echo "gen-skills-total:${phase_elapsed}" >> "$log_dir/timing.log"
    echo "Phase 3b 合計実行時間: ${phase_elapsed}秒"

    echo ""
}

# --- Phase 4: ログ収集 ---
collect_logs() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"  # オプショナル: テストケース名（省略時はプラグイン名を使用）
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    # テストケース名が指定されていればそれを使用、なければプラグイン名を使用
    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    echo "=== Phase 4: ログ収集 [${effective_name}] (plugin: ${plugin_name}) ==="

    if [ ! -d "$log_dir" ]; then
        echo "ログディレクトリが見つかりません: $log_dir"
        return 1
    fi

    # .sdd-config.json をログディレクトリにコピー（まだコピーされていない場合）
    if [ -f "$test_dir/.sdd-config.json" ] && [ ! -f "$log_dir/config.json" ]; then
        cp "$test_dir/.sdd-config.json" "$log_dir/config.json"
        echo "config.json を収集しました"
    fi

    # .sdd/ ディレクトリ構造を記録（session-start 後、まだ記録されていない場合）
    if [ -d "$test_dir/.sdd" ] && [ ! -f "$log_dir/sdd-structure-after-session.log" ]; then
        find "$test_dir/.sdd" -type f | sort > "$log_dir/sdd-structure-after-session.log" 2>&1 || true
        echo "sdd-structure-after-session.log を収集しました"
    fi

    # AI-SDD-PRINCIPLES.md をコピー（まだコピーされていない場合）
    if [ -f "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" ] && [ ! -f "$log_dir/AI-SDD-PRINCIPLES.md" ]; then
        cp "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" "$log_dir/AI-SDD-PRINCIPLES.md"
        echo "AI-SDD-PRINCIPLES.md を収集しました"
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

### sdd-workflow-with-ja-config (既存設定継承テスト: sdd-workflow + lang: ja)

> このテストは、既存の `.sdd-config.json` (lang: ja) がある状態で `sdd-workflow` プラグインを使用した場合に、設定が正しく継承されるかを検証します。

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| session-start.sh 実行 | - | 既存 .sdd-config.json を上書きしないこと |
| .sdd-config.json 保持 | - | lang: ja が維持されていること |
| SDD_LANG 言語設定 (config.json) | - | 期待値: ja（既存設定を継承） |
| .sdd ディレクトリ作成 | - | |
| AI-SDD-PRINCIPLES.md 配置 | - | |
| /sdd-init 実行 | - | |
| CLAUDE.md AI-SDD セクション | - | |
| CLAUDE.md 言語検証 | - | 日本語テンプレートで生成されていること |
| /constitution init 実行 | - | |
| CONSTITUTION.md 言語検証 | - | **日本語で生成されていること（重要）** |
| /generate-prd 実行 | - | |
| PRD 言語検証 | - | 日本語で生成されていること |
| /generate-spec 実行 | - | |
| 仕様書 言語検証 | - | 日本語で生成されていること |

## 実行時間

SUMMARY_EOF

    # テストケース一覧（プラグイン + 追加テストケース）
    local test_cases=()
    for plugin_dir in "$PLUGINS_DIR"/*/; do
        test_cases+=("$(basename "$plugin_dir")")
    done
    test_cases+=("sdd-workflow-with-ja-config")

    # 実行時間テーブルを追加
    for test_case in "${test_cases[@]}"; do
        local log_dir="${TEST_BASE}/logs/${test_case}"
        local timing_file="${log_dir}/timing.log"

        echo "### ${test_case}" >> "$summary_file"
        echo "" >> "$summary_file"

        if [ -f "$timing_file" ]; then
            echo "| フェーズ | 実行時間 |" >> "$summary_file"
            echo "|---------|----------|" >> "$summary_file"

            while IFS=: read -r phase seconds; do
                local minutes=$((seconds / 60))
                local remaining_seconds=$((seconds % 60))
                if [ "$minutes" -gt 0 ]; then
                    echo "| ${phase} | ${minutes}分${remaining_seconds}秒 (${seconds}秒) |" >> "$summary_file"
                else
                    echo "| ${phase} | ${seconds}秒 |" >> "$summary_file"
                fi
            done < "$timing_file"

            # 合計時間を計算
            local total_seconds=0
            while IFS=: read -r phase seconds; do
                if [ "$phase" != "gen-skills-total" ]; then
                    total_seconds=$((total_seconds + seconds))
                fi
            done < "$timing_file"

            local total_minutes=$((total_seconds / 60))
            local total_remaining=$((total_seconds % 60))
            echo "| **合計** | **${total_minutes}分${total_remaining}秒 (${total_seconds}秒)** |" >> "$summary_file"
        else
            echo "タイミング情報なし" >> "$summary_file"
        fi
        echo "" >> "$summary_file"
    done

    echo "## ログファイル" >> "$summary_file"
    echo "" >> "$summary_file"

    # ログファイル一覧を追加
    for test_case in "${test_cases[@]}"; do
        local log_dir="${TEST_BASE}/logs/${test_case}"

        echo "### ${test_case}" >> "$summary_file"
        echo "" >> "$summary_file"

        if [ -d "$log_dir" ]; then
            for f in "$log_dir"/*; do
                if [ -f "$f" ]; then
                    echo "- \`logs/${test_case}/$(basename "$f")\`" >> "$summary_file"
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
            echo "Usage: $0 run <plugin_dir> [test_case_name]"
            exit 1
        fi
        run_test "$2" "${3:-}"
        ;;
    sdd-init)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 sdd-init <plugin_dir> [test_case_name]"
            exit 1
        fi
        run_sdd_init_test "$2" "${3:-}"
        ;;
    gen-skills)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 gen-skills <plugin_dir> [test_case_name]"
            exit 1
        fi
        run_gen_skills_test "$2" "${3:-}"
        ;;
    collect)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 collect <plugin_dir> [test_case_name]"
            exit 1
        fi
        collect_logs "$2" "${3:-}"
        ;;
    summary)
        generate_summary
        ;;
    help|*)
        echo "Usage: $0 {setup|run|sdd-init|gen-skills|collect|summary} [plugin_dir] [test_case_name]"
        echo ""
        echo "Commands:"
        echo "  setup                              テスト環境を構築"
        echo "  run <plugin_dir> [test_case_name]  session-start テスト実行"
        echo "  sdd-init <plugin_dir> [test_case_name]  /sdd-init テスト実行"
        echo "  gen-skills <plugin_dir> [test_case_name]  生成系スキルテスト実行"
        echo "  collect <plugin_dir> [test_case_name]   ログ収集"
        echo "  summary                            TEST_SUMMARY.md 生成"
        echo ""
        echo "test_case_name: オプション。テストケース名（省略時はプラグイン名を使用）"
        echo "                例: sdd-workflow-with-ja-config"
        exit 1
        ;;
esac
