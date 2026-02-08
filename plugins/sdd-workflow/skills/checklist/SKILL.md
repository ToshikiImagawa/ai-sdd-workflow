---
name: checklist
description: "Generate quality assurance checklists from specifications and plans with structured IDs and categories"
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Checklist - Quality Checklist Generation

Automatically generates comprehensive quality assurance checklists from specifications, design documents, and task
breakdowns.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

| Argument        | Required | Description                                                        |
|:----------------|:---------|:-------------------------------------------------------------------|
| `feature-name`  | Yes      | Target feature name or path (e.g., `user-auth`, `auth/user-login`) |
| `ticket-number` | -        | Used for output directory name. Uses feature-name if omitted       |

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
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md (PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md (required)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md (required)
Load ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/tasks.md (if exists)
```

**For hierarchical structure** (when argument contains `/`):

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md (parent feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md (child feature spec, required)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md (parent feature design, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md (child feature design, required)
Load ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/tasks.md (if exists)
```

**Note the difference in naming conventions**:

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
| **P1 - High**   | P1   | Must pass before merge   | Before PR creation |
| **P2 - Medium** | P2   | Should pass before merge | During PR review   |
| **P3 - Low**    | P3   | Nice to have             | Opportunistic      |

## Output Format

### Checklist Document

For a complete checklist example with all categories (CHK-101 through CHK-903), priority levels, and completion criteria, see:

**Reference**: `examples/checklist_full_example.md`

The example includes 9 categories (Requirements, Specification, Design, Implementation, Testing, Documentation, Security, Performance, Deployment) with 60 total items across P1/P2/P3 priority levels.

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/checklist.md`

## Checklist Template Integration

This command uses the template from `templates/${SDD_LANG:-en}/checklist_template.md` (within this skill directory) as a base and customizes it
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
/generate-spec {feature}
   |
/task-breakdown {feature}
   |
/checklist {feature} {ticket}  <- Generate checklist
   |
/implement {feature} {ticket}  <- Use checklist during implementation
   |
Review against checklist before PR
```

## Notes

- Checklist items are derived from specifications, not invented
- IDs (CHK-101, CHK-201, etc.) are stable across updates and organized by category
- Priority levels (P1, P2, P3) can be customized per project
- Some items may require manual verification
- Automated checks should be integrated into CI/CD where possible
- Archive checklist with task logs for future reference
