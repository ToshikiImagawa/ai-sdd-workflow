#!/bin/bash
# scan-existing-docs.sh
# Scan for existing PRD/spec/design documents
# Usage: scan-existing-docs.sh <feature-name>

set -e

FEATURE_NAME="$1"
if [ -z "$FEATURE_NAME" ]; then
    echo "[scan-existing-docs] ERROR: feature-name required" >&2
    exit 1
fi

# Environment variables (with defaults)
SDD_ROOT="${SDD_ROOT:-.sdd}"
SDD_REQUIREMENT_DIR="${SDD_REQUIREMENT_DIR:-requirement}"
SDD_SPECIFICATION_DIR="${SDD_SPECIFICATION_DIR:-specification}"
SDD_REQUIREMENT_PATH="${SDD_REQUIREMENT_PATH:-${SDD_ROOT}/${SDD_REQUIREMENT_DIR}}"
SDD_SPECIFICATION_PATH="${SDD_SPECIFICATION_PATH:-${SDD_ROOT}/${SDD_SPECIFICATION_DIR}}"
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Create cache directory
CACHE_DIR="${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor"
mkdir -p "$CACHE_DIR"

echo "[scan-existing-docs] Scanning for: ${FEATURE_NAME}" >&2
echo "[scan-existing-docs] SDD_ROOT: ${SDD_ROOT}" >&2
echo "[scan-existing-docs] SDD_REQUIREMENT_PATH: ${SDD_REQUIREMENT_PATH}" >&2
echo "[scan-existing-docs] SDD_SPECIFICATION_PATH: ${SDD_SPECIFICATION_PATH}" >&2

# Initialize results
PRD_EXISTS="false"
SPEC_EXISTS="false"
DESIGN_EXISTS="false"
PRD_PATH=""
SPEC_PATH=""
DESIGN_PATH=""
STRUCTURE="none"

# Check flat structure
FLAT_PRD="${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/${FEATURE_NAME}.md"
FLAT_SPEC="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${FEATURE_NAME}_spec.md"
FLAT_DESIGN="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${FEATURE_NAME}_design.md"

echo "[scan-existing-docs] Checking flat structure..." >&2
echo "[scan-existing-docs]   PRD: ${FLAT_PRD}" >&2
echo "[scan-existing-docs]   Spec: ${FLAT_SPEC}" >&2
echo "[scan-existing-docs]   Design: ${FLAT_DESIGN}" >&2

if [ -f "$FLAT_PRD" ] || [ -f "$FLAT_SPEC" ] || [ -f "$FLAT_DESIGN" ]; then
    STRUCTURE="flat"
    if [ -f "$FLAT_PRD" ]; then
        PRD_EXISTS="true"
        PRD_PATH="$FLAT_PRD"
        echo "[scan-existing-docs]   ✓ PRD found: ${FLAT_PRD}" >&2
    fi
    if [ -f "$FLAT_SPEC" ]; then
        SPEC_EXISTS="true"
        SPEC_PATH="$FLAT_SPEC"
        echo "[scan-existing-docs]   ✓ Spec found: ${FLAT_SPEC}" >&2
    fi
    if [ -f "$FLAT_DESIGN" ]; then
        DESIGN_EXISTS="true"
        DESIGN_PATH="$FLAT_DESIGN"
        echo "[scan-existing-docs]   ✓ Design found: ${FLAT_DESIGN}" >&2
    fi
fi

# Check hierarchical structure (if feature-name contains '/')
if [[ "$FEATURE_NAME" == */* ]]; then
    PARENT_FEATURE="${FEATURE_NAME%/*}"
    CHILD_FEATURE="${FEATURE_NAME##*/}"

    echo "[scan-existing-docs] Checking hierarchical structure..." >&2
    echo "[scan-existing-docs]   Parent: ${PARENT_FEATURE}, Child: ${CHILD_FEATURE}" >&2

    # Check child feature documents
    HIER_PRD="${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/${PARENT_FEATURE}/${CHILD_FEATURE}.md"
    HIER_SPEC="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${PARENT_FEATURE}/${CHILD_FEATURE}_spec.md"
    HIER_DESIGN="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${PARENT_FEATURE}/${CHILD_FEATURE}_design.md"

    echo "[scan-existing-docs]   Child PRD: ${HIER_PRD}" >&2
    echo "[scan-existing-docs]   Child Spec: ${HIER_SPEC}" >&2
    echo "[scan-existing-docs]   Child Design: ${HIER_DESIGN}" >&2

    if [ -f "$HIER_PRD" ] || [ -f "$HIER_SPEC" ] || [ -f "$HIER_DESIGN" ]; then
        STRUCTURE="hierarchical"
        if [ -f "$HIER_PRD" ]; then
            PRD_EXISTS="true"
            PRD_PATH="$HIER_PRD"
            echo "[scan-existing-docs]   ✓ Child PRD found: ${HIER_PRD}" >&2
        fi
        if [ -f "$HIER_SPEC" ]; then
            SPEC_EXISTS="true"
            SPEC_PATH="$HIER_SPEC"
            echo "[scan-existing-docs]   ✓ Child Spec found: ${HIER_SPEC}" >&2
        fi
        if [ -f "$HIER_DESIGN" ]; then
            DESIGN_EXISTS="true"
            DESIGN_PATH="$HIER_DESIGN"
            echo "[scan-existing-docs]   ✓ Child Design found: ${HIER_DESIGN}" >&2
        fi
    fi

    # Also check parent index documents
    PARENT_PRD="${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/${PARENT_FEATURE}/index.md"
    PARENT_SPEC="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${PARENT_FEATURE}/index_spec.md"
    PARENT_DESIGN="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${PARENT_FEATURE}/index_design.md"

    if [ -f "$PARENT_PRD" ]; then
        echo "[scan-existing-docs]   ℹ Parent PRD found: ${PARENT_PRD}" >&2
    fi
    if [ -f "$PARENT_SPEC" ]; then
        echo "[scan-existing-docs]   ℹ Parent Spec found: ${PARENT_SPEC}" >&2
    fi
    if [ -f "$PARENT_DESIGN" ]; then
        echo "[scan-existing-docs]   ℹ Parent Design found: ${PARENT_DESIGN}" >&2
    fi
else
    # Check if this might be a parent feature (check for index files)
    INDEX_PRD="${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/${FEATURE_NAME}/index.md"
    INDEX_SPEC="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${FEATURE_NAME}/index_spec.md"
    INDEX_DESIGN="${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/${FEATURE_NAME}/index_design.md"

    if [ -f "$INDEX_PRD" ] || [ -f "$INDEX_SPEC" ] || [ -f "$INDEX_DESIGN" ]; then
        STRUCTURE="hierarchical-parent"
        if [ -f "$INDEX_PRD" ]; then
            PRD_EXISTS="true"
            PRD_PATH="$INDEX_PRD"
            echo "[scan-existing-docs]   ✓ Parent PRD found: ${INDEX_PRD}" >&2
        fi
        if [ -f "$INDEX_SPEC" ]; then
            SPEC_EXISTS="true"
            SPEC_PATH="$INDEX_SPEC"
            echo "[scan-existing-docs]   ✓ Parent Spec found: ${INDEX_SPEC}" >&2
        fi
        if [ -f "$INDEX_DESIGN" ]; then
            DESIGN_EXISTS="true"
            DESIGN_PATH="$INDEX_DESIGN"
            echo "[scan-existing-docs]   ✓ Parent Design found: ${INDEX_DESIGN}" >&2
        fi
    fi
fi

# Output JSON
cat > "$CACHE_DIR/existing-docs.json" <<EOF
{
  "prd_exists": ${PRD_EXISTS},
  "spec_exists": ${SPEC_EXISTS},
  "design_exists": ${DESIGN_EXISTS},
  "prd_path": "${PRD_PATH}",
  "spec_path": "${SPEC_PATH}",
  "design_path": "${DESIGN_PATH}",
  "structure": "${STRUCTURE}",
  "feature_name": "${FEATURE_NAME}"
}
EOF

echo "[scan-existing-docs] Results saved to: ${CACHE_DIR}/existing-docs.json" >&2
echo "[scan-existing-docs] Structure: ${STRUCTURE}" >&2
echo "[scan-existing-docs] PRD: ${PRD_EXISTS}, Spec: ${SPEC_EXISTS}, Design: ${DESIGN_EXISTS}" >&2

# Determine case
if [ "$DESIGN_EXISTS" = "true" ] || [ "$SPEC_EXISTS" = "true" ]; then
    echo "[scan-existing-docs] Case: A (Existing documents)" >&2
else
    echo "[scan-existing-docs] Case: B (No documents, reverse-engineering needed)" >&2
fi
