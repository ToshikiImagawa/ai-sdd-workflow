#!/bin/bash
# validate-files.sh
# Scan specification and requirement files for /constitution validate
# Reduces Claude's Glob/Grep overhead by pre-scanning file structure

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

# Parse paths
if command -v jq &> /dev/null; then
    SDD_ROOT=$(jq -r '.root // ".sdd"' "$CONFIG_FILE")
    REQUIREMENT_DIR=$(jq -r '.directories.requirement // "requirement"' "$CONFIG_FILE")
    SPECIFICATION_DIR=$(jq -r '.directories.specification // "specification"' "$CONFIG_FILE")
else
    SDD_ROOT=$(grep -o '"root"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    REQUIREMENT_DIR=$(grep -o '"requirement"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SPECIFICATION_DIR=$(grep -o '"specification"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_ROOT="${SDD_ROOT:-.sdd}"
    REQUIREMENT_DIR="${REQUIREMENT_DIR:-requirement}"
    SPECIFICATION_DIR="${SPECIFICATION_DIR:-specification}"
fi

REQUIREMENT_PATH="${PROJECT_ROOT}/${SDD_ROOT}/${REQUIREMENT_DIR}"
SPECIFICATION_PATH="${PROJECT_ROOT}/${SDD_ROOT}/${SPECIFICATION_DIR}"

# Output directory
OUTPUT_DIR="${PROJECT_ROOT}/.sdd/.cache/constitution"
mkdir -p "$OUTPUT_DIR"

# --- Phase 1: Scan requirement files ---
echo "[validate-files] Scanning requirement files..." >&2

REQUIREMENT_FILES="${OUTPUT_DIR}/requirement_files.txt"

if [ -d "$REQUIREMENT_PATH" ]; then
    find "$REQUIREMENT_PATH" -type f -name "*.md" | sort > "$REQUIREMENT_FILES"
    REQUIREMENT_COUNT=$(wc -l < "$REQUIREMENT_FILES" | tr -d ' ')
    echo "[validate-files] Found ${REQUIREMENT_COUNT} requirement files" >&2
else
    echo "[validate-files] Requirement directory not found: ${REQUIREMENT_PATH}" >&2
fi

# --- Phase 2: Scan specification files ---
echo "[validate-files] Scanning specification files..." >&2

SPEC_FILES="${OUTPUT_DIR}/spec_files.txt"
DESIGN_FILES="${OUTPUT_DIR}/design_files.txt"

if [ -d "$SPECIFICATION_PATH" ]; then
    find "$SPECIFICATION_PATH" -type f -name "*_spec.md" | sort > "$SPEC_FILES"
    find "$SPECIFICATION_PATH" -type f -name "*_design.md" | sort > "$DESIGN_FILES"

    SPEC_COUNT=$(wc -l < "$SPEC_FILES" | tr -d ' ')
    DESIGN_COUNT=$(wc -l < "$DESIGN_FILES" | tr -d ' ')

    echo "[validate-files] Found ${SPEC_COUNT} specification files" >&2
    echo "[validate-files] Found ${DESIGN_COUNT} design files" >&2
else
    echo "[validate-files] Specification directory not found: ${SPECIFICATION_PATH}" >&2
fi

# --- Phase 3: Generate summary ---
SUMMARY_FILE="${OUTPUT_DIR}/scan_summary.json"
cat > "$SUMMARY_FILE" << EOF
{
  "scanned_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "requirement_files": ${REQUIREMENT_COUNT:-0},
  "spec_files": ${SPEC_COUNT:-0},
  "design_files": ${DESIGN_COUNT:-0},
  "total_files": $((${REQUIREMENT_COUNT:-0} + ${SPEC_COUNT:-0} + ${DESIGN_COUNT:-0}))
}
EOF

echo "[validate-files] Summary: $(cat "$SUMMARY_FILE")" >&2

# --- Phase 4: Export to CLAUDE_ENV_FILE ---
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    # Remove existing CONSTITUTION_* variables
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        grep -v '^export CONSTITUTION_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi

    # Write metadata
    {
        echo "export CONSTITUTION_CACHE_DIR=\"${OUTPUT_DIR}\""
        echo "export CONSTITUTION_REQUIREMENT_FILES=\"${REQUIREMENT_FILES}\""
        echo "export CONSTITUTION_SPEC_FILES=\"${SPEC_FILES}\""
        echo "export CONSTITUTION_DESIGN_FILES=\"${DESIGN_FILES}\""
        echo "export CONSTITUTION_SUMMARY=\"${SUMMARY_FILE}\""
    } >> "$CLAUDE_ENV_FILE"

    echo "[validate-files] Environment variables exported to CLAUDE_ENV_FILE" >&2
fi

echo "[validate-files] Scan complete" >&2
echo "[validate-files] Cache location: ${OUTPUT_DIR}" >&2
exit 0
