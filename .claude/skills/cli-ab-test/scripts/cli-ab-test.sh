#!/bin/bash
# cli-ab-test.sh
# CLI有効/無効のA/Bテスト実行スクリプト
# sdd-workflow (ベースライン) と sdd-workflow-with-cli (CLI有効) で
# 同一タスクを実行し、トークン使用量を比較する。
#
# Usage:
#   cli-ab-test.sh setup                              - テスト環境を構築
#   cli-ab-test.sh run <plugin_dir> [test_case_name]  - session-start テスト実行
#   cli-ab-test.sh sdd-init <plugin_dir> [test_case_name] - /sdd-init テスト実行
#   cli-ab-test.sh gen-skills <plugin_dir> [test_case_name] - 生成系スキルテスト実行（前提条件構築）
#   cli-ab-test.sh cli-skills <plugin_dir> [test_case_name] - CLI分岐スキルテスト実行（メトリクス比較対象）
#   cli-ab-test.sh collect <plugin_dir> [test_case_name]  - ログ収集
#   cli-ab-test.sh summary                            - TEST_SUMMARY.md テンプレート生成

set -euo pipefail

TEST_BASE="/tmp/ai-sdd-cli-ab-test"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# --- Phase 1: Setup ---
setup() {
    echo "=== Phase 1: テスト環境構築 (CLI A/B) ==="

    # クリーンアップ
    if [ -d "$TEST_BASE" ]; then
        rm -rf "$TEST_BASE"
        echo "既存のテストディレクトリを削除しました"
    fi

    mkdir -p "$TEST_BASE"
    echo "テストベースディレクトリ作成: $TEST_BASE"

    # ベースライン: sdd-workflow (CLI無効)
    local baseline_dir="${TEST_BASE}/sdd-workflow"
    mkdir -p "$baseline_dir"
    cd "$baseline_dir"

    git init -q
    echo "" > CLAUDE.md
    git add CLAUDE.md
    git commit -q -m "initial commit"

    echo "テストディレクトリ作成: ${baseline_dir} (git initialized, ベースライン)"

    # CLI有効: sdd-workflow-with-cli
    local cli_dir="${TEST_BASE}/sdd-workflow-with-cli"
    mkdir -p "$cli_dir"
    cd "$cli_dir"

    git init -q
    echo "" > CLAUDE.md
    git add CLAUDE.md
    git commit -q -m "initial commit"

    # CLI有効設定
    cat > ".sdd-config.json" << 'EOF'
{
  "root": ".sdd",
  "lang": "en",
  "cli": {
    "enabled": true
  }
}
EOF
    git add .sdd-config.json
    git commit -q -m "add .sdd-config.json with cli enabled"

    echo "テストディレクトリ作成: ${cli_dir} (git initialized, CLI有効)"

    # ログディレクトリ
    mkdir -p "${TEST_BASE}/logs"
    echo "ログディレクトリ作成: ${TEST_BASE}/logs"

    echo ""
    echo "=== セットアップ完了 ==="
    echo "テストディレクトリ: $TEST_BASE"
    echo "テストケース:"
    echo "  - sdd-workflow (ベースライン: CLI無効)"
    echo "  - sdd-workflow-with-cli (CLI有効)"
}

# --- Phase 2: サブセッション実行 (session-start + 基本検証) ---
run_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 2: session-start テスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local start_time
    start_time=$(date +%s)

    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    echo "session-start フックが実行されました。このメッセージが表示されれば正常です。" | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      > "$log_dir/session-start.jsonl" 2>"$log_dir/session-start.stderr.log" || true

    # メトリクス収集
    if [ -f "$log_dir/session-start.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/session-start.jsonl" > "$log_dir/session-start-metrics.json" 2>/dev/null || true
    fi

    echo "ログ保存: $log_dir/session-start.jsonl"

    # .sdd-config.json を保存
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

# --- Phase 2b: /sdd-init テスト ---
run_sdd_init_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 2b: /sdd-init テスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local start_time
    start_time=$(date +%s)

    # 前提条件チェック
    echo "--- session-start 実行確認 ---"
    local session_start_ok=true

    if [ ! -f "$test_dir/.sdd-config.json" ]; then
        echo "ERROR: .sdd-config.json が存在しません"
        session_start_ok=false
    fi

    if [ ! -d "$test_dir/.sdd" ]; then
        echo "ERROR: .sdd ディレクトリが存在しません"
        session_start_ok=false
    fi

    if [ ! -f "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" ]; then
        echo "ERROR: AI-SDD-PRINCIPLES.md が存在しません"
        session_start_ok=false
    fi

    if [ "$session_start_ok" = true ]; then
        echo "OK: session-start.sh の実行を確認"
    else
        echo "WARNING: session-start.sh が正しく実行されていない可能性があります"
    fi

    # session-start 実行確認結果をログに保存
    echo "session_start_executed: $session_start_ok" > "$log_dir/session-start-check.log"
    echo "checked_files:" >> "$log_dir/session-start-check.log"
    echo "  .sdd-config.json: $([ -f "$test_dir/.sdd-config.json" ] && echo 'exists' || echo 'missing')" >> "$log_dir/session-start-check.log"
    echo "  .sdd/: $([ -d "$test_dir/.sdd" ] && echo 'exists' || echo 'missing')" >> "$log_dir/session-start-check.log"
    echo "  .sdd/AI-SDD-PRINCIPLES.md: $([ -f "$test_dir/.sdd/AI-SDD-PRINCIPLES.md" ] && echo 'exists' || echo 'missing')" >> "$log_dir/session-start-check.log"

    echo "--- /sdd-init --ci 実行 ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    echo "/sdd-init --ci" | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/sdd-init.jsonl" 2>"$log_dir/sdd-init.stderr.log" || true

    # メトリクス収集
    if [ -f "$log_dir/sdd-init.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/sdd-init.jsonl" > "$log_dir/sdd-init-metrics.json" 2>/dev/null || true
    fi

    echo "ログ保存: $log_dir/sdd-init.jsonl"

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

# --- Phase 2c: 生成系スキルテスト ---
run_gen_skills_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 2c: 生成系スキルテスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local phase_start
    phase_start=$(date +%s)

    # /constitution init テスト
    echo "--- /constitution init テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    local start_time
    start_time=$(date +%s)
    echo '/constitution init A sample CLI tool project using TypeScript.' | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/constitution-init.jsonl" 2>"$log_dir/constitution-init.stderr.log" || true
    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo "constitution-init:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/constitution-init.jsonl (${elapsed}秒)"

    # メトリクス収集
    if [ -f "$log_dir/constitution-init.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/constitution-init.jsonl" > "$log_dir/constitution-init-metrics.json" 2>/dev/null || true
    fi

    # CONSTITUTION.md を保存
    if [ -f "$test_dir/.sdd/CONSTITUTION.md" ]; then
        cp "$test_dir/.sdd/CONSTITUTION.md" "$log_dir/CONSTITUTION.md"
        echo "CONSTITUTION.md 保存完了"
    fi

    # /generate-prd テスト
    echo "--- /generate-prd テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    echo "/generate-prd --ci A sample task management feature. Users can create, edit, and delete tasks." | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/generate-prd.jsonl" 2>"$log_dir/generate-prd.stderr.log" || true
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "generate-prd:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/generate-prd.jsonl (${elapsed}秒)"

    # メトリクス収集
    if [ -f "$log_dir/generate-prd.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/generate-prd.jsonl" > "$log_dir/generate-prd-metrics.json" 2>/dev/null || true
    fi

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

    # /generate-spec テスト
    echo "--- /generate-spec テスト ---"
    cd "$test_dir"
    start_time=$(date +%s)
    echo "/generate-spec --ci User authentication feature. Supports login and logout with email and password." | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/generate-spec.jsonl" 2>"$log_dir/generate-spec.stderr.log" || true
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "generate-spec:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/generate-spec.jsonl (${elapsed}秒)"

    # メトリクス収集
    if [ -f "$log_dir/generate-spec.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/generate-spec.jsonl" > "$log_dir/generate-spec-metrics.json" 2>/dev/null || true
    fi

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

    # ディレクトリ構造を再記録（生成スキル実行後）
    cd "$test_dir"
    if [ -d ".sdd" ]; then
        find .sdd -type f | sort > "$log_dir/sdd-structure-after-gen.log" 2>&1 || true
        echo "sdd-structure-after-gen.log 保存完了"
    fi

    local phase_end
    phase_end=$(date +%s)
    local phase_elapsed=$((phase_end - phase_start))
    echo "gen-skills-total:${phase_elapsed}" >> "$log_dir/timing.log"
    echo "Phase 2c 合計実行時間: ${phase_elapsed}秒"

    echo ""
}

# --- Phase 3: CLI分岐スキルテスト ---
run_cli_skills_test() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    mkdir -p "$log_dir"

    echo "=== Phase 3: CLI分岐スキルテスト [${effective_name}] (plugin: ${plugin_name}) ==="

    local phase_start
    phase_start=$(date +%s)

    # 設計書からフィーチャー名を動的に取得
    local feature_name=""
    if [ -d "$test_dir/.sdd/specification" ]; then
        for f in "$test_dir/.sdd/specification"/*_design.md; do
            if [ -f "$f" ]; then
                local basename_f
                basename_f="$(basename "$f")"
                feature_name="${basename_f%_design.md}"
                echo "検出されたフィーチャー名: ${feature_name}"
                break
            fi
        done
    fi

    if [ -z "$feature_name" ]; then
        echo "WARNING: 設計書が見つかりません。_spec.md からフィーチャー名を取得します。"
        if [ -d "$test_dir/.sdd/specification" ]; then
            for f in "$test_dir/.sdd/specification"/*_spec.md; do
                if [ -f "$f" ]; then
                    local basename_f
                    basename_f="$(basename "$f")"
                    feature_name="${basename_f%_spec.md}"
                    echo "検出されたフィーチャー名 (spec): ${feature_name}"
                    break
                fi
            done
        fi
    fi

    if [ -z "$feature_name" ]; then
        echo "ERROR: フィーチャー名を取得できません。specification ディレクトリにファイルがありません。"
        echo "cli-skills フェーズをスキップします。"
        return 1
    fi

    # /task-breakdown テスト
    echo "--- /task-breakdown --ci ${feature_name} テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    local start_time
    start_time=$(date +%s)
    echo "/task-breakdown --ci ${feature_name}" | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/task-breakdown.jsonl" 2>"$log_dir/task-breakdown.stderr.log" || true
    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    echo "task-breakdown:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/task-breakdown.jsonl (${elapsed}秒)"

    # メトリクス収集
    if [ -f "$log_dir/task-breakdown.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/task-breakdown.jsonl" > "$log_dir/task-breakdown-metrics.json" 2>/dev/null || true
        python3 "$REPO_ROOT/.claude/skills/cli-ab-test/scripts/collect-quality-metrics.py" \
          "$log_dir/task-breakdown.jsonl" > "$log_dir/task-breakdown-quality.json" 2>/dev/null || true
    fi

    # タスクファイルを保存
    if [ -d "$test_dir/.sdd/task" ]; then
        find "$test_dir/.sdd/task" -type f | sort > "$log_dir/task-files.log" 2>&1 || true
        echo "task-files.log 保存完了"
    fi

    # /constitution validate テスト
    echo "--- /constitution validate テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    start_time=$(date +%s)
    echo "/constitution validate" | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/constitution-validate.jsonl" 2>"$log_dir/constitution-validate.stderr.log" || true
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "constitution-validate:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/constitution-validate.jsonl (${elapsed}秒)"

    # メトリクス収集
    if [ -f "$log_dir/constitution-validate.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/constitution-validate.jsonl" > "$log_dir/constitution-validate-metrics.json" 2>/dev/null || true
        python3 "$REPO_ROOT/.claude/skills/cli-ab-test/scripts/collect-quality-metrics.py" \
          "$log_dir/constitution-validate.jsonl" > "$log_dir/constitution-validate-quality.json" 2>/dev/null || true
    fi

    # /check-spec テスト
    echo "--- /check-spec ${feature_name} --ci テスト ---"
    cd "$test_dir"
    unset CLAUDECODE SDD_LANG SDD_ROOT SDD_REQUIREMENT_DIR SDD_SPECIFICATION_DIR SDD_TASK_DIR SDD_REQUIREMENT_PATH SDD_SPECIFICATION_PATH SDD_TASK_PATH 2>/dev/null || true
    start_time=$(date +%s)
    echo "/check-spec ${feature_name} --ci" | claude --plugin-dir "$plugin_dir" --print --verbose --output-format stream-json \
      --allowedTools 'Bash(*)' 'Read' 'Write' 'Edit' 'Glob' 'Grep' 'Skill' \
      > "$log_dir/check-spec.jsonl" 2>"$log_dir/check-spec.stderr.log" || true
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "check-spec:${elapsed}" >> "$log_dir/timing.log"
    echo "ログ保存: $log_dir/check-spec.jsonl (${elapsed}秒)"

    # メトリクス収集
    if [ -f "$log_dir/check-spec.jsonl" ]; then
        python3 "$REPO_ROOT/scripts/collect-metrics.py" \
          "$log_dir/check-spec.jsonl" > "$log_dir/check-spec-metrics.json" 2>/dev/null || true
        python3 "$REPO_ROOT/.claude/skills/cli-ab-test/scripts/collect-quality-metrics.py" \
          "$log_dir/check-spec.jsonl" > "$log_dir/check-spec-quality.json" 2>/dev/null || true
    fi

    # ディレクトリ構造を再記録（CLI分岐スキル実行後）
    cd "$test_dir"
    if [ -d ".sdd" ]; then
        find .sdd -type f | sort > "$log_dir/sdd-structure-after-cli-skills.log" 2>&1 || true
        echo "sdd-structure-after-cli-skills.log 保存完了"
    fi

    local phase_end
    phase_end=$(date +%s)
    local phase_elapsed=$((phase_end - phase_start))
    echo "cli-skills-total:${phase_elapsed}" >> "$log_dir/timing.log"
    echo "Phase 3 合計実行時間: ${phase_elapsed}秒"

    echo ""
}

# --- Phase 4: ログ収集 ---
collect_logs() {
    local plugin_dir="$1"
    local test_case_name="${2:-}"
    local plugin_name
    plugin_name="$(basename "$plugin_dir")"

    local effective_name="${test_case_name:-$plugin_name}"
    local test_dir="${TEST_BASE}/${effective_name}"
    local log_dir="${TEST_BASE}/logs/${effective_name}"

    echo "=== Phase 3: ログ収集 [${effective_name}] (plugin: ${plugin_name}) ==="

    if [ ! -d "$log_dir" ]; then
        echo "ログディレクトリが見つかりません: $log_dir"
        return 1
    fi

    # .sdd-config.json をログディレクトリにコピー（まだコピーされていない場合）
    if [ -f "$test_dir/.sdd-config.json" ] && [ ! -f "$log_dir/config.json" ]; then
        cp "$test_dir/.sdd-config.json" "$log_dir/config.json"
        echo "config.json を収集しました"
    fi

    # .sdd/ ディレクトリ構造を記録（まだ記録されていない場合）
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
    local test_cases=("sdd-workflow" "sdd-workflow-with-cli")

    cat > "$summary_file" << 'SUMMARY_EOF'
# CLI A/B Test Summary

> CLI有効/無効のトークン使用量比較テスト（CLI分岐スキルに特化）

## テスト実行情報

| 項目 | 値 |
|------|-----|
| 実行日時 | TIMESTAMP_PLACEHOLDER |
| テストベース | /tmp/ai-sdd-cli-ab-test |

## 前提条件構築（Phase 2）

> session-start → sdd-init → gen-skills はCLI分岐しないため、メトリクス比較対象外。
> 前提ファイル（CONSTITUTION.md, PRD, spec, design）を生成するために実行。

### sdd-workflow (ベースライン: CLI無効)

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| session-start.sh 実行 | - | |
| /sdd-init 実行 | - | |
| /constitution init 実行 | - | |
| /generate-prd 実行 | - | |
| /generate-spec 実行 | - | |

### sdd-workflow-with-cli (CLI有効)

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| session-start.sh 実行 | - | CLI自動起動を確認 |
| /sdd-init 実行 | - | |
| /constitution init 実行 | - | |
| /generate-prd 実行 | - | |
| /generate-spec 実行 | - | |

## CLI分岐スキルテスト結果（Phase 3 — メトリクス比較対象）

### sdd-workflow (ベースライン: CLI無効)

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| /task-breakdown 実行 | - | .sdd/task/ 配下にタスクファイル生成 |
| /constitution validate 実行 | - | 検証レポート出力 |
| /check-spec 実行 | - | 整合性チェック結果出力 |

### sdd-workflow-with-cli (CLI有効)

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| /task-breakdown 実行 | - | .sdd/task/ 配下にタスクファイル生成 |
| /constitution validate 実行 | - | 検証レポート出力 |
| /check-spec 実行 | - | 整合性チェック結果出力 |

## 実行時間

SUMMARY_EOF

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
                if [ "$phase" != "gen-skills-total" ] && [ "$phase" != "cli-skills-total" ]; then
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

    # トークン使用量比較テーブル
    local baseline_dir="${TEST_BASE}/logs/sdd-workflow"
    local cli_dir="${TEST_BASE}/logs/sdd-workflow-with-cli"

    python3 - "$baseline_dir" "$cli_dir" >> "$summary_file" << 'PYEOF'
import json, sys, os

baseline_dir = sys.argv[1]
cli_dir = sys.argv[2]

# CLI分岐スキルのみがメトリクス比較対象
comparison_phases = ["task-breakdown", "constitution-validate", "check-spec"]
# 前提条件構築フェーズ（参考情報として記録）
setup_phases = ["session-start", "sdd-init", "constitution-init", "generate-prd", "generate-spec"]

print("## トークン使用量比較 (CLI A/B) — CLI分岐スキル")
print()
print("> CLI分岐スキル（`SDD_CLI_AVAILABLE` で処理が変わるスキル）のみを比較対象とします。")
print()
print("| フェーズ | CLI無効 (tokens) | CLI無効 (cost) | CLI有効 (tokens) | CLI有効 (cost) | 削減率 |")
print("|---------|-----------------|---------------|-----------------|---------------|--------|")

def read_metrics(directory, phase):
    filepath = os.path.join(directory, f"{phase}-metrics.json")
    if os.path.isfile(filepath):
        with open(filepath) as f:
            return json.load(f)
    return None

def format_row(phase, b_data, c_data):
    bt = b_data.get("total_tokens", 0) if b_data else 0
    bc = b_data.get("cost_usd") if b_data else None
    ct = c_data.get("total_tokens", 0) if c_data else 0
    cc = c_data.get("cost_usd") if c_data else None

    b_tokens_str = f"{bt:,}" if b_data else "-"
    b_cost_str = f"${bc:.4f}" if bc is not None else "-"
    c_tokens_str = f"{ct:,}" if c_data else "-"
    c_cost_str = f"${cc:.4f}" if cc is not None else "-"
    reduction_str = "-"
    if bt > 0 and ct > 0:
        r = ((bt - ct) / bt) * 100
        reduction_str = f"{r:+.1f}%"

    print(f"| {phase} | {b_tokens_str} | {b_cost_str} | {c_tokens_str} | {c_cost_str} | {reduction_str} |")
    return bt, bc or 0, ct, cc or 0

total_b_tokens = 0
total_c_tokens = 0
total_b_cost = 0.0
total_c_cost = 0.0

for phase in comparison_phases:
    b_data = read_metrics(baseline_dir, phase)
    c_data = read_metrics(cli_dir, phase)
    bt, bc, ct, cc = format_row(phase, b_data, c_data)
    total_b_tokens += bt
    total_c_tokens += ct
    total_b_cost += bc
    total_c_cost += cc

# 合計行
total_reduction_str = "-"
if total_b_tokens > 0 and total_c_tokens > 0:
    r = ((total_b_tokens - total_c_tokens) / total_b_tokens) * 100
    total_reduction_str = f"{r:+.1f}%"

print(f"| **合計** | **{total_b_tokens:,}** | **${total_b_cost:.4f}** | **{total_c_tokens:,}** | **${total_c_cost:.4f}** | **{total_reduction_str}** |")
print()

# 前提条件構築フェーズ（参考情報）
print("### 前提条件構築フェーズ（参考）")
print()
print("> 以下はCLI分岐しないスキルのため、トークン比較の参考情報です。")
print()
print("| フェーズ | CLI無効 (tokens) | CLI無効 (cost) | CLI有効 (tokens) | CLI有効 (cost) |")
print("|---------|-----------------|---------------|-----------------|---------------|")

for phase in setup_phases:
    b_data = read_metrics(baseline_dir, phase)
    c_data = read_metrics(cli_dir, phase)
    bt = b_data.get("total_tokens", 0) if b_data else 0
    bc = b_data.get("cost_usd") if b_data else None
    ct = c_data.get("total_tokens", 0) if c_data else 0
    cc = c_data.get("cost_usd") if c_data else None
    b_tokens_str = f"{bt:,}" if b_data else "-"
    b_cost_str = f"${bc:.4f}" if bc is not None else "-"
    c_tokens_str = f"{ct:,}" if c_data else "-"
    c_cost_str = f"${cc:.4f}" if cc is not None else "-"
    print(f"| {phase} | {b_tokens_str} | {b_cost_str} | {c_tokens_str} | {c_cost_str} |")

print()

# 品質比較テーブル
print("## 出力品質比較 (CLI A/B)")
print()

quality_phases = ["task-breakdown", "constitution-validate", "check-spec"]
quality_metrics_keys = [
    ("text_length", "テキスト長"),
    ("section_count", "セクション数"),
    ("table_count", "テーブル数"),
    ("checklist_count", "チェックリスト数"),
    ("detected_issues", "検出項目数"),
]

def read_quality(directory, phase):
    filepath = os.path.join(directory, f"{phase}-quality.json")
    if os.path.isfile(filepath):
        with open(filepath) as f:
            return json.load(f)
    return None

# ヘッダー
header = "| 指標 |"
separator = "|------|"
for phase in quality_phases:
    header += f" CLI無効 ({phase}) | CLI有効 ({phase}) |"
    separator += "------|------|"
print(header)
print(separator)

for key, label in quality_metrics_keys:
    row = f"| {label} |"
    for phase in quality_phases:
        b_q = read_quality(baseline_dir, phase)
        c_q = read_quality(cli_dir, phase)
        b_val = b_q.get(key, "-") if b_q else "-"
        c_val = c_q.get(key, "-") if c_q else "-"
        row += f" {b_val} | {c_val} |"
    print(row)

print()
PYEOF

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
    cli-skills)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 cli-skills <plugin_dir> [test_case_name]"
            exit 1
        fi
        run_cli_skills_test "$2" "${3:-}"
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
        echo "Usage: $0 {setup|run|sdd-init|gen-skills|cli-skills|collect|summary} [plugin_dir] [test_case_name]"
        echo ""
        echo "Commands:"
        echo "  setup                              テスト環境を構築（ベースライン + CLI有効）"
        echo "  run <plugin_dir> [test_case_name]  session-start テスト実行"
        echo "  sdd-init <plugin_dir> [test_case_name]  /sdd-init テスト実行"
        echo "  gen-skills <plugin_dir> [test_case_name]  生成系スキルテスト実行（前提条件構築）"
        echo "  cli-skills <plugin_dir> [test_case_name]  CLI分岐スキルテスト実行（メトリクス比較対象）"
        echo "  collect <plugin_dir> [test_case_name]   ログ収集"
        echo "  summary                            TEST_SUMMARY.md 生成（トークン比較テーブル付き）"
        echo ""
        echo "test_case_name: オプション。テストケース名（省略時はプラグイン名を使用）"
        echo "                例: sdd-workflow-with-cli"
        exit 1
        ;;
esac
