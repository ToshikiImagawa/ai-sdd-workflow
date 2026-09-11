# Quality Checklist: {Feature Name}

## Meta Information

| Item              | Content                                  |
|:------------------|:-----------------------------------------|
| Feature Name      | {Feature Name}                           |
| Ticket Number     | {Ticket Number}                          |
| Specification     | `${SDD_SPECIFICATION_PATH}/{feature}_spec.md`   |
| Design Draft      | `${SDD_TASK_PATH}/{ticket}/design-draft.md` (omit if already deleted) |
| v4.x Design Doc   | `${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_design.md` (omit if the project has none) |
| Generated Date    | YYYY-MM-DD                               |
| Checklist Version | 1.0                                      |

## Checklist Summary

| Category              | Total Items | P1 | P2 | P3 |
|:----------------------|:------------|:---|:---|:---|
| Requirements Review   | -           | -  | -  | -  |
| Specification Review  | -           | -  | -  | -  |
| Design Review         | -           | -  | -  | -  |
| Implementation Review | -           | -  | -  | -  |
| Testing Review        | -           | -  | -  | -  |
| Documentation Review  | -           | -  | -  | -  |
| Security Review       | -           | -  | -  | -  |
| Performance Review    | -           | -  | -  | -  |
| Deployment Review     | -           | -  | -  | -  |

**Priority Levels** — record here whether you actually compared this definition against the SKILL.md
body and found them consistent, or found and resolved a discrepancy (do not copy this line verbatim as
if that comparison had been performed):

- **P1 - High**: Must pass before merge (checked before PR creation)
- **P2 - Medium**: Should pass before merge (checked during PR review)
- **P3 - Low**: Nice to have (checked opportunistically)

**Category-to-ID mapping** (`CHK-{category}{seq}` format; `run-checklist`'s verification logic depends on this mapping):

`CHK-1xx`=Requirements, `CHK-2xx`=Specification, `CHK-3xx`=Design, `CHK-4xx`=Implementation, `CHK-5xx`=Testing,
`CHK-6xx`=Documentation, `CHK-7xx`=Security, `CHK-8xx`=Performance, `CHK-9xx`=Deployment

**Basis** (per item, required): which document and statement the item was extracted from
(e.g. `PRD FR-003`, `design §6 Architecture`), or `synthesized from: {component}` when derived from an
implementation component's existence rather than quoted from a document.

---

## Requirements Review

### CHK-101 [P1] Functional Requirements Coverage

- [ ] All functional requirements (FR-xxx) from PRD are implemented
- [ ] Each requirement maps to specific implementation
- [ ] No requirements are partially implemented

**Basis**: PRD FR-xxx (extracted)

**Verification**:

- Review PRD
- Check implementation coverage
- Run `/check-spec {feature}` for consistency

---

### CHK-102 [P1] Non-Functional Requirements

- [ ] Performance requirements (NFR-xxx) are met
- [ ] Security requirements are implemented
- [ ] Scalability requirements are addressed

**Basis**: PRD NFR-xxx (extracted)

**Verification**:

- Review NFR specifications
- Run performance tests
- Review security audit results

---

### CHK-103 [P2] Acceptance Criteria

- [ ] All acceptance criteria from PRD are met
- [ ] Edge cases identified in PRD are handled
- [ ] User scenarios are validated

**Verification**:

- Run end-to-end tests
- Manual user flow testing

---

### CHK-104 [P1] CONSTITUTION.md Compliance

- [ ] The applicable principles from `CONSTITUTION.md` are stated in the Spec/Design doc
- [ ] The implementation complies with the stated principles
- [ ] Any deviation from a principle follows the exception process (justification, review approval)

**Verification**:

- Run `/constitution validate`
- Review the "Principle Alignment" section of the Spec/Design doc

---

### CHK-105 [P2] Template Sync with Constitution

- [ ] SPECIFICATION_TEMPLATE.md / DESIGN_DOC_TEMPLATE.md in use is aligned with the latest CONSTITUTION.md version
- [ ] No missing updates due to `/constitution sync` not being run

**Verification**:

- Compare CONSTITUTION.md change history with each template's last update date

---

## Specification Review

### CHK-201 [P1] Public API Implementation

- [ ] All APIs defined in spec are implemented
- [ ] API signatures match specification exactly
- [ ] Return types match specification

**Verification**:

```bash
# Compare implementation with spec
```

**Reference**: Specification § Public API

---

### CHK-202 [P1] Data Model Consistency

- [ ] Type definitions match specification
- [ ] Required fields are enforced
- [ ] Optional fields are properly handled
- [ ] Field constraints are validated

**Verification**:

- Compare implementation types with spec types
- Check database schema matches spec
- Verify validation logic

---

### CHK-203 [P1] Behavior Alignment

- [ ] Sequence diagrams in spec are followed
- [ ] State transitions match specification
- [ ] Error handling follows spec patterns

**Verification**:

- Trace code execution flow
- Compare with sequence diagrams

---

### CHK-204 [P2] Constraint Enforcement

- [ ] All constraints in spec are implemented
- [ ] Boundary conditions are handled
- [ ] Invalid inputs are rejected appropriately

**Verification**:

- Review constraint tests
- Test boundary values

---

## Design Review

### CHK-301 [P1] Architecture Alignment

- [ ] Module structure matches design document
- [ ] Layer separation is maintained
- [ ] Dependencies flow in correct direction

**Verification**:

- Compare directory structure with design doc
- Review import statements
- Check for circular dependencies

---

### CHK-302 [P1] Technology Stack Compliance

- [ ] All specified libraries are used
- [ ] No unapproved dependencies added
- [ ] Version constraints are followed

**Verification**:

- Compare dependencies with design doc

---

### CHK-303 [P2] Design Decisions Documented

- [ ] All significant design decisions are documented
- [ ] Rationale for decisions is clear
- [ ] Trade-offs are explained
- [ ] Alternatives considered are noted

**Verification**:

- Review "Design Decisions" section

---

### CHK-304 [P2] Integration Points Verified

- [ ] External API integrations are tested
- [ ] Database connections are configured
- [ ] Message queue connections work
- [ ] Third-party service integrations are verified

**Verification**:

- Run integration tests
- Check configuration files

---

## Implementation Review

### CHK-401 [P1] Code Structure

- [ ] Code follows project conventions
- [ ] Naming is clear and consistent
- [ ] No dead code or commented-out blocks
- [ ] File organization is logical

**Verification**:

- Code review
- Run linter

---

### CHK-402 [P1] Error Handling

- [ ] All error cases are handled
- [ ] Errors are logged appropriately
- [ ] User-facing errors are clear
- [ ] No silent failures

**Verification**:

- Review error handling code
- Test error scenarios

---

### CHK-403 [P2] Code Quality

- [ ] No code smells detected
- [ ] Complexity is reasonable
- [ ] No duplicate code
- [ ] Functions are single-purpose

**Verification**:

- Run static analysis tools
- Review cyclomatic complexity

---

## Testing Review

### CHK-501 [P1] Unit Test Coverage

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

### CHK-502 [P1] Integration Tests

- [ ] Integration tests cover all main flows
- [ ] External service mocks are realistic
- [ ] Database operations are tested
- [ ] API endpoints are tested

**Verification**:

- Run integration test suite
- Review test scenarios

---

### CHK-503 [P1] Edge Case Testing

- [ ] Null/undefined inputs tested
- [ ] Empty collections tested
- [ ] Maximum/minimum values tested
- [ ] Concurrent operations tested

**Verification**:

- Review edge case test suite
- Check boundary value tests

---

### CHK-504 [P2] Non-Functional Testing

- [ ] Performance tests pass
- [ ] Load tests pass
- [ ] Security tests pass
- [ ] Accessibility tests pass (if applicable)

**Verification**:

- Run performance benchmarks
- Execute load testing

---

## Documentation Review

### CHK-601 [P2] Code Comments

- [ ] Complex logic is commented
- [ ] Public APIs have documentation
- [ ] Non-obvious decisions are explained
- [ ] TODOs are tracked (or removed)

**Verification**:

- Review code comments
- Check documentation coverage

---

### CHK-602 [P2] Design Document Updated

- [ ] Design doc reflects implementation
- [ ] Recent decisions are documented
- [ ] Diagrams are up-to-date
- [ ] Change history is maintained

**Verification**:

- Review design document
- Compare with implementation

---

## Security Review

### CHK-701 [P1] Input Validation

- [ ] All user inputs are validated
- [ ] SQL injection prevention in place
- [ ] XSS prevention in place
- [ ] CSRF protection implemented (if applicable)

**Verification**:

- Review validation code
- Run security scanners

---

### CHK-702 [P1] Authentication & Authorization

- [ ] Authentication is required where needed
- [ ] Authorization checks are in place
- [ ] Role-based access control works
- [ ] Session management is secure

**Verification**:

- Test with different user roles
- Check unauthorized access attempts

---

### CHK-703 [P1] Data Protection

- [ ] Sensitive data is encrypted
- [ ] Passwords are hashed (never plain text)
- [ ] API keys are not hardcoded
- [ ] PII is handled appropriately

**Verification**:

- Review encryption implementation
- Check environment variables

---

## Performance Review

### CHK-801 [P2] Response Time

- [ ] API response times meet requirements
- [ ] Database queries are optimized
- [ ] N+1 query problems are avoided
- [ ] Caching is implemented where appropriate

**Verification**:

- Run performance profiling
- Check database query plans

---

### CHK-802 [P3] Resource Usage

- [ ] Memory usage is reasonable
- [ ] No memory leaks detected
- [ ] CPU usage is acceptable
- [ ] Network bandwidth is efficient

**Verification**:

- Run resource monitoring
- Profile memory usage

---

## Deployment Review

### CHK-901 [P1] Configuration Management

- [ ] Environment variables are documented
- [ ] Configuration files are correct
- [ ] Secrets are properly managed
- [ ] Feature flags are configured (if applicable)

**Verification**:

- Review configuration documentation
- Verify secrets management

---

### CHK-902 [P1] Database Migrations

- [ ] Migrations are tested
- [ ] Rollback migrations exist
- [ ] Data migration is safe
- [ ] No data loss risk

**Verification**:

- Run migrations in test environment
- Test rollback process

---

### CHK-903 [P2] Deployment Plan

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

All P1 items must be complete:

- [ ] All P1 items checked
- [ ] All tests passing
- [ ] Spec consistency verified
- [ ] Ready for code review

### Pre-Merge Checklist

All P1 and P2 items must be complete:

- [ ] All P1 items checked
- [ ] All P2 items checked
- [ ] Code review approved
- [ ] CI/CD pipeline green
- [ ] Ready for merge

### Pre-Release Checklist

All items (including P3) should be complete:

- [ ] All P1 items checked
- [ ] All P2 items checked
- [ ] All P3 items checked
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

- PRD: `${SDD_REQUIREMENT_PATH}/[{path}/]{name}.md` (if exists)
- Abstract Specification: `${SDD_SPECIFICATION_PATH}/[{path}/]{name}_spec.md`
- Technical Design Draft: `${SDD_TASK_PATH}/{ticket}/design-draft.md` (temporary; omit this line if it was
  already deleted at implementation completion)
- v4.x Persistent Design Doc: `${SDD_SPECIFICATION_PATH}/[{path}/]{name}_design.md` (supplementary input in a
  project carried over from v4.x; omit this line if the project has none)

※ For hierarchical structure, parent features use `index.md`, `index_spec.md`, `index_design.md`. The design
draft is ticket-scoped, so its path is the same in both structures
