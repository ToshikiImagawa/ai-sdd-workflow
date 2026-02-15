---
name: constitution
description: "Define and manage non-negotiable project principles (Constitution) and verify synchronization with other documents"
argument-hint: "<subcommand> [arguments]"
version: 3.0.0
license: MIT
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Skill, Bash
---

# Constitution - Project Principles Management

Define the project's non-negotiable principles (Constitution)
and verify that all specifications and design documents comply with them.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## What is a Project Constitution?

A Project Constitution defines **non-negotiable principles that form the foundation of all design decisions**.

### Constitution Characteristics

| Characteristic     | Description                                                     |
|:-------------------|:----------------------------------------------------------------|
| **Non-negotiable** | Not open to debate. Changes require careful consideration       |
| **Persistent**     | Consistently applied across the entire project                  |
| **Hierarchical**   | Higher principles take precedence over lower ones               |
| **Verifiable**     | Can automatically verify spec/design compliance with principles |

### Constitution Examples

| Principle Category | Example Principles                       |
|:-------------------|:-----------------------------------------|
| **Architecture**   | Library-First, Clean Architecture        |
| **Development**    | Test-First, Specification-Driven         |
| **Quality**        | Test Coverage > 80%, Zero Runtime Errors |
| **Technical**      | TypeScript Only, No Any Types            |
| **Business**       | Privacy by Design, Accessibility First   |

## Input

$ARGUMENTS

| Subcommand     | Description                      | Additional Arguments  |
|:---------------|:---------------------------------|:----------------------|
| `init`         | Initialize constitution file     | -                     |
| `validate`     | Validate constitution compliance | -                     |
| `add`          | Add new principle                | `"principle-name"`    |
| `bump-version` | Version bump                     | `major\|minor\|patch` |

### Input Examples

```
/constitution init                      # Initialize constitution file
/constitution validate                  # Validate constitution compliance
/constitution add "Library-First"       # Add new principle
/constitution bump-version major        # Major version bump
```

## Processing Flow

### 1. Initialize (init)

Create a constitution file in the project:

```bash
/constitution init
```

**Generated File**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

**Processing Flow**:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` already exists
2. If exists: Skip (respecting an existing constitution)
3. If not exist:
    - Read `templates/${SDD_LANG:-en}/constitution_template.md`
    - Analyze project context (language, framework, domain)
    - Generate a customized constitution based on context

**Content**: Template customized for the project

### 2. Add Principle (add)

Add a new principle to a constitution:

```bash
/constitution add "Library-First"
```

**Process**:

1. Confirm principle details with the user
2. Add to the appropriate category
3. Bump minor version (e.g., 1.0.0 -> 1.1.0)
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

Constitution updated
  Version: 1.0.0 -> 2.0.0
  Changes: Added principle P4
```

**Version Bump Rules**:

| Change Type        | Version Impact | Example        |
|:-------------------|:---------------|:---------------|
| Add principle      | MAJOR (X.y.z)  | 1.0.0 -> 2.0.0 |
| Modify principle   | MAJOR (X.y.z)  | 1.0.0 -> 2.0.0 |
| Remove principle   | MAJOR (X.y.z)  | 1.0.0 -> 2.0.0 |
| Clarify principle  | MINOR (x.Y.z)  | 1.0.0 -> 1.1.0 |
| Update enforcement | MINOR (x.Y.z)  | 1.0.0 -> 1.1.0 |
| Fix typo           | PATCH (x.y.Z)  | 1.0.0 -> 1.0.1 |

### 5. Validate (validate)

Verify all specifications and design documents comply with constitution:

```bash
/constitution validate
```

**Optimized Execution Flow**:

**Phase 1: Shell Script** - Execute `validate-files.sh` to scan file structure:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/constitution/scripts/validate-files.sh"
```

This script:

1. Scans all requirement files (`${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/**/*.md`)
2. Scans all specification files (`*_spec.md`)
3. Scans all design files (`*_design.md`)
4. Generates file lists and summary JSON
5. Exports environment variables to `$CLAUDE_ENV_FILE`:
    - `CONSTITUTION_REQUIREMENT_FILES` - List of requirement files
    - `CONSTITUTION_SPEC_FILES` - List of spec files
    - `CONSTITUTION_DESIGN_FILES` - List of design files
    - `CONSTITUTION_SUMMARY` - JSON summary with file counts

**Phase 2: Claude** - Read files from pre-scanned lists and validate content

**Validation Targets**:

- `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/**/*.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/**/*_spec.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/**/*_design.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`

**Validation Items**:

| Validation Item             | Check Content                                  |
|:----------------------------|:-----------------------------------------------|
| **Principle Mention**       | Are principles mentioned in specs/designs?     |
| **Principle Compliance**    | Do implementation decisions follow principles? |
| **Contradiction Detection** | Are there descriptions contrary to principles? |
| **Template Sync**           | Do templates reflect latest constitution?      |

**Validation Output Format**: See `examples/validation_report.md` for the complete report template.

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

- [x] `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md`
    - Added P1 reference to API section
    - Updated constraints to include P3

- [x] `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`
    - Added "Principle Compliance" section
    - Updated decision framework to match constitution

- [x] `skills/checklist/templates/checklist_template.md`
    - Added principle verification items
    - CHK-CONST-001: P1 verification
    - CHK-CONST-002: P2 verification
    - CHK-CONST-003: P3 verification

## Sync Status

All documents synchronized with Constitution v2.0.0

````

### 7. Version Management (bump-version)

Update constitution version:

```bash
/constitution bump-version major   # Major version bump (breaking change)
/constitution bump-version minor   # Minor version bump (add principle)
/constitution bump-version patch   # Patch version bump (typo fix)
```

**Semantic Versioning**:

| Version Type | Use Case                                                  | Example        |
|:-------------|:----------------------------------------------------------|:---------------|
| Major        | Remove/significantly change existing principle (breaking) | 1.0.0 -> 2.0.0 |
| Minor        | Add new principle                                         | 1.0.0 -> 1.1.0 |
| Patch        | Fix expression of principle, typo fix                     | 1.0.0 -> 1.0.1 |

## Constitution File Structure

For a complete constitution file example with all categories (Business, Architecture, Development Methodology, Technical
Constraints), principle hierarchy, verification items, and change history, see:

**Reference**: `examples/constitution_file_structure.md`

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

## Output

Depending on sub command, use the `templates/${SDD_LANG:-en}/constitution_output.md` template for output formatting.

## Constitution and Other Documents

### Documents to Synchronize

| Document                                                      | Sync Content                          |
|:--------------------------------------------------------------|:--------------------------------------|
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` | Add principle reference sections      |
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`    | Add principle compliance checklist    |
| `*_spec.md`                                                   | Design based on principles            |
| `*_design.md`                                                 | Explicitly state principle compliance |

### Sync Verification

Running `/constitution validate` automatically verifies:

1. **Template Constitution Version**: Does it reflect latest constitution?
2. **Principle Mention in Specs**: Are principles appropriately mentioned?
3. **Design Decision Compliance**: Do design decisions follow principles?

## Use Cases

| Scenario                 | Command                            | Purpose                        |
|:-------------------------|:-----------------------------------|:-------------------------------|
| **Project Start**        | `/constitution init`               | Create constitution file       |
| **Add New Principle**    | `/constitution add`                | Add principle and bump version |
| **Before Creating Spec** | `/constitution validate`           | Check latest constitution      |
| **Before Review**        | `/constitution validate`           | Verify constitution compliance |
| **Major Policy Change**  | `/constitution bump-version major` | Major version bump             |

## Constitution Change Rules

### Change Process

```
1. Propose change (discuss in Issue, etc.)
   |
2. Team approval
   |
3. Update constitution file
   |
4. Bump version
   |
5. Update affected documents
   |
6. Verify with /constitution validate
```

### Conditions for Major Version Bump

Major version bump required for any of the following:

- Removal of existing principle
- Significant change to existing principle
- Change in principle priority
- Breaking changes affecting existing specs/designs

## Best Practices

See `references/best_practices.md` for detailed guidance on:

- When to create a constitution
- Principle design guidelines (good vs. bad principles)
- Constitution vs. style guide comparison
- Advanced features (principle templates, constitution as code)

## AI-SDD Workflow Integration

```
Constitution (Project-Level Principles)
         |
PRD (Business Requirements)
         |
Specification (Logical Design)
         |
Design Document (Technical Implementation)
         |
Implementation (Code)
```

Constitution principles are checked at each level.

## Notes

- Constitution file location: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`
- Keep principles few (3-7) and high-impact
- Constitution versioning follows semantic versioning
- See `references/best_practices.md` for additional recommendations
