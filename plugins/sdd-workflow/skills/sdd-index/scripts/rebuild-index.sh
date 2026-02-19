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
    # Calculate cache directory path using Python (GitHub Copilot-style naming)
    CACHE_DIR=$(python3 -c "
import hashlib
from pathlib import Path
project_root = Path('${PROJECT_ROOT}').resolve()
project_name = project_root.name
project_hash = hashlib.sha256(project_root.as_posix().encode()).hexdigest()[:8]
cache_dir = Path.home() / '.cache' / 'sdd-cli' / f'{project_name}.{project_hash}'
print(cache_dir)
")
    METADATA_FILE="${CACHE_DIR}/metadata.json"
    if [ -f "$METADATA_FILE" ]; then
        echo "export SDD_INDEX_METADATA=\"$METADATA_FILE\"" >> "$CLAUDE_ENV_FILE"
    fi
    echo "export SDD_CACHE_DIR=\"$CACHE_DIR\"" >> "$CLAUDE_ENV_FILE"
fi

echo "✓ Index rebuild completed" >&2
