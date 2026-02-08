#!/bin/bash
# init-structure.sh
# Static file operations for /sdd-init skill
# This script performs directory creation and template copying to reduce Claude's tool call overhead

set -euo pipefail

# Get project root
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
else
    PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi

# Read configuration from .sdd-config.json (must exist before running this script)
CONFIG_FILE="${PROJECT_ROOT}/.sdd-config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: .sdd-config.json not found. This script requires configuration file." >&2
    exit 1
fi

# Parse configuration (use jq if available, fallback to grep)
if command -v jq &> /dev/null; then
    SDD_ROOT=$(jq -r '.root // ".sdd"' "$CONFIG_FILE")
    SDD_REQUIREMENT_DIR=$(jq -r '.directories.requirement // "requirement"' "$CONFIG_FILE")
    SDD_SPECIFICATION_DIR=$(jq -r '.directories.specification // "specification"' "$CONFIG_FILE")
    SDD_TASK_DIR=$(jq -r '.directories.task // "task"' "$CONFIG_FILE")
    SDD_LANG=$(jq -r '.lang // "en"' "$CONFIG_FILE")
else
    SDD_ROOT=$(grep -o '"root"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_REQUIREMENT_DIR=$(grep -o '"requirement"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_SPECIFICATION_DIR=$(grep -o '"specification"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_TASK_DIR=$(grep -o '"task"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_LANG=$(grep -o '"lang"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')

    # Set defaults if parsing failed
    SDD_ROOT="${SDD_ROOT:-.sdd}"
    SDD_REQUIREMENT_DIR="${SDD_REQUIREMENT_DIR:-requirement}"
    SDD_SPECIFICATION_DIR="${SDD_SPECIFICATION_DIR:-specification}"
    SDD_TASK_DIR="${SDD_TASK_DIR:-task}"
    SDD_LANG="${SDD_LANG:-en}"
fi

# Paths
SDD_DIR="${PROJECT_ROOT}/${SDD_ROOT}"

# Plugin root (from CLAUDE_PLUGIN_ROOT environment variable)
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    # Fallback: detect from script location (for development)
    # This script is at: plugins/sdd-workflow/skills/sdd-init/scripts/init-structure.sh
    # Note: sdd-workflow-ja/skills is a symlink to sdd-workflow/skills
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # Go up 3 levels: scripts -> sdd-init -> skills -> sdd-workflow
    PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
fi

# --- Phase 1: Ensure .sdd root exists ---
echo "[init-structure] Ensuring ${SDD_ROOT}/ directory exists..." >&2

mkdir -p "$SDD_DIR"

echo "[init-structure] Root directory ready: ${SDD_ROOT}/" >&2
echo "[init-structure] Note: Subdirectories (${SDD_REQUIREMENT_DIR}, ${SDD_SPECIFICATION_DIR}, ${SDD_TASK_DIR}) will be created automatically when files are generated" >&2

# --- Phase 2: Copy templates (if not exist) ---
echo "[init-structure] Checking templates..." >&2

# Template source paths (from other skills)
# Note: CONSTITUTION.md is generated via /constitution init, not copied here
GENERATE_PRD_SKILL="${PLUGIN_ROOT}/skills/generate-prd"
GENERATE_SPEC_SKILL="${PLUGIN_ROOT}/skills/generate-spec"

# Template mappings
# Note: CONSTITUTION.md is NOT copied here - it should be generated via /constitution init
# which customizes the template based on project context
declare -A TEMPLATES=(
    ["${SDD_DIR}/PRD_TEMPLATE.md"]="${GENERATE_PRD_SKILL}/templates/${SDD_LANG}/prd_template.md"
    ["${SDD_DIR}/SPECIFICATION_TEMPLATE.md"]="${GENERATE_SPEC_SKILL}/templates/${SDD_LANG}/spec_template.md"
    ["${SDD_DIR}/DESIGN_DOC_TEMPLATE.md"]="${GENERATE_SPEC_SKILL}/templates/${SDD_LANG}/design_template.md"
)

COPIED_COUNT=0
SKIPPED_COUNT=0

for target in "${!TEMPLATES[@]}"; do
    source="${TEMPLATES[$target]}"

    if [ -f "$target" ]; then
        echo "[init-structure] Skipped (exists): $(basename "$target")" >&2
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    elif [ -f "$source" ]; then
        cp "$source" "$target"
        echo "[init-structure] Copied: $(basename "$target")" >&2
        COPIED_COUNT=$((COPIED_COUNT + 1))
    else
        echo "[init-structure] WARNING: Source template not found: $source" >&2
    fi
done

echo "[init-structure] Templates copied: $COPIED_COUNT, skipped: $SKIPPED_COUNT" >&2

# --- Phase 3: Cleanup ---
UPDATE_REQUIRED_FILE="${SDD_DIR}/UPDATE_REQUIRED.md"
if [ -f "$UPDATE_REQUIRED_FILE" ]; then
    rm -f "$UPDATE_REQUIRED_FILE"
    echo "[init-structure] Deleted: UPDATE_REQUIRED.md" >&2
fi

# --- Phase 4: Export environment variables to CLAUDE_ENV_FILE ---
# Note: These variables are already set by session-start.sh, but we ensure they're current
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    # Remove existing SDD_* variables to prevent duplicates
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        grep -v '^export SDD_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi

    # Write current values
    {
        echo "export SDD_ROOT=\"$SDD_ROOT\""
        echo "export SDD_REQUIREMENT_DIR=\"$SDD_REQUIREMENT_DIR\""
        echo "export SDD_SPECIFICATION_DIR=\"$SDD_SPECIFICATION_DIR\""
        echo "export SDD_TASK_DIR=\"$SDD_TASK_DIR\""
        echo "export SDD_REQUIREMENT_PATH=\"${SDD_ROOT}/${SDD_REQUIREMENT_DIR}\""
        echo "export SDD_SPECIFICATION_PATH=\"${SDD_ROOT}/${SDD_SPECIFICATION_DIR}\""
        echo "export SDD_TASK_PATH=\"${SDD_ROOT}/${SDD_TASK_DIR}\""
        echo "export SDD_LANG=\"$SDD_LANG\""
    } >> "$CLAUDE_ENV_FILE"

    echo "[init-structure] Environment variables exported to CLAUDE_ENV_FILE" >&2
fi

echo "[init-structure] Completed successfully" >&2
exit 0