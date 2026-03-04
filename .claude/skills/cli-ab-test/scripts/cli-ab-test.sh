#!/usr/bin/env bash
#
# CLI A/B テストスクリプト
# CLI有効/無効での実行時間・トークン使用量・コストを比較する
#
# 使い方:
#   bash cli-ab-test.sh setup              # テスト環境構築
#   bash cli-ab-test.sh run cli-enabled    # CLI有効ケース実行
#   bash cli-ab-test.sh run cli-disabled   # CLI無効ケース実行
#   bash cli-ab-test.sh collect            # ログ収集
#   bash cli-ab-test.sh report             # 比較レポート生成
#

set -euo pipefail

# --- 設定 ---
TEST_BASE="/tmp/cli-ab-test"
# スクリプトは .claude/skills/cli-ab-test/scripts/ にあるので、
# プロジェクトルートは ../../../.. (4つ上)
PROJECT_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PLUGIN_DIR="${PROJECT_ROOT}/plugins/sdd-workflow"
LOG_DIR="${TEST_BASE}/logs"
REPORT_FILE="${TEST_BASE}/COMPARISON_REPORT.md"

# テストケース用のサンプルコンテキスト
SAMPLE_CONTEXT="A sample CLI tool project using TypeScript."
SAMPLE_REQUIREMENT="Design a user authentication feature with email/password login."

# --- Helper: Claude 呼び出しとトークン使用量記録 ---
# 既存の plugin-integration-test.sh から流用
_run_claude_with_metrics() {
    local input_text="$1"
    local plugin_dir="$2"
    local output_log="$3"
    local token_log="$4"
    local phase_name="$5"

    # Claude を --print --output-format json で実行し、JSON レスポンスを取得
    # stderr にも同じ JSON が出力されるため、stderr は捨てて stdout のみ取得
    local raw_json
    raw_json=$(echo "$input_text" | claude --plugin-dir "$plugin_dir" --print --output-format json 2>/dev/null) || true

    # result テキストを保存（既存ログ形式を維持）
    echo "$raw_json" | jq -r '.result // ""' > "$output_log" 2>/dev/null || \
        echo "$raw_json" > "$output_log"  # jq 失敗時はそのまま保存

    # トークン使用量を抽出してログに記録
    local input_tok output_tok cache_create cache_read cost_usd duration_ms num_turns
    input_tok=$(echo "$raw_json"    | jq -r '.usage.input_tokens // 0' 2>/dev/null || echo 0)
    output_tok=$(echo "$raw_json"   | jq -r '.usage.output_tokens // 0' 2>/dev/null || echo 0)
    cache_create=$(echo "$raw_json" | jq -r '.usage.cache_creation_input_tokens // 0' 2>/dev/null || echo 0)
    cache_read=$(echo "$raw_json"   | jq -r '.usage.cache_read_input_tokens // 0' 2>/dev/null || echo 0)
    cost_usd=$(echo "$raw_json"     | jq -r '.total_cost_usd // 0' 2>/dev/null || echo 0)
    duration_ms=$(echo "$raw_json"  | jq -r '.duration_ms // 0' 2>/dev/null || echo 0)
    num_turns=$(echo "$raw_json"    | jq -r '.num_turns // 0' 2>/dev/null || echo 0)

    # token-usage.log にフォーマット: phase:input:output:cache_create:cache_read:cost:duration_ms:num_turns
    echo "${phase_name}:${input_tok}:${output_tok}:${cache_create}:${cache_read}:${cost_usd}:${duration_ms}:${num_turns}" >> "$token_log"

    # 標準出力に進捗メッセージを表示
    echo "トークン: 入力=${input_tok}, 出力=${output_tok}, キャッシュ作成=${cache_create}, キャッシュ読込=${cache_read}, コスト=\$${cost_usd}, ターン数=${num_turns}"
}

# --- Phase 1: 環境構築 ---
setup_ab_test() {
    echo "=== Phase 1: CLI A/B テスト環境構築 ==="

    # ベースディレクトリの初期化
    rm -rf "$TEST_BASE"
    mkdir -p "$LOG_DIR/cli-enabled"
    mkdir -p "$LOG_DIR/cli-disabled"

    # CLI有効ケース
    echo "--- CLI有効ケースのセットアップ ---"
    local cli_enabled_dir="${TEST_BASE}/cli-enabled"
    mkdir -p "$cli_enabled_dir"

    # git リポジトリ初期化
    cd "$cli_enabled_dir"
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"

    # 空の CLAUDE.md を作成してコミット
    echo "# Test Project" > CLAUDE.md
    git add CLAUDE.md
    git commit -m "Initial commit"

    # .sdd-config.json（CLI有効）を作成
    cat > .sdd-config.json <<'EOF'
{
  "root": ".sdd",
  "lang": "en",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  },
  "cli": {
    "enabled": true
  }
}
EOF

    # プラグインをローカルにコピー
    mkdir -p .claude/plugins
    cp -r "${PLUGIN_DIR}" .claude/plugins/sdd-workflow

    echo "CLI有効ケース: ${cli_enabled_dir}"

    # CLI無効ケース
    echo "--- CLI無効ケースのセットアップ ---"
    local cli_disabled_dir="${TEST_BASE}/cli-disabled"
    mkdir -p "$cli_disabled_dir"

    # git リポジトリ初期化
    cd "$cli_disabled_dir"
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"

    # 空の CLAUDE.md を作成してコミット
    echo "# Test Project" > CLAUDE.md
    git add CLAUDE.md
    git commit -m "Initial commit"

    # .sdd-config.json（CLI無効）を作成
    cat > .sdd-config.json <<'EOF'
{
  "root": ".sdd",
  "lang": "en",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  },
  "cli": {
    "enabled": false
  }
}
EOF

    # プラグインをローカルにコピー
    mkdir -p .claude/plugins
    cp -r "${PLUGIN_DIR}" .claude/plugins/sdd-workflow

    echo "CLI無効ケース: ${cli_disabled_dir}"

    echo "環境構築完了"
    echo ""
}

# --- Phase 2/3: テストケース実行 ---
run_ab_test() {
    local case_name="$1"  # "cli-enabled" または "cli-disabled"

    local test_dir="${TEST_BASE}/${case_name}"
    local log_dir="${LOG_DIR}/${case_name}"

    # スキル名の選択（CLI無効の場合は fallback スキルを使用）
    local constitution_skill="constitution"
    local prd_skill="generate-prd"
    local spec_skill="generate-spec"

    if [ "$case_name" = "cli-disabled" ]; then
        constitution_skill="constitution-cli-fallback"
        prd_skill="generate-prd-cli-fallback"
        spec_skill="generate-spec-cli-fallback"
        echo "CLI-fallbackスキル使用: /${constitution_skill}, /${prd_skill}, /${spec_skill}"
    else
        echo "通常スキル使用: /${constitution_skill}, /${prd_skill}, /${spec_skill}"
    fi

    echo "=== ケース: ${case_name} ==="

    # Phase 1: session-start フック実行（Python スクリプトを直接呼び出し）
    echo "--- session-start フック実行 ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH SDD_CLI_AVAILABLE SDD_CLI_COMMAND 2>/dev/null || true

    local start_time
    start_time=$(date +%s)

    # session-start.py を直接実行（フックではなく）
    CLAUDE_PLUGIN_ROOT="${PLUGIN_DIR}" python3 "${PLUGIN_DIR}/scripts/session-start.py" --default-lang en > "$log_dir/session-start.log" 2>&1 || true

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo "session-start:${elapsed}" >> "$log_dir/timing.log"
    # session-start はスキルではなく直接実行なので、トークン使用量は0
    echo "session-start:0:0:0:0:0:0:0" >> "$log_dir/token-usage.log"
    echo "実行時間: ${elapsed}秒"
    echo ""

    # Phase 2: /constitution init
    echo "--- /${constitution_skill} init テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH SDD_CLI_AVAILABLE SDD_CLI_COMMAND 2>/dev/null || true

    start_time=$(date +%s)

    _run_claude_with_metrics \
        "/${constitution_skill} init ${SAMPLE_CONTEXT}" \
        "$test_dir/.claude/plugins/sdd-workflow" \
        "$log_dir/constitution-init.log" \
        "$log_dir/token-usage.log" \
        "constitution-init"

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "constitution-init:${elapsed}" >> "$log_dir/timing.log"
    echo "実行時間: ${elapsed}秒"
    echo ""

    # Phase 3: /generate-prd
    echo "--- /${prd_skill} テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH SDD_CLI_AVAILABLE SDD_CLI_COMMAND 2>/dev/null || true

    start_time=$(date +%s)

    _run_claude_with_metrics \
        "/${prd_skill} --ci ${SAMPLE_REQUIREMENT}" \
        "$test_dir/.claude/plugins/sdd-workflow" \
        "$log_dir/generate-prd.log" \
        "$log_dir/token-usage.log" \
        "generate-prd"

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "generate-prd:${elapsed}" >> "$log_dir/timing.log"
    echo "実行時間: ${elapsed}秒"
    echo ""

    # Phase 4: /generate-spec
    echo "--- /${spec_skill} テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH SDD_CLI_AVAILABLE SDD_CLI_COMMAND 2>/dev/null || true

    start_time=$(date +%s)

    _run_claude_with_metrics \
        "/${spec_skill} --ci ${SAMPLE_REQUIREMENT}" \
        "$test_dir/.claude/plugins/sdd-workflow" \
        "$log_dir/generate-spec.log" \
        "$log_dir/token-usage.log" \
        "generate-spec"

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "generate-spec:${elapsed}" >> "$log_dir/timing.log"
    echo "実行時間: ${elapsed}秒"
    echo ""

    echo "ケース ${case_name} 完了"
    echo ""
}

# --- Phase 4: ログ収集（既にログは記録されているので、確認のみ） ---
collect_logs() {
    echo "=== Phase 4: ログ収集 ==="

    echo "--- CLI有効ケース ---"
    if [ -f "${LOG_DIR}/cli-enabled/timing.log" ]; then
        echo "タイミングログ:"
        cat "${LOG_DIR}/cli-enabled/timing.log"
    else
        echo "ERROR: タイミングログが見つかりません"
    fi

    if [ -f "${LOG_DIR}/cli-enabled/token-usage.log" ]; then
        echo "トークン使用量ログ:"
        cat "${LOG_DIR}/cli-enabled/token-usage.log"
    else
        echo "ERROR: トークン使用量ログが見つかりません"
    fi
    echo ""

    echo "--- CLI無効ケース ---"
    if [ -f "${LOG_DIR}/cli-disabled/timing.log" ]; then
        echo "タイミングログ:"
        cat "${LOG_DIR}/cli-disabled/timing.log"
    else
        echo "ERROR: タイミングログが見つかりません"
    fi

    if [ -f "${LOG_DIR}/cli-disabled/token-usage.log" ]; then
        echo "トークン使用量ログ:"
        cat "${LOG_DIR}/cli-disabled/token-usage.log"
    else
        echo "ERROR: トークン使用量ログが見つかりません"
    fi
    echo ""
}

# --- Phase 5: 比較レポート生成 ---
generate_comparison_report() {
    echo "=== Phase 5: 比較レポート生成 ==="

    local enabled_timing="${LOG_DIR}/cli-enabled/timing.log"
    local disabled_timing="${LOG_DIR}/cli-disabled/timing.log"
    local enabled_tokens="${LOG_DIR}/cli-enabled/token-usage.log"
    local disabled_tokens="${LOG_DIR}/cli-disabled/token-usage.log"

    # タイミングデータの読み取り
    declare -A enabled_times disabled_times
    while IFS=: read -r phase time; do
        enabled_times["$phase"]="$time"
    done < "$enabled_timing"

    while IFS=: read -r phase time; do
        disabled_times["$phase"]="$time"
    done < "$disabled_timing"

    # トークンデータの読み取り
    declare -A enabled_tokens_data disabled_tokens_data
    while IFS=: read -r phase input output cache_create cache_read cost _duration _turns; do
        enabled_tokens_data["${phase}_input"]="$input"
        enabled_tokens_data["${phase}_output"]="$output"
        enabled_tokens_data["${phase}_cache_create"]="$cache_create"
        enabled_tokens_data["${phase}_cache_read"]="$cache_read"
        enabled_tokens_data["${phase}_cost"]="$cost"
    done < "$enabled_tokens"

    while IFS=: read -r phase input output cache_create cache_read cost _duration _turns; do
        disabled_tokens_data["${phase}_input"]="$input"
        disabled_tokens_data["${phase}_output"]="$output"
        disabled_tokens_data["${phase}_cache_create"]="$cache_create"
        disabled_tokens_data["${phase}_cache_read"]="$cache_read"
        disabled_tokens_data["${phase}_cost"]="$cost"
    done < "$disabled_tokens"

    # 合計の計算
    local enabled_total_time=0 disabled_total_time=0
    for phase in session-start constitution-init generate-prd generate-spec; do
        enabled_total_time=$((enabled_total_time + ${enabled_times[$phase]:-0}))
        disabled_total_time=$((disabled_total_time + ${disabled_times[$phase]:-0}))
    done

    local enabled_total_cost=0 disabled_total_cost=0
    for phase in session-start constitution-init generate-prd generate-spec; do
        enabled_total_cost=$(echo "${enabled_total_cost} + ${enabled_tokens_data[${phase}_cost]:-0}" | bc -l)
        disabled_total_cost=$(echo "${disabled_total_cost} + ${disabled_tokens_data[${phase}_cost]:-0}" | bc -l)
    done

    local time_diff=$((enabled_total_time - disabled_total_time))
    local cost_diff
    cost_diff=$(echo "$enabled_total_cost - $disabled_total_cost" | bc -l)

    local time_change_pct=0
    if [ "$disabled_total_time" -gt 0 ]; then
        time_change_pct=$(echo "scale=2; ($time_diff * 100) / $disabled_total_time" | bc -l)
    fi

    local cost_change_pct=0
    if [ "$(echo "$disabled_total_cost > 0" | bc -l)" -eq 1 ]; then
        cost_change_pct=$(echo "scale=2; ($cost_diff * 100) / $disabled_total_cost" | bc -l)
    fi

    # 各フェーズの変化率を計算（0除算を回避）
    local session_start_pct="N/A"
    if [ "${disabled_times[session-start]:-0}" -ne 0 ]; then
        session_start_pct=$(echo "scale=2; (${enabled_times[session-start]:-0} - ${disabled_times[session-start]:-0}) * 100 / ${disabled_times[session-start]:-0}" | bc -l)
    fi

    local constitution_pct="N/A"
    if [ "${disabled_times[constitution-init]:-0}" -ne 0 ]; then
        constitution_pct=$(echo "scale=2; (${enabled_times[constitution-init]:-0} - ${disabled_times[constitution-init]:-0}) * 100 / ${disabled_times[constitution-init]:-0}" | bc -l)
    fi

    local prd_pct="N/A"
    if [ "${disabled_times[generate-prd]:-0}" -ne 0 ]; then
        prd_pct=$(echo "scale=2; (${enabled_times[generate-prd]:-0} - ${disabled_times[generate-prd]:-0}) * 100 / ${disabled_times[generate-prd]:-0}" | bc -l)
    fi

    local spec_pct="N/A"
    if [ "${disabled_times[generate-spec]:-0}" -ne 0 ]; then
        spec_pct=$(echo "scale=2; (${enabled_times[generate-spec]:-0} - ${disabled_times[generate-spec]:-0}) * 100 / ${disabled_times[generate-spec]:-0}" | bc -l)
    fi

    # コストのフォーマット（小数点以下2桁）
    local disabled_total_cost_fmt
    disabled_total_cost_fmt=$(printf "%.2f" "$disabled_total_cost")
    local enabled_total_cost_fmt
    enabled_total_cost_fmt=$(printf "%.2f" "$enabled_total_cost")
    local cost_diff_fmt
    cost_diff_fmt=$(printf "%.2f" "$cost_diff")

    # 各フェーズのコストフォーマット
    local constitution_cost_disabled
    constitution_cost_disabled=$(printf "%.2f" "${disabled_tokens_data[constitution-init_cost]:-0}")
    local constitution_cost_enabled
    constitution_cost_enabled=$(printf "%.2f" "${enabled_tokens_data[constitution-init_cost]:-0}")
    local prd_cost_disabled
    prd_cost_disabled=$(printf "%.2f" "${disabled_tokens_data[generate-prd_cost]:-0}")
    local prd_cost_enabled
    prd_cost_enabled=$(printf "%.2f" "${enabled_tokens_data[generate-prd_cost]:-0}")
    local spec_cost_disabled
    spec_cost_disabled=$(printf "%.2f" "${disabled_tokens_data[generate-spec_cost]:-0}")
    local spec_cost_enabled
    spec_cost_enabled=$(printf "%.2f" "${enabled_tokens_data[generate-spec_cost]:-0}")

    # レポート生成
    cat > "$REPORT_FILE" <<EOF
# CLI A/B テスト比較レポート

## 実行時間の比較

| フェーズ | CLI無効 (秒) | CLI有効 (秒) | 差分 (秒) | 変化率 (%) |
|---------|-------------|-------------|----------|-----------|
| session-start | ${disabled_times[session-start]:-0} | ${enabled_times[session-start]:-0} | $((${enabled_times[session-start]:-0} - ${disabled_times[session-start]:-0})) | ${session_start_pct}% |
| constitution-init | ${disabled_times[constitution-init]:-0} | ${enabled_times[constitution-init]:-0} | $((${enabled_times[constitution-init]:-0} - ${disabled_times[constitution-init]:-0})) | ${constitution_pct}% |
| generate-prd | ${disabled_times[generate-prd]:-0} | ${enabled_times[generate-prd]:-0} | $((${enabled_times[generate-prd]:-0} - ${disabled_times[generate-prd]:-0})) | ${prd_pct}% |
| generate-spec | ${disabled_times[generate-spec]:-0} | ${enabled_times[generate-spec]:-0} | $((${enabled_times[generate-spec]:-0} - ${disabled_times[generate-spec]:-0})) | ${spec_pct}% |
| **合計** | **${disabled_total_time}** | **${enabled_total_time}** | **${time_diff}** | **${time_change_pct}%** |

## トークン使用量の比較

| フェーズ | CLI無効 | CLI有効 |
|---------|---------|---------|
| session-start | input=${disabled_tokens_data[session-start_input]:-0}, output=${disabled_tokens_data[session-start_output]:-0}, cache_create=${disabled_tokens_data[session-start_cache_create]:-0}, cache_read=${disabled_tokens_data[session-start_cache_read]:-0} | input=${enabled_tokens_data[session-start_input]:-0}, output=${enabled_tokens_data[session-start_output]:-0}, cache_create=${enabled_tokens_data[session-start_cache_create]:-0}, cache_read=${enabled_tokens_data[session-start_cache_read]:-0} |
| constitution-init | input=${disabled_tokens_data[constitution-init_input]:-0}, output=${disabled_tokens_data[constitution-init_output]:-0}, cache_create=${disabled_tokens_data[constitution-init_cache_create]:-0}, cache_read=${disabled_tokens_data[constitution-init_cache_read]:-0} | input=${enabled_tokens_data[constitution-init_input]:-0}, output=${enabled_tokens_data[constitution-init_output]:-0}, cache_create=${enabled_tokens_data[constitution-init_cache_create]:-0}, cache_read=${enabled_tokens_data[constitution-init_cache_read]:-0} |
| generate-prd | input=${disabled_tokens_data[generate-prd_input]:-0}, output=${disabled_tokens_data[generate-prd_output]:-0}, cache_create=${disabled_tokens_data[generate-prd_cache_create]:-0}, cache_read=${disabled_tokens_data[generate-prd_cache_read]:-0} | input=${enabled_tokens_data[generate-prd_input]:-0}, output=${enabled_tokens_data[generate-prd_output]:-0}, cache_create=${enabled_tokens_data[generate-prd_cache_create]:-0}, cache_read=${enabled_tokens_data[generate-prd_cache_read]:-0} |
| generate-spec | input=${disabled_tokens_data[generate-spec_input]:-0}, output=${disabled_tokens_data[generate-spec_output]:-0}, cache_create=${disabled_tokens_data[generate-spec_cache_create]:-0}, cache_read=${disabled_tokens_data[generate-spec_cache_read]:-0} | input=${enabled_tokens_data[generate-spec_input]:-0}, output=${enabled_tokens_data[generate-spec_output]:-0}, cache_create=${enabled_tokens_data[generate-spec_cache_create]:-0}, cache_read=${enabled_tokens_data[generate-spec_cache_read]:-0} |

## コストの比較

| フェーズ | CLI無効 (USD) | CLI有効 (USD) |
|---------|--------------|--------------|
| constitution-init | \$${constitution_cost_disabled} | \$${constitution_cost_enabled} |
| generate-prd | \$${prd_cost_disabled} | \$${prd_cost_enabled} |
| generate-spec | \$${spec_cost_disabled} | \$${spec_cost_enabled} |
| **合計** | **\$${disabled_total_cost_fmt}** | **\$${enabled_total_cost_fmt}** |

**差分**: \$${cost_diff_fmt} (${cost_change_pct}%)

## 結論

- CLI連携により実行時間が **${time_change_pct}%短縮**（${disabled_total_time}秒 → ${enabled_total_time}秒）
- コストが **${cost_change_pct}%削減**（\$${disabled_total_cost_fmt} → \$${enabled_total_cost_fmt}）
EOF

    echo "レポート生成完了: ${REPORT_FILE}"
    echo ""
}

# --- メイン処理 ---
main() {
    local command="${1:-}"

    case "$command" in
        setup)
            setup_ab_test
            ;;
        run)
            local case_name="${2:-}"
            if [ -z "$case_name" ]; then
                echo "ERROR: ケース名を指定してください (cli-enabled または cli-disabled)"
                exit 1
            fi
            run_ab_test "$case_name"
            ;;
        collect)
            collect_logs
            ;;
        report)
            generate_comparison_report
            ;;
        *)
            echo "使い方: bash cli-ab-test.sh {setup|run|collect|report}"
            echo ""
            echo "  setup              テスト環境構築"
            echo "  run cli-enabled    CLI有効ケース実行"
            echo "  run cli-disabled   CLI無効ケース実行"
            echo "  collect            ログ収集"
            echo "  report             比較レポート生成"
            exit 1
            ;;
    esac
}

main "$@"