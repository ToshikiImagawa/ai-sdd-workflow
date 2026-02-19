#!/bin/bash
set -euo pipefail

# SDD dependency visualization script

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
OUTPUT_FILE="${PROJECT_ROOT}/${SDD_ROOT}/.cache/index/dependency-graph.mmd"

# Execute CLI (pass all arguments)
sdd-cli visualize "$@" \
    --root "$SDD_ROOT" \
    --output "$OUTPUT_FILE"

# Export environment variables
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    echo "export SDD_DEPENDENCY_GRAPH=\"$OUTPUT_FILE\"" >> "$CLAUDE_ENV_FILE"
fi

echo "✓ Visualization completed" >&2
