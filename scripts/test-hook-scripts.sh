#!/bin/sh
# test-hook-scripts.sh
# Regression tests for plugins/sdd-workflow/scripts/{pre-tool-use,post-tool-use,user-prompt-submit}.py
# POSIX compatible (macOS bash 3.2 / dash)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_SCRIPTS_DIR="${REPO_ROOT}/plugins/sdd-workflow/scripts"

PASS_COUNT=0
FAIL_COUNT=0

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
}

log_fail() {
    printf '%sFAIL%s %s\n' "$RED" "$NC" "$1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

TMP_DIR=""
# shellcheck disable=SC2329
cleanup() {
    if [ -n "$TMP_DIR" ] && [ -d "$TMP_DIR" ]; then
        rm -rf "$TMP_DIR"
    fi
}
trap cleanup EXIT

# Set up a fake project with .sdd structure
TMP_DIR="$(mktemp -d)"
mkdir -p "$TMP_DIR/.sdd/requirement" "$TMP_DIR/.sdd/specification/auth" "$TMP_DIR/src"
touch "$TMP_DIR/.sdd/specification/auth/user-login_design.md"

# run_hook <test-name> <script> <stdin-json> <expected-exit> <expected-output-substring>
# expected-output-substring empty means stdout must be empty
run_hook() {
    name="$1"
    script="$2"
    stdin_json="$3"
    expected_exit="$4"
    expected_substr="$5"

    set +e
    output=$(printf '%s' "$stdin_json" | python3 "${HOOK_SCRIPTS_DIR}/${script}" 2>&1)
    actual_exit=$?
    set -e

    if [ "$actual_exit" -ne "$expected_exit" ]; then
        log_fail "${name}: exit code ${actual_exit} (expected ${expected_exit})"
        return
    fi
    if [ -n "$expected_substr" ]; then
        case "$output" in
            *"$expected_substr"*) ;;
            *)
                log_fail "${name}: output missing '${expected_substr}' (got: ${output})"
                return
                ;;
        esac
    else
        if [ -n "$output" ]; then
            log_fail "${name}: expected empty output (got: ${output})"
            return
        fi
    fi
    log_pass "$name"
}

echo "=== pre-tool-use.py ==="

run_hook "pre: valid spec name passes" "pre-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/specification/user-login_spec.md\"}}" \
    0 ""

run_hook "pre: specification without suffix is denied via JSON" "pre-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/specification/user-login.md\"}}" \
    0 "\"permissionDecision\": \"deny\""

run_hook "pre: deny reason mentions the naming violation" "pre-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/specification/user-login.md\"}}" \
    0 "Naming violation"

run_hook "pre: requirement with _spec suffix is denied via JSON" "pre-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/requirement/user-login_spec.md\"}}" \
    0 "\"permissionDecision\": \"deny\""

run_hook "pre: requirement without suffix passes" "pre-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/requirement/user-login.md\"}}" \
    0 ""

run_hook "pre: non-sdd file passes" "pre-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/src/main.py\"}}" \
    0 ""

run_hook "pre: invalid stdin is a no-op" "pre-tool-use.py" \
    "not-json" \
    0 ""

# Constitution injection tests (separate project with .sdd/CONSTITUTION.md)
CONST_DIR="$TMP_DIR/const-project"
mkdir -p "$CONST_DIR/.sdd" "$CONST_DIR/src"
printf '# Project Constitution\n\n- Simplicity first\n' > "$CONST_DIR/.sdd/CONSTITUTION.md"
SESSION_ID="test-hook-$$"
rm -f "${TMPDIR:-/tmp}/sdd-constitution-injected-${SESSION_ID}"

run_hook "pre: source edit injects CONSTITUTION principles" "pre-tool-use.py" \
    "{\"cwd\": \"$CONST_DIR\", \"session_id\": \"$SESSION_ID\", \"tool_input\": {\"file_path\": \"$CONST_DIR/src/main.py\"}}" \
    0 "Simplicity first"

run_hook "pre: second injection in same session is suppressed" "pre-tool-use.py" \
    "{\"cwd\": \"$CONST_DIR\", \"session_id\": \"$SESSION_ID\", \"tool_input\": {\"file_path\": \"$CONST_DIR/src/other.py\"}}" \
    0 ""

run_hook "pre: non-source file gets no injection" "pre-tool-use.py" \
    "{\"cwd\": \"$CONST_DIR\", \"session_id\": \"$SESSION_ID-doc\", \"tool_input\": {\"file_path\": \"$CONST_DIR/README.md\"}}" \
    0 ""

rm -f "${TMPDIR:-/tmp}/sdd-constitution-injected-${SESSION_ID}"

echo "=== post-tool-use.py ==="

run_hook "post: spec edit reminds consistency check" "post-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/specification/auth/user-login_spec.md\"}}" \
    0 "doc-consistency-checker"

run_hook "post: PRD edit reminds downstream propagation" "post-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/.sdd/requirement/user-login.md\"}}" \
    0 "downstream"

run_hook "post: source edit with matching design doc reminds sync" "post-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/src/user-login.py\"}}" \
    0 "user-login_design.md"

run_hook "post: source edit without design doc is silent" "post-tool-use.py" \
    "{\"cwd\": \"$TMP_DIR\", \"tool_input\": {\"file_path\": \"$TMP_DIR/src/main.py\"}}" \
    0 ""

echo "=== user-prompt-submit.py ==="

run_hook "prompt: vague ja expression is detected" "user-prompt-submit.py" \
    "{\"prompt\": \"いい感じに直して\"}" \
    0 "Vibe Coding"

run_hook "prompt: vague en expression is detected" "user-prompt-submit.py" \
    "{\"prompt\": \"just make it work somehow\"}" \
    0 "Vibe Coding"

run_hook "prompt: clear instruction is silent" "user-prompt-submit.py" \
    "{\"prompt\": \"Add a --verbose flag to session-start.py that logs config values\"}" \
    0 ""

echo ""
echo "Results: ${PASS_COUNT} passed, ${FAIL_COUNT} failed"
if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
