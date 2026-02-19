#!/bin/bash
set -euo pipefail

# SDD document search script

# Get environment variables
SDD_ROOT="${SDD_ROOT:-.sdd}"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Check CLI existence
if ! command -v sdd-cli &> /dev/null; then
    echo "Error: sdd-cli not found." >&2
    echo "Please install the CLI tool from the plugin directory:" >&2
    echo "  cd \${CLAUDE_PLUGIN_ROOT}/cli && uv pip install -e ." >&2
    exit 1
fi

# Check index existence
INDEX_DB="${PROJECT_ROOT}/${SDD_ROOT}/.cache/index/index.db"
if [ ! -f "$INDEX_DB" ]; then
    echo "Error: Index not found at $INDEX_DB" >&2
    echo "Please run /sdd-index to build the index first." >&2
    exit 1
fi

# Output file path
OUTPUT_FILE="${PROJECT_ROOT}/${SDD_ROOT}/.cache/index/search-results.json"

# Execute CLI (pass all arguments)
sdd-cli search "$@" \
    --root "$SDD_ROOT" \
    --format json \
    --output "$OUTPUT_FILE"

# Export environment variables
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    echo "export SDD_SEARCH_RESULTS=\"$OUTPUT_FILE\"" >> "$CLAUDE_ENV_FILE"
    # Save search query if first argument is a query
    if [ $# -gt 0 ] && [[ ! "$1" =~ ^-- ]]; then
        echo "export SDD_SEARCH_QUERY=\"$1\"" >> "$CLAUDE_ENV_FILE"
    fi
fi

echo "✓ Search completed" >&2
