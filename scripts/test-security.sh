#!/usr/bin/env bash
#
# Security regression test suite for AI-SDD workflow
#
# This script runs comprehensive security tests to detect potential vulnerabilities
# and ensure security controls are not bypassed or removed.
#
# Usage:
#   bash scripts/test-security.sh           # Run all security tests
#   bash scripts/test-security.sh --quick   # Run quick security checks only
#
# Exit codes:
#   0 - All security tests passed
#   1 - Security test failures detected (CRITICAL)
#   2 - Script execution error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Security Regression Test Suite${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Parse arguments
QUICK_MODE=false
if [ "${1:-}" = "--quick" ]; then
    QUICK_MODE=true
    echo -e "${YELLOW}Running in quick mode (essential checks only)${NC}"
    echo ""
fi

#
# Test 1: Python security unit tests
#
run_python_security_tests() {
    echo -e "${BLUE}[1/5] Running Python security unit tests...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if command -v python3 >/dev/null 2>&1; then
        # Check if pytest is available
        if python3 -m pytest --version >/dev/null 2>&1; then
            if python3 -m pytest "${REPO_ROOT}/tests/test_security_session_start.py" -v --tb=short; then
                echo -e "${GREEN}✓ Python security tests passed${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}✗ SECURITY FAILURE: Python security tests failed${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                return 1
            fi
        else
            echo -e "${YELLOW}⚠ pytest not available, skipping Python unit tests${NC}"
            echo -e "${YELLOW}  Install pytest: pip3 install pytest${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ python3 not available, skipping Python unit tests${NC}"
    fi
    echo ""
}

#
# Test 2: Validate repository URL function exists
#
check_validate_function_exists() {
    echo -e "${BLUE}[2/5] Checking validate_repository_url function exists...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    local session_start_py="${REPO_ROOT}/plugins/sdd-workflow/scripts/session-start.py"

    if [ ! -f "$session_start_py" ]; then
        echo -e "${RED}✗ SECURITY FAILURE: session-start.py not found${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi

    if grep -q "def validate_repository_url" "$session_start_py"; then
        echo -e "${GREEN}✓ validate_repository_url function exists${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ SECURITY FAILURE: validate_repository_url function not found${NC}"
        echo -e "${RED}  This function is critical for preventing command injection attacks${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    echo ""
}

#
# Test 3: Validate that detect_cli calls validation
#
check_validation_is_called() {
    echo -e "${BLUE}[3/5] Checking that detect_cli calls validate_repository_url...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    local session_start_py="${REPO_ROOT}/plugins/sdd-workflow/scripts/session-start.py"

    if grep -q "validate_repository_url(cli_cfg.repository)" "$session_start_py"; then
        echo -e "${GREEN}✓ validate_repository_url is called in detect_cli${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ SECURITY FAILURE: validate_repository_url is not called${NC}"
        echo -e "${RED}  URL validation MUST be performed before constructing commands${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    echo ""
}

#
# Test 4: Integration tests with malicious URLs
#
run_integration_security_tests() {
    echo -e "${BLUE}[4/5] Running integration security tests...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Check if security test fixtures exist
    local fixture_14="${REPO_ROOT}/tests/fixtures/14-cli-invalid-url"
    local fixture_15="${REPO_ROOT}/tests/fixtures/15-cli-command-substitution"

    if [ ! -d "$fixture_14" ] || [ ! -d "$fixture_15" ]; then
        echo -e "${YELLOW}⚠ Security test fixtures not found, skipping integration tests${NC}"
        echo ""
        return 0
    fi

    # Run session-start tests which include security fixtures
    local test_output
    test_output=$(bash "${REPO_ROOT}/scripts/test-session-start.sh" 2>&1)

    if echo "$test_output" | grep -q "PASS 14-cli-invalid-url" && \
       echo "$test_output" | grep -q "PASS 15-cli-command-substitution"; then
        echo -e "${GREEN}✓ Integration security tests passed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ SECURITY FAILURE: Integration security tests failed${NC}"
        echo -e "${YELLOW}Test output:${NC}"
        echo "$test_output" | tail -20
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    echo ""
}

#
# Test 5: ShellCheck security linting (if available)
#
run_shellcheck_security() {
    if [ "$QUICK_MODE" = true ]; then
        echo -e "${YELLOW}[5/5] Skipping ShellCheck (quick mode)${NC}"
        echo ""
        return 0
    fi

    echo -e "${BLUE}[5/5] Running ShellCheck security linting...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if ! command -v shellcheck >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ ShellCheck not available, skipping shell security linting${NC}"
        echo ""
        return 0
    fi

    # Check shell scripts for security issues
    local shell_scripts=(
        "${REPO_ROOT}/scripts/test-session-start.sh"
        "${REPO_ROOT}/.claude/skills/cli-integration-test/scripts/cli-integration-test.sh"
    )

    local shellcheck_failed=false
    for script in "${shell_scripts[@]}"; do
        if [ -f "$script" ]; then
            if ! shellcheck -S warning "$script" >/dev/null 2>&1; then
                echo -e "${YELLOW}⚠ ShellCheck warnings in $(basename "$script")${NC}"
                shellcheck_failed=true
            fi
        fi
    done

    if [ "$shellcheck_failed" = false ]; then
        echo -e "${GREEN}✓ ShellCheck security linting passed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠ ShellCheck found warnings (not critical)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))  # Warnings are not failures
    fi
    echo ""
}

#
# Run all tests
#
main() {
    local start_time
    start_time=$(date +%s)

    # Run tests
    check_validate_function_exists || true
    check_validation_is_called || true
    run_python_security_tests || true
    run_integration_security_tests || true
    run_shellcheck_security || true

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    # Print summary
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}Security Test Summary${NC}"
    echo -e "${BLUE}=================================${NC}"
    echo -e "Total tests:   ${TOTAL_TESTS}"
    echo -e "${GREEN}Passed tests:  ${PASSED_TESTS}${NC}"

    if [ "$FAILED_TESTS" -gt 0 ]; then
        echo -e "${RED}Failed tests:  ${FAILED_TESTS}${NC}"
        echo -e "${RED}SECURITY ALERT: Critical security tests failed!${NC}"
        echo -e "${RED}Please review the failures above before proceeding.${NC}"
        echo ""
        echo -e "Elapsed time:  ${elapsed}s"
        exit 1
    else
        echo -e "Failed tests:  0"
        echo -e "${GREEN}All security tests passed ✓${NC}"
        echo ""
        echo -e "Elapsed time:  ${elapsed}s"
        exit 0
    fi
}

# Trap errors
trap 'echo -e "${RED}Script execution error${NC}"; exit 2' ERR

# Run main
main "$@"
