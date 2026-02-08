#!/bin/bash
# find-design-docs.sh
# Find design documents and related files for /check-spec
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

SPECIFICATION_PATH="${PROJECT_ROOT}/${SDD_ROOT}/${SPECIFICATION_DIR}"

# Target feature name (optional argument)
FEATURE_NAME="${1:-}"

# Output directory
OUTPUT_DIR="${PROJECT_ROOT}/.sdd/.cache/check-spec"
mkdir -p "$OUTPUT_DIR"

# --- Phase 1: Find design documents ---
echo "[find-design-docs] Scanning design documents..." >&2

DESIGN_FILES="${OUTPUT_DIR}/design_files.txt"
SPEC_FILES="${OUTPUT_DIR}/spec_files.txt"

if [ ! -d "$SPECIFICATION_PATH" ]; then
    echo "[find-design-docs] ERROR: Specification directory not found: ${SPECIFICATION_PATH}" >&2
    exit 1
fi

if [ -n "$FEATURE_NAME" ]; then
    # Specific feature: search for matching design doc
    echo "[find-design-docs] Searching for feature: ${FEATURE_NAME}" >&2

    # Try flat structure first
    FLAT_DESIGN="${SPECIFICATION_PATH}/${FEATURE_NAME}_design.md"
    FLAT_SPEC="${SPECIFICATION_PATH}/${FEATURE_NAME}_spec.md"

    # Try hierarchical structure
    HIER_DESIGN="${SPECIFICATION_PATH}/${FEATURE_NAME}/index_design.md"
    HIER_SPEC="${SPECIFICATION_PATH}/${FEATURE_NAME}/index_spec.md"

    # Check which exists
    if [ -f "$FLAT_DESIGN" ]; then
        echo "$FLAT_DESIGN" > "$DESIGN_FILES"
        [ -f "$FLAT_SPEC" ] && echo "$FLAT_SPEC" > "$SPEC_FILES"
        echo "[find-design-docs] Found flat structure: ${FEATURE_NAME}_design.md" >&2
    elif [ -f "$HIER_DESIGN" ]; then
        echo "$HIER_DESIGN" > "$DESIGN_FILES"
        [ -f "$HIER_SPEC" ] && echo "$HIER_SPEC" > "$SPEC_FILES"
        echo "[find-design-docs] Found hierarchical structure: ${FEATURE_NAME}/index_design.md" >&2
    else
        # Search for partial matches
        find "$SPECIFICATION_PATH" -type f -name "*${FEATURE_NAME}*_design.md" | sort > "$DESIGN_FILES"
        find "$SPECIFICATION_PATH" -type f -name "*${FEATURE_NAME}*_spec.md" | sort > "$SPEC_FILES"

        if [ ! -s "$DESIGN_FILES" ]; then
            echo "[find-design-docs] WARNING: No design document found for: ${FEATURE_NAME}" >&2
        else
            echo "[find-design-docs] Found $(wc -l < "$DESIGN_FILES" | tr -d ' ') matching design file(s)" >&2
        fi
    fi
else
    # All design documents
    echo "[find-design-docs] Searching for all design documents..." >&2
    find "$SPECIFICATION_PATH" -type f -name "*_design.md" | sort > "$DESIGN_FILES"
    find "$SPECIFICATION_PATH" -type f -name "*_spec.md" | sort > "$SPEC_FILES"

    DESIGN_COUNT=$(wc -l < "$DESIGN_FILES" | tr -d ' ')
    SPEC_COUNT=$(wc -l < "$SPEC_FILES" | tr -d ' ')

    echo "[find-design-docs] Found ${DESIGN_COUNT} design documents" >&2
    echo "[find-design-docs] Found ${SPEC_COUNT} specification documents" >&2
fi

# --- Phase 2: Generate file mapping ---
# For each design doc, find corresponding spec and implementation
MAPPING_FILE="${OUTPUT_DIR}/file_mapping.json"
echo "{" > "$MAPPING_FILE"
echo "  \"design_documents\": [" >> "$MAPPING_FILE"

FIRST=true
while IFS= read -r design_file; do
    [ -z "$design_file" ] && continue

    # Extract feature name from design file
    BASENAME=$(basename "$design_file" "_design.md")
    DIRNAME=$(dirname "$design_file")

    # Find corresponding spec
    SPEC_FILE=""
    if [ -f "${DIRNAME}/${BASENAME}_spec.md" ]; then
        SPEC_FILE="${DIRNAME}/${BASENAME}_spec.md"
    fi

    # Add to JSON
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        echo "," >> "$MAPPING_FILE"
    fi

    cat >> "$MAPPING_FILE" << EOF
    {
      "design": "${design_file}",
      "spec": "${SPEC_FILE}",
      "feature_name": "${BASENAME}"
    }
EOF
done < "$DESIGN_FILES"

echo "" >> "$MAPPING_FILE"
echo "  ]" >> "$MAPPING_FILE"
echo "}" >> "$MAPPING_FILE"

echo "[find-design-docs] File mapping generated" >&2

# --- Phase 3: Export to CLAUDE_ENV_FILE ---
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    # Remove existing CHECK_SPEC_* variables
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        grep -v '^export CHECK_SPEC_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi

    # Write metadata
    {
        echo "export CHECK_SPEC_CACHE_DIR=\"${OUTPUT_DIR}\""
        echo "export CHECK_SPEC_DESIGN_FILES=\"${DESIGN_FILES}\""
        echo "export CHECK_SPEC_SPEC_FILES=\"${SPEC_FILES}\""
        echo "export CHECK_SPEC_MAPPING=\"${MAPPING_FILE}\""
    } >> "$CLAUDE_ENV_FILE"

    echo "[find-design-docs] Environment variables exported to CLAUDE_ENV_FILE" >&2
fi

echo "[find-design-docs] Scan complete" >&2
echo "[find-design-docs] Cache location: ${OUTPUT_DIR}" >&2
exit 0
