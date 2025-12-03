#!/bin/bash
# check-spec-exists.sh
# PreToolUse フック用スクリプト
# Edit/Write ツール使用前に対応する仕様書の存在を確認

# 環境変数から対象ファイルパスを取得
# Claude Code は TOOL_INPUT を JSON で渡す
FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

# ファイルパスが取得できない場合は終了
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# ソースコードファイルかどうかを判定
# .docs/ 配下のファイルは対象外
if [[ "$FILE_PATH" == *".docs/"* ]]; then
    exit 0
fi

# 設定ファイル等は対象外
if [[ "$FILE_PATH" == *".json" ]] || [[ "$FILE_PATH" == *".md" ]] || [[ "$FILE_PATH" == *".yml" ]] || [[ "$FILE_PATH" == *".yaml" ]]; then
    exit 0
fi

# テストファイルは対象外（一般的なテストファイルパターン）
if [[ "$FILE_PATH" == *".test."* ]] || [[ "$FILE_PATH" == *".spec."* ]] || [[ "$FILE_PATH" == *"_test."* ]] || [[ "$FILE_PATH" == *"test_"* ]] || [[ "$FILE_PATH" == *"/test/"* ]] || [[ "$FILE_PATH" == *"/tests/"* ]]; then
    exit 0
fi

# .docs/specification/ ディレクトリの存在確認
SPEC_DIR=".docs/specification"
if [ ! -d "$SPEC_DIR" ]; then
    # 仕様書ディレクトリが存在しない場合は警告のみ
    echo "[AI-SDD Warning] .docs/specification/ ディレクトリが存在しません。" >&2
    echo "仕様書なしでの実装はVibe Codingのリスクがあります。" >&2
    echo "/generate_spec コマンドで仕様書を作成することを推奨します。" >&2
    exit 0
fi

# 仕様書が1つも存在しない場合は警告
SPEC_COUNT=$(find "$SPEC_DIR" -name "*_spec.md" 2>/dev/null | wc -l)
if [ "$SPEC_COUNT" -eq 0 ]; then
    echo "[AI-SDD Warning] 仕様書が存在しません。" >&2
    echo "仕様書なしでの実装はVibe Codingのリスクがあります。" >&2
    echo "/generate_spec コマンドで仕様書を作成することを推奨します。" >&2
fi

# 正常終了（実装をブロックしない）
exit 0
