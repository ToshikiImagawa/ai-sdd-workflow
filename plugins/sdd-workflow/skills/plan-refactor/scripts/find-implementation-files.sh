#!/bin/bash
# find-implementation-files.sh
# Find implementation files related to feature
# Usage: find-implementation-files.sh <feature-name> [scope-dir]

set -e

FEATURE_NAME="$1"
SCOPE_DIR="$2"  # Optional: e.g., "src/" or "lib/"

if [ -z "$FEATURE_NAME" ]; then
    echo "[find-implementation-files] ERROR: feature-name required" >&2
    exit 1
fi

# Environment variables
SDD_ROOT="${SDD_ROOT:-.sdd}"
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
SEARCH_DIR="${CLAUDE_PROJECT_DIR}"

if [ -n "$SCOPE_DIR" ]; then
    SEARCH_DIR="${CLAUDE_PROJECT_DIR}/${SCOPE_DIR}"
    echo "[find-implementation-files] Limiting search to: ${SCOPE_DIR}" >&2
else
    echo "[find-implementation-files] Searching entire project (excluding common directories)" >&2
fi

# Create cache directory
CACHE_DIR="${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor"
mkdir -p "$CACHE_DIR"

echo "[find-implementation-files] Searching for: ${FEATURE_NAME}" >&2

# Step 1: File name matching (fast)
echo "[find-implementation-files] Step 1: Filename matching..." >&2
find "$SEARCH_DIR" -type f \
    \( -name "*${FEATURE_NAME}*" \) \
    ! -path "*/node_modules/*" \
    ! -path "*/.git/*" \
    ! -path "*/${SDD_ROOT}/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/.next/*" \
    ! -path "*/coverage/*" \
    ! -path "*/.cache/*" \
    2>/dev/null > "$CACHE_DIR/files-by-name.txt" || true

FILE_BY_NAME_COUNT=$(wc -l < "$CACHE_DIR/files-by-name.txt" | tr -d ' ')
echo "[find-implementation-files]   Found ${FILE_BY_NAME_COUNT} files by name" >&2

# Step 2: File content matching (slower, limited to source directories)
echo "[find-implementation-files] Step 2: Content matching..." >&2

# Determine directories to search for content
if [ -z "$SCOPE_DIR" ]; then
    # Default: search only common source directories
    CONTENT_SEARCH_DIRS=()
    for dir in src lib app components services modules; do
        if [ -d "${CLAUDE_PROJECT_DIR}/${dir}" ]; then
            CONTENT_SEARCH_DIRS+=("${CLAUDE_PROJECT_DIR}/${dir}")
        fi
    done

    if [ ${#CONTENT_SEARCH_DIRS[@]} -eq 0 ]; then
        # Fallback: search entire project if no common directories found
        CONTENT_SEARCH_DIRS=("${CLAUDE_PROJECT_DIR}")
    fi
else
    CONTENT_SEARCH_DIRS=("$SEARCH_DIR")
fi

: > "$CACHE_DIR/files-by-content.txt"  # Clear file

for dir in "${CONTENT_SEARCH_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "[find-implementation-files]   Searching in: ${dir}" >&2
        grep -ril "$FEATURE_NAME" "$dir" \
            --exclude-dir=node_modules \
            --exclude-dir=.git \
            --exclude-dir=dist \
            --exclude-dir=build \
            --exclude-dir=.next \
            --exclude-dir=coverage \
            --exclude-dir=.cache \
            --exclude="*.min.js" \
            --exclude="*.min.css" \
            --exclude="*.map" \
            2>/dev/null >> "$CACHE_DIR/files-by-content.txt" || true
    fi
done

FILE_BY_CONTENT_COUNT=$(wc -l < "$CACHE_DIR/files-by-content.txt" | tr -d ' ')
echo "[find-implementation-files]   Found ${FILE_BY_CONTENT_COUNT} files by content" >&2

# Step 3: Merge and deduplicate
cat "$CACHE_DIR/files-by-name.txt" "$CACHE_DIR/files-by-content.txt" | sort -u > "$CACHE_DIR/all-files.txt"

FILE_COUNT=$(wc -l < "$CACHE_DIR/all-files.txt" | tr -d ' ')

# Step 4: Separate by file type
: > "$CACHE_DIR/implementation-files.txt"  # Main implementation files
: > "$CACHE_DIR/test-files.txt"            # Test files
: > "$CACHE_DIR/config-files.txt"          # Config/build files

while IFS= read -r file; do
    if [[ "$file" =~ \.(test|spec)\.(ts|tsx|js|jsx|py)$ ]] || [[ "$file" =~ /__tests__/ ]] || [[ "$file" =~ /tests?/ ]]; then
        echo "$file" >> "$CACHE_DIR/test-files.txt"
    elif [[ "$file" =~ \.(json|yml|yaml|toml|lock)$ ]] || [[ "$file" =~ package\.json$ ]] || [[ "$file" =~ tsconfig\.json$ ]]; then
        echo "$file" >> "$CACHE_DIR/config-files.txt"
    else
        echo "$file" >> "$CACHE_DIR/implementation-files.txt"
    fi
done < "$CACHE_DIR/all-files.txt"

IMPL_COUNT=$(wc -l < "$CACHE_DIR/implementation-files.txt" | tr -d ' ')
TEST_COUNT=$(wc -l < "$CACHE_DIR/test-files.txt" | tr -d ' ')
CONFIG_COUNT=$(wc -l < "$CACHE_DIR/config-files.txt" | tr -d ' ')

# Output JSON
cat > "$CACHE_DIR/implementation-files.json" <<EOF
{
  "feature_name": "${FEATURE_NAME}",
  "file_count": ${FILE_COUNT},
  "implementation_count": ${IMPL_COUNT},
  "test_count": ${TEST_COUNT},
  "config_count": ${CONFIG_COUNT},
  "scope_dir": "${SCOPE_DIR:-all}",
  "files_list_path": "${CACHE_DIR}/all-files.txt",
  "implementation_list_path": "${CACHE_DIR}/implementation-files.txt",
  "test_list_path": "${CACHE_DIR}/test-files.txt",
  "config_list_path": "${CACHE_DIR}/config-files.txt",
  "files_by_name_count": ${FILE_BY_NAME_COUNT},
  "files_by_content_count": ${FILE_BY_CONTENT_COUNT}
}
EOF

echo "[find-implementation-files] Results saved to: ${CACHE_DIR}/implementation-files.json" >&2
echo "[find-implementation-files] Total: ${FILE_COUNT} files" >&2
echo "[find-implementation-files]   Implementation: ${IMPL_COUNT}" >&2
echo "[find-implementation-files]   Tests: ${TEST_COUNT}" >&2
echo "[find-implementation-files]   Config: ${CONFIG_COUNT}" >&2

# Warning if too many files
if [ "$FILE_COUNT" -gt 20 ]; then
    echo "[find-implementation-files] ⚠ WARNING: ${FILE_COUNT} files found. Consider narrowing scope with --scope argument." >&2
fi
