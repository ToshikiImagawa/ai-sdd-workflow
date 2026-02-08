# Constitution Compliance Report Example

This example shows the expected output format for `/constitution validate`.

```markdown
# Constitution Compliance Report

**Constitution Version**: 2.0.0
**Validation Date**: YYYY-MM-DD
**Project**: {Project Name}

## Compliance Summary

| Principle | Status | Score |
|:---|:---|:---|
| P1: Specification-First | Compliant | 95% |
| P2: Test-First | Partial | 78% |
| P3: Library-First | Compliant | 100% |
| P4: API Versioning | Non-Compliant | 45% |

## Detailed Analysis

### P1: Specification-First Development

**Status**: Compliant (95%)

**Verification**:

- [x] All features have specifications
- [x] Specs exist before implementation
- [ ] 2 legacy features missing specs (user-profile, settings)

**Recommendations**:

- Create specs for legacy features: user-profile, settings
- Run `/generate-spec` for these features

---

### P2: Test-First Implementation

**Status**: Partial Compliance (78%)

**Verification**:

- [x] Test coverage >=80% (Current: 78.3%)
- [ ] Not all features follow TDD commit pattern
- [x] Code review includes test verification

**Recommendations**:

- Increase coverage by 1.7% to meet threshold
- Enforce commit message convention for new code
- Focus on user-profile module (current coverage: 65%)

---

### P4: API Versioning

**Status**: Non-Compliant (45%)

**Verification**:

- [ ] Only 45% of APIs include version numbers
- [ ] No versioning strategy documented
- [x] Breaking changes are documented

**Recommendations**:

- Document API versioning strategy in constitution
- Add version prefix to all API endpoints
- Create migration guide for breaking changes

---

## Action Items

### Critical (Block Deployment)

1. **P4 Compliance**: Implement API versioning
    - Add `/api/v1/` prefix to all endpoints
    - Document versioning strategy
    - Update client code

### High Priority

2. **P2 Compliance**: Increase test coverage to 80%+
    - Focus on user-profile module
    - Add edge case tests

3. **P1 Compliance**: Create missing specifications
    - user-profile feature
    - settings feature

### Medium Priority

4. Enforce commit message convention
5. Update code review checklist

## Next Steps

1. Address critical action items
2. Re-run validation after fixes
3. Update constitution if patterns emerge
```
