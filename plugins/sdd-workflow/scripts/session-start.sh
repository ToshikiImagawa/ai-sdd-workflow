#!/bin/bash
# session-start.sh
# SessionStart hook script
# Loads .sdd-config.json at session start (generates if not exists) and initializes environment variables

# Get project root
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
else
    PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi

# Path to .sdd-config.json
CONFIG_FILE="${PROJECT_ROOT}/.sdd-config.json"

# Default values
DOCS_ROOT=".sdd"
REQUIREMENT_DIR="requirement"
SPECIFICATION_DIR="specification"
TASK_DIR="task"

# Legacy structure detection and migration warning
LEGACY_DETECTED=false
LEGACY_DOCS_ROOT=""
LEGACY_REQUIREMENT=""
LEGACY_TASK=""

# Check for legacy structure only if .sdd-config.json doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    # Detect legacy docs root (.docs)
    if [ -d "${PROJECT_ROOT}/.docs" ] && [ ! -d "${PROJECT_ROOT}/.sdd" ]; then
        LEGACY_DETECTED=true
        LEGACY_DOCS_ROOT=".docs"
        DOCS_ROOT=".docs"
    fi

    # Detect legacy requirement directory (requirement-diagram)
    if [ -d "${PROJECT_ROOT}/${DOCS_ROOT}/requirement-diagram" ]; then
        LEGACY_DETECTED=true
        LEGACY_REQUIREMENT="requirement-diagram"
        REQUIREMENT_DIR="requirement-diagram"
    fi

    # Detect legacy task directory (review)
    if [ -d "${PROJECT_ROOT}/${DOCS_ROOT}/review" ] && [ ! -d "${PROJECT_ROOT}/${DOCS_ROOT}/task" ]; then
        LEGACY_DETECTED=true
        LEGACY_TASK="review"
        TASK_DIR="review"
    fi

    # Show warning if legacy structure detected
    if [ "$LEGACY_DETECTED" = true ]; then
        echo "[AI-SDD Migration] Legacy directory structure detected." >&2
        echo "" >&2
        echo "Detected legacy structure:" >&2
        [ -n "$LEGACY_DOCS_ROOT" ] && echo "  - Docs root: .docs → .sdd (recommended)" >&2
        [ -n "$LEGACY_REQUIREMENT" ] && echo "  - Requirement: requirement-diagram → requirement (recommended)" >&2
        [ -n "$LEGACY_TASK" ] && echo "  - Task log: review → task (recommended)" >&2
        echo "" >&2
        echo "Your current structure will continue to work, but you can migrate with:" >&2
        echo "  /sdd_migrate - Migrate to new structure or generate compatibility config" >&2
        echo "" >&2
    else
        # No legacy structure detected and no .sdd-config.json exists, auto-generate default config
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
        echo "[AI-SDD] .sdd-config.json auto-generated." >&2
    fi
fi

# Load configuration if file exists
if [ -f "$CONFIG_FILE" ]; then
    if command -v jq &> /dev/null; then
        # jq is available
        CONFIGURED_DOCS_ROOT=$(jq -r '.docsRoot // empty' "$CONFIG_FILE" 2>/dev/null)
        CONFIGURED_REQUIREMENT=$(jq -r '.directories.requirement // empty' "$CONFIG_FILE" 2>/dev/null)
        CONFIGURED_SPECIFICATION=$(jq -r '.directories.specification // empty' "$CONFIG_FILE" 2>/dev/null)
        CONFIGURED_TASK=$(jq -r '.directories.task // empty' "$CONFIG_FILE" 2>/dev/null)

        # Override with configured values if present
        [ -n "$CONFIGURED_DOCS_ROOT" ] && DOCS_ROOT="$CONFIGURED_DOCS_ROOT"
        [ -n "$CONFIGURED_REQUIREMENT" ] && REQUIREMENT_DIR="$CONFIGURED_REQUIREMENT"
        [ -n "$CONFIGURED_SPECIFICATION" ] && SPECIFICATION_DIR="$CONFIGURED_SPECIFICATION"
        [ -n "$CONFIGURED_TASK" ] && TASK_DIR="$CONFIGURED_TASK"
    else
        # jq not available, use grep for basic parsing
        CONFIGURED_DOCS_ROOT=$(grep -o '"docsRoot"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        CONFIGURED_REQUIREMENT=$(grep -o '"requirement"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        CONFIGURED_SPECIFICATION=$(grep -o '"specification"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        CONFIGURED_TASK=$(grep -o '"task"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')

        # Override if configured
        [ -n "$CONFIGURED_DOCS_ROOT" ] && DOCS_ROOT="$CONFIGURED_DOCS_ROOT"
        [ -n "$CONFIGURED_REQUIREMENT" ] && REQUIREMENT_DIR="$CONFIGURED_REQUIREMENT"
        [ -n "$CONFIGURED_SPECIFICATION" ] && SPECIFICATION_DIR="$CONFIGURED_SPECIFICATION"
        [ -n "$CONFIGURED_TASK" ] && TASK_DIR="$CONFIGURED_TASK"
    fi
fi

# Write to environment file (if provided by Claude Code)
if [ -n "$CLAUDE_ENV_FILE" ]; then
    # Remove existing SDD_* environment variables (prevent duplicate writes)
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        # Use temp file to exclude lines starting with SDD_
        grep -v '^export SDD_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi

    # Base directory names
    echo "export SDD_DOCS_ROOT=\"$DOCS_ROOT\"" >> "$CLAUDE_ENV_FILE"
    echo "export SDD_REQUIREMENT_DIR=\"$REQUIREMENT_DIR\"" >> "$CLAUDE_ENV_FILE"
    echo "export SDD_SPECIFICATION_DIR=\"$SPECIFICATION_DIR\"" >> "$CLAUDE_ENV_FILE"
    echo "export SDD_TASK_DIR=\"$TASK_DIR\"" >> "$CLAUDE_ENV_FILE"

    # Full paths (for convenience)
    echo "export SDD_REQUIREMENT_PATH=\"${DOCS_ROOT}/${REQUIREMENT_DIR}\"" >> "$CLAUDE_ENV_FILE"
    echo "export SDD_SPECIFICATION_PATH=\"${DOCS_ROOT}/${SPECIFICATION_DIR}\"" >> "$CLAUDE_ENV_FILE"
    echo "export SDD_TASK_PATH=\"${DOCS_ROOT}/${TASK_DIR}\"" >> "$CLAUDE_ENV_FILE"
fi

exit 0
