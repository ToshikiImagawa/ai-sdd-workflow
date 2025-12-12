# Project Constitution

**Version**: 1.0.0
**Last Updated**: YYYY-MM-DD
**Status**: Active

## Purpose

This document defines the non-negotiable principles and standards that govern this project's development. All code, specifications, and design decisions must align with these principles.

## Principle Hierarchy

```
1. Business Principles (Highest Priority)
   ↓
2. Architecture Principles
   ↓
3. Development Methodology Principles
   ↓
4. Technical Constraints
```

Higher priority principles take precedence over lower priority principles.

---

## 1. Business Principles (Highest Priority)

### B-001: {Principle Name}

**Principle**: {Description of the principle}

**Scope**: {Applicable scope}

**Validation Method**:

- [ ] {Validation item 1}
- [ ] {Validation item 2}
- [ ] {Validation item 3}

**Violation Examples**:

- {Violation example 1}
- {Violation example 2}

**Compliant Examples**:

- {Compliant example 1}
- {Compliant example 2}

---

### B-002: {Principle Name}

**Principle**: {Description of the principle}

**Scope**: {Applicable scope}

**Validation Method**:

- [ ] {Validation item 1}
- [ ] {Validation item 2}

---

## 2. Architecture Principles

### A-001: Library-First

**Principle**: Leverage existing libraries whenever possible and avoid reinventing the wheel

**Scope**: All implementations

**Validation Method**:

- [ ] Did you research existing libraries before implementing from scratch?
- [ ] Is there a clear reason for custom implementation?

**Violation Examples**:

- Custom implementation without researching libraries
- Custom implementation of well-known problems (encryption, authentication, etc.)

**Compliant Examples**:

- Research existing libraries and select appropriate one
- When implementing custom solution, clearly document reasons in design doc (performance, reducing dependencies, etc.)

---

### A-002: Clean Architecture

**Principle**: Strictly separate layers and maintain unidirectional dependency flow from outer to inner layers

**Scope**: All module designs

**Validation Method**:

- [ ] Dependency direction follows Presentation → Application → Domain → Infrastructure
- [ ] Inner layers do not depend on outer layers
- [ ] Domain logic does not depend on infrastructure

**Violation Examples**:

- Domain logic directly references database access layer
- Business logic mixed with framework-specific code

**Compliant Examples**:

- Layer separation using Dependency Inversion Principle (DIP)
- Loosely coupled design through interfaces

---

## 3. Development Methodology Principles

### D-001: Test-First

**Principle**: Write tests before implementation (TDD)

**Scope**: All core features

**Validation Method**:

- [ ] Test cases created before implementation
- [ ] Test coverage > 80%
- [ ] Follows flow of writing failing tests first, then making them pass with implementation

**Violation Examples**:

- Adding tests after implementation is complete
- Merging without tests

**Compliant Examples**:

- Follow Red → Green → Refactor cycle
- Test case creation → Implementation → Refactoring

---

### D-002: Specification-Driven

**Principle**: Never implement without specifications

**Scope**: All new features and changes

**Validation Method**:

- [ ] `*_spec.md` exists
- [ ] `*_design.md` exists
- [ ] Specifications are up-to-date (updated before implementation)

**Violation Examples**:

- Starting implementation based only on verbal instructions
- Implementing with outdated specifications

**Compliant Examples**:

- Follow Specify → Plan → Tasks → Implement flow
- Manage specifications as Single Source of Truth

---

## Development Standards

### Code Quality

| Standard        | Requirement                   | Tool                   | Enforcement     |
|:----------------|:------------------------------|:-----------------------|:----------------|
| **Linting**     | Zero errors, zero warnings    | ESLint/Prettier        | Pre-commit hook |
| **Type Safety** | Strict type checking          | TypeScript strict mode | CI/CD           |
| **Complexity**  | Cyclomatic complexity ≤ 10    | SonarQube              | Code review     |
| **Duplication** | No blocks duplicated ≥3 times | CodeClimate            | CI/CD gate      |

### Documentation

| Standard           | Requirement                            | Location              | Update Frequency      |
|:-------------------|:---------------------------------------|:----------------------|:----------------------|
| **Specifications** | All features have `*_spec.md`          | `.sdd/specification/` | Before implementation |
| **Design Docs**    | All implementations have `*_design.md` | `.sdd/specification/` | During design phase   |
| **API Docs**       | All public APIs documented             | In source files       | With code changes     |
| **README**         | Up-to-date setup instructions          | Project root          | As needed             |

### Testing

| Standard              | Requirement                | Enforcement          | Exemptions          |
|:----------------------|:---------------------------|:---------------------|:--------------------|
| **Unit Coverage**     | ≥80% line coverage         | CI/CD gate           | UI components (60%) |
| **Integration Tests** | All main flows covered     | Manual review        | -                   |
| **Edge Cases**        | Boundary conditions tested | Code review          | -                   |
| **Performance Tests** | Response times meet NFRs   | Automated benchmarks | -                   |

### Security

| Standard                | Requirement                    | Enforcement         | Review Frequency |
|:------------------------|:-------------------------------|:--------------------|:-----------------|
| **Input Validation**    | All user inputs validated      | Security review     | Every PR         |
| **Authentication**      | Industry-standard methods only | Architecture review | Design phase     |
| **Secrets Management**  | No secrets in code             | Pre-commit hooks    | Every commit     |
| **Dependency Scanning** | No critical vulnerabilities    | CI/CD gate          | Daily            |

## Architectural Constraints

### Layered Architecture

```
Presentation Layer
      ↓
Business Logic Layer
      ↓
Data Access Layer
      ↓
Database
```

**Rules**:

- No layer may skip levels
- No circular dependencies
- Dependency direction always downward
- Each layer has single responsibility

### Technology Stack Constraints

| Layer        | Allowed Technologies         | Prohibited               | Rationale                    |
|:-------------|:-----------------------------|:-------------------------|:-----------------------------|
| **Frontend** | React, TypeScript            | jQuery, plain JS         | Type safety, modern patterns |
| **Backend**  | Node.js, Express, TypeScript | JavaScript without types | Consistency, safety          |
| **Database** | PostgreSQL                   | MongoDB                  | Relational data model        |
| **Testing**  | Jest, Testing Library        | Enzyme                   | Active maintenance           |

**Exception Process**: Propose changes via RFC with team approval

### Module Organization

```
src/
├── domain/           # Business logic (pure, no dependencies)
├── application/      # Use cases, orchestration
├── infrastructure/   # External integrations
└── presentation/     # API, UI
```

**Dependency Rules**:

- `domain/` depends on nothing
- `application/` depends on `domain/`
- `infrastructure/` depends on `domain/` and `application/`
- `presentation/` depends on all layers

## Decision-Making Framework

When facing technical trade-offs, prioritize in this order:

1. **Correctness** - Does it meet specifications?
2. **Security** - Is it safe?
3. **Simplicity** - Is it the simplest solution?
4. **Performance** - Is it fast enough?
5. **Maintainability** - Can we maintain it?
6. **Developer Experience** - Is it easy to work with?

**Tiebreaker**: Choose option that's easier to change later.

## Quality Gates

### Pre-Commit

- [ ] Linter passes
- [ ] No secrets detected
- [ ] Tests pass locally

### Pre-PR

- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] Spec consistency verified (`/check_spec`)
- [ ] Design doc updated

### Pre-Merge

- [ ] Code review approved (2 reviewers)
- [ ] CI/CD pipeline green
- [ ] No merge conflicts
- [ ] Documentation updated

### Pre-Release

- [ ] QA sign-off
- [ ] Performance benchmarks pass
- [ ] Security scan clean
- [ ] Deployment plan reviewed

## 4. Technical Constraints

### T-001: {Programming Language Constraints}

**Principle**: {Language-specific constraints}

**Scope**: All source code

**Validation Method**:

- [ ] {Validation item 1}
- [ ] {Validation item 2}

**Violation Examples**:

- {Violation example}

**Compliant Examples**:

- {Compliant example}

---

### T-002: No Runtime Errors

**Principle**: No runtime errors are tolerated (must be detected at compile time)

**Scope**: All code

**Validation Method**:

- [ ] Strict mode enabled (TypeScript, etc.)
- [ ] Proper use of type guards
- [ ] Error Boundary implementation (frontend)
- [ ] Comprehensive error handling

**Violation Examples**:

- Excessive use of `any` type
- Async processing without try-catch
- Unhandled Promise rejections

**Compliant Examples**:

- Clear type definitions for all functions
- Comprehensive error case handling
- Utilize Result/Option types

---

### T-003: {Security Constraints}

**Principle**: {Security-related constraints}

**Scope**: {Applicable scope}

**Validation Method**:

- [ ] {Validation item 1}
- [ ] {Validation item 2}

---

## Guidelines for Adding Principles

When adding new principles, consider the following:

### Criteria for Good Principles

| Criterion        | Description                                                      |
|:-----------------|:-----------------------------------------------------------------|
| **Verifiable**   | Can be verified with checklist                                   |
| **Clear**        | No ambiguity, clear judgment of compliance/violation             |
| **Justifiable**  | Can explain why the principle is necessary                       |
| **Achievable**   | Entire team can practice it                                      |
| **Persistent**   | Not a temporary policy, but a long-term principle to be followed |

### Addition Process

```
1. Proposal (Discussion via Issue, etc.)
   ↓
2. Team approval
   ↓
3. Add to constitution file
   ↓
4. Minor version bump (e.g., 1.0.0 → 1.1.0)
   ↓
5. Update affected documents
   ↓
6. Validate with /constitution validate
```

## Compliance

### Enforcement Mechanisms

**Automated**:

- Pre-commit hooks (formatting, secrets)
- CI/CD pipelines (tests, coverage, security)
- Dependency scanning (vulnerabilities)

**Manual**:

- Code review (architecture, design decisions)
- Design review (principle compliance)
- Periodic audits (quarterly)

### Violation Handling

| Severity     | Action                         | Example                           |
|:-------------|:-------------------------------|:----------------------------------|
| **Critical** | Block merge immediately        | No tests, failed security scan    |
| **Major**    | Require explicit justification | Custom implementation without ADR |
| **Minor**    | Fix in current PR or follow-up | Minor doc updates                 |

### Exception Process

When principle compliance is not possible:

1. **Document**: Create Architecture Decision Record (ADR)
2. **Justify**: Explain why principle cannot be followed
3. **Mitigate**: Describe compensating controls
4. **Review**: Get approval from tech lead + 2 reviewers
5. **Track**: Add to technical debt log
6. **Plan**: Set timeline for resolution (if temporary)

### Audit Trail

All exceptions and violations are logged for:

- Pattern identification
- Constitution refinement
- Compliance metrics
- Team retrospectives

## Metrics and Monitoring

Track compliance through:

| Metric                   | Target           | Measurement              |
|:-------------------------|:-----------------|:-------------------------|
| **Spec Coverage**        | 100% of features | `/constitution validate` |
| **Test Coverage**        | ≥80%             | CI/CD reports            |
| **Code Quality**         | A grade          | SonarQube                |
| **Security Score**       | 0 critical/high  | Dependency scans         |
| **Constitution Version** | Document in PRs  | Manual                   |

Review metrics monthly in team retrospective.

## Adoption

### For New Team Members

1. Read this constitution (required, day 1)
2. Review architecture decision records
3. Complete training exercises
4. Shadow experienced developer
5. First PR reviewed by constitution champion

### For Existing Code

**Migration Strategy**:

- New code: Full compliance required
- Modified code: Bring up to compliance if touching >30% of file
- Legacy code: Compliance not required unless major refactor

**Timeline**: Aim for 80% compliance within 6 months

## Contact

- **Constitution Champions**: [List names/roles]
- **Questions**: [Slack channel/email]
- **Propose Changes**: [RFC process link]

## Version History

### v1.0.0 (YYYY-MM-DD)

**Initial constitution established**

- Defined core principles (P1-P3)
- Set development standards
- Established architectural constraints
- Created decision-making framework
- B-001, B-002: Defined business principles
- A-001, A-002: Defined architecture principles
- D-001, D-002: Defined development methodology principles
- T-001, T-002, T-003: Defined technical constraints

---

## Amendment Process

### Minor Version (x.Y.z)

**Scope**: Clarifications, additional examples, enforcement method updates

**Process**:

1. Propose change in PR
2. Team discussion (async, 3 business days)
3. Approval by 50% of team
4. Update version
5. Communicate changes in team meeting

**Timeline**: ~1 week

### Major Version (X.y.z)

**Scope**: New principles, changes to existing principles, removal of principles

**Process**:

1. Create RFC (Request for Comments) document
2. Team-wide discussion (minimum 1 week)
3. Present at team meeting
4. Vote (approval requires 75% of team)
5. Update version
6. Create migration guide for affected code
7. Schedule team training session
8. Monitor compliance for 2 weeks

**Timeline**: ~1 month

---

## Related Documents

### Documents That Should Reference This Constitution

| Document                         | How to Reference                                      |
|:---------------------------------|:------------------------------------------------------|
| `.sdd/SPECIFICATION_TEMPLATE.md` | Include section referencing principles                |
| `.sdd/DESIGN_DOC_TEMPLATE.md`    | Include checklist for principle compliance            |
| `*_spec.md`                      | Describe design based on principles                   |
| `*_design.md`                    | Clearly state that design decisions comply with principles |

### Validating Constitution Compliance

```bash
/constitution validate
```

Use this command to automatically verify that all specifications and design documents comply with the constitution.

---

## Semantic Versioning

Constitution versions follow these rules:

| Version Type | Usage                                        | Example       |
|:-------------|:---------------------------------------------|:--------------|
| Major        | Removal/major changes to existing principles (breaking changes) | 1.0.0 → 2.0.0 |
| Minor        | Addition of new principles                   | 1.0.0 → 1.1.0 |
| Patch        | Expression fixes, typo corrections           | 1.0.0 → 1.0.1 |

---

*This constitution is a living document. It should evolve with the team's learning and the project's needs.*
