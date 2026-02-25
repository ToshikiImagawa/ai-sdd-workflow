#!/bin/bash
# scan-documents.sh
# Scan AI-SDD documents for Front Matter presence
# Used by /recommend-front-matter skill

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
    TASK_DIR=$(jq -r '.directories.task // "task"' "$CONFIG_FILE")
    SDD_LANG=$(jq -r '.lang // "en"' "$CONFIG_FILE")
else
    SDD_ROOT=$(grep -o '"root"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    REQUIREMENT_DIR=$(grep -o '"requirement"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SPECIFICATION_DIR=$(grep -o '"specification"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    TASK_DIR=$(grep -o '"task"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    SDD_LANG=$(grep -o '"lang"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"\([^"]*\)"$/\1/')

    # Set defaults if parsing failed
    SDD_ROOT="${SDD_ROOT:-.sdd}"
    REQUIREMENT_DIR="${REQUIREMENT_DIR:-requirement}"
    SPECIFICATION_DIR="${SPECIFICATION_DIR:-specification}"
    TASK_DIR="${TASK_DIR:-task}"
    SDD_LANG="${SDD_LANG:-en}"
fi

# Paths
SDD_DIR="${PROJECT_ROOT}/${SDD_ROOT}"
REQUIREMENT_PATH="${SDD_DIR}/${REQUIREMENT_DIR}"
SPECIFICATION_PATH="${SDD_DIR}/${SPECIFICATION_DIR}"
TASK_PATH="${SDD_DIR}/${TASK_DIR}"

# Output directory
OUTPUT_DIR="${SDD_DIR}/.cache/recommend-front-matter"
mkdir -p "$OUTPUT_DIR"

# --- Helper Functions ---

# Check if file has Front Matter
has_front_matter() {
    local file="$1"

    # Check if first line is '---'
    if head -n 1 "$file" 2>/dev/null | grep -q '^---$'; then
        # Check if there's a closing '---' within first 50 lines
        if head -n 50 "$file" 2>/dev/null | tail -n +2 | grep -q '^---$'; then
            return 0  # Has front matter
        fi
    fi
    return 1  # No front matter
}

# Determine document type from file path
determine_type() {
    local filepath="$1"
    local basename
    basename="$(basename "$filepath" .md)"

    if [[ "$filepath" == *"/${REQUIREMENT_DIR}/"* ]]; then
        echo "prd"
    elif [[ "$filepath" == *"/${SPECIFICATION_DIR}/"* ]]; then
        if [[ "$basename" == *"_spec" ]]; then
            echo "spec"
        elif [[ "$basename" == *"_design" ]]; then
            echo "design"
        else
            echo "unknown"
        fi
    elif [[ "$filepath" == *"/${TASK_DIR}/"* ]]; then
        if [[ "$basename" == *"implementation_log"* ]] || [[ "$basename" == *"impl_log"* ]]; then
            echo "implementation-log"
        else
            echo "task"
        fi
    else
        echo "unknown"
    fi
}

# Extract title from first heading
extract_title() {
    local file="$1"
    local title

    # Skip Front Matter if exists
    local skip_lines=0
    if has_front_matter "$file"; then
        # Count lines until closing ---
        skip_lines=$(head -n 50 "$file" 2>/dev/null | tail -n +2 | grep -n '^---$' | head -1 | cut -d: -f1)
        skip_lines=$((skip_lines + 1))  # Include closing ---
    fi

    # Extract first # heading
    if [ $skip_lines -gt 0 ]; then
        title=$(tail -n +$((skip_lines + 1)) "$file" 2>/dev/null | grep -m 1 '^#\s' | sed 's/^#\s*//' || echo "")
    else
        title=$(grep -m 1 '^#\s' "$file" 2>/dev/null | sed 's/^#\s*//' || echo "")
    fi

    # Fallback to basename if no heading found
    if [ -z "$title" ]; then
        title="$(basename "$file" .md)"
    fi

    echo "$title"
}

# Escape JSON strings
escape_json() {
    local str="$1"
    # Escape backslashes, double quotes, newlines
    echo "$str" | sed 's/\\/\\\\/g; s/"/\\"/g; s/$/\\n/' | tr -d '\n' | sed 's/\\n$//'
}

# --- Phase 1: Scan documents ---
echo "[scan-documents] Scanning AI-SDD documents..." >&2

ALL_DOCUMENTS=()
TOTAL_COUNT=0
WITH_FM_COUNT=0
WITHOUT_FM_COUNT=0

# Scan requirement/ directory
if [ -d "$REQUIREMENT_PATH" ]; then
    while IFS= read -r -d '' file; do
        ALL_DOCUMENTS+=("$file")
    done < <(find "$REQUIREMENT_PATH" -type f -name "*.md" -print0)
fi

# Scan specification/ directory
if [ -d "$SPECIFICATION_PATH" ]; then
    while IFS= read -r -d '' file; do
        # Only include *_spec.md and *_design.md
        basename="$(basename "$file" .md)"
        if [[ "$basename" == *"_spec" ]] || [[ "$basename" == *"_design" ]]; then
            ALL_DOCUMENTS+=("$file")
        fi
    done < <(find "$SPECIFICATION_PATH" -type f -name "*.md" -print0)
fi

# Scan task/ directory
if [ -d "$TASK_PATH" ]; then
    while IFS= read -r -d '' file; do
        ALL_DOCUMENTS+=("$file")
    done < <(find "$TASK_PATH" -type f -name "*.md" -print0)
fi

TOTAL_COUNT=${#ALL_DOCUMENTS[@]}

echo "[scan-documents] Found ${TOTAL_COUNT} total documents" >&2

# --- Phase 2: Analyze documents and generate JSON ---
SCAN_RESULT="${OUTPUT_DIR}/scan_result.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Start JSON
cat > "$SCAN_RESULT" << EOF
{
  "scan_timestamp": "${TIMESTAMP}",
  "total_documents": ${TOTAL_COUNT},
  "documents_with_front_matter": 0,
  "documents_without_front_matter": 0,
  "documents": [
EOF

FIRST=true
for file in "${ALL_DOCUMENTS[@]}"; do
    # Get relative path
    RELATIVE_PATH="${file#${SDD_DIR}/}"
    BASENAME="$(basename "$file" .md)"

    # Check Front Matter
    HAS_FM=false
    if has_front_matter "$file"; then
        HAS_FM=true
        WITH_FM_COUNT=$((WITH_FM_COUNT + 1))
    else
        WITHOUT_FM_COUNT=$((WITHOUT_FM_COUNT + 1))
    fi

    # Determine type
    DOC_TYPE=$(determine_type "$file")

    # Extract title
    TITLE=$(extract_title "$file")
    TITLE_ESCAPED=$(escape_json "$TITLE")

    # Add comma separator (except first entry)
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        echo "," >> "$SCAN_RESULT"
    fi

    # Write document entry
    cat >> "$SCAN_RESULT" << EOF
    {
      "path": "${file}",
      "relative_path": "${RELATIVE_PATH}",
      "basename": "${BASENAME}",
      "type": "${DOC_TYPE}",
      "has_front_matter": ${HAS_FM},
      "title_line": "${TITLE_ESCAPED}"
    }
EOF
done

# Close JSON
cat >> "$SCAN_RESULT" << EOF

  ]
}
EOF

# Update counts in JSON
if command -v jq &> /dev/null; then
    TMP_FILE="${SCAN_RESULT}.tmp"
    jq ".documents_with_front_matter = ${WITH_FM_COUNT} | .documents_without_front_matter = ${WITHOUT_FM_COUNT}" "$SCAN_RESULT" > "$TMP_FILE"
    mv "$TMP_FILE" "$SCAN_RESULT"
else
    # Manual update (less robust but works without jq)
    sed -i.bak "s/\"documents_with_front_matter\": 0/\"documents_with_front_matter\": ${WITH_FM_COUNT}/" "$SCAN_RESULT"
    sed -i.bak "s/\"documents_without_front_matter\": 0/\"documents_without_front_matter\": ${WITHOUT_FM_COUNT}/" "$SCAN_RESULT"
    rm -f "${SCAN_RESULT}.bak"
fi

echo "[scan-documents] Scan complete" >&2
echo "[scan-documents] Total: ${TOTAL_COUNT}, With Front Matter: ${WITH_FM_COUNT}, Without: ${WITHOUT_FM_COUNT}" >&2

# --- Phase 3: Export to CLAUDE_ENV_FILE ---
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    # Remove existing RECOMMEND_FM_* variables
    if [ -f "$CLAUDE_ENV_FILE" ]; then
        grep -v '^export RECOMMEND_FM_' "$CLAUDE_ENV_FILE" > "${CLAUDE_ENV_FILE}.tmp" 2>/dev/null || true
        mv "${CLAUDE_ENV_FILE}.tmp" "$CLAUDE_ENV_FILE" 2>/dev/null || true
    fi

    # Write environment variables
    {
        echo "export RECOMMEND_FM_CACHE_DIR=\"${OUTPUT_DIR}\""
        echo "export RECOMMEND_FM_SCAN_RESULT=\"${SCAN_RESULT}\""
        echo "export SDD_LANG=\"${SDD_LANG}\""
    } >> "$CLAUDE_ENV_FILE"

    echo "[scan-documents] Environment variables exported to CLAUDE_ENV_FILE" >&2
fi

echo "[scan-documents] Results saved to: ${SCAN_RESULT}" >&2
exit 0
