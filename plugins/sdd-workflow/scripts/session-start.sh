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

    # If legacy structure detected
    if [ "$LEGACY_DETECTED" = true ]; then
        # Auto-generate .sdd-config.json with legacy values
        cat > "$CONFIG_FILE" << EOF
{
  "root": "${DOCS_ROOT}",
  "directories": {
    "requirement": "${REQUIREMENT_DIR}",
    "specification": "${SPECIFICATION_DIR}",
    "task": "${TASK_DIR}"
  }
}
EOF
        echo "[AI-SDD Migration] Legacy directory structure detected." >&2
        echo "" >&2
        echo "Detected legacy structure:" >&2
        [ -n "$LEGACY_DOCS_ROOT" ] && echo "  - Root directory: .docs" >&2
        [ -n "$LEGACY_REQUIREMENT" ] && echo "  - Requirement: requirement-diagram" >&2
        [ -n "$LEGACY_TASK" ] && echo "  - Task log: review" >&2
        echo "" >&2
        echo ".sdd-config.json auto-generated based on legacy structure." >&2
        echo "To migrate to new structure, run:" >&2
        echo "  /sdd_migrate - Migrate to new structure" >&2
        echo "" >&2
    else
        # No legacy structure detected and no .sdd-config.json exists, auto-generate default config
        cat > "$CONFIG_FILE" << 'EOF'
{
  "root": ".sdd",
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
        CONFIGURED_DOCS_ROOT=$(jq -r '.root // empty' "$CONFIG_FILE" 2>/dev/null)
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
        CONFIGURED_DOCS_ROOT=$(grep -o '"root"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
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

# Environment variable output
# If CLAUDE_ENV_FILE is provided by Claude Code, write to it
# Otherwise output to stdout (for Claude Code to read)
output_env_vars() {
    echo "export SDD_ROOT=\"$DOCS_ROOT\""
    echo "export SDD_REQUIREMENT_DIR=\"$REQUIREMENT_DIR\""
    echo "export SDD_SPECIFICATION_DIR=\"$SPECIFICATION_DIR\""
    echo "export SDD_TASK_DIR=\"$TASK_DIR\""
    echo "export SDD_REQUIREMENT_PATH=\"${DOCS_ROOT}/${REQUIREMENT_DIR}\""
    echo "export SDD_SPECIFICATION_PATH=\"${DOCS_ROOT}/${SPECIFICATION_DIR}\""
    echo "export SDD_TASK_PATH=\"${DOCS_ROOT}/${TASK_DIR}\""
}

if [ -n "$CLAUDE_ENV_FILE" ]; then
    # Remove existing SDD_* environment variables (prevent duplicate writes)
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        # Use temp file to exclude lines starting with SDD_
        grep -v '^export SDD_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi
    output_env_vars >> "$CLAUDE_ENV_FILE"
else
    # If CLAUDE_ENV_FILE is not available, output to stdout
    # Claude Code hooks read stdout and interpret as environment variables
    output_env_vars
fi

# Version comparison function (compare major.minor only, ignore patch)
# Return: 0 = same or newer, 1 = older
compare_major_minor() {
    local plugin_version
    local project_version
    plugin_version="$1"
    project_version="$2"

    # Extract major and minor using parameter expansion (no subshell)
    local plugin_major
    local plugin_minor
    local project_major
    local project_minor
    plugin_major="${plugin_version%%.*}"
    plugin_minor="${plugin_version#*.}"; plugin_minor="${plugin_minor%%.*}"
    project_major="${project_version%%.*}"
    project_minor="${project_version#*.}"; project_minor="${project_minor%%.*}"

    # Compare as numbers
    if [ "$project_major" -lt "$plugin_major" ] 2>/dev/null; then
        return 1
    elif [ "$project_major" -eq "$plugin_major" ] && [ "$project_minor" -lt "$plugin_minor" ] 2>/dev/null; then
        return 1
    fi
    return 0
}

# AI-SDD-PRINCIPLES.md version check
PRINCIPLES_FILE="${PROJECT_ROOT}/${DOCS_ROOT}/AI-SDD-PRINCIPLES.md"
SDD_DIR="${PROJECT_ROOT}/${DOCS_ROOT}"
PLUGIN_JSON="${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"

# Only check if .sdd/ directory exists
if [ -d "$SDD_DIR" ]; then
    SHOW_WARNING=false
    WARNING_REASON=""
    PLUGIN_VERSION=""
    PROJECT_VERSION=""

    # Get plugin version
    if [ -f "$PLUGIN_JSON" ]; then
        if command -v jq &> /dev/null; then
            PLUGIN_VERSION=$(jq -r '.version // empty' "$PLUGIN_JSON" 2>/dev/null)
        else
            PLUGIN_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$PLUGIN_JSON" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
        fi
    fi

    if [ ! -f "$PRINCIPLES_FILE" ]; then
        # AI-SDD-PRINCIPLES.md doesn't exist
        SHOW_WARNING=true
        WARNING_REASON="missing"
    elif [ -n "$PLUGIN_VERSION" ]; then
        # Get version from AI-SDD-PRINCIPLES.md (frontmatter)
        PROJECT_VERSION=$(grep -A5 '^---$' "$PRINCIPLES_FILE" 2>/dev/null | grep '^version:' | sed 's/version:[[:space:]]*["'\'']\?\([^"'\'']*\)["'\'']\?/\1/' | tr -d ' ')

        if [ -z "$PROJECT_VERSION" ]; then
            # No version info (old format)
            SHOW_WARNING=true
            WARNING_REASON="no_version"
        elif ! compare_major_minor "$PLUGIN_VERSION" "$PROJECT_VERSION"; then
            # Version is outdated
            SHOW_WARNING=true
            WARNING_REASON="outdated"
        fi
    fi

    if [ "$SHOW_WARNING" = true ]; then
        echo "" >&2
        case "$WARNING_REASON" in
            "missing")
                echo "[AI-SDD Warning] AI-SDD-PRINCIPLES.md not found." >&2
                echo "" >&2
                echo "This project may have been initialized with plugin v2.2.0 or earlier." >&2
                ;;
            "no_version")
                echo "[AI-SDD Warning] AI-SDD-PRINCIPLES.md has no version info." >&2
                echo "" >&2
                echo "Old format AI-SDD-PRINCIPLES.md detected." >&2
                ;;
            "outdated")
                echo "[AI-SDD Warning] AI-SDD-PRINCIPLES.md version is outdated." >&2
                echo "" >&2
                echo "  Plugin version: v${PLUGIN_VERSION}" >&2
                echo "  Project version: v${PROJECT_VERSION}" >&2
                ;;
        esac
        echo "" >&2
        echo "Run the following command to update:" >&2
        echo "  /sdd_init" >&2
        echo "" >&2
        echo "This will:" >&2
        echo "  - Update .sdd/AI-SDD-PRINCIPLES.md" >&2
        echo "  - Update AI-SDD section in CLAUDE.md" >&2
        echo "" >&2
    fi
fi

exit 0