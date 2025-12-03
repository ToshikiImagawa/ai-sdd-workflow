#!/bin/bash
# check-spec-exists.sh
# PreToolUse hook script
# Verifies specification existence before Edit/Write tool usage

# Get target file path from environment variable
# Claude Code passes TOOL_INPUT as JSON
# Use jq if available, otherwise fallback to grep/sed
if command -v jq &> /dev/null; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null)
else
    FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

# Exit if file path cannot be obtained
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Get repository root (if under git management)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
    # Use current directory if not a git repository
    REPO_ROOT="$(pwd)"
fi

# Determine if it's a source code file
# Files under .docs/ are excluded
if [[ "$FILE_PATH" == *".docs/"* ]] || [[ "$FILE_PATH" == *"/.docs/"* ]]; then
    exit 0
fi

# Configuration files etc. are excluded
if [[ "$FILE_PATH" == *".json" ]] || [[ "$FILE_PATH" == *".md" ]] || [[ "$FILE_PATH" == *".yml" ]] || [[ "$FILE_PATH" == *".yaml" ]]; then
    exit 0
fi

# Test files are excluded (common test file patterns)
# Jest: __tests__/, __mocks__/, *.test.*, *.spec.*
# Python: test_*, *_test.py, /tests/
# Storybook: *.stories.*
# E2E: /e2e/, /cypress/
if [[ "$FILE_PATH" == *".test."* ]] || [[ "$FILE_PATH" == *".spec."* ]] || \
   [[ "$FILE_PATH" == *"_test."* ]] || [[ "$FILE_PATH" == *"test_"* ]] || \
   [[ "$FILE_PATH" == *"/test/"* ]] || [[ "$FILE_PATH" == *"/tests/"* ]] || \
   [[ "$FILE_PATH" == *"/__tests__/"* ]] || [[ "$FILE_PATH" == *"/__mocks__/"* ]] || \
   [[ "$FILE_PATH" == *".stories."* ]] || \
   [[ "$FILE_PATH" == *"/e2e/"* ]] || [[ "$FILE_PATH" == *"/cypress/"* ]]; then
    exit 0
fi

# Check if .docs/specification/ directory exists (relative to repository root)
SPEC_DIR="${REPO_ROOT}/.docs/specification"
if [ ! -d "$SPEC_DIR" ]; then
    # Warning only if specification directory doesn't exist
    echo "[AI-SDD Warning] .docs/specification/ directory does not exist." >&2
    echo "Implementation without specifications carries Vibe Coding risks." >&2
    echo "Recommend creating specifications with /generate_spec command." >&2
    exit 0
fi

# Warning if no specifications exist
SPEC_COUNT=$(find "$SPEC_DIR" -name "*_spec.md" 2>/dev/null | wc -l)
if [ "$SPEC_COUNT" -eq 0 ]; then
    echo "[AI-SDD Warning] No specifications exist." >&2
    echo "Implementation without specifications carries Vibe Coding risks." >&2
    echo "Recommend creating specifications with /generate_spec command." >&2
fi

# Normal exit (does not block implementation)
exit 0
