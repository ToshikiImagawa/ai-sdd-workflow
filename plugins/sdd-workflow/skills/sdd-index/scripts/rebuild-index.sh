#!/bin/bash
set -euo pipefail

# SDD index rebuild script

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

# Check SDD directory existence
if [ ! -d "${PROJECT_ROOT}/${SDD_ROOT}" ]; then
    echo "Error: SDD root directory not found: ${SDD_ROOT}" >&2
    echo "Please run /sdd-init to initialize the SDD workflow." >&2
    exit 1
fi

# Build index
echo "Building SDD document index..." >&2
sdd-cli index --root "${SDD_ROOT}"

# Export environment variables
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    METADATA_FILE="${PROJECT_ROOT}/${SDD_ROOT}/.cache/index/metadata.json"
    if [ -f "$METADATA_FILE" ]; then
        echo "export SDD_INDEX_METADATA=\"$METADATA_FILE\"" >> "$CLAUDE_ENV_FILE"
    fi
fi

echo "✓ Index rebuild completed" >&2
