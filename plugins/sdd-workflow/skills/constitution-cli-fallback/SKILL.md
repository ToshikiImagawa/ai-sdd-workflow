---
name: constitution-cli-fallback
description: "Define and manage non-negotiable project principles (Constitution) and verify synchronization with other documents"
argument-hint: "<subcommand> [arguments]"
version: 3.1.0
license: MIT
user-invocable: false
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
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

| Subcommand     | Description                      | Additional Arguments   |
|:---------------|:---------------------------------|:-----------------------|
| `init`         | Initialize constitution file     | `[context]` (optional) |
| `validate`     | Validate constitution compliance | -                      |
| `add`          | Add new principle                | `"principle-name"`     |
| `bump-version` | Version bump                     | `major\|minor\|patch`  |

### Input Examples

```
init                      # Initialize constitution file (interactive)
init "TypeScript/React Web application"  # Initialize with context (non-interactive)
validate                  # Validate constitution compliance
add "Library-First"       # Add new principle
bump-version major        # Major version bump
```

## Processing Flow

### 1. Initialize (init)

Create a constitution file in the project:

**Generated File**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

**Processing Flow**:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` already exists
2. If exists: Skip (respecting an existing constitution)
3. If not exist:
    - Read `templates/${SDD_LANG:-en}/constitution_template.md`
    - **If context argument is provided**: Use it as the project context
    - **If no context argument**: Interactively ask the user about the project context (language, framework, domain)
    - Use the loaded template as the base document and customize it by replacing placeholders based on the project
      context

#### Template Application Notes

- Replace placeholders (`{Principle Name}`, `{Description of the principle}`, `{Applicable scope}`, `{Validation item}`,
  `YYYY-MM-DD`, etc.) with project-specific content
- Pre-filled principle examples (A-001: Library-First, A-002: Clean Architecture, D-001: Test-First, D-002:
  Specification-Driven) should be kept, adjusted, or replaced based on project context
- Placeholder-only sections (B-001, B-002, T-001, T-003) must be filled with project-specific principles or removed if
  not applicable
- Maintain the template's overall structure (headings, tables, sections)

#### Language Consistency

> **CRITICAL**: The output language MUST match the template language.
> Do NOT mix languages regardless of the user's global language settings.

- `SDD_LANG=en` (or unset) -> All content in English (use `templates/en/`)
- `SDD_LANG=ja` -> All content in Japanese (use `templates/ja/`)
- The template language is the authoritative source for the output language

**Content**: Template customized for the project

### 2. Add Principle (add)

Add a new principle to a constitution:

**Process**:

1. Confirm principle details with the user
2. Add to the appropriate category
3. Bump minor version (e.g., 1.0.0 -> 1.1.0)
4. Record in change history

### 3. Show Current Constitution (show)

**Output Content**:

- Current version
- All principles
- Recent changes
- Compliance status

### 4. Update Constitution (update)

**Interactive Prompts**:

```
What type of change?
1. Add new principle (MAJOR)
2. Modify existing principle (MAJOR)
3. Clarify existing principle (MINOR)
4. Update enforcement methods (MINOR)
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

**Optimized Execution Flow**:

**Phase 1: Shell Script** - Execute `validate-files.sh` to scan file structure:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/constitution-cli-fallback/scripts/validate-files.sh"
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

**Purpose**: Ensure principles are reflected in other documents

**Actions**:

1. **Update Specification Template**: Add principle references, update constraints section, sync terminology
2. **Update Design Template**: Add principle compliance section, update decision framework
3. **Update Task Templates**: Add compliance verification tasks, update completion criteria
4. **Update Checklist Template**: Add principle verification items, update priorities

### 7. Version Management (bump-version)

Update constitution version:

**Semantic Versioning**:

| Version Type | Use Case                                                  | Example        |
|:-------------|:----------------------------------------------------------|:---------------|
| Major        | Remove/significantly change existing principle (breaking) | 1.0.0 -> 2.0.0 |
| Minor        | Add new principle                                         | 1.0.0 -> 1.1.0 |
| Patch        | Fix expression of principle, typo fix                     | 1.0.0 -> 1.0.1 |

## Constitution File Structure

For a complete constitution file example with all categories, see:

**Reference**: `examples/constitution_file_structure.md`

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

## Output

Depending on sub command, use the `templates/${SDD_LANG:-en}/constitution_output.md` template for output formatting.

## Quality Checks

- [ ] Language consistent (matches template language, not user's global settings)
- [ ] Template structure maintained (headings, tables, sections preserved)
- [ ] All placeholders replaced with project-specific content
- [ ] Dates replaced (`YYYY-MM-DD` -> actual date)

## Constitution and Other Documents

### Documents to Synchronize

| Document                                                      | Sync Content                          |
|:--------------------------------------------------------------|:--------------------------------------|
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` | Add principle reference sections      |
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`    | Add principle compliance checklist    |
| `*_spec.md`                                                   | Design based on principles            |
| `*_design.md`                                                 | Explicitly state principle compliance |

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
