# Result Format Template

## Checklist Item Update Format

When a verification passes:

```markdown
- [x] {original item text} ✅ Verified: {YYYY-MM-DD}
```

When a verification fails:

```markdown
- [ ] {original item text} ❌ Failed: {YYYY-MM-DD}
```

When manual verification is required:

```markdown
- [ ] {original item text} ⚠️ Manual verification required
```

When verification is skipped:

```markdown
- [ ] {original item text} ⏭️ Skipped: {reason}
```

## Automated Verification Result Block

Add after each CHK section that was verified:

```markdown
**Automated Verification Result**:
- Command: `{executed command}`
- Status: {PASSED | FAILED | SKIPPED}
- {Additional metrics if applicable}
- Executed: {YYYY-MM-DD HH:mm:ss}
```

### Examples by Category

#### Testing (CHK-5xx)

```markdown
**Automated Verification Result**:
- Command: `npm test -- --coverage`
- Status: PASSED
- Tests: 45 passed, 0 failed
- Coverage: 85.2% lines, 78.5% branches
- Executed: 2024-01-15 10:30:45
```

#### Implementation (CHK-4xx)

```markdown
**Automated Verification Result**:
- Command: `eslint . && tsc --noEmit`
- Status: PASSED
- Lint Errors: 0
- Type Errors: 0
- Executed: 2024-01-15 10:31:20
```

#### Security (CHK-7xx)

```markdown
**Automated Verification Result**:
- Command: `npm audit`
- Status: PASSED
- Vulnerabilities: 0 critical, 0 high, 2 moderate
- Executed: 2024-01-15 10:32:00
```

#### Law Proof (CHK-205, opt-in)

```markdown
**Automated Verification Result**:
- Command: `run-verification.py proof --laws-dir .sdd/laws/auth/user-login`
- Status: PASSED
- Laws directories: 1 checked (verdict: not-requested)
- Note: PASS means the reference model (main.bend) satisfies the approved laws. It does not prove the project's implementation.
- Warnings: 1 source drift (non-blocking): `sort_len` (§3.1.1) - consider re-running `/draft-laws`
- Recommendation: a human may move `laws-status` to `proven` (this skill never edits the spec)
- Executed: 2024-01-15 10:33:00
```

For SKIPPED (unapproved / expired approval) include the current hash from `reason`; for FAIL list each failing directory and its `reason` (e.g. orphan laws, disallowed import).

## Failure Details Format

When a verification fails, include details:

```markdown
**Automated Verification Result**:
- Command: `npm test`
- Status: FAILED
- Tests: 42 passed, 3 failed
- Failed Tests:
  - `auth.test.ts`: "should validate token expiry"
  - `user.test.ts`: "should reject invalid email"
  - `api.test.ts`: "should return 401 for unauthenticated"
- Executed: 2024-01-15 10:30:45
```
