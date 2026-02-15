# Example: Case A (Existing Documents)

This example demonstrates `/plan-refactor` usage when PRD, spec, and design documents already exist.

## Scenario

**Feature:** User authentication module
**Problem:** Current implementation has tight coupling between auth and session management, making it hard to test and extend.
**Existing Docs:**
- `.sdd/requirement/auth.md` (PRD exists)
- `.sdd/specification/auth_spec.md` (Spec exists)
- `.sdd/specification/auth_design.md` (Design exists)

## Command

```bash
/plan-refactor auth
```

## Expected Behavior

### Phase 1: Pre-flight Checks

```
[plan-refactor] Running document scan...
[scan-existing-docs] Scanning for: auth
[scan-existing-docs] Structure: flat
[scan-existing-docs] PRD: true, Spec: true, Design: true

Detected: Case A (Existing documents found)
```

### Phase 2: Implementation Discovery

```
[plan-refactor] Searching for implementation files...
[find-implementation-files] Found 8 files
- src/auth/login.ts
- src/auth/session.ts
- src/auth/middleware.ts
- tests/auth/login.test.ts
- ...
```

### Phase 3: Analysis and Plan Generation

Claude reads:
1. `.sdd/requirement/auth.md` - Understands original requirements
2. `.sdd/specification/auth_spec.md` - Reviews functional specs
3. `.sdd/specification/auth_design.md` - Analyzes current design
4. Implementation files (`src/auth/*.ts`) - Compares with design

Claude identifies:
- **Gap 1:** Session management is tightly coupled to auth logic
- **Gap 2:** Hard to mock for unit testing
- **Gap 3:** Violates Single Responsibility Principle

### Phase 4: Design Doc Update

Claude edits `.sdd/specification/auth_design.md` and appends:

```markdown
## Refactoring Plan

### Purpose and Background

**Why Refactoring is Needed:**

The current authentication module tightly couples session management with auth logic, making it difficult to:
- Write isolated unit tests
- Extend with new auth providers (OAuth, SAML)
- Maintain and debug

**Business/Technical Drivers:**
- New feature request: Add OAuth support (PR #123)
- Technical debt: High coupling score (8/10)
- Testing difficulty: Only 45% unit test coverage due to tight coupling

### Current State Analysis

**Problems Identified:**

1. **Tight Coupling between Auth and Session** (Severity: High)
   - Description: `LoginService` directly instantiates `SessionManager`, making it impossible to test in isolation
   - Impact: Cannot write unit tests without database; slow test execution (5s per test)
   - Location: `src/auth/login.ts:45-67`

2. **Hard-coded Dependencies** (Severity: Medium)
   - Description: Auth providers are hard-coded, not configurable
   - Impact: Cannot add new auth methods without modifying core logic
   - Location: `src/auth/providers.ts:12-30`

**Code Quality Metrics:**
- Cyclomatic complexity: 12 (target: <10)
- Code duplication: 23% (validation logic repeated across files)
- Test coverage: 45% (target: >80%)

### Refactoring Strategy

**Goals:**

1. Decouple session management from authentication logic
2. Introduce dependency injection for testability
3. Extract auth providers into a plugin system

**Approach:**

- **Pattern:** Dependency Injection + Strategy Pattern
- **Technique:** Extract Interface → Inject Dependencies → Replace Implementation

**Trade-offs:**

| Aspect | Before | After | Trade-off |
|:--|:--|:--|:--|
| Complexity | Low (monolithic) | Medium (more classes) | Increased initial complexity, better maintainability |
| Performance | Fast (direct calls) | Fast (negligible DI overhead) | No significant impact |
| Testability | Poor (45% coverage) | Good (target 80%+) | Easier to write tests |

### Migration Plan

**Phase 1: Preparation** (Estimated: 3 days)

- **Task 1.1:** Add integration tests for current behavior
- **Task 1.2:** Document current API contracts
- **Task 1.3:** Set up feature flag `NEW_AUTH_SYSTEM`

**Phase 2: Refactoring** (Estimated: 5 days)

- **Task 2.1:** Extract `ISessionManager` interface
- **Task 2.2:** Refactor `LoginService` to accept `ISessionManager` via constructor
- **Task 2.3:** Extract auth providers to plugin system
- **Task 2.4:** Update tests to use mocks

**Phase 3: Validation** (Estimated: 2 days)

- **Task 3.1:** Verify all tests pass
- **Task 3.2:** Performance benchmark (login latency <200ms target)
- **Task 3.3:** Code review
- **Task 3.4:** Remove feature flag after 1 week in production

**Phase 4: Deployment** (Estimated: 3 days)

- **Task 4.1:** Deploy to staging
- **Task 4.2:** Smoke tests
- **Task 4.3:** Gradual rollout (10% → 50% → 100%)
- **Task 4.4:** Monitor for 1 week

### Impact Analysis

**Breaking Changes:**

- [x] Internal API only (no external impact)

**Affected Components:**

| Component | Type | Impact | Mitigation |
|:--|:--|:--|:--|
| `LoginService` | Internal | Constructor signature changes | Update all instantiation sites |
| `SessionManager` | Internal | Now interface-based | Existing implementations work as-is |

**Rollback Plan:**

1. Revert to commit `abc123` (before refactoring)
2. Re-enable old implementation via feature flag
3. Notify team via Slack #auth-updates

**Rollback Trigger Criteria:**
- Error rate > 2%
- Login latency > 500ms

### Testing Strategy

**Unit Tests:**
- Mock `ISessionManager` and verify auth logic in isolation

**Integration Tests:**
- Test full auth flow with real database

**Manual Testing:**
- [ ] Test login with username/password
- [ ] Test logout
- [ ] Test session expiry

### Success Criteria

**Metrics:**

| Metric | Current | Target | Measurement Method |
|:--|:--|:--|:--|
| Code complexity | 12 | <10 | SonarQube |
| Test coverage | 45% | 80%+ | Jest coverage |
| Duplication | 23% | <10% | SonarQube |

**Acceptance Criteria:**

- [ ] All existing functionality preserved
- [ ] All tests pass (unit + integration)
- [ ] Code review approved by 2 engineers
- [ ] Performance within 10% of baseline
```

### Phase 5: Next Steps

```
✅ Refactoring plan added to auth_design.md

Next steps:
1. Review the plan at: .sdd/specification/auth_design.md
2. Run `/task-breakdown auth` to create actionable tasks
3. Execute tasks with `/implement auth`
```

## Notes

- In Case A, existing documents provide context for better refactoring plans
- Claude understands original intent from PRD and compares with current implementation
- Refactoring plan is integrated into existing design doc, maintaining traceability
