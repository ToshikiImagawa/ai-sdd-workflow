---
name: doc-consistency-checker-cli
description: "CLI-enhanced document consistency checker. Automatically checks consistency between PRD ↔ *_spec.md ↔ *_design.md using sdd-cli for structural validation."
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Glob, Grep, Bash
---

# Doc Consistency Checker (CLI) - Document Consistency Check

CLI-enhanced version: Uses `sdd-cli lint` for structural validation and dependency chain verification,
focusing LLM effort on terminology consistency and semantic analysis.

## Language Configuration

!`echo "Current language: ${SDD_LANG:-en}"`

When reading templates, use the path: `templates/${SDD_LANG:-en}/`

## Prerequisites

**Before execution, read the following references:**

- AI-SDD principles document: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md`
- `references/prerequisites_directory_paths.md` - Directory path resolution
- `references/cli_integration_guide.md` - CLI command reference
- `references/cli_error_handling.md` - Error handling and fallback strategies

## Input

This skill is triggered automatically via hooks during document updates or before implementation.

| Input Source       | Description                                                    |
|:-------------------|:---------------------------------------------------------------|
| Feature context    | Current feature being worked on (from task or document update) |
| Document paths     | Automatically resolved from `${SDD_*}` environment variables   |

**Note**: This skill is `user-invocable: false` and cannot be called directly.

## Document Dependencies

See `references/document_dependencies.md` for the document dependency chain and direction meaning.

## Processing Flow

### Phase 1: CLI - Structural Validation & Dependency Chain

Use `sdd-cli` for structural and cross-reference validation:

```bash
# Validate all documents structurally
sdd-cli lint --json
```

**From CLI output, extract:**

1. Front matter validation results (required fields, type-specific fields)
2. Dependency chain: PRD <- spec <- design (via `depends_on`)
3. Missing cross-references
4. Structural errors and warnings

**Error Handling**: If CLI fails, fall back to manual Glob/Grep/Read approach for document discovery and validation.

### Phase 2: LLM - Semantic Consistency Analysis

With structural validation done by CLI, focus LLM on semantic checks:

#### 1. PRD <-> spec Consistency

| Check Item                                | Description                                            |
|:------------------------------------------|:-------------------------------------------------------|
| **Requirement ID Mapping**                | Are PRD requirement IDs referenced in spec?            |
| **Functional Requirement Coverage**       | Are PRD functional requirements covered in spec?       |
| **Non-Functional Requirement Reflection** | Are PRD non-functional requirements reflected in spec? |
| **Terminology Consistency**               | Is same terminology used in PRD and spec?              |

#### 2. spec <-> design Consistency

| Check Item                                     | Description                                          |
|:-----------------------------------------------|:-----------------------------------------------------|
| **API Definition Match**                       | Is spec API detailed in design?                      |
| **Data Model Match**                           | Do spec type definitions match design?               |
| **Requirement Reflection in Design Decisions** | Are spec requirements reflected in design decisions? |
| **Constraint Consideration**                   | Are spec constraints considered in design?           |

#### 3. design <-> Implementation Consistency

| Check Item                     | Description                                                    |
|:-------------------------------|:---------------------------------------------------------------|
| **Module Structure Match**     | Does design module structure match actual directory structure? |
| **Interface Definition Match** | Do design definitions match implementation code?               |
| **Technology Stack Match**     | Are libraries documented in design actually being used?        |

### Phase 3: Integrate Results

Merge CLI structural results with LLM semantic results into unified report.

## Automatic Detection Patterns

### Inconsistency Detection

1. **Missing**: Exists in upstream document but not reflected in downstream
2. **Contradiction**: Different content described in upstream and downstream
3. **Obsolescence**: Downstream changes not reflected in upstream

## Output Format

Read `templates/${SDD_LANG:-en}/consistency_report.md` and use it for consistency check output.

## Document Update Triggers

Based on consistency check results, recommend document updates in the following cases:

### When to Update `*_spec.md`

- Public API signature changes (arguments, return values, types)
- New data model additions
- Fundamental changes to existing behavior

### When to Update `*_design.md`

- Technology stack changes (library additions/changes)
- Important architectural decisions
- Module structure changes

### When Updates Are NOT Needed

- Internal implementation optimization (no interface changes)
- Bug fixes (correcting deviations from specifications)
- Refactoring (no behavior changes)

## Notes

- This skill **detects and reports** but does not auto-fix
- Inconsistency resolution is left to developer judgment
- Prioritize upstream documents (PRD > spec > design)
- Do not uniformly treat specs as correct, as implementation may be correct and specs outdated
