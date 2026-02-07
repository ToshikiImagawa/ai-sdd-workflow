#!/bin/bash
# prepare-prd.sh
# Prepare templates and references for /generate-prd skill
# Reduces Claude's Read tool calls by pre-loading necessary files

set -euo pipefail

# Get project root
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
else
    PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi

# Read configuration
CONFIG_FILE="${PROJECT_ROOT}/.sdd-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: .sdd-config.json not found" >&2
    exit 1
fi

# Parse SDD_LANG
if command -v jq &> /dev/null; then
    SDD_LANG=$(jq -r '.lang // "en"' "$CONFIG_FILE")
    SDD_ROOT=$(jq -r '.root // ".sdd"' "$CONFIG_FILE")
else
    SDD_LANG=$(grep -o '"lang"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_ROOT=$(grep -o '"root"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_LANG="${SDD_LANG:-en}"
    SDD_ROOT="${SDD_ROOT:-.sdd}"
fi

# Plugin root
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PLUGIN_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
fi

SKILL_DIR="${PLUGIN_ROOT}/skills/generate-prd"

# Output directory for Claude to read
OUTPUT_DIR="${PROJECT_ROOT}/.sdd/.cache/generate-prd"
mkdir -p "$OUTPUT_DIR"

# --- Phase 1: Template Preparation ---
echo "[prepare-prd] Preparing templates..." >&2

# Check project template first
PROJECT_TEMPLATE="${PROJECT_ROOT}/${SDD_ROOT}/PRD_TEMPLATE.md"
SKILL_TEMPLATE="${SKILL_DIR}/templates/${SDD_LANG}/prd_template.md"

if [ -f "$PROJECT_TEMPLATE" ]; then
    cp "$PROJECT_TEMPLATE" "$OUTPUT_DIR/prd_template.md"
    echo "[prepare-prd] Using project template: ${SDD_ROOT}/PRD_TEMPLATE.md" >&2
elif [ -f "$SKILL_TEMPLATE" ]; then
    cp "$SKILL_TEMPLATE" "$OUTPUT_DIR/prd_template.md"
    echo "[prepare-prd] Using skill template: templates/${SDD_LANG}/prd_template.md" >&2
else
    echo "[prepare-prd] ERROR: No template found" >&2
    exit 1
fi

# --- Phase 2: Copy Reference Files ---
echo "[prepare-prd] Copying reference files..." >&2

REFERENCES_DIR="${SKILL_DIR}/references"
if [ -d "$REFERENCES_DIR" ]; then
    cp -r "$REFERENCES_DIR" "$OUTPUT_DIR/"
    echo "[prepare-prd] Reference files copied" >&2
fi

# --- Phase 3: Export metadata to CLAUDE_ENV_FILE ---
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    # Remove existing GENERATE_PRD_* variables
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        grep -v '^export GENERATE_PRD_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi

    # Write metadata
    {
        echo "export GENERATE_PRD_CACHE_DIR=\"${OUTPUT_DIR}\""
        echo "export GENERATE_PRD_TEMPLATE=\"${OUTPUT_DIR}/prd_template.md\""
        echo "export GENERATE_PRD_REFERENCES=\"${OUTPUT_DIR}/references\""
    } >> "$CLAUDE_ENV_FILE"

    echo "[prepare-prd] Environment variables exported to CLAUDE_ENV_FILE" >&2
fi

echo "[prepare-prd] Preparation complete" >&2
echo "[prepare-prd] Cache location: ${OUTPUT_DIR}" >&2
exit 0
