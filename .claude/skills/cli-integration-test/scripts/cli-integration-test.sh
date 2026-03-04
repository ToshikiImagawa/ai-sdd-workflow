#!/bin/bash
# shellcheck disable=SC2155
# cli-integration-test.sh
# sdd-cli と sdd-workflow プラグインの統合テスト
#
# Usage:
#   cli-integration-test.sh setup              - テスト環境を構築
#   cli-integration-test.sh test <test_dir>    - CLIテストを実行
#   cli-integration-test.sh summary            - サマリーレポート生成

set -euo pipefail

TEST_BASE="/tmp/ai-sdd-cli-integration-test"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# --- Setup: テスト環境構築 ---
setup() {
    echo "=== CLI Integration Test: 環境構築 ==="

    # クリーンアップ
    if [ -d "$TEST_BASE" ]; then
        rm -rf "$TEST_BASE"
        echo "既存のテストディレクトリを削除しました"
    fi

    mkdir -p "$TEST_BASE"
    mkdir -p "$TEST_BASE/logs"

    echo "テストベースディレクトリ作成: $TEST_BASE"
    echo ""
    echo "次のステップ:"
    echo "1. plugin-integration-test を実行してドキュメントを生成"
    echo "2. 生成されたテストディレクトリのパスを指定して 'test' コマンドを実行"
}

# --- Test: CLIテスト実行 ---
run_test() {
    local test_dir="$1"
    local test_name="$(basename "$test_dir")"
    local log_dir="${TEST_BASE}/logs/${test_name}"

    mkdir -p "$log_dir"

    echo "=== CLI Integration Test: ${test_name} ==="

    if [ ! -d "$test_dir" ]; then
        echo "ERROR: テストディレクトリが存在しません: $test_dir"
        exit 1
    fi

    if [ ! -f "$test_dir/.sdd-config.json" ]; then
        echo "ERROR: .sdd-config.json が存在しません"
        exit 1
    fi

    local phase_start
    phase_start=$(date +%s)

    # CLI コマンドのベース
    local cli_cmd="uvx --from git+https://github.com/ToshikiImagawa/ai-sdd-workflow-cli.git sdd-cli"

    # 1. CLI 検出確認
    echo "--- CLI 検出確認 ---"
    local cli_detection_result="UNKNOWN"

    if grep -q '"cli"' "$test_dir/.sdd-config.json"; then
        local cli_enabled=$(jq -r '.cli.enabled // "null"' "$test_dir/.sdd-config.json")
        if [ "$cli_enabled" = "true" ]; then
            if command -v uvx >/dev/null 2>&1; then
                echo "✓ cli.enabled=true かつ uvx が利用可能"
                cli_detection_result="PASS"
            else
                echo "✗ cli.enabled=true だが uvx が見つからない"
                cli_detection_result="FAIL"
            fi
        elif [ "$cli_enabled" = "false" ]; then
            echo "○ cli.enabled=false → CLI テストをスキップ"
            cli_detection_result="SKIPPED"
            echo "cli-detection:${cli_detection_result}" >> "$log_dir/cli-test.log"
            echo "CLIが無効のため、テストをスキップしました"
            return 0
        fi
    else
        echo "INFO: cli 設定なし → 自動検出モード"
        if command -v sdd-cli >/dev/null 2>&1; then
            echo "✓ sdd-cli が PATH にある"
            cli_detection_result="PASS"
        else
            echo "○ sdd-cli が PATH にない → CLI テストをスキップ"
            cli_detection_result="NOT_FOUND"
            echo "cli-detection:${cli_detection_result}" >> "$log_dir/cli-test.log"
            echo "CLIが見つからないため、テストをスキップしました"
            return 0
        fi
    fi

    echo "cli-detection:${cli_detection_result}" >> "$log_dir/cli-test.log"

    # 2. sdd-cli lint --json テスト
    echo ""
    echo "--- sdd-cli lint --json テスト ---"
    cd "$test_dir"
    local start_time
    start_time=$(date +%s)
    local lint_exit_code=0

    $cli_cmd lint --json > "$log_dir/cli-lint.log" 2>&1 || lint_exit_code=$?

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    echo "cli-lint:${elapsed}" >> "$log_dir/timing.log"
    echo "cli-lint-exit-code:${lint_exit_code}" >> "$log_dir/cli-test.log"

    if [ $lint_exit_code -eq 0 ]; then
        echo "✓ lint 正常終了 (${elapsed}秒)"
    else
        echo "✗ lint 異常終了 (exit=${lint_exit_code}, ${elapsed}秒)"
    fi

    # 3. sdd-cli index --quiet テスト
    echo ""
    echo "--- sdd-cli index --quiet テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    local index_exit_code=0

    $cli_cmd index --quiet > "$log_dir/cli-index.log" 2>&1 || index_exit_code=$?

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))

    echo "cli-index:${elapsed}" >> "$log_dir/timing.log"
    echo "cli-index-exit-code:${index_exit_code}" >> "$log_dir/cli-test.log"

    if [ $index_exit_code -eq 0 ]; then
        echo "✓ index 正常終了 (${elapsed}秒)"
    else
        echo "✗ index 異常終了 (exit=${index_exit_code}, ${elapsed}秒)"
    fi

    # 4. sdd-cli search --format json テスト
    echo ""
    echo "--- sdd-cli search --format json テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    local search_exit_code=0

    $cli_cmd search --format json "spec" > "$log_dir/cli-search.log" 2>&1 || search_exit_code=$?

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))

    echo "cli-search:${elapsed}" >> "$log_dir/timing.log"
    echo "cli-search-exit-code:${search_exit_code}" >> "$log_dir/cli-test.log"

    if [ $search_exit_code -eq 0 ]; then
        echo "✓ search 正常終了 (${elapsed}秒)"
    else
        echo "✗ search 異常終了 (exit=${search_exit_code}, ${elapsed}秒)"
    fi

    local phase_end
    phase_end=$(date +%s)
    local phase_elapsed=$((phase_end - phase_start))
    echo "total:${phase_elapsed}" >> "$log_dir/timing.log"

    echo ""
    echo "=== テスト完了 ==="
    echo "合計実行時間: ${phase_elapsed}秒"
    echo "ログディレクトリ: $log_dir"
    echo ""
}

# --- Summary: サマリーレポート生成 ---
generate_summary() {
    local summary_file="${TEST_BASE}/CLI_TEST_SUMMARY.md"

    cat > "$summary_file" << 'SUMMARY_EOF'
# CLI Integration Test Summary

> sdd-cli と sdd-workflow プラグインの統合テスト結果

## テスト実行情報

| 項目 | 値 |
|------|-----|
| 実行日時 | TIMESTAMP_PLACEHOLDER |
| テストベース | /tmp/ai-sdd-cli-integration-test |

## テスト結果

SUMMARY_EOF

    # 各テストケースの結果を追加
    for log_dir in "$TEST_BASE"/logs/*/; do
        if [ ! -d "$log_dir" ]; then
            continue
        fi

        local test_name="$(basename "$log_dir")"
        local test_log="${log_dir}/cli-test.log"
        local timing_log="${log_dir}/timing.log"

        echo "### ${test_name}" >> "$summary_file"
        echo "" >> "$summary_file"

        if [ ! -f "$test_log" ]; then
            echo "テスト未実行" >> "$summary_file"
            echo "" >> "$summary_file"
            continue
        fi

        # テスト結果テーブル
        echo "| テスト項目 | 結果 | 終了コード |" >> "$summary_file"
        echo "|-----------|------|-----------|" >> "$summary_file"

        local detection=$(grep "^cli-detection:" "$test_log" 2>/dev/null | cut -d: -f2 || echo "UNKNOWN")
        echo "| CLI 検出 | ${detection} | - |" >> "$summary_file"

        if [ "$detection" = "SKIPPED" ] || [ "$detection" = "NOT_FOUND" ]; then
            echo "" >> "$summary_file"
            continue
        fi

        local lint_code=$(grep "^cli-lint-exit-code:" "$test_log" 2>/dev/null | cut -d: -f2 || echo "?")
        local index_code=$(grep "^cli-index-exit-code:" "$test_log" 2>/dev/null | cut -d: -f2 || echo "?")
        local search_code=$(grep "^cli-search-exit-code:" "$test_log" 2>/dev/null | cut -d: -f2 || echo "?")

        local lint_result="FAIL"
        [ "$lint_code" = "0" ] && lint_result="PASS"

        local index_result="FAIL"
        [ "$index_code" = "0" ] && index_result="PASS"

        local search_result="FAIL"
        [ "$search_code" = "0" ] && search_result="PASS"

        echo "| lint --json | ${lint_result} | ${lint_code} |" >> "$summary_file"
        echo "| index --quiet | ${index_result} | ${index_code} |" >> "$summary_file"
        echo "| search --format json | ${search_result} | ${search_code} |" >> "$summary_file"
        echo "" >> "$summary_file"

        # 実行時間テーブル
        if [ -f "$timing_log" ]; then
            echo "#### 実行時間" >> "$summary_file"
            echo "" >> "$summary_file"
            echo "| コマンド | 実行時間 |" >> "$summary_file"
            echo "|---------|----------|" >> "$summary_file"

            while IFS=: read -r cmd seconds; do
                echo "| ${cmd} | ${seconds}秒 |" >> "$summary_file"
            done < "$timing_log"
            echo "" >> "$summary_file"
        fi
    done

    # ログファイル一覧
    echo "## ログファイル" >> "$summary_file"
    echo "" >> "$summary_file"

    for log_dir in "$TEST_BASE"/logs/*/; do
        if [ ! -d "$log_dir" ]; then
            continue
        fi

        local test_name="$(basename "$log_dir")"
        echo "### ${test_name}" >> "$summary_file"
        echo "" >> "$summary_file"

        for f in "$log_dir"/*; do
            if [ -f "$f" ]; then
                echo "- \`logs/${test_name}/$(basename "$f")\`" >> "$summary_file"
            fi
        done
        echo "" >> "$summary_file"
    done

    # タイムスタンプを置換
    sed -i '' "s/TIMESTAMP_PLACEHOLDER/${TIMESTAMP}/" "$summary_file" 2>/dev/null || \
    sed -i "s/TIMESTAMP_PLACEHOLDER/${TIMESTAMP}/" "$summary_file" 2>/dev/null || true

    echo "CLI_TEST_SUMMARY.md 生成: $summary_file"
    cat "$summary_file"
}

# --- メイン ---
case "${1:-help}" in
    setup)
        setup
        ;;
    test)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 test <test_dir>"
            echo ""
            echo "Example:"
            echo "  $0 test /tmp/ai-sdd-plugin-test/en-cli-enabled"
            exit 1
        fi
        run_test "$2"
        ;;
    summary)
        generate_summary
        ;;
    help|*)
        echo "Usage: $0 {setup|test|summary} [test_dir]"
        echo ""
        echo "Commands:"
        echo "  setup              テスト環境を構築"
        echo "  test <test_dir>    指定ディレクトリでCLIテストを実行"
        echo "  summary            CLI_TEST_SUMMARY.md 生成"
        echo ""
        echo "Example workflow:"
        echo "  1. bash $0 setup"
        echo "  2. Run plugin-integration-test to generate documents"
        echo "  3. bash $0 test /tmp/ai-sdd-plugin-test/en-cli-enabled"
        echo "  4. bash $0 summary"
        exit 1
        ;;
esac
