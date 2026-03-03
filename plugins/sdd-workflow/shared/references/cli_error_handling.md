# CLI Error Handling Patterns

This document defines standard error handling patterns for `sdd-cli` integration across all AI-SDD workflow skills.

## Exit Code Handling

### Standard Exit Codes

| Exit Code | Meaning                        | Action                                                    |
|:----------|:-------------------------------|:----------------------------------------------------------|
| `0`       | Success                        | Parse JSON output, proceed with normal flow               |
| `1`       | Validation errors found (lint) | Parse JSON for issue details, include in report           |
| `2+`      | CLI execution failure          | Report error to user, fall back to Strategy B if critical |

### Exit Code Patterns

**Success (exit 0)**:

```bash
RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    # Parse JSON and proceed
    echo "$RESULT" | jq '.results[]'
fi
```

**Validation errors (exit 1) - Still parse JSON**:

```bash
LINT_RESULT=$(${SDD_CLI_COMMAND} lint --json 2>&1)
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    # No issues found
    echo "✓ All structural checks passed"
elif [ $EXIT_CODE -eq 1 ]; then
    # Validation errors found - parse issues
    echo "$LINT_RESULT" | jq '.issues[]'
else
    # CLI execution failure
    echo "Error: CLI execution failed (exit $EXIT_CODE)"
fi
```

**CLI execution failure (exit >1)**:

```bash
SEARCH_RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
EXIT_CODE=$?
if [ $EXIT_CODE -gt 1 ]; then
    # Critical error - fall back to Strategy B
    echo "CLI execution failed. Falling back to LLM document scan."
    bash "${CLAUDE_PLUGIN_ROOT}/skills/${SKILL_NAME}/scripts/${FALLBACK_SCRIPT}.sh"
fi
```

## stderr vs stdout

### Output Stream Handling

- **stdout**: JSON output (search/lint results)
- **stderr**: CLI warnings, progress messages, errors
- **Redirect pattern**: `2>&1` merges stderr into stdout for combined capture

### Recommended Pattern

```bash
# Capture both stdout and stderr
RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)

# Separate JSON from error messages (if needed)
JSON_OUTPUT=$(echo "$RESULT" | jq '.' 2>/dev/null)
if [ $? -ne 0 ]; then
    # Not valid JSON - likely an error message
    echo "CLI error: $RESULT"
fi
```

### With --quiet Flag

Use `--quiet` to suppress progress messages on stderr:

```bash
${SDD_CLI_COMMAND} search --format json --quiet 2>&1
${SDD_CLI_COMMAND} lint --json --quiet 2>&1
```

## Common Error Scenarios

### 1. CLI Not Found

**Symptom**: `SDD_CLI_AVAILABLE="false"` or command not found error

**Action**: Fall back to Strategy B (LLM operations)

```bash
if [ "$SDD_CLI_AVAILABLE" != "true" ]; then
    # Strategy B: Manual document scan
    bash "${CLAUDE_PLUGIN_ROOT}/skills/${SKILL_NAME}/scripts/${FALLBACK_SCRIPT}.sh"
fi
```

### 2. JSON Parse Error

**Symptom**: CLI returns non-JSON output or malformed JSON

**Action**: Report raw output to user, fall back if critical

```bash
RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
JSON_CHECK=$(echo "$RESULT" | jq '.' 2>/dev/null)
if [ $? -ne 0 ]; then
    # JSON parse failed
    echo "Warning: CLI returned invalid JSON. Raw output:"
    echo "$RESULT"
    # Fall back to Strategy B for critical operations
fi
```

### 3. Empty Results (Valid Scenario)

**Symptom**: `search` returns `{"results": []}`

**Action**: Valid scenario (no matching documents found), proceed with appropriate handling

```bash
RESULT=$(${SDD_CLI_COMMAND} search --feature-id "${FEATURE}" --format json 2>&1)
COUNT=$(echo "$RESULT" | jq '.results | length')
if [ "$COUNT" -eq 0 ]; then
    # No documents found - valid scenario
    echo "No documents found for feature '${FEATURE}'"
    # Prompt user to create documents or handle gracefully
fi
```

### 4. Index Not Built

**Symptom**: `search` fails with "index not found" error

**Action**: Automatically build index, retry search

```bash
SEARCH_RESULT=$(${SDD_CLI_COMMAND} search --feature-id "${FEATURE}" --format json 2>&1)
if echo "$SEARCH_RESULT" | grep -q "index not found"; then
    # Build index and retry
    ${SDD_CLI_COMMAND} index 2>&1
    SEARCH_RESULT=$(${SDD_CLI_COMMAND} search --feature-id "${FEATURE}" --format json 2>&1)
fi
```

### 5. Permission Denied

**Symptom**: CLI fails with permission error

**Action**: Report to user, suggest troubleshooting

```bash
RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
if echo "$RESULT" | grep -qi "permission denied"; then
    echo "Error: Permission denied when accessing CLI."
    echo "Suggestion: Check file permissions or run with appropriate privileges."
    # Fall back to Strategy B
fi
```

### 6. Network Error (uvx CLI)

**Symptom**: CLI fails to download from GitHub (when using uvx)

**Action**: Report to user, fall back to Strategy B

```bash
RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
if echo "$RESULT" | grep -qi "network\|connection\|timeout"; then
    echo "Warning: Network error when accessing CLI. Falling back to LLM operations."
    # Fall back to Strategy B
fi
```

## Error Reporting to User

### Structured Error Messages

**Template**:

```markdown
⚠️ CLI Error

**Command**: `${SDD_CLI_COMMAND} search --format json`
**Exit Code**: 2
**Error Output**:
```

[raw CLI output]

```

**Action**: Falling back to LLM document scan (Strategy B).
```

### Integration with Skill Output

Include CLI errors in the skill's output report:

```markdown
## CLI Pre-Check Results

❌ **Structural Validation Failed**

CLI lint detected the following issues:

| Severity | Rule | File | Message |
|:---------|:-----|:-----|:--------|
| error | duplicate-id | `.sdd/requirement/user-login.md` | ID 'prd-user-auth' is duplicated |
| warning | orphan-reference | `.sdd/specification/user-login_spec.md` | Reference 'prd-old-feature' not found |

**Recommendation**: Resolve structural issues before proceeding with implementation.
```

## Timeout Handling

### Long-Running Operations

For large repositories, `search` and `lint` may take significant time.

**Pattern**: Set timeout for CLI operations

```bash
# Timeout after 30 seconds
timeout 30s ${SDD_CLI_COMMAND} search --format json 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
    echo "Warning: CLI search timed out. Falling back to targeted scan."
    # Fall back to Strategy B or limit scope
fi
```

## Retry Logic (Optional)

For transient errors (network issues, etc.), retry with exponential backoff.

**Pattern**:

```bash
MAX_RETRIES=3
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 1 ]; then
        # Success or validation errors (both valid)
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep $((2 ** RETRY_COUNT))  # Exponential backoff: 2s, 4s, 8s
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "CLI failed after $MAX_RETRIES retries. Falling back to Strategy B."
fi
```

## Graceful Degradation Strategy

### Fallback Hierarchy

1. **Primary**: CLI with full features (search + lint)
2. **Partial**: CLI search only (lint unavailable)
3. **Fallback**: Shell script + LLM operations (Strategy B)

**Implementation**:

```bash
# Try CLI search
if [ "$SDD_CLI_AVAILABLE" = "true" ]; then
    SEARCH_RESULT=$(${SDD_CLI_COMMAND} search --format json 2>&1)
    if [ $? -eq 0 ]; then
        # CLI search succeeded - try lint
        LINT_RESULT=$(${SDD_CLI_COMMAND} lint --json 2>&1)
        if [ $? -gt 1 ]; then
            # Lint failed, but search succeeded - partial CLI mode
            echo "Warning: CLI lint unavailable. Using search results only."
        fi
    else
        # CLI search failed - full fallback to Strategy B
        bash "${CLAUDE_PLUGIN_ROOT}/skills/${SKILL_NAME}/scripts/${FALLBACK_SCRIPT}.sh"
    fi
else
    # CLI not available - Strategy B
    bash "${CLAUDE_PLUGIN_ROOT}/skills/${SKILL_NAME}/scripts/${FALLBACK_SCRIPT}.sh"
fi
```

## Best Practices

1. **Always check exit codes**: Don't assume CLI commands succeed
2. **Validate JSON before parsing**: Use `jq '.'` to verify JSON validity
3. **Provide meaningful error messages**: Help users understand what went wrong
4. **Fall back gracefully**: Don't block the workflow if CLI fails
5. **Log CLI output for debugging**: Include raw output in error reports
6. **Use `--quiet` in CI/automation**: Suppress progress messages for cleaner logs
7. **Set reasonable timeouts**: Prevent hanging on large repositories

## Testing Error Scenarios

### Local Testing Commands

```bash
# Test CLI not available
unset SDD_CLI_AVAILABLE
# Run skill and verify Strategy B fallback

# Test invalid JSON
SDD_CLI_COMMAND="echo 'not json'"
# Run skill and verify error handling

# Test empty results
# Create empty .sdd directory, run search
# Verify graceful handling of no documents

# Test permission error
chmod 000 .sdd
# Run skill and verify error reporting
chmod 755 .sdd
```

---

**Last Updated**: 2026-03-03
**Maintained by**: AI-SDD Workflow Plugin
