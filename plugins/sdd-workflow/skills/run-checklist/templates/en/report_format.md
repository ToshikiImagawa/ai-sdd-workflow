# Verification Report Format

## Report Structure

```markdown
# Verification Report: {Feature Name}

## Summary

| Metric            | Value                    |
|:------------------|:-------------------------|
| Feature           | {feature-name}           |
| Ticket            | {ticket-number}          |
| Executed          | {YYYY-MM-DD HH:mm:ss}    |
| Total Items       | {total}                  |
| Verified          | {passed + failed count}  |
| Passed            | {passed count}           |
| Failed            | {failed count}           |
| Skipped           | {skipped count}          |
| Manual Required   | {manual count}           |

## Results by Category

### Testing Review (CHK-5xx)

| ID       | Priority | Status  | Details                    |
|:---------|:---------|:--------|:---------------------------|
| CHK-501  | P1       | ✅ PASS | 85.2% coverage             |
| CHK-502  | P1       | ✅ PASS | All integration tests pass |
| CHK-503  | P1       | ❌ FAIL | 2 edge cases missing       |

### Implementation Review (CHK-4xx)

| ID       | Priority | Status  | Details                    |
|:---------|:---------|:--------|:---------------------------|
| CHK-401  | P1       | ✅ PASS | No lint errors             |
| CHK-402  | P1       | ✅ PASS | Type check passed          |

### Security Review (CHK-7xx)

| ID       | Priority | Status  | Details                    |
|:---------|:---------|:--------|:---------------------------|
| CHK-701  | P1       | ✅ PASS | No vulnerabilities found   |
| CHK-702  | P1       | ⚠️ SKIP | Auth testing requires manual review |

## Command Execution Log

### npm test -- --coverage
- Exit Code: 0
- Duration: 12.5s
- Output Summary:
  ```
  Test Suites: 5 passed, 5 total
  Tests:       45 passed, 45 total
  Coverage:    85.2% statements, 78.5% branches
  ```

### eslint .
- Exit Code: 0
- Duration: 3.2s
- Output Summary:
  ```
  ✔ No problems found
  ```

## Failed Verifications

### CHK-503 [P1] Edge Case Testing

**Reason**: Missing test coverage for boundary conditions

**Details**:
- Missing test for empty array input
- Missing test for maximum value overflow

**Recommendation**: Add edge case tests before merge

## Manual Verification Required

The following items require manual review:

| ID       | Category          | Reason                              |
|:---------|:------------------|:------------------------------------|
| CHK-103  | Requirements      | Acceptance criteria validation      |
| CHK-304  | Design            | Integration point verification      |
| CHK-702  | Security          | Authentication flow review          |

## Next Steps

1. Fix failed verifications (CHK-503)
2. Complete manual verifications
3. Re-run `/run-checklist` to update status
4. Proceed to PR review when all P1 items pass
```
