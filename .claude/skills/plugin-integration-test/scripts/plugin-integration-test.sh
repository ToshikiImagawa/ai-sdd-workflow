#!/bin/bash
# plugin-integration-test.sh
# sdd-workflow / sdd-workflow-ja プラグインの統合テスト実行スクリプト
#
# Usage:
#   plugin-integration-test.sh setup              - テスト環境を構築
#   plugin-integration-test.sh run <plugin_dir>   - サブセッションでテスト実行
#   plugin-integration-test.sh sdd-init <plugin_dir> - /sdd-init テスト実行
#   plugin-integration-test.sh gen-skills <plugin_dir> - 生成系スキルテスト実行
#   plugin-integration-test.sh cli-test <plugin_dir>  - CLI テスト実行
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

    # 追加テストケース: sdd-workflow + cli.enabled: true (CLI 連携テスト)
    # このテストは、CLI が uvx 経由で検出・利用されるかを検証する
    local cli_test_dir="${TEST_BASE}/sdd-workflow-with-cli"
    mkdir -p "$cli_test_dir"
    cd "$cli_test_dir"

    # git init + 空 CLAUDE.md をコミット
    git init -q
    echo "" > CLAUDE.md
    git add CLAUDE.md
    git commit -q -m "initial commit"

    # 事前に cli.enabled: true の .sdd-config.json を配置
    cat > ".sdd-config.json" << 'EOF'
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
    git add .sdd-config.json
    git commit -q -m "add .sdd-config.json with cli.enabled: true"

    echo "テストディレクトリ作成: ${cli_test_dir} (git initialized, .sdd-config.json with cli.enabled: true)"

    # 追加テストケース: sdd-workflow + cli.enabled: false (フォールバック専用)
    # このテストは、CLI を強制的に無効化し、フォールバックスキルの動作を検証する
    local cli_disabled_test_dir="${TEST_BASE}/sdd-workflow-cli-disabled"
    mkdir -p "$cli_disabled_test_dir"
    cd "$cli_disabled_test_dir"

    # git init + 空 CLAUDE.md をコミット
    git init -q
    echo "" > CLAUDE.md
    git add CLAUDE.md
    git commit -q -m "initial commit"

    # cli.enabled: false の .sdd-config.json を配置
    cat > ".sdd-config.json" << 'EOF'
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
    git add .sdd-config.json
    git commit -q -m "add .sdd-config.json with cli.enabled: false"

    echo "テストディレクトリ作成: ${cli_disabled_test_dir} (git initialized, cli.enabled: false)"

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
    echo "  - sdd-workflow-with-cli (sdd-workflow + cli.enabled: true)"
    echo "  - sdd-workflow-cli-disabled (sdd-workflow + cli.enabled: false, フォールバック専用)"
}

# --- Helper: Claude 呼び出しとトークン使用量記録 ---
_run_claude_with_metrics() {
    local input_text="$1"
    local plugin_dir="$2"
    local output_log="$3"
    local token_log="$4"
    local phase_name="$5"

    # Claude を --print --output-format json で実行し、JSON レスポンスを取得
    local raw_json
    raw_json=$(echo "$input_text" | claude --plugin-dir "$plugin_dir" --print --output-format json 2>&1) || true

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
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    _run_claude_with_metrics \
        "session-start フックが実行されました。このメッセージが表示されれば正常です。" \
        "$plugin_dir" \
        "$log_dir/session-start.log" \
        "$log_dir/token-usage.log" \
        "session-start"

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
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    _run_claude_with_metrics \
        "/sdd-init --ci" \
        "$plugin_dir" \
        "$log_dir/sdd-init.log" \
        "$log_dir/token-usage.log" \
        "sdd-init"

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

    # テストケース名に基づいてスキルを選択（CLI-fallbackスキルの使用）
    local constitution_skill="constitution"
    local prd_skill="generate-prd"
    local spec_skill="generate-spec"

    if [ "$effective_name" = "sdd-workflow-cli-disabled" ]; then
        constitution_skill="constitution-cli-fallback"
        prd_skill="generate-prd-cli-fallback"
        spec_skill="generate-spec-cli-fallback"
        echo "CLI-fallbackスキル使用: /${constitution_skill}, /${prd_skill}, /${spec_skill}"
    fi

    # /constitution init テスト
    echo "--- /${constitution_skill} init テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    local start_time
    start_time=$(date +%s)
    _run_claude_with_metrics \
        "/${constitution_skill} init A sample CLI tool project using TypeScript." \
        "$plugin_dir" \
        "$log_dir/constitution-init.log" \
        "$log_dir/token-usage.log" \
        "constitution-init"
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
    echo "--- /${prd_skill} テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    _run_claude_with_metrics \
        "/${prd_skill} --ci A sample task management feature. Users can create, edit, and delete tasks." \
        "$plugin_dir" \
        "$log_dir/generate-prd.log" \
        "$log_dir/token-usage.log" \
        "generate-prd"
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
    echo "--- /${spec_skill} テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    _run_claude_with_metrics \
        "/${spec_skill} --ci User authentication feature. Supports login and logout with email and password." \
        "$plugin_dir" \
        "$log_dir/generate-spec.log" \
        "$log_dir/token-usage.log" \
        "generate-spec"
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

# --- Phase 3c: CLI テスト ---
run_cli_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"  # オプショナル: テストケース名（省略時はプラグイン名を使用）
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    # テストケース名が指定されていればそれを使用、なければプラグイン名を使用
    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 3c: CLI テスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local phase_start
    phase_start=$(date +%s)

    # CLI コマンドのベース
    local cli_cmd="uvx --from git+https://github.com/ToshikiImagawa/ai-sdd-workflow-cli.git sdd-cli"

    # 1. CLI 検出確認: .sdd-config.json から cli.enabled 設定を確認し、
    #    session-start が正しく CLI を検出したかを間接的に検証
    echo "--- CLI 検出確認 ---"
    local cli_detection_result="UNKNOWN"

    if [ -f "$test_dir/.sdd-config.json" ]; then
        # .sdd-config.json に cli.enabled が含まれているか確認
        if grep -q '"cli"' "$test_dir/.sdd-config.json"; then
            local cli_enabled=$(jq -r '.cli.enabled // "null"' "$test_dir/.sdd-config.json")
            if [ "$cli_enabled" = "true" ]; then
                # cli.enabled: true の場合、uvx が利用可能であれば検出成功のはず
                if command -v uvx >/dev/null 2>&1; then
                    echo "OK: cli.enabled=true かつ uvx が利用可能 → CLI 検出成功と推定"
                    cli_detection_result="PASS"
                else
                    echo "WARNING: cli.enabled=true だが uvx が見つからない → CLI 検出失敗の可能性"
                    cli_detection_result="WARN"
                fi
            elif [ "$cli_enabled" = "false" ]; then
                echo "OK: cli.enabled=false → CLI 検出をスキップ（正常）"
                cli_detection_result="SKIPPED"
            else
                echo "INFO: cli 設定なし → 自動検出モード"
                if command -v sdd-cli >/dev/null 2>&1; then
                    echo "OK: sdd-cli が PATH にある → CLI 検出成功"
                    cli_detection_result="PASS"
                else
                    echo "INFO: sdd-cli が PATH にない → CLI 未検出（正常）"
                    cli_detection_result="NOT_FOUND"
                fi
            fi
        else
            echo "INFO: .sdd-config.json に cli 設定なし → 自動検出モード"
            if command -v sdd-cli >/dev/null 2>&1; then
                echo "OK: sdd-cli が PATH にある → CLI 検出成功"
                cli_detection_result="PASS"
            else
                echo "INFO: sdd-cli が PATH にない → CLI 未検出（正常）"
                cli_detection_result="NOT_FOUND"
            fi
        fi
    else
        echo "ERROR: .sdd-config.json が存在しません"
        cli_detection_result="MISSING"
    fi

    echo "cli-detection:${cli_detection_result}" >> "$log_dir/cli-test.log"

    # 追加検証: Claude セッション内で実際の環境変数を確認
    echo "--- 環境変数検証（Claude セッション内） ---"
    cd "$test_dir"
    local env_check_cmd='echo "SDD_CLI_AVAILABLE=${SDD_CLI_AVAILABLE}"; echo "SDD_CLI_COMMAND=${SDD_CLI_COMMAND}"'
    local env_result
    env_result=$(echo "$env_check_cmd" | claude --plugin-dir "$plugin_dir" --print 2>&1 | grep "SDD_CLI" || true)

    if [ ! -z "$env_result" ]; then
        echo "$env_result" | tee -a "$log_dir/cli-env-vars.log"

        # SDD_CLI_AVAILABLE の値を抽出して検証
        if echo "$env_result" | grep -q "SDD_CLI_AVAILABLE=true"; then
            echo "✓ 環境変数確認: SDD_CLI_AVAILABLE=true が設定されています"
            if [ "$cli_detection_result" = "WARN" ]; then
                # 推定が WARN だったが実際は成功している場合
                cli_detection_result="PASS"
                echo "cli-detection:${cli_detection_result}" >> "$log_dir/cli-test.log"
            fi
        elif echo "$env_result" | grep -q "SDD_CLI_AVAILABLE=false"; then
            echo "✓ 環境変数確認: SDD_CLI_AVAILABLE=false （CLI 未検出）"
        else
            echo "⚠ 環境変数確認: SDD_CLI_AVAILABLE が設定されていません"
        fi
    else
        echo "INFO: 環境変数の確認をスキップ（セッション起動に失敗した可能性）"
    fi

    # 2. sdd-cli lint --json テスト
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
    echo "ログ保存: $log_dir/cli-lint.log (${elapsed}秒, exit=${lint_exit_code})"

    # 3. sdd-cli index --quiet テスト
    echo "--- sdd-cli index --quiet テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    local index_exit_code=0
    $cli_cmd index --quiet > "$log_dir/cli-index.log" 2>&1 || index_exit_code=$?
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "cli-index:${elapsed}" >> "$log_dir/timing.log"
    echo "cli-index-exit-code:${index_exit_code}" >> "$log_dir/cli-test.log"
    echo "ログ保存: $log_dir/cli-index.log (${elapsed}秒, exit=${index_exit_code})"

    # 4. sdd-cli search --format json テスト
    echo "--- sdd-cli search --format json テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    local search_exit_code=0
    $cli_cmd search --format json "spec" > "$log_dir/cli-search.log" 2>&1 || search_exit_code=$?
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "cli-search:${elapsed}" >> "$log_dir/timing.log"
    echo "cli-search-exit-code:${search_exit_code}" >> "$log_dir/cli-test.log"
    echo "ログ保存: $log_dir/cli-search.log (${elapsed}秒, exit=${search_exit_code})"

    local phase_end
    phase_end=$(date +%s)
    local phase_elapsed=$((phase_end - phase_start))
    echo "cli-test-total:${phase_elapsed}" >> "$log_dir/timing.log"
    echo "Phase 3c 合計実行時間: ${phase_elapsed}秒"

    echo ""
}

# --- Helper: メトリクス収集 ---
collect_metrics() {
    local phase_name="$1"
    local test_dir="$2"
    local log_dir="$3"
    local file_pattern="${4:-*.md}"  # 対象ファイルパターン（デフォルト: *.md）

    local metrics_file="${log_dir}/metrics.log"
    local total_size=0
    local total_lines=0
    local file_count=0

    # 指定されたパターンに一致するファイルのサイズと行数を集計
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            local size=$(wc -c < "$file" | tr -d ' ')
            local lines=$(wc -l < "$file" | tr -d ' ')
            total_size=$((total_size + size))
            total_lines=$((total_lines + lines))
            file_count=$((file_count + 1))
        fi
    done < <(find "$test_dir/.sdd" -type f -name "$file_pattern" -print0 2>/dev/null)

    # metrics.log に追記
    # フォーマット: phase:file_count:total_size_bytes:total_lines
    echo "${phase_name}:${file_count}:${total_size}:${total_lines}" >> "$metrics_file"
    echo "メトリクス記録: ${phase_name} (ファイル数: ${file_count}, 合計サイズ: ${total_size} bytes, 合計行数: ${total_lines})"
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

### sdd-workflow-with-cli (CLI 連携テスト: sdd-workflow + cli.enabled: true)

> このテストは、`cli.enabled: true` の `.sdd-config.json` がある状態で `sdd-workflow` プラグインを使用し、CLI が `uvx` 経由で検出・利用されるかを検証します。

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| session-start.sh 実行 | - | |
| .sdd-config.json 保持 | - | cli.enabled: true が維持されていること |
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
| CLI 検出 (SDD_CLI_AVAILABLE) | - | cli.enabled: true から CLI が検出されること |
| sdd-cli lint --json 実行 | - | 正常終了し JSON 出力を返すこと |
| sdd-cli index 実行 | - | 正常終了しインデックスが作成されること |
| sdd-cli search 実行 | - | 正常終了し検索結果を返すこと |

## 実行時間

SUMMARY_EOF

    # テストケース一覧（プラグイン + 追加テストケース）
    local test_cases=()
    for plugin_dir in "$PLUGINS_DIR"/*/; do
        test_cases+=("$(basename "$plugin_dir")")
    done
    test_cases+=("sdd-workflow-with-ja-config")
    test_cases+=("sdd-workflow-with-cli")
    test_cases+=("sdd-workflow-cli-disabled")

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
                if [ "$phase" != "gen-skills-total" ] && [ "$phase" != "cli-test-total" ]; then
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

    # CLI連携 A/B テスト結果の比較表を追加
    echo "## CLI連携 A/B テスト結果" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "> CLI有無による実行時間とメトリクスの比較" >> "$summary_file"
    echo "" >> "$summary_file"

    local cli_disabled_timing="${TEST_BASE}/logs/sdd-workflow-cli-disabled/timing.log"
    local cli_enabled_timing="${TEST_BASE}/logs/sdd-workflow-with-cli/timing.log"
    local cli_disabled_metrics="${TEST_BASE}/logs/sdd-workflow-cli-disabled/metrics.log"
    local cli_enabled_metrics="${TEST_BASE}/logs/sdd-workflow-with-cli/metrics.log"

    if [ -f "$cli_disabled_timing" ] && [ -f "$cli_enabled_timing" ]; then
        echo "### 実行時間の比較" >> "$summary_file"
        echo "" >> "$summary_file"
        echo "| フェーズ | CLI無効 (秒) | CLI有効 (秒) | 差分 (秒) | 変化率 (%) |" >> "$summary_file"
        echo "|---------|-------------|-------------|----------|-----------|" >> "$summary_file"

        # 主要フェーズの比較（constitution-init, generate-prd, generate-spec）
        for phase in "constitution-init" "generate-prd" "generate-spec"; do
            local time_disabled=$(grep "^${phase}:" "$cli_disabled_timing" 2>/dev/null | cut -d: -f2)
            local time_enabled=$(grep "^${phase}:" "$cli_enabled_timing" 2>/dev/null | cut -d: -f2)

            if [ ! -z "$time_disabled" ] && [ ! -z "$time_enabled" ]; then
                local time_diff=$((time_enabled - time_disabled))
                local time_percent=0
                if [ "$time_disabled" -gt 0 ]; then
                    time_percent=$(( (time_diff * 100) / time_disabled ))
                fi

                local sign=""
                if [ "$time_diff" -gt 0 ]; then
                    sign="+"
                fi

                echo "| ${phase} | ${time_disabled} | ${time_enabled} | ${sign}${time_diff} | ${sign}${time_percent}% |" >> "$summary_file"
            fi
        done

        # 合計時間の計算と比較
        local total_disabled=0
        local total_enabled=0
        while IFS=: read -r phase seconds; do
            if [ "$phase" != "gen-skills-total" ] && [ "$phase" != "cli-test-total" ]; then
                total_disabled=$((total_disabled + seconds))
            fi
        done < "$cli_disabled_timing"

        while IFS=: read -r phase seconds; do
            if [ "$phase" != "gen-skills-total" ] && [ "$phase" != "cli-test-total" ]; then
                total_enabled=$((total_enabled + seconds))
            fi
        done < "$cli_enabled_timing"

        local total_diff=$((total_enabled - total_disabled))
        local total_percent=0
        if [ "$total_disabled" -gt 0 ]; then
            total_percent=$(( (total_diff * 100) / total_disabled ))
        fi

        local sign=""
        if [ "$total_diff" -gt 0 ]; then
            sign="+"
        fi

        echo "| **合計** | **${total_disabled}** | **${total_enabled}** | **${sign}${total_diff}** | **${sign}${total_percent}%** |" >> "$summary_file"
        echo "" >> "$summary_file"
    else
        echo "実行時間データなし" >> "$summary_file"
        echo "" >> "$summary_file"
    fi

    # メトリクス分析セクション
    echo "## パフォーマンス分析" >> "$summary_file"
    echo "" >> "$summary_file"

    if [ -f "$cli_disabled_metrics" ] && [ -f "$cli_enabled_metrics" ]; then
        echo "### 生成ファイルメトリクス" >> "$summary_file"
        echo "" >> "$summary_file"
        echo "| フェーズ | CLI無効 (ファイル数) | CLI有効 (ファイル数) | CLI無効 (合計サイズ) | CLI有効 (合計サイズ) |" >> "$summary_file"
        echo "|---------|-------------------|-------------------|-------------------|-------------------|" >> "$summary_file"

        for phase in "constitution-init" "generate-prd" "generate-spec"; do
            local disabled_data=$(grep "^${phase}:" "$cli_disabled_metrics" 2>/dev/null)
            local enabled_data=$(grep "^${phase}:" "$cli_enabled_metrics" 2>/dev/null)

            if [ ! -z "$disabled_data" ] && [ ! -z "$enabled_data" ]; then
                local file_count_disabled=$(echo "$disabled_data" | cut -d: -f2)
                local size_disabled=$(echo "$disabled_data" | cut -d: -f3)
                local file_count_enabled=$(echo "$enabled_data" | cut -d: -f2)
                local size_enabled=$(echo "$enabled_data" | cut -d: -f3)

                echo "| ${phase} | ${file_count_disabled} | ${file_count_enabled} | ${size_disabled} bytes | ${size_enabled} bytes |" >> "$summary_file"
            fi
        done

        echo "" >> "$summary_file"
    fi

    # 推奨事項セクション
    echo "## 推奨事項" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "### CLI連携の使い分け" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "| シナリオ | 推奨 | 理由 |" >> "$summary_file"
    echo "|---------|------|------|" >> "$summary_file"
    echo "| 初回仕様書生成 | **Fallback（CLI無効）** | 高速で初期ドラフトを作成 |" >> "$summary_file"
    echo "| 整合性チェック | **CLI有効** | 構造検証が重要 |" >> "$summary_file"
    echo "| 既存ドキュメント更新 | **CLI有効** | 依存関係チェックが必要 |" >> "$summary_file"
    echo "| CI/CD自動化 | **CLI有効** | lintによる品質保証 |" >> "$summary_file"
    echo "" >> "$summary_file"

    echo "### パフォーマンス最適化の提案" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "1. **CLI呼び出しの最適化**:" >> "$summary_file"
    echo "   - \`lint --quiet\` で進捗メッセージを抑制" >> "$summary_file"
    echo "   - \`search --limit 10\` で結果数を制限" >> "$summary_file"
    echo "   - 不要な CLI 呼び出しを削減" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "2. **Strategy A/B の選択的適用**:" >> "$summary_file"
    echo "   - 新規ドキュメント生成時は Strategy B のみ使用" >> "$summary_file"
    echo "   - 既存ドキュメント更新時のみ Strategy A を使用" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "3. **トークン消費の削減**:" >> "$summary_file"
    echo "   - CLI出力の要約（長い JSON を短縮）" >> "$summary_file"
    echo "   - lint エラーのフィルタリング（critical のみ表示）" >> "$summary_file"
    echo "" >> "$summary_file"

    # トークン使用量分析セクションを追加
    echo "## トークン使用量・API コスト分析" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "> 各フェーズでの API 呼び出しメトリクス" >> "$summary_file"
    echo "" >> "$summary_file"

    # テストケース別のトークン使用量テーブルを生成
    for test_case in "${test_cases[@]}"; do
        local log_dir="${TEST_BASE}/logs/${test_case}"
        local token_file="${log_dir}/token-usage.log"

        echo "### ${test_case}" >> "$summary_file"
        echo "" >> "$summary_file"

        if [ -f "$token_file" ]; then
            echo "| フェーズ | 入力トークン | 出力トークン | キャッシュ作成 | キャッシュ読込 | コスト (USD) | ターン数 |" >> "$summary_file"
            echo "|---------|------------|------------|-------------|-------------|------------|--------|" >> "$summary_file"

            local total_input=0
            local total_output=0
            local total_cache_create=0
            local total_cache_read=0
            local total_cost=0
            local total_turns=0

            while IFS=: read -r phase input_tok output_tok cache_create cache_read cost_usd duration_ms num_turns; do
                if [ ! -z "$phase" ]; then
                    total_input=$((total_input + input_tok))
                    total_output=$((total_output + output_tok))
                    total_cache_create=$((total_cache_create + cache_create))
                    total_cache_read=$((total_cache_read + cache_read))
                    # cost_usd は浮動小数点なので bc で加算（bc が利用可能な場合）
                    if command -v bc >/dev/null 2>&1; then
                        total_cost=$(echo "$total_cost + $cost_usd" | bc -l)
                    fi
                    total_turns=$((total_turns + num_turns))

                    echo "| ${phase} | ${input_tok} | ${output_tok} | ${cache_create} | ${cache_read} | \$${cost_usd} | ${num_turns} |" >> "$summary_file"
                fi
            done < "$token_file"

            # 合計行を追加
            echo "| **合計** | **${total_input}** | **${total_output}** | **${total_cache_create}** | **${total_cache_read}** | **\$${total_cost}** | **${total_turns}** |" >> "$summary_file"
        else
            echo "トークン使用量データなし" >> "$summary_file"
        fi
        echo "" >> "$summary_file"
    done

    # Context 使用率分析（Haiku 200K を想定）
    echo "## Context 使用率分析" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "> Haiku 200K コンテキストウィンドウ (200,000 トークン) を想定" >> "$summary_file"
    echo "" >> "$summary_file"

    for test_case in "${test_cases[@]}"; do
        local log_dir="${TEST_BASE}/logs/${test_case}"
        local token_file="${log_dir}/token-usage.log"

        if [ -f "$token_file" ]; then
            local max_input=0
            while IFS=: read -r phase input_tok output_tok cache_create cache_read cost_usd duration_ms num_turns; do
                if [ "$input_tok" -gt "$max_input" ]; then
                    max_input=$input_tok
                fi
            done < "$token_file"

            if [ "$max_input" -gt 0 ]; then
                local usage_percent=$(( (max_input * 100) / 200000 ))
                echo "- **${test_case}**: 最大入力トークン = ${max_input}, Context 使用率 = ${usage_percent}% (200K 中)" >> "$summary_file"
            fi
        fi
    done
    echo "" >> "$summary_file"

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
    cli-test)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 cli-test <plugin_dir> [test_case_name]"
            exit 1
        fi
        run_cli_test "$2" "${3:-}"
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
        echo "Usage: $0 {setup|run|sdd-init|gen-skills|cli-test|collect|summary} [plugin_dir] [test_case_name]"
        echo ""
        echo "Commands:"
        echo "  setup                              テスト環境を構築"
        echo "  run <plugin_dir> [test_case_name]  session-start テスト実行"
        echo "  sdd-init <plugin_dir> [test_case_name]  /sdd-init テスト実行"
        echo "  gen-skills <plugin_dir> [test_case_name]  生成系スキルテスト実行"
        echo "  cli-test <plugin_dir> [test_case_name]   CLI テスト実行"
        echo "  collect <plugin_dir> [test_case_name]   ログ収集"
        echo "  summary                            TEST_SUMMARY.md 生成"
        echo ""
        echo "test_case_name: オプション。テストケース名（省略時はプラグイン名を使用）"
        echo "                例: sdd-workflow-with-ja-config"
        exit 1
        ;;
esac
