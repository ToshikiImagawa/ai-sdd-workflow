---
description: "Define and manage non-negotiable project principles (Constitution) and verify synchronization with other documents"
argument-hint: "<subcommand> [arguments]"
allowed-tools: Read, Write, Edit, Glob, Grep, Skill
---

# Constitution - Project Principles Management

Define the project's non-negotiable principles (Constitution) and verify that all specifications and design documents comply with them.

## Prerequisites

### Plugin Update Check

**Before execution, check if `.sdd/UPDATE_REQUIRED.md` exists.**

If this file exists, the AI-SDD plugin needs to be updated. Display a warning to the user and prompt them to run the following command:

```
/sdd_init
```

### AI-SDD Principles Document

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `.sdd/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles.

This command manages project principles following AI-SDD principles.

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

This document uses default values for examples, but replace with custom values if environment variables or configuration file exists.

## What is a Project Constitution?

A Project Constitution defines **non-negotiable principles that form the foundation of all design decisions**.

### Constitution Characteristics

| Characteristic    | Description                                                      |
|:------------------|:-----------------------------------------------------------------|
| **Non-negotiable** | Not open to debate. Changes require careful consideration       |
| **Persistent**    | Consistently applied across the entire project                   |
| **Hierarchical**  | Higher principles take precedence over lower ones                |
| **Verifiable**    | Can automatically verify spec/design compliance with principles  |

### Constitution Examples

| Principle Category  | Example Principles                                     |
|:-------------------|:-------------------------------------------------------|
| **Architecture**   | Library-First, Clean Architecture                      |
| **Development**    | Test-First, Specification-Driven                       |
| **Quality**        | Test Coverage > 80%, Zero Runtime Errors               |
| **Technical**      | TypeScript Only, No Any Types                          |
| **Business**       | Privacy by Design, Accessibility First                 |

## Input

$ARGUMENTS

| Subcommand | Description | Additional Arguments |
|:--|:--|:--|
| `init` | Initialize constitution file | - |
| `validate` | Validate constitution compliance | - |
| `add` | Add new principle | `"principle-name"` |
| `bump-version` | Version bump | `major\|minor\|patch` |

### Input Examples

```
/constitution init                      # Initialize constitution file
/constitution validate                  # Validate constitution compliance
/constitution add "Library-First"       # Add new principle
/constitution bump-version major        # Major version bump
```

## Processing Flow

### 1. Initialize (init)

Create constitution file in project:

```bash
/constitution init
```

**Generated File**: `.sdd/CONSTITUTION.md`

**Skill Used**: `sdd-workflow:sdd-templates`

**Processing Flow**:

1. Check if `.sdd/CONSTITUTION.md` already exists
2. If exists: Skip (respect existing constitution)
3. If not exist:
   - Reference `sdd-workflow:sdd-templates` skill's `templates/constitution_template.md`
   - Analyze project context (language, framework, domain)
   - Generate customized constitution based on context

**Content**: Template customized for the project

### 2. Add Principle (add)

Add new principle to constitution:

```bash
/constitution add "Library-First"
```

**Process**:

1. Confirm principle details with user
2. Add to appropriate category
3. Bump minor version (e.g., 1.0.0 → 1.1.0)
4. Record in change history

### 3. Show Current Constitution (show)

**Command**: `/constitution show`

**Output Content**:

- Current version
- All principles
- Recent changes
- Compliance status

### 4. Update Constitution (update)

**Command**: `/constitution update`

**Interactive Prompts**:

```
What type of change?
1. Add new principle (MAJOR)
2. Modify existing principle (MAJOR)
3. Clarify existing principle (MINOR)
4. Update enforcement methods (MINOR)

> 1

Describe the new principle:
> ...

Rationale:
> ...

How will it be enforced?
> ...

Are there exceptions?
> ...

Review proposed change:
[Display formatted principle]

Confirm (y/n)?
> y

✓ Constitution updated
  Version: 1.0.0 → 2.0.0
  Changes: Added principle P4
```

**Version Bump Rules**:

| Change Type        | Version Impact | Example       |
|:-------------------|:---------------|:--------------|
| Add principle      | MAJOR (X.y.z)  | 1.0.0 → 2.0.0 |
| Modify principle   | MAJOR (X.y.z)  | 1.0.0 → 2.0.0 |
| Remove principle   | MAJOR (X.y.z)  | 1.0.0 → 2.0.0 |
| Clarify principle  | MINOR (x.Y.z)  | 1.0.0 → 1.1.0 |
| Update enforcement | MINOR (x.Y.z)  | 1.0.0 → 1.1.0 |
| Fix typo           | PATCH (x.y.Z)  | 1.0.0 → 1.0.1 |

### 5. Validate (validate)

Verify all specifications and design documents comply with constitution:

```bash
/constitution validate
```

**Validation Targets**:

- `.sdd/requirement/**/*.md`
- `.sdd/specification/**/*_spec.md`
- `.sdd/specification/**/*_design.md`
- `.sdd/PRD_TEMPLATE.md`
- `.sdd/SPECIFICATION_TEMPLATE.md`
- `.sdd/DESIGN_DOC_TEMPLATE.md`

**Validation Items**:

| Validation Item        | Check Content                                    |
|:-----------------------|:-------------------------------------------------|
| **Principle Mention**  | Are principles mentioned in specs/designs?       |
| **Principle Compliance** | Do implementation decisions follow principles? |
| **Contradiction Detection** | Are there descriptions contrary to principles? |
| **Template Sync**      | Do templates reflect latest constitution?        |

**Validation Check**:

````markdown
# Constitution Compliance Report

**Constitution Version**: 2.0.0
**Validation Date**: YYYY-MM-DD
**Project**: {Project Name}

## Compliance Summary

| Principle | Status | Score |
|:---|:---|:---|
| P1: Specification-First | ✓ Compliant | 95% |
| P2: Test-First | ⚠ Partial | 78% |
| P3: Library-First | ✓ Compliant | 100% |
| P4: API Versioning | ✗ Non-Compliant | 45% |

## Detailed Analysis

### P1: Specification-First Development

**Status**: ✓ Compliant (95%)

**Verification**:

- [x] All features have specifications
- [x] Specs exist before implementation
- [ ] 2 legacy features missing specs (user-profile, settings)

**Recommendations**:

- Create specs for legacy features: user-profile, settings
- Run `/generate_spec` for these features

---

### P2: Test-First Implementation

**Status**: ⚠ Partial Compliance (78%)

**Verification**:

- [x] Test coverage ≥80% (Current: 78.3%)
- [ ] Not all features follow TDD commit pattern
- [x] Code review includes test verification

**Recommendations**:

- Increase coverage by 1.7% to meet threshold
- Enforce commit message convention for new code
- Focus on user-profile module (current coverage: 65%)

---

### P4: API Versioning

**Status**: ✗ Non-Compliant (45%)

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

````

### 6. Sync Principles (sync)

**Command**: `/constitution sync`

**Purpose**: Ensure principles are reflected in other documents

**Actions**:

1. **Update Specification Template**:
    - Add principle references
    - Update constraints section
    - Sync terminology

2. **Update Design Template**:
    - Add principle compliance section
    - Update decision framework
    - Sync architectural constraints

3. **Update Task Templates**:
    - Add compliance verification tasks
    - Update completion criteria
    - Reference relevant principles

4. **Update Checklist Template**:
    - Add principle verification items
    - Update priorities
    - Sync quality gates

**Output**:

````markdown
# Constitution Sync Report

## Documents Updated

- [x] `.sdd/SPECIFICATION_TEMPLATE.md`
    - Added P1 reference to API section
    - Updated constraints to include P3

- [x] `.sdd/DESIGN_DOC_TEMPLATE.md`
    - Added "Principle Compliance" section
    - Updated decision framework to match constitution

- [x] `skills/sdd-templates/templates/checklist_template.md`
    - Added principle verification items
    - CHK-CONST-001: P1 verification
    - CHK-CONST-002: P2 verification
    - CHK-CONST-003: P3 verification

## Sync Status

✓ All documents synchronized with Constitution v2.0.0

````

### 7. Version Management (bump-version)

Update constitution version:

```bash
/constitution bump-version major   # Major version bump (breaking change)
/constitution bump-version minor   # Minor version bump (add principle)
/constitution bump-version patch   # Patch version bump (typo fix)
```

**Semantic Versioning**:

| Version Type | Use Case                                      | Example       |
|:-------------|:----------------------------------------------|:--------------|
| Major        | Remove/significantly change existing principle (breaking) | 1.0.0 → 2.0.0 |
| Minor        | Add new principle                             | 1.0.0 → 1.1.0 |
| Patch        | Fix expression of principle, typo fix         | 1.0.0 → 1.0.1 |

## Constitution File Structure

````markdown
# Project Constitution

## Metadata

| Item         | Content    |
|:-------------|:-----------|
| Version      | 1.2.0      |
| Created      | 2024-01-01 |
| Last Updated | 2024-06-15 |

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

Higher priority principles take precedence over lower ones.

---

## 1. Business Principles (Highest Priority)

### B-001: Privacy by Design

**Principle**: Prioritize user privacy in all considerations

**Scope**: All features and data models

**Verification**:

- [ ] Is personal information collection minimized?
- [ ] Is data retention period defined?
- [ ] Can users delete their data?

**Violation Examples**:

- Collecting unnecessary personal information
- Indefinite data retention period

**Compliance Examples**:

- Collect only minimum necessary information
- Define clear data retention period

---

### B-002: Accessibility First

**Principle**: Design for accessibility to all users

**Scope**: UI/UX design

**Verification**:

- [ ] WCAG 2.1 AA compliant
- [ ] Operable with keyboard only
- [ ] Screen reader compatible

---

## 2. Architecture Principles

### A-001: Library-First

**Principle**: Leverage existing libraries whenever possible; avoid reinventing the wheel

**Scope**: All implementations

**Verification**:

- [ ] Did you research existing libraries before new implementation?
- [ ] Is there a clear reason for custom implementation?

**Violation Examples**:

- Custom implementation without library research

**Compliance Examples**:

- Research existing libraries and select appropriate one
- Document reason in design doc if custom implementation needed

---

### A-002: Clean Architecture

**Principle**: Enforce layer separation with unidirectional dependency from outside to inside

**Scope**: All module designs

**Verification**:

- [ ] Presentation → Application → Domain → Infrastructure
- [ ] Inner layers don't depend on outer layers

---

## 3. Development Methodology Principles

### D-001: Test-First

**Principle**: Write tests before implementation (TDD)

**Scope**: All core features

**Verification**:

- [ ] Test cases created before implementation
- [ ] Test Coverage > 80%

---

### D-002: Specification-Driven

**Principle**: Don't implement without specification

**Scope**: All new features and changes

**Verification**:

- [ ] `*_spec.md` exists
- [ ] `*_design.md` exists

---

## 4. Technical Constraints

### T-001: TypeScript Only

**Principle**: Write all code in TypeScript

**Scope**: All source code

**Verification**:

- [ ] No .js files exist
- [ ] No any type usage

---

### T-002: No Runtime Errors

**Principle**: Don't tolerate runtime errors (detect at compile time)

**Scope**: All code

**Verification**:

- [ ] Strict mode enabled
- [ ] Proper use of type guards
- [ ] Error Boundary implementation

---

## Change History

### v1.2.0 (2024-06-15)

- [Added] T-002: No Runtime Errors

### v1.1.0 (2024-03-10)

- [Added] A-002: Clean Architecture
- [Updated] D-001: Changed test coverage target to 80%

### v1.0.0 (2024-01-01)

- Initial version created
````

**Save Location**: `.sdd/CONSTITUTION.md`

## Output

Depending on sub command, use the output-templates skill to output constitution management results.

## Constitution and Other Documents

### Documents to Synchronize

| Document                         | Sync Content                          |
|:---------------------------------|:--------------------------------------|
| `.sdd/SPECIFICATION_TEMPLATE.md` | Add principle reference sections      |
| `.sdd/DESIGN_DOC_TEMPLATE.md`    | Add principle compliance checklist    |
| `*_spec.md`                      | Design based on principles            |
| `*_design.md`                    | Explicitly state principle compliance |

### Sync Verification

Running `/constitution validate` automatically verifies:

1. **Template Constitution Version**: Does it reflect latest constitution?
2. **Principle Mention in Specs**: Are principles appropriately mentioned?
3. **Design Decision Compliance**: Do design decisions follow principles?

## Use Cases

| Scenario                 | Command                            | Purpose                           |
|:-------------------------|:-----------------------------------|:----------------------------------|
| **Project Start**        | `/constitution init`               | Create constitution file          |
| **Add New Principle**    | `/constitution add`                | Add principle and bump version    |
| **Before Creating Spec** | `/constitution validate`           | Check latest constitution         |
| **Before Review**        | `/constitution validate`           | Verify constitution compliance    |
| **Major Policy Change**  | `/constitution bump-version major` | Major version bump                |

## Constitution Change Rules

### Change Process

```
1. Propose change (discuss in Issue, etc.)
   ↓
2. Team approval
   ↓
3. Update constitution file
   ↓
4. Bump version
   ↓
5. Update affected documents
   ↓
6. Verify with /constitution validate
```

### Conditions for Major Version Bump

Major version bump required for any of the following:

- Removal of existing principle
- Significant change to existing principle
- Change in principle priority
- Breaking changes affecting existing specs/designs

## Best Practices

### When to Create Constitution

| Project Stage       | Recommended Action                                   |
|:--------------------|:-----------------------------------------------------|
| **New Project**     | Create constitution in setup phase                   |
| **Existing Project** | Create constitution to formalize practices          |
| **Team Scaling**    | Create constitution to ensure consistency            |
| **Quality Issues**  | Create constitution to raise standards               |

### Principle Design Guidelines

**Good Principles Are**:

- ✓ Clear and unambiguous
- ✓ Enforceable (can be checked)
- ✓ Justified (has clear rationale)
- ✓ Practical (can be followed)
- ✓ Specific (not vague)

**Bad Principles Are**:

- ✗ Vague ("Write good code")
- ✗ Unenforceable ("Be creative")
- ✗ Unjustified ("Because I said so")
- ✗ Impractical ("100% coverage on everything")
- ✗ Contradictory (conflicts with other principles)

### Constitution vs. Style Guide

| Document         | Purpose                   | Examples                            |
|:-----------------|:--------------------------|:------------------------------------|
| **Constitution** | Non-negotiable principles | TDD, Spec-first, Security standards |
| **Style Guide**  | Coding conventions        | Naming, formatting, comment style   |

Both are important, but constitution takes precedence.

## AI-SDD Workflow Integration

```
Constitution (Project-Level Principles)
         ↓
PRD (Business Requirements)
         ↓
Specification (Logical Design)
         ↓
Design Document (Technical Implementation)
         ↓
Implementation (Code)
```

Constitution principles are checked at each level.

## Advanced Features

### Principle Templates

Common principle templates you can adapt:

````markdown
### P{n}: {Principle Name}

**Principle**: {One sentence declaration}

**Rationale**: {Why this matters}

**Enforcement**:

- {How it's checked}
- {Tool/process used}

**Exceptions**: {When this doesn't apply}

**Version Added**: {X.Y.Z}
````

### Constitution as Code

Export constitution to machine-readable format:

```
/constitution export --format json
```

Output: `.sdd/constitution.json`

```json
{
  "version": "1.0.0",
  "principles": [
    {
      "id": "P1",
      "name": "Specification-First",
      "enforceable": true,
      "checks": [
        {
          "type": "file_exists",
          "pattern": ".sdd/specification/*_spec.md"
        }
      ]
    }
  ]
}
```

Use in CI/CD pipelines for automated validation.

## Notes

- Constitution file should be placed directly under `.sdd/` (`.sdd/CONSTITUTION.md`)
- Constitution is a living document, updated as team learns
- Version all changes to track evolution
- Major version changes may require code migration
- Keep principles few (3-7) and high-impact
- Too many principles = ignored principles
- Review constitution quarterly for relevance
- Constitution applies to AI-generated code too
- Use `/constitution validate` in PR checks
- Constitution violations should block merge (with explicit override process)
- Constitution changes should be made with team-wide consensus
- Always consider impact on existing specs/designs
- Explicitly state "why this principle is necessary"
- Define principles in verifiable form
- Constitution versioning follows semantic versioning