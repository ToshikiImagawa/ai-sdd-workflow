---
description: "Generate quality assurance checklists from specifications and plans with structured IDs and categories"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Checklist - Quality Checklist Generation

Automatically generates comprehensive quality assurance checklists from specifications, design documents, and task
breakdowns.

## Prerequisites

**Before execution, you must read the AI-SDD principles document.**

AI-SDD principles document path (search in the following order and use the first file found):
1. `.sdd/AI-SDD-PRINCIPLES.md` (from project root - for plugin users)
2. `../AI-SDD-PRINCIPLES.md` (relative path from this file - for plugin development)
3. `plugins/sdd-workflow/AI-SDD-PRINCIPLES.md` (from project root - for plugin development)

Understand AI-SDD principles.

This command follows AI-SDD principles for quality assurance.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value        | Description                    |
|:-------------------------|:---------------------|:-------------------------------|
| `SDD_ROOT`               | `.sdd`               | Root directory                 |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | PRD/Requirements directory     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`          | Task log directory             |

**Path Resolution Priority:**

1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or
configuration file exists.

## Input

$ARGUMENTS

### Input Format

```
/checklist {feature-name} {ticket-number}
/checklist {feature-name}  # Uses feature-name as ticket directory
```

### Input Examples

```
/checklist user-auth TICKET-123
/checklist task-management
/checklist auth/user-login TICKET-789  # For hierarchical structure
```

## Processing Flow

### 1. Load Source Documents

Both flat and hierarchical structures are supported.

**For flat structure**:

```
Load .sdd/requirement/{feature-name}.md (PRD, if exists)
Load .sdd/specification/{feature-name}_spec.md (required)
Load .sdd/specification/{feature-name}_design.md (required)
Load .sdd/task/{ticket}/tasks.md (if exists)
```

**For hierarchical structure** (when argument contains `/`):

```
Load .sdd/requirement/{parent-feature}/index.md (parent feature PRD, if exists)
Load .sdd/requirement/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load .sdd/specification/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load .sdd/specification/{parent-feature}/{feature-name}_spec.md (child feature spec, required)
Load .sdd/specification/{parent-feature}/index_design.md (parent feature design, if exists)
Load .sdd/specification/{parent-feature}/{feature-name}_design.md (child feature design, required)
Load .sdd/task/{ticket}/tasks.md (if exists)
```

**⚠️ Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

### 2. Extract Verification Points

From each document, extract checkable items:

**From PRD** (if exists):

| Extract Item                          | Purpose                     |
|:--------------------------------------|:----------------------------|
| Functional Requirements (FR-xxx)      | Verify feature completeness |
| Non-Functional Requirements (NFR-xxx) | Verify quality attributes   |
| Acceptance Criteria                   | Verify business value       |

**From Abstract Specification**:

| Extract Item       | Purpose                         |
|:-------------------|:--------------------------------|
| Public APIs        | Verify interface implementation |
| Data Models        | Verify type definitions         |
| Behavior Contracts | Verify sequence flows           |
| Constraints        | Verify edge case handling       |

**From Technical Design**:

| Extract Item       | Purpose                       |
|:-------------------|:------------------------------|
| Module Structure   | Verify architecture alignment |
| Technology Stack   | Verify dependencies           |
| Design Decisions   | Verify rationale documented   |
| Integration Points | Verify external connections   |

**From Task Breakdown** (if exists):

| Extract Item        | Purpose                      |
|:--------------------|:-----------------------------|
| Completion Criteria | Verify task-level acceptance |
| Dependencies        | Verify implementation order  |
| Test Requirements   | Verify test coverage         |

### 3. Generate Checklist Items

Transform extracted points into actionable checklist items:

**ID Assignment Format**: `CHK-{category}{nn}`

```
CHK-101, CHK-102, ... (Category 1)
CHK-201, CHK-202, ... (Category 2)
CHK-301, CHK-302, ... (Category 3)
```

| Category Number | Category Name         |
|:----------------|:----------------------|
| 1               | Requirements Review   |
| 2               | Specification Review  |
| 3               | Design Review         |
| 4               | Implementation Review |
| 5               | Testing Review        |
| 6               | Documentation Review  |
| 7               | Security Review       |
| 8               | Performance Review    |
| 9               | Deployment Review     |

**Categories**:

| Category                  | Purpose                           | Examples                                       |
|:--------------------------|:----------------------------------|:-----------------------------------------------|
| **Requirements Review**   | Verify all requirements addressed | FR-xxx coverage, NFR-xxx validation            |
| **Specification Review**  | Verify spec completeness          | API signatures, data models                    |
| **Design Review**         | Verify design quality             | Architecture patterns, tech stack              |
| **Implementation Review** | Verify code quality               | Code structure, naming conventions             |
| **Testing Review**        | Verify test adequacy              | Unit tests, integration tests, edge cases      |
| **Documentation Review**  | Verify documentation              | Code comments, design docs, README             |
| **Security Review**       | Verify security measures          | Authentication, authorization, data validation |
| **Performance Review**    | Verify performance                | Response times, resource usage                 |
| **Deployment Review**     | Verify deployment readiness       | Configuration, migrations, rollback plan       |

### 4. Organize by Priority

Assign priority levels:

| Priority        | Mark | Criteria                 | When to Check      |
|:----------------|:-----|:-------------------------|:-------------------|
| **P1 - High**   | 🔴   | Must pass before merge   | Before PR creation |
| **P2 - Medium** | 🟡   | Should pass before merge | During PR review   |
| **P3 - Low**    | 🟢   | Nice to have             | Opportunistic      |

## Output Format

### Checklist Document

````markdown
# Quality Checklist: {Feature Name}

## Meta Information

| Item | Content |
|:---|:---|
| Feature Name | {Feature Name} |
| Ticket Number | {Ticket Number} |
| Specification | `.sdd/specification/[{path}/]{feature}_spec.md` |
| Design Document | `.sdd/specification/[{path}/]{feature}_design.md` |
| Generated Date | YYYY-MM-DD |
| Checklist Version | 1.0 |

※ For hierarchical structure, parent feature uses `index_spec.md`, `index_design.md`

## Checklist Summary

| Category | Total Items | P1 🔴 | P2 🟡 | P3 🟢 |
|:---|:---|:---|:---|:---|
| Requirements Review | 5 | 3 | 2 | 0 |
| Specification Review | 8 | 5 | 3 | 0 |
| Design Review | 6 | 2 | 3 | 1 |
| Implementation Review | 12 | 4 | 5 | 3 |
| Testing Review | 10 | 6 | 4 | 0 |
| Documentation Review | 4 | 0 | 2 | 2 |
| Security Review | 5 | 5 | 0 | 0 |
| Performance Review | 3 | 0 | 2 | 1 |
| Deployment Review | 7 | 4 | 3 | 0 |
| **Total** | **60** | **29** | **24** | **7** |

---

## Requirements Review

### CHK-101 [P1] 🔴 Functional Requirements Coverage

- [ ] All functional requirements (FR-xxx) from PRD are implemented
- [ ] Each requirement maps to specific implementation
- [ ] No requirements are partially implemented

**Verification**:
- Review PRD: `.sdd/requirement/[{path}/]{feature}.md`
- Check implementation coverage
- Run `/check_spec {feature}` for consistency

**Related Requirements**: FR-001, FR-002, FR-003

---

### CHK-102 [P1] 🔴 Non-Functional Requirements

- [ ] Performance requirements (NFR-xxx) are met
- [ ] Security requirements are implemented
- [ ] Scalability requirements are addressed

**Verification**:
- Review NFR specifications
- Run performance tests
- Review security audit results

**Related Requirements**: NFR-001 (Response time < 200ms), NFR-002 (Rate limiting)

---

### CHK-103 [P2] 🟡 Acceptance Criteria

- [ ] All acceptance criteria from PRD are met
- [ ] Edge cases identified in PRD are handled
- [ ] User scenarios are validated

**Verification**:
- Run end-to-end tests
- Manual user flow testing
- Stakeholder demo

---

## Specification Review

### CHK-201 [P1] 🔴 Public API Implementation

- [ ] All APIs defined in `*_spec.md` are implemented
- [ ] API signatures match specification exactly
- [ ] Return types match specification

**Verification**:
```bash
# Example for TypeScript
grep -r "export function" src/ | compare with spec
```

**Reference**: `.sdd/specification/[{path}/]{feature}_spec.md` § Public API

---

### CHK-202 [P1] 🔴 Data Model Consistency

- [ ] Type definitions match specification
- [ ] Required fields are enforced
- [ ] Optional fields are properly handled
- [ ] Field constraints are validated

**Verification**:
- Compare implementation types with spec types
- Check database schema matches spec
- Verify validation logic

**Reference**: `.sdd/specification/[{path}/]{feature}_spec.md` § Data Model

---

### CHK-203 [P1] 🔴 Behavior Alignment

- [ ] Sequence diagrams in spec are followed
- [ ] State transitions match specification
- [ ] Error handling follows spec patterns

**Verification**:
- Trace code execution flow
- Compare with sequence diagrams
- Test error scenarios

---

### CHK-204 [P2] 🟡 Constraint Enforcement

- [ ] All constraints in spec are implemented
- [ ] Boundary conditions are handled
- [ ] Invalid inputs are rejected appropriately

**Verification**:
- Review constraint tests
- Test boundary values
- Test invalid inputs

---

## Design Review

### CHK-301 [P1] 🔴 Architecture Alignment

- [ ] Module structure matches design document
- [ ] Layer separation is maintained
- [ ] Dependencies flow in correct direction

**Verification**:
- Compare directory structure with design doc
- Review import statements
- Check for circular dependencies

**Reference**: `.sdd/specification/[{path}/]{feature}_design.md` § Architecture

---

### CHK-302 [P1] 🔴 Technology Stack Compliance

- [ ] All specified libraries are used
- [ ] No unapproved dependencies added
- [ ] Version constraints are followed

**Verification**:
```bash
# Compare package.json with design doc
cat package.json | grep dependencies
```

**Reference**: `.sdd/specification/[{path}/]{feature}_design.md` § Technology Stack

---

### CHK-303 [P2] 🟡 Design Decisions Documented

- [ ] All significant design decisions are documented
- [ ] Rationale for decisions is clear
- [ ] Trade-offs are explained
- [ ] Alternatives considered are noted

**Verification**:
- Review "Design Decisions" section in design doc
- Check for recent updates
- Verify decisions match implementation

---

### CHK-304 [P2] 🟡 Integration Points Verified

- [ ] External API integrations are tested
- [ ] Database connections are configured
- [ ] Message queue connections work
- [ ] Third-party service integrations are verified

**Verification**:
- Run integration tests
- Check configuration files
- Verify credentials (in secure manner)

---

## Implementation Review

### CHK-401 [P1] 🔴 Code Structure

- [ ] Code follows project conventions
- [ ] Naming is clear and consistent
- [ ] No dead code or commented-out blocks
- [ ] File organization is logical

**Verification**:
- Code review
- Run linter
- Check for TODOs and FIXMEs

---

### CHK-402 [P1] 🔴 Error Handling

- [ ] All error cases are handled
- [ ] Errors are logged appropriately
- [ ] User-facing errors are clear
- [ ] No silent failures

**Verification**:
- Review error handling code
- Test error scenarios
- Check logging output

---

### CHK-403 [P2] 🟡 Code Quality

- [ ] No code smells detected
- [ ] Complexity is reasonable
- [ ] No duplicate code
- [ ] Functions are single-purpose

**Verification**:
- Run static analysis tools
- Review cyclomatic complexity
- Check for duplication

---

## Testing Review

### CHK-501 [P1] 🔴 Unit Test Coverage

- [ ] Unit tests exist for all business logic
- [ ] Code coverage ≥ 80%
- [ ] All public functions are tested
- [ ] Edge cases are covered

**Verification**:
```bash
npm test -- --coverage
```

**Target**: ≥80% line coverage, ≥90% branch coverage

---

### CHK-502 [P1] 🔴 Integration Tests

- [ ] Integration tests cover all main flows
- [ ] External service mocks are realistic
- [ ] Database operations are tested
- [ ] API endpoints are tested

**Verification**:
- Run integration test suite
- Review test scenarios
- Check mock implementations

---

### CHK-503 [P1] 🔴 Edge Case Testing

- [ ] Null/undefined inputs tested
- [ ] Empty collections tested
- [ ] Maximum/minimum values tested
- [ ] Concurrent operations tested

**Verification**:
- Review edge case test suite
- Check boundary value tests
- Run stress tests

---

### CHK-504 [P2] 🟡 Non-Functional Testing

- [ ] Performance tests pass
- [ ] Load tests pass
- [ ] Security tests pass
- [ ] Accessibility tests pass (if applicable)

**Verification**:
- Run performance benchmarks
- Execute load testing
- Run security scanners

---

## Documentation Review

### CHK-601 [P2] 🟡 Code Comments

- [ ] Complex logic is commented
- [ ] Public APIs have JSDoc/docstrings
- [ ] Non-obvious decisions are explained
- [ ] TODOs are tracked (or removed)

**Verification**:
- Review code comments
- Check documentation coverage
- Verify comment quality

---

### CHK-602 [P2] 🟡 Design Document Updated

- [ ] Design doc reflects implementation
- [ ] Recent decisions are documented
- [ ] Diagrams are up-to-date
- [ ] Change history is maintained

**Verification**:
- Review `.sdd/specification/[{path}/]{feature}_design.md`
- Compare with implementation
- Check last update date

---

## Security Review

### CHK-701 [P1] 🔴 Input Validation

- [ ] All user inputs are validated
- [ ] SQL injection prevention in place
- [ ] XSS prevention in place
- [ ] CSRF protection implemented (if applicable)

**Verification**:
- Review validation code
- Run security scanners
- Manual penetration testing

---

### CHK-702 [P1] 🔴 Authentication & Authorization

- [ ] Authentication is required where needed
- [ ] Authorization checks are in place
- [ ] Role-based access control works
- [ ] Session management is secure

**Verification**:
- Test with different user roles
- Check unauthorized access attempts
- Review auth middleware

---

### CHK-703 [P1] 🔴 Data Protection

- [ ] Sensitive data is encrypted
- [ ] Passwords are hashed (never plain text)
- [ ] API keys are not hardcoded
- [ ] PII is handled appropriately

**Verification**:
- Review encryption implementation
- Check environment variables
- Audit data storage

---

## Performance Review

### CHK-801 [P2] 🟡 Response Time

- [ ] API response times meet NFR requirements
- [ ] Database queries are optimized
- [ ] N+1 query problems are avoided
- [ ] Caching is implemented where appropriate

**Verification**:
- Run performance profiling
- Check database query plans
- Review caching strategy

**Target**: Response time < 200ms (per NFR-001)

---

### CHK-802 [P3] 🟢 Resource Usage

- [ ] Memory usage is reasonable
- [ ] No memory leaks detected
- [ ] CPU usage is acceptable
- [ ] Network bandwidth is efficient

**Verification**:
- Run resource monitoring
- Profile memory usage
- Load test with monitoring

---

## Deployment Review

### CHK-901 [P1] 🔴 Configuration Management

- [ ] Environment variables are documented
- [ ] Configuration files are correct
- [ ] Secrets are properly managed
- [ ] Feature flags are configured (if applicable)

**Verification**:
- Review `.env.example`
- Check configuration documentation
- Verify secrets management

---

### CHK-902 [P1] 🔴 Database Migrations

- [ ] Migrations are tested
- [ ] Rollback migrations exist
- [ ] Data migration is safe
- [ ] No data loss risk

**Verification**:
- Run migrations in test environment
- Test rollback process
- Review migration scripts

---

### CHK-903 [P1] 🔴 Deployment Plan

- [ ] Deployment steps are documented
- [ ] Rollback plan exists
- [ ] Monitoring is in place
- [ ] Alerts are configured

**Verification**:
- Review deployment documentation
- Test rollback procedure
- Verify monitoring dashboards

---

## Completion Criteria

### Pre-PR Checklist

All P1 (🔴 High) items must be complete:
- [ ] All P1 items checked (29/29)
- [ ] All tests passing
- [ ] Spec consistency verified (`/check_spec`)
- [ ] Ready for code review

### Pre-Merge Checklist

All P1 and P2 items must be complete:
- [ ] All P1 items checked (29/29)
- [ ] All P2 items checked (24/24)
- [ ] Code review approved
- [ ] CI/CD pipeline green
- [ ] Ready for merge

### Pre-Release Checklist

All items through P3 should be complete:
- [ ] All P1 items checked (29/29)
- [ ] All P2 items checked (24/24)
- [ ] All P3 items checked (7/7)
- [ ] QA sign-off
- [ ] Ready for production deployment

---

## Notes

- This checklist was auto-generated from specifications and design documents
- Update this checklist if requirements or design changes
- Use this as a guide; not all items may be applicable
- Add project-specific items as needed
````

**Save Location**: `.sdd/task/{ticket}/checklist.md`

## Checklist Template Integration

This command uses the template from `skills/sdd-templates/templates/checklist_template.md` as a base and customizes it
based on:

- Project-specific requirements
- Programming language conventions
- Technology stack
- Team standards

## Update Existing Checklist

To update an existing checklist after spec changes:

```
/checklist user-auth TICKET-123 --update
```

This will:

1. Load existing checklist
2. Compare with current specs
3. Add new items
4. Mark obsolete items
5. Preserve completion status

## Export Formats

### GitHub Issues

```
/checklist user-auth TICKET-123 --export github-issues
```

Creates individual GitHub issues for P0 items.

### Notion/Linear

```
/checklist user-auth TICKET-123 --export csv
```

Exports checklist as CSV for import to project management tools.

## Best Practices

| Practice             | Benefit                                                 |
|:---------------------|:--------------------------------------------------------|
| **Generate early**   | Use checklist as implementation guide                   |
| **Update regularly** | Keep in sync with spec changes                          |
| **Track completion** | Mark items as they're verified                          |
| **Customize**        | Add project-specific items                              |
| **Archive**          | Keep checklist with implementation for future reference |

## Integration with Other Commands

```
/generate_spec {feature}
   ↓
/task_breakdown {feature}
   ↓
/checklist {feature} {ticket}  ← Generate checklist
   ↓
/implement {feature} {ticket}  ← Use checklist during implementation
   ↓
Review against checklist before PR
```

## Notes

- Checklist items are derived from specifications, not invented
- IDs (CHK-101, CHK-201, etc.) are stable across updates and organized by category
- Priority levels (P1 🔴, P2 🟡, P3 🟢) can be customized per project
- Some items may require manual verification
- Automated checks should be integrated into CI/CD where possible
- Archive checklist with task logs for future reference
