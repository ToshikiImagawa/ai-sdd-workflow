# CLI Error Handling

## Exit Codes

| Code | Meaning | Action |
|:-----|:--------|:-------|
| 0 | Success | Parse JSON output normally |
| 1 | General error | Log error, fall back to non-CLI approach |
| 2 | Invalid arguments | Fix command arguments and retry |
| 3 | No documents found | Report to user (not necessarily an error) |
| 4 | Configuration error | Check `.sdd-config.json` |

## Error Handling Strategy

### Retry Policy

- **Max retries**: 1 (retry once on transient errors)
- **Retryable errors**: Exit code 1 (general error)
- **Non-retryable errors**: Exit codes 2, 3, 4

### Fallback Strategy

When CLI command fails after retry:

1. Log the CLI error for debugging
2. Fall back to non-CLI approach (Glob/Grep/Read)
3. Continue execution without interruption

**IMPORTANT**: CLI failure should never block skill execution. Always have a fallback path.

- On success: parse JSON, continue with CLI results
- On retryable failure: retry once, then fall back to Glob/Grep/Read
- On non-retryable failure or invalid JSON output: log and fall back immediately

## Timeout Handling

- CLI commands should complete within 30 seconds
- If timeout occurs, fall back to non-CLI approach
- Use `timeout 30` prefix for Bash commands if needed
