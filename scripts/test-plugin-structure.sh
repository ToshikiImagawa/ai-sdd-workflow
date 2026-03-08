#!/bin/sh
# test-plugin-structure.sh
# Validates 3-layer skill split structure (router / -cli / -cli-fallback)
# POSIX compatible (macOS bash 3.2 / dash)

set -e

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PLUGIN_DIR="${REPO_ROOT}/plugins/sdd-workflow"
SKILLS_DIR="${PLUGIN_DIR}/skills"
SHARED_REFS_DIR="${PLUGIN_DIR}/shared/references"

# Target skills with 3-layer split
ROUTER_SKILLS="check-spec constitution doc-consistency-checker implement plan-refactor task-breakdown"

# Counters
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# Colors (only if terminal supports it)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    NC=''
fi

log_pass() {
    printf '%sPASS%s %s\n' "$GREEN" "$NC" "$1"
    PASS_COUNT=$((PASS_COUNT + 1))
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
}

log_fail() {
    printf '%sFAIL%s %s\n' "$RED" "$NC" "$1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
}

# ============================================================
# Check 1: Router skill SKILL.md has allowed-tools: Skill only
# ============================================================
printf "=== Check 1: Router Skill allowed-tools ===\n\n"

for skill in $ROUTER_SKILLS; do
    skill_md="${SKILLS_DIR}/${skill}/SKILL.md"
    if [ ! -f "$skill_md" ]; then
        log_fail "${skill}: SKILL.md not found"
        continue
    fi
    allowed=$(grep '^allowed-tools:' "$skill_md" | sed 's/^allowed-tools:[[:space:]]*//' | sed 's/[[:space:]]*$//')
    if [ "$allowed" = "Skill" ]; then
        log_pass "${skill}: allowed-tools is 'Skill' only"
    else
        log_fail "${skill}: allowed-tools is '${allowed}' (expected: 'Skill')"
    fi
done

printf "\n"

# ============================================================
# Check 2: Sub-skill directories and SKILL.md existence
# ============================================================
printf "=== Check 2: Sub-skill Existence ===\n\n"

for skill in $ROUTER_SKILLS; do
    for suffix in cli cli-fallback; do
        sub_dir="${SKILLS_DIR}/${skill}-${suffix}"
        sub_md="${sub_dir}/SKILL.md"
        if [ -d "$sub_dir" ] && [ -f "$sub_md" ]; then
            log_pass "${skill}-${suffix}: directory and SKILL.md exist"
        elif [ ! -d "$sub_dir" ]; then
            log_fail "${skill}-${suffix}: directory not found"
        else
            log_fail "${skill}-${suffix}: SKILL.md not found"
        fi
    done
done

printf "\n"

# ============================================================
# Check 3: Sub-skills have user-invocable: false
# ============================================================
printf "=== Check 3: Sub-skill user-invocable ===\n\n"

for skill in $ROUTER_SKILLS; do
    for suffix in cli cli-fallback; do
        sub_md="${SKILLS_DIR}/${skill}-${suffix}/SKILL.md"
        [ -f "$sub_md" ] || continue
        invocable=$(grep '^user-invocable:' "$sub_md" | sed 's/^user-invocable:[[:space:]]*//' | sed 's/[[:space:]]*$//')
        if [ "$invocable" = "false" ]; then
            log_pass "${skill}-${suffix}: user-invocable is false"
        else
            log_fail "${skill}-${suffix}: user-invocable is '${invocable}' (expected: 'false')"
        fi
    done
done

printf "\n"

# ============================================================
# Check 4: Symlinks in sub-skills resolve correctly
# ============================================================
printf "=== Check 4: Symlink Resolution ===\n\n"

for skill in $ROUTER_SKILLS; do
    for suffix in cli cli-fallback; do
        sub_dir="${SKILLS_DIR}/${skill}-${suffix}"
        [ -d "$sub_dir" ] || continue

        # Find all symlinks in sub-skill directory
        symlinks=$(find "$sub_dir" -type l 2>/dev/null)
        if [ -z "$symlinks" ]; then
            # No symlinks is acceptable for some skills
            continue
        fi

        broken=0
        total_links=0
        echo "$symlinks" | while IFS= read -r link; do
            [ -z "$link" ] && continue
            total_links=$((total_links + 1))
            if [ ! -e "$link" ]; then
                relpath="${link#"$REPO_ROOT"/}"
                target=$(readlink "$link")
                log_fail "${relpath}: broken symlink -> ${target}"
                broken=$((broken + 1))
            fi
        done

        # Check if all symlinks resolved (re-count outside subshell)
        broken_count=$(find "$sub_dir" -type l ! -exec test -e {} \; -print 2>/dev/null | wc -l | tr -d ' ')
        link_count=$(find "$sub_dir" -type l 2>/dev/null | wc -l | tr -d ' ')
        if [ "$broken_count" -eq 0 ] && [ "$link_count" -gt 0 ]; then
            log_pass "${skill}-${suffix}: all ${link_count} symlinks resolve correctly"
        elif [ "$broken_count" -gt 0 ]; then
            log_fail "${skill}-${suffix}: ${broken_count}/${link_count} broken symlinks"
        fi
    done
done

printf "\n"

# ============================================================
# Check 5: CLI skills have cli_integration_guide.md and cli_error_handling.md
# ============================================================
printf "=== Check 5: CLI Reference Symlinks ===\n\n"

CLI_REFS="cli_integration_guide.md cli_error_handling.md"

for skill in $ROUTER_SKILLS; do
    refs_dir="${SKILLS_DIR}/${skill}-cli/references"
    if [ ! -d "$refs_dir" ]; then
        log_fail "${skill}-cli: references/ directory not found"
        continue
    fi

    all_ok=1
    for ref in $CLI_REFS; do
        ref_path="${refs_dir}/${ref}"
        if [ -L "$ref_path" ] && [ -e "$ref_path" ]; then
            : # symlink exists and resolves
        elif [ -L "$ref_path" ]; then
            log_fail "${skill}-cli/references/${ref}: broken symlink"
            all_ok=0
        else
            log_fail "${skill}-cli/references/${ref}: not found or not a symlink"
            all_ok=0
        fi
    done

    if [ "$all_ok" -eq 1 ]; then
        log_pass "${skill}-cli: CLI reference symlinks present and valid"
    fi
done

printf "\n"

# ============================================================
# Summary
# ============================================================
printf "=== Summary ===\n"
printf "Passed: %d / %d\n" "$PASS_COUNT" "$TOTAL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
    printf '%sFAILED%s - %d test(s) failed\n' "$RED" "$NC" "$FAIL_COUNT"
    exit 1
fi

printf '%sPASSED%s - all structure tests passed\n' "$GREEN" "$NC"
exit 0
