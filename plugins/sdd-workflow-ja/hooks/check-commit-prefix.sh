#!/bin/bash
# check-commit-prefix.sh
# PostToolUse フック用スクリプト（Bash ツール実行後）
# コミットメッセージ規約をチェック

# 環境変数から実行されたコマンドを取得
# jq が利用可能な場合は jq を使用、そうでなければ grep/sed でフォールバック
if command -v jq &> /dev/null; then
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)
else
    COMMAND=$(echo "$TOOL_INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

# git commit コマンドでない場合は終了
if [[ ! "$COMMAND" == *"git commit"* ]]; then
    exit 0
fi

# 最新のコミットメッセージを取得
COMMIT_MSG=$(git log -1 --format="%s" 2>/dev/null)

if [ -z "$COMMIT_MSG" ]; then
    exit 0
fi

# AI-SDD コミットメッセージ規約のチェック
# [docs], [spec], [design] プレフィックスの確認

# 変更されたファイルを取得
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null)

# .docs/ 配下のファイルが含まれているかチェック
HAS_DOCS_FILES=false
HAS_SPEC_FILES=false
HAS_DESIGN_FILES=false

for file in $CHANGED_FILES; do
    if [[ "$file" == ".docs/"* ]] || [[ "$file" == *"_spec.md" ]] || [[ "$file" == *"_design.md" ]]; then
        HAS_DOCS_FILES=true
    fi
    if [[ "$file" == *"_spec.md" ]]; then
        HAS_SPEC_FILES=true
    fi
    if [[ "$file" == *"_design.md" ]]; then
        HAS_DESIGN_FILES=true
    fi
done

# ドキュメントファイルが変更されている場合のみチェック
if [ "$HAS_DOCS_FILES" = true ]; then
    # プレフィックスのチェック
    if [[ ! "$COMMIT_MSG" =~ ^\[(docs|spec|design)\] ]]; then
        echo "[AI-SDD Warning] ドキュメント変更のコミットメッセージにプレフィックスがありません。" >&2
        echo "" >&2
        echo "推奨プレフィックス:" >&2
        echo "  [docs]   - ドキュメントの追加・更新" >&2
        echo "  [spec]   - 仕様書の追加・更新（*_spec.md）" >&2
        echo "  [design] - 設計書の追加・更新（*_design.md）" >&2
        echo "" >&2

        # より適切なプレフィックスを提案
        if [ "$HAS_SPEC_FILES" = true ] && [ "$HAS_DESIGN_FILES" = false ]; then
            echo "このコミットには *_spec.md が含まれています。" >&2
            echo "推奨: [spec] ${COMMIT_MSG}" >&2
        elif [ "$HAS_DESIGN_FILES" = true ] && [ "$HAS_SPEC_FILES" = false ]; then
            echo "このコミットには *_design.md が含まれています。" >&2
            echo "推奨: [design] ${COMMIT_MSG}" >&2
        else
            echo "推奨: [docs] ${COMMIT_MSG}" >&2
        fi

        # 警告のみで終了（ブロックしない）
        exit 0
    fi

    # プレフィックスとファイルの整合性チェック
    if [[ "$COMMIT_MSG" =~ ^\[spec\] ]] && [ "$HAS_SPEC_FILES" = false ]; then
        echo "[AI-SDD Warning] [spec] プレフィックスですが、*_spec.md ファイルが含まれていません。" >&2
    fi

    if [[ "$COMMIT_MSG" =~ ^\[design\] ]] && [ "$HAS_DESIGN_FILES" = false ]; then
        echo "[AI-SDD Warning] [design] プレフィックスですが、*_design.md ファイルが含まれていません。" >&2
    fi
fi

# 正常終了
exit 0
