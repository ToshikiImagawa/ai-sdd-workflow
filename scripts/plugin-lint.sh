#!/bin/sh
# plugin-lint.sh
# Shell script version of .claude/skills/plugin-lint/SKILL.md checks
# POSIX compatible (macOS bash 3.2 / dash)
# Uses temp files for counters to avoid subshell variable scoping issues

set -e

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PLUGIN_DIR="${REPO_ROOT}/plugins/sdd-workflow"

# Temp files for counters (avoids subshell scoping issues with pipes)
TMP_DIR="$(mktemp -d)"
WARN_FILE="${TMP_DIR}/warn_count"
ERROR_FILE="${TMP_DIR}/error_count"
printf '0' > "$WARN_FILE"
printf '0' > "$ERROR_FILE"

# shellcheck disable=SC2329
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# Colors (only if terminal supports it)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

log_warn() {
    printf "${YELLOW}WARN${NC} %s\n" "$1"
    count=$(cat "$WARN_FILE")
    printf '%d' "$((count + 1))" > "$WARN_FILE"
}

log_error() {
    printf "${RED}ERROR${NC} %s\n" "$1"
    count=$(cat "$ERROR_FILE")
    printf '%d' "$((count + 1))" > "$ERROR_FILE"
}

log_ok() {
    printf "${GREEN}OK${NC} %s\n" "$1"
}

# ============================================================
# Check 1: Code Block Detection in Prompt Markdown (warning only)
# ============================================================
printf "=== Check 1: Code Block Detection ===\n\n"

check1_found=0

# Check agents/*.md
for f in "$PLUGIN_DIR"/agents/*.md; do
    [ -f "$f" ] || continue
    matches=$(grep -n '^```' "$f" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        relpath="${f#"$REPO_ROOT"/}"
        echo "$matches" | while IFS= read -r line; do
            lineno="${line%%:*}"
            content="${line#*:}"
            block_type=$(echo "$content" | sed 's/^```[[:space:]]*//' | sed 's/[[:space:]].*//')
            [ -z "$block_type" ] && block_type="plain"
            log_warn "${relpath}:${lineno} - code block (${block_type})"
        done
        check1_found=1
    fi
done

# Check skills/*/SKILL.md (excluding templates/, examples/, references/)
for f in "$PLUGIN_DIR"/skills/*/SKILL.md; do
    [ -f "$f" ] || continue
    matches=$(grep -n '^```' "$f" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        relpath="${f#"$REPO_ROOT"/}"
        echo "$matches" | while IFS= read -r line; do
            lineno="${line%%:*}"
            content="${line#*:}"
            block_type=$(echo "$content" | sed 's/^```[[:space:]]*//' | sed 's/[[:space:]].*//')
            [ -z "$block_type" ] && block_type="plain"
            log_warn "${relpath}:${lineno} - code block (${block_type})"
        done
        check1_found=1
    fi
done

if [ "$check1_found" -eq 0 ]; then
    log_ok "No code blocks found in prompt Markdown files"
fi
printf "\n"

# ============================================================
# Check 2: Support File Structure Validation (error on failure)
# ============================================================
printf "=== Check 2: Support File Structure ===\n\n"

ALLOWED_DIRS="templates examples references scripts"

for skill_dir in "$PLUGIN_DIR"/skills/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"

    # --- 2.1 Directory Name Accuracy ---
    for entry in "$skill_dir"*/; do
        [ -d "$entry" ] || continue
        dir_name="$(basename "$entry")"
        found=0
        for allowed in $ALLOWED_DIRS; do
            if [ "$dir_name" = "$allowed" ]; then
                found=1
                break
            fi
        done
        if [ "$found" -eq 0 ]; then
            log_error "skills/${skill_name}/${dir_name}/ - unexpected directory (allowed: ${ALLOWED_DIRS})"
        fi
    done

    # Also check for unexpected files (not SKILL.md, not README.md, not directories)
    for entry in "$skill_dir"*; do
        [ -e "$entry" ] || continue
        [ -d "$entry" ] && continue
        fname="$(basename "$entry")"
        if [ "$fname" != "SKILL.md" ] && [ "$fname" != "README.md" ]; then
            log_error "skills/${skill_name}/${fname} - unexpected file at skill root (only SKILL.md and README.md allowed)"
        fi
    done

    # --- 2.2 File Name Convention (snake_case) ---
    for sub_dir in templates examples references; do
        check_dir="${skill_dir}${sub_dir}"
        [ -d "$check_dir" ] || continue
        find "$check_dir" -type f | while IFS= read -r filepath; do
            fname="$(basename "$filepath")"
            if ! echo "$fname" | grep -qE '^[a-z0-9_]+\.[a-z]+$'; then
                relpath="${filepath#"$REPO_ROOT"/}"
                log_error "${relpath} - filename not snake_case (expected: ^[a-z0-9_]+\\.[a-z]+$)"
            fi
        done
    done

    # --- 2.3 Language Directory Completeness ---
    templates_dir="${skill_dir}templates"
    if [ -d "$templates_dir" ]; then
        has_en=0
        has_ja=0
        [ -d "${templates_dir}/en" ] && has_en=1
        [ -d "${templates_dir}/ja" ] && has_ja=1

        if [ "$has_en" -eq 0 ]; then
            log_error "skills/${skill_name}/templates/ - missing en/ directory"
        fi
        if [ "$has_ja" -eq 0 ]; then
            log_error "skills/${skill_name}/templates/ - missing ja/ directory"
        fi

        # --- 2.4 Language File Set Consistency ---
        if [ "$has_en" -eq 1 ] && [ "$has_ja" -eq 1 ]; then
            en_files="$(cd "${templates_dir}/en" && find . -type f | sort)"
            ja_files="$(cd "${templates_dir}/ja" && find . -type f | sort)"

            if [ "$en_files" != "$ja_files" ]; then
                echo "$en_files" | while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    if ! echo "$ja_files" | grep -qFx "$f"; then
                        log_error "skills/${skill_name}/templates/ - file ${f#./} exists in en/ but not in ja/"
                    fi
                done
                echo "$ja_files" | while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    if ! echo "$en_files" | grep -qFx "$f"; then
                        log_error "skills/${skill_name}/templates/ - file ${f#./} exists in ja/ but not in en/"
                    fi
                done
            else
                log_ok "skills/${skill_name}/templates/ - en/ and ja/ file sets match"
            fi
        fi
    fi

    # --- 2.5 Support File Extension (.md required for templates/ and references/) ---
    for sub_dir in templates references; do
        check_dir="${skill_dir}${sub_dir}"
        [ -d "$check_dir" ] || continue
        find "$check_dir" -type f | while IFS= read -r filepath; do
            fname="$(basename "$filepath")"
            ext="${fname##*.}"
            if [ "$ext" != "md" ]; then
                relpath="${filepath#"$REPO_ROOT"/}"
                log_error "${relpath} - extension .${ext} not allowed (expected: .md)"
            fi
        done
    done
done

# ============================================================
# Summary
# ============================================================
WARN_COUNT=$(cat "$WARN_FILE")
ERROR_COUNT=$(cat "$ERROR_FILE")

printf "\n=== Summary ===\n"
printf "Warnings: %d (code blocks in prompts)\n" "$WARN_COUNT"
printf "Errors:   %d (structure violations)\n" "$ERROR_COUNT"

if [ "$ERROR_COUNT" -gt 0 ]; then
    printf '\n%sFAILED%s - %d error(s) found\n' "$RED" "$NC" "$ERROR_COUNT"
    exit 1
fi

printf '\n%sPASSED%s - plugin lint checks completed\n' "$GREEN" "$NC"
exit 0
