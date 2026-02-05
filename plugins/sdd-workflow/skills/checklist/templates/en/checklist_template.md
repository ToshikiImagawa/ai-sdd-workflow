# Quality Checklist: {Feature Name}

## Meta Information

| Item              | Content                                  |
|:------------------|:-----------------------------------------|
| Feature Name      | {Feature Name}                           |
| Ticket Number     | {Ticket Number}                          |
| Specification     | `.sdd/specification/{feature}_spec.md`   |
| Design Document   | `.sdd/specification/{feature}_design.md` |
| Generated Date    | YYYY-MM-DD                               |
| Checklist Version | 1.0                                      |

## Checklist Summary

| Category              | Total Items | P0 | P1 | P2 | P3 |
|:----------------------|:------------|:---|:---|:---|:---|
| Requirements Review   | -           | -  | -  | -  | -  |
| Specification Review  | -           | -  | -  | -  | -  |
| Design Review         | -           | -  | -  | -  | -  |
| Implementation Review | -           | -  | -  | -  | -  |
| Testing Review        | -           | -  | -  | -  | -  |
| Documentation Review  | -           | -  | -  | -  | -  |
| Security Review       | -           | -  | -  | -  | -  |
| Performance Review    | -           | -  | -  | -  | -  |
| Deployment Review     | -           | -  | -  | -  | -  |

**Priority Levels**:

- **P0**: Critical - Must pass before merge
- **P1**: High - Should pass before merge
- **P2**: Medium - Should pass before release
- **P3**: Low - Nice to have

---

## Requirements Review

### CHK001 [P0] - Functional Requirements Coverage

- [ ] All functional requirements (FR-xxx) from PRD are implemented
- [ ] Each requirement maps to specific implementation
- [ ] No requirements are partially implemented

**Verification**:

- Review PRD
- Check implementation coverage
- Run `/check_spec {feature}` for consistency

---

### CHK002 [P0] - Non-Functional Requirements

- [ ] Performance requirements (NFR-xxx) are met
- [ ] Security requirements are implemented
- [ ] Scalability requirements are addressed

**Verification**:

- Review NFR specifications
- Run performance tests
- Review security audit results

---

### CHK003 [P1] - Acceptance Criteria

- [ ] All acceptance criteria from PRD are met
- [ ] Edge cases identified in PRD are handled
- [ ] User scenarios are validated

**Verification**:

- Run end-to-end tests
- Manual user flow testing

---

## Specification Review

### CHK004 [P0] - Public API Implementation

- [ ] All APIs defined in spec are implemented
- [ ] API signatures match specification exactly
- [ ] Return types match specification

**Verification**:

```bash
# Compare implementation with spec
```

**Reference**: Specification § Public API

---

### CHK005 [P0] - Data Model Consistency

- [ ] Type definitions match specification
- [ ] Required fields are enforced
- [ ] Optional fields are properly handled
- [ ] Field constraints are validated

**Verification**:

- Compare implementation types with spec types
- Check database schema matches spec
- Verify validation logic

---

### CHK006 [P0] - Behavior Alignment

- [ ] Sequence diagrams in spec are followed
- [ ] State transitions match specification
- [ ] Error handling follows spec patterns

**Verification**:

- Trace code execution flow
- Compare with sequence diagrams

---

### CHK007 [P1] - Constraint Enforcement

- [ ] All constraints in spec are implemented
- [ ] Boundary conditions are handled
- [ ] Invalid inputs are rejected appropriately

**Verification**:

- Review constraint tests
- Test boundary values

---

## Design Review

### CHK008 [P0] - Architecture Alignment

- [ ] Module structure matches design document
- [ ] Layer separation is maintained
- [ ] Dependencies flow in correct direction

**Verification**:

- Compare directory structure with design doc
- Review import statements
- Check for circular dependencies

---

### CHK009 [P0] - Technology Stack Compliance

- [ ] All specified libraries are used
- [ ] No unapproved dependencies added
- [ ] Version constraints are followed

**Verification**:

- Compare dependencies with design doc

---

### CHK010 [P1] - Design Decisions Documented

- [ ] All significant design decisions are documented
- [ ] Rationale for decisions is clear
- [ ] Trade-offs are explained
- [ ] Alternatives considered are noted

**Verification**:

- Review "Design Decisions" section

---

### CHK011 [P1] - Integration Points Verified

- [ ] External API integrations are tested
- [ ] Database connections are configured
- [ ] Message queue connections work
- [ ] Third-party service integrations are verified

**Verification**:

- Run integration tests
- Check configuration files

---

## Implementation Review

### CHK012 [P0] - Code Structure

- [ ] Code follows project conventions
- [ ] Naming is clear and consistent
- [ ] No dead code or commented-out blocks
- [ ] File organization is logical

**Verification**:

- Code review
- Run linter

---

### CHK013 [P0] - Error Handling

- [ ] All error cases are handled
- [ ] Errors are logged appropriately
- [ ] User-facing errors are clear
- [ ] No silent failures

**Verification**:

- Review error handling code
- Test error scenarios

---

### CHK014 [P1] - Code Quality

- [ ] No code smells detected
- [ ] Complexity is reasonable
- [ ] No duplicate code
- [ ] Functions are single-purpose

**Verification**:

- Run static analysis tools
- Review cyclomatic complexity

---

## Testing Review

### CHK015 [P0] - Unit Test Coverage

- [ ] Unit tests exist for all business logic
- [ ] Code coverage ≥ 80%
- [ ] All public functions are tested
- [ ] Edge cases are covered

**Verification**:

```bash
# Run test coverage
```

**Target**: ≥80% line coverage

---

### CHK016 [P0] - Integration Tests

- [ ] Integration tests cover all main flows
- [ ] External service mocks are realistic
- [ ] Database operations are tested
- [ ] API endpoints are tested

**Verification**:

- Run integration test suite
- Review test scenarios

---

### CHK017 [P0] - Edge Case Testing

- [ ] Null/undefined inputs tested
- [ ] Empty collections tested
- [ ] Maximum/minimum values tested
- [ ] Concurrent operations tested

**Verification**:

- Review edge case test suite
- Check boundary value tests

---

### CHK018 [P1] - Non-Functional Testing

- [ ] Performance tests pass
- [ ] Load tests pass
- [ ] Security tests pass
- [ ] Accessibility tests pass (if applicable)

**Verification**:

- Run performance benchmarks
- Execute load testing

---

## Documentation Review

### CHK019 [P1] - Code Comments

- [ ] Complex logic is commented
- [ ] Public APIs have documentation
- [ ] Non-obvious decisions are explained
- [ ] TODOs are tracked (or removed)

**Verification**:

- Review code comments
- Check documentation coverage

---

### CHK020 [P1] - Design Document Updated

- [ ] Design doc reflects implementation
- [ ] Recent decisions are documented
- [ ] Diagrams are up-to-date
- [ ] Change history is maintained

**Verification**:

- Review design document
- Compare with implementation

---

## Security Review

### CHK021 [P0] - Input Validation

- [ ] All user inputs are validated
- [ ] SQL injection prevention in place
- [ ] XSS prevention in place
- [ ] CSRF protection implemented (if applicable)

**Verification**:

- Review validation code
- Run security scanners

---

### CHK022 [P0] - Authentication & Authorization

- [ ] Authentication is required where needed
- [ ] Authorization checks are in place
- [ ] Role-based access control works
- [ ] Session management is secure

**Verification**:

- Test with different user roles
- Check unauthorized access attempts

---

### CHK023 [P0] - Data Protection

- [ ] Sensitive data is encrypted
- [ ] Passwords are hashed (never plain text)
- [ ] API keys are not hardcoded
- [ ] PII is handled appropriately

**Verification**:

- Review encryption implementation
- Check environment variables

---

## Performance Review

### CHK024 [P1] - Response Time

- [ ] API response times meet requirements
- [ ] Database queries are optimized
- [ ] N+1 query problems are avoided
- [ ] Caching is implemented where appropriate

**Verification**:

- Run performance profiling
- Check database query plans

---

### CHK025 [P2] - Resource Usage

- [ ] Memory usage is reasonable
- [ ] No memory leaks detected
- [ ] CPU usage is acceptable
- [ ] Network bandwidth is efficient

**Verification**:

- Run resource monitoring
- Profile memory usage

---

## Deployment Review

### CHK026 [P0] - Configuration Management

- [ ] Environment variables are documented
- [ ] Configuration files are correct
- [ ] Secrets are properly managed
- [ ] Feature flags are configured (if applicable)

**Verification**:

- Review configuration documentation
- Verify secrets management

---

### CHK027 [P0] - Database Migrations

- [ ] Migrations are tested
- [ ] Rollback migrations exist
- [ ] Data migration is safe
- [ ] No data loss risk

**Verification**:

- Run migrations in test environment
- Test rollback process

---

### CHK028 [P0] - Deployment Plan

- [ ] Deployment steps are documented
- [ ] Rollback plan exists
- [ ] Monitoring is in place
- [ ] Alerts are configured

**Verification**:

- Review deployment documentation
- Test rollback procedure

---

## Completion Criteria

### Pre-PR Checklist

All P0 items must be complete:

- [ ] All P0 items checked
- [ ] All tests passing
- [ ] Spec consistency verified
- [ ] Ready for code review

### Pre-Merge Checklist

All P0 and P1 items must be complete:

- [ ] All P0 items checked
- [ ] All P1 items checked
- [ ] Code review approved
- [ ] CI/CD pipeline green
- [ ] Ready for merge

### Pre-Release Checklist

All items through P2 should be complete:

- [ ] All P0 items checked
- [ ] All P1 items checked
- [ ] All P2 items checked
- [ ] QA sign-off
- [ ] Ready for production deployment

---

## Notes

- This checklist is a template; customize based on project needs
- Add project-specific items as needed
- Remove items not applicable to your context
- Update checklist if requirements change

---

## Reference Documents

- PRD: `.sdd/requirement/[{path}/]{name}.md` (if exists)
- Abstract Specification: `.sdd/specification/[{path}/]{name}_spec.md`
- Technical Design: `.sdd/specification/[{path}/]{name}_design.md`

※ For hierarchical structure, parent features use `index.md`, `index_spec.md`, `index_design.md`
