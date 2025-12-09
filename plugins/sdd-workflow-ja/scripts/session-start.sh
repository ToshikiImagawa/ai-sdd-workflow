#!/bin/bash
# session-start.sh
# SessionStart フック用スクリプト
# セッション開始時に .sdd-config.json を読み込み（存在しなければ生成）、環境変数を初期化する

# プロジェクトルートを取得
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
else
    PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi

# .sdd-config.json のパス
CONFIG_FILE="${PROJECT_ROOT}/.sdd-config.json"

# デフォルト値
DOCS_ROOT=".sdd"
REQUIREMENT_DIR="requirement"
SPECIFICATION_DIR="specification"
TASK_DIR="task"

# 旧構成の検出とマイグレーション警告
LEGACY_DETECTED=false
LEGACY_DOCS_ROOT=""
LEGACY_REQUIREMENT=""
LEGACY_TASK=""

# .sdd-config.json が存在しない場合のみ旧構成をチェック
if [ ! -f "$CONFIG_FILE" ]; then
    # 旧ドキュメントルート (.docs) の検出
    if [ -d "${PROJECT_ROOT}/.docs" ] && [ ! -d "${PROJECT_ROOT}/.sdd" ]; then
        LEGACY_DETECTED=true
        LEGACY_DOCS_ROOT=".docs"
        DOCS_ROOT=".docs"
    fi

    # 旧要求仕様ディレクトリ (requirement-diagram) の検出
    if [ -d "${PROJECT_ROOT}/${DOCS_ROOT}/requirement-diagram" ]; then
        LEGACY_DETECTED=true
        LEGACY_REQUIREMENT="requirement-diagram"
        REQUIREMENT_DIR="requirement-diagram"
    fi

    # 旧タスクディレクトリ (review) の検出
    if [ -d "${PROJECT_ROOT}/${DOCS_ROOT}/review" ] && [ ! -d "${PROJECT_ROOT}/${DOCS_ROOT}/task" ]; then
        LEGACY_DETECTED=true
        LEGACY_TASK="review"
        TASK_DIR="review"
    fi

    # 旧構成が検出された場合
    if [ "$LEGACY_DETECTED" = true ]; then
        # 旧構成の値で .sdd-config.json を自動生成
        cat > "$CONFIG_FILE" << EOF
{
  "docsRoot": "${DOCS_ROOT}",
  "directories": {
    "requirement": "${REQUIREMENT_DIR}",
    "specification": "${SPECIFICATION_DIR}",
    "task": "${TASK_DIR}"
  }
}
EOF
        echo "[AI-SDD Migration] 旧バージョンのディレクトリ構成を検出しました。" >&2
        echo "" >&2
        echo "検出された旧構成:" >&2
        [ -n "$LEGACY_DOCS_ROOT" ] && echo "  - ドキュメントルート: .docs" >&2
        [ -n "$LEGACY_REQUIREMENT" ] && echo "  - 要求仕様: requirement-diagram" >&2
        [ -n "$LEGACY_TASK" ] && echo "  - タスクログ: review" >&2
        echo "" >&2
        echo "旧構成に基づいて .sdd-config.json を自動生成しました。" >&2
        echo "新構成に移行する場合は以下のコマンドを実行してください:" >&2
        echo "  /sdd_migrate - 新構成への移行" >&2
        echo "" >&2
    else
        # 旧構成が検出されず、.sdd-config.json も存在しない場合、デフォルトの設定ファイルを自動生成
        cat > "$CONFIG_FILE" << 'EOF'
{
  "docsRoot": ".sdd",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
EOF
        echo "[AI-SDD] .sdd-config.json を自動生成しました。" >&2
    fi
fi

# 設定ファイルが存在する場合は設定値を読み込む
if [ -f "$CONFIG_FILE" ]; then
    if command -v jq &> /dev/null; then
        # jqが利用可能な場合
        CONFIGURED_DOCS_ROOT=$(jq -r '.docsRoot // empty' "$CONFIG_FILE" 2>/dev/null)
        CONFIGURED_REQUIREMENT=$(jq -r '.directories.requirement // empty' "$CONFIG_FILE" 2>/dev/null)
        CONFIGURED_SPECIFICATION=$(jq -r '.directories.specification // empty' "$CONFIG_FILE" 2>/dev/null)
        CONFIGURED_TASK=$(jq -r '.directories.task // empty' "$CONFIG_FILE" 2>/dev/null)

        # 設定値があれば上書き
        [ -n "$CONFIGURED_DOCS_ROOT" ] && DOCS_ROOT="$CONFIGURED_DOCS_ROOT"
        [ -n "$CONFIGURED_REQUIREMENT" ] && REQUIREMENT_DIR="$CONFIGURED_REQUIREMENT"
        [ -n "$CONFIGURED_SPECIFICATION" ] && SPECIFICATION_DIR="$CONFIGURED_SPECIFICATION"
        [ -n "$CONFIGURED_TASK" ] && TASK_DIR="$CONFIGURED_TASK"
    else
        # jqがない場合はgrepで簡易的に読み込み
        CONFIGURED_DOCS_ROOT=$(grep -o '"docsRoot"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        CONFIGURED_REQUIREMENT=$(grep -o '"requirement"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        CONFIGURED_SPECIFICATION=$(grep -o '"specification"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        CONFIGURED_TASK=$(grep -o '"task"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')

        # 設定値があれば上書き
        [ -n "$CONFIGURED_DOCS_ROOT" ] && DOCS_ROOT="$CONFIGURED_DOCS_ROOT"
        [ -n "$CONFIGURED_REQUIREMENT" ] && REQUIREMENT_DIR="$CONFIGURED_REQUIREMENT"
        [ -n "$CONFIGURED_SPECIFICATION" ] && SPECIFICATION_DIR="$CONFIGURED_SPECIFICATION"
        [ -n "$CONFIGURED_TASK" ] && TASK_DIR="$CONFIGURED_TASK"
    fi
fi

# 環境変数の出力
# Claude Code が CLAUDE_ENV_FILE を提供する場合はそちらに書き出し
# 提供されない場合は stdout に出力（Claude Code が読み取る）
output_env_vars() {
    echo "export SDD_DOCS_ROOT=\"$DOCS_ROOT\""
    echo "export SDD_REQUIREMENT_DIR=\"$REQUIREMENT_DIR\""
    echo "export SDD_SPECIFICATION_DIR=\"$SPECIFICATION_DIR\""
    echo "export SDD_TASK_DIR=\"$TASK_DIR\""
    echo "export SDD_REQUIREMENT_PATH=\"${DOCS_ROOT}/${REQUIREMENT_DIR}\""
    echo "export SDD_SPECIFICATION_PATH=\"${DOCS_ROOT}/${SPECIFICATION_DIR}\""
    echo "export SDD_TASK_PATH=\"${DOCS_ROOT}/${TASK_DIR}\""
}

if [ -n "$CLAUDE_ENV_FILE" ]; then
    # 既存のSDD_*環境変数を削除（重複書き込み対策）
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        # 一時ファイルを使用してSDD_*で始まる行を除外
        grep -v '^export SDD_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi
    output_env_vars >> "$CLAUDE_ENV_FILE"
else
    # CLAUDE_ENV_FILE がない場合、stdout に出力
    # Claude Code のフックは stdout を読み取り、環境変数として解釈する
    output_env_vars
fi

exit 0