#!/bin/sh
# test-session-start.sh
# Golden-file regression test runner for session-start.sh
# POSIX compatible (macOS bash 3.2 / dash)

set -e

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SESSION_START="${REPO_ROOT}/plugins/sdd-workflow/scripts/session-start.sh"
FIXTURES_DIR="${REPO_ROOT}/tests/fixtures"

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
}

log_fail() {
    printf '%sFAIL%s %s\n' "$RED" "$NC" "$1"
}

# Track last temp dir for trap cleanup on unexpected exit
LAST_TMP_DIR=""
# shellcheck disable=SC2329
cleanup_on_exit() {
    if [ -n "$LAST_TMP_DIR" ] && [ -d "$LAST_TMP_DIR" ]; then
        rm -rf "$LAST_TMP_DIR"
    fi
}
trap cleanup_on_exit EXIT

# Run a single test fixture
run_fixture() {
    fixture_dir="$1"
    fixture_name="$(basename "$fixture_dir")"
    expected_file="${fixture_dir}/expected_env.txt"
    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    if [ ! -f "$expected_file" ]; then
        log_fail "${fixture_name}: expected_env.txt not found"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi

    # Create isolated temp directory (tracked for trap cleanup)
    tmp_dir="$(mktemp -d)"
    LAST_TMP_DIR="$tmp_dir"

    # Create mock PROJECT_ROOT
    mock_project="${tmp_dir}/project"
    mkdir -p "$mock_project"

    # Create mock CLAUDE_PLUGIN_ROOT (with required files)
    mock_plugin="${tmp_dir}/plugin"
    mkdir -p "${mock_plugin}/.claude-plugin"
    # Copy plugin.json for version detection
    if [ -f "${REPO_ROOT}/plugins/sdd-workflow/.claude-plugin/plugin.json" ]; then
        cp "${REPO_ROOT}/plugins/sdd-workflow/.claude-plugin/plugin.json" "${mock_plugin}/.claude-plugin/plugin.json"
    fi
    # Create minimal AI-SDD-PRINCIPLES.source.md
    printf '%s\n' "---" "version: \"0.0.0\"" "---" "# Test" > "${mock_plugin}/AI-SDD-PRINCIPLES.source.md"

    # Create CLAUDE.md to suppress version warning
    printf '%s\n' "## AI-SDD Instructions (v99.99.99)" > "${mock_project}/CLAUDE.md"

    # Copy .sdd-config.json if fixture provides it
    if [ -f "${fixture_dir}/.sdd-config.json" ]; then
        cp "${fixture_dir}/.sdd-config.json" "${mock_project}/.sdd-config.json"
    fi

    # Run setup.sh if fixture provides it
    if [ -f "${fixture_dir}/setup.sh" ]; then
        PROJECT_ROOT="$mock_project" sh "${fixture_dir}/setup.sh"
    fi

    # Create CLAUDE_ENV_FILE
    env_file="${tmp_dir}/env_output"
    touch "$env_file"

    # Run session-start.sh in subprocess with mocked environment
    exit_code=0
    CLAUDE_PLUGIN_ROOT="$mock_plugin" \
        CLAUDE_PROJECT_DIR="$mock_project" \
        CLAUDE_ENV_FILE="$env_file" \
        bash "$SESSION_START" > /dev/null 2>&1 || exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        printf "  session-start.sh exited with code %d\n" "$exit_code" >&2
    fi

    # Extract and sort SDD_* export lines from env file
    actual_file="${tmp_dir}/actual_env.txt"
    if [ -f "$env_file" ]; then
        grep '^export SDD_' "$env_file" | sort > "$actual_file" 2>/dev/null || true
    else
        touch "$actual_file"
    fi

    # Sort expected for comparison
    sorted_expected="${tmp_dir}/expected_sorted.txt"
    sort "$expected_file" > "$sorted_expected"

    # Compare
    if diff -u "$sorted_expected" "$actual_file" > "${tmp_dir}/diff_output" 2>&1; then
        log_pass "$fixture_name"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        log_fail "$fixture_name"
        printf "  Expected vs Actual diff:\n"
        sed 's/^/    /' "${tmp_dir}/diff_output"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # Cleanup
    rm -rf "$tmp_dir"
    LAST_TMP_DIR=""
}

# Main
printf "=== session-start.sh Regression Tests ===\n\n"

# Check prerequisites
if [ ! -f "$SESSION_START" ]; then
    printf "Error: session-start.sh not found at %s\n" "$SESSION_START" >&2
    exit 1
fi

if [ ! -d "$FIXTURES_DIR" ]; then
    printf "Error: fixtures directory not found at %s\n" "$FIXTURES_DIR" >&2
    exit 1
fi

# Run all fixtures (sorted for deterministic order)
for fixture_dir in "$FIXTURES_DIR"/*/; do
    # Skip if not a directory
    [ -d "$fixture_dir" ] || continue
    # Skip if no expected_env.txt
    [ -f "${fixture_dir}/expected_env.txt" ] || continue
    run_fixture "$fixture_dir"
done

# Summary
printf "\n=== Results: %d passed, %d failed, %d total ===\n" "$PASS_COUNT" "$FAIL_COUNT" "$TOTAL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi

exit 0
