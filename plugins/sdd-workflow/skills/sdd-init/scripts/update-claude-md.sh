#!/bin/bash
# update-claude-md.sh
# Automatically update CLAUDE.md with AI-SDD Instructions section

set -euo pipefail

# ============================================================================
# Environment Variables
# ============================================================================

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Plugin root (from CLAUDE_PLUGIN_ROOT environment variable)
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    # Fallback: detect from script location (for development)
    # This script is at: plugins/sdd-workflow/skills/sdd-init/scripts/update-claude-md.sh
    # Note: sdd-workflow-ja/skills is a symlink to sdd-workflow/skills
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # Go up 3 levels: scripts -> sdd-init -> skills -> sdd-workflow
    PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
fi

SDD_LANG="${SDD_LANG:-en}"

# ============================================================================
# Utility Functions
# ============================================================================

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Error handling
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# ============================================================================
# Main Processing
# ============================================================================

main() {
    # 1. Validate prerequisites
    if ! command_exists jq; then
        error_exit "jq command not found. Please install jq: brew install jq"
    fi

    # 2. Get plugin version
    PLUGIN_JSON="${PLUGIN_ROOT}/.claude-plugin/plugin.json"
    if [ ! -f "$PLUGIN_JSON" ]; then
        error_exit "plugin.json not found at: $PLUGIN_JSON"
    fi

    PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_JSON")
    if [ -z "$PLUGIN_VERSION" ] || [ "$PLUGIN_VERSION" = "null" ]; then
        error_exit "Failed to read version from plugin.json"
    fi

    # 3. Load template and replace version
    TEMPLATE_FILE="${PLUGIN_ROOT}/skills/sdd-init/templates/${SDD_LANG}/claude_md_template.md"
    if [ ! -f "$TEMPLATE_FILE" ]; then
        error_exit "Template file not found at: $TEMPLATE_FILE"
    fi

    CONTENT=$(sed "s/{PLUGIN_VERSION}/$PLUGIN_VERSION/g" "$TEMPLATE_FILE")

    # 4. Determine operation
    CLAUDE_MD="${PROJECT_ROOT}/CLAUDE.md"

    if [ ! -f "$CLAUDE_MD" ]; then
        # Case 1: Create new CLAUDE.md
        echo "$CONTENT" > "$CLAUDE_MD"
        echo "✓ Created CLAUDE.md with AI-SDD Instructions (v${PLUGIN_VERSION})"
    elif ! grep -q "## AI-SDD Instructions" "$CLAUDE_MD"; then
        # Case 2: Append section
        echo "" >> "$CLAUDE_MD"
        echo "$CONTENT" >> "$CLAUDE_MD"
        echo "✓ Appended AI-SDD Instructions section (v${PLUGIN_VERSION})"
    else
        # Case 3: Update existing section
        # Extract current version from section title
        CURRENT_VERSION=$(grep "## AI-SDD Instructions" "$CLAUDE_MD" | sed -n 's/.*v\([0-9.]*\).*/\1/p' | head -n 1)

        if [ -z "$CURRENT_VERSION" ]; then
            # No version found in title, treat as old version
            CURRENT_VERSION="unknown"
        fi

        if [ "$CURRENT_VERSION" != "$PLUGIN_VERSION" ]; then
            # Replace section (from "## AI-SDD Instructions" to next "## " or EOF)
            # Use a temporary file to store the new content
            TEMP_CONTENT="${CLAUDE_MD}.content.tmp"
            echo "$CONTENT" > "$TEMP_CONTENT"

            awk '
                BEGIN { in_section=0; content_printed=0 }
                /^## AI-SDD Instructions/ {
                    if (!in_section) {
                        in_section=1
                        # Print the new content from temp file
                        while ((getline line < "'"$TEMP_CONTENT"'") > 0) {
                            print line
                        }
                        close("'"$TEMP_CONTENT"'")
                        content_printed=1
                    }
                    next
                }
                /^## / && in_section {
                    in_section=0
                }
                !in_section {
                    print
                }
            ' "$CLAUDE_MD" > "${CLAUDE_MD}.tmp"

            rm -f "$TEMP_CONTENT"
            mv "${CLAUDE_MD}.tmp" "$CLAUDE_MD"
            echo "✓ Updated AI-SDD Instructions section (v${CURRENT_VERSION} → v${PLUGIN_VERSION})"
        else
            echo "✓ AI-SDD Instructions section is up to date (v${PLUGIN_VERSION})"
        fi
    fi

    exit 0
}

# ============================================================================
# Execute
# ============================================================================

main "$@"
