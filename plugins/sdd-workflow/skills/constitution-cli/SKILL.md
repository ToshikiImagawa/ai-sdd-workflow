---
name: constitution-cli
description: "CLI-enhanced constitution management. Define and manage non-negotiable project principles and verify synchronization with other documents using sdd-cli."
argument-hint: "<subcommand> [arguments]"
version: 3.1.0
license: MIT
user-invocable: false
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Constitution (CLI) - Project Principles Management

CLI-enhanced version: Uses `sdd-cli lint` for structural validation of principle documents
and `sdd-cli search` for related document discovery.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/cli_integration_guide.md` - CLI command reference
- `references/cli_error_handling.md` - Error handling and fallback strategies

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

Same as non-CLI version. Create a constitution file in the project:

**Generated File**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

**Processing Flow**:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` already exists
2. If exists: Skip (respecting an existing constitution)
3. If not exist:
    - Read `templates/${SDD_LANG:-en}/constitution_template.md`
    - **If context argument is provided**: Use it as the project context
    - **If no context argument**: Interactively ask the user about the project context
    - Customize template based on project context

#### Language Consistency

> **CRITICAL**: The output language MUST match the template language.

- `SDD_LANG=en` (or unset) -> All content in English (use `templates/en/`)
- `SDD_LANG=ja` -> All content in Japanese (use `templates/ja/`)

### 2. Add Principle (add)

Same as non-CLI version:

1. Confirm principle details with the user
2. Add to the appropriate category
3. Bump minor version
4. Record in change history

### 3-4. Show / Update

Same as non-CLI version.

### 5. Validate (validate) - CLI Enhanced

Verify all specifications and design documents comply with constitution:

**Phase 1: CLI - Structural Validation & Document Discovery**

```bash
# Validate all document structures
sdd-cli lint --json

# Find all related documents
sdd-cli search --format json
```

**From CLI output, extract:**

1. List of all requirement, spec, and design documents
2. Front matter validation results
3. Dependency chain validation
4. Structural issues

**Error Handling**: If CLI fails, fall back to the shell script approach:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/constitution-cli/scripts/validate-files.sh"
```

**Phase 2: LLM - Principle Compliance Check**

With document list from CLI, focus LLM on semantic validation:

| Validation Item             | Check Content                                  |
|:----------------------------|:-----------------------------------------------|
| **Principle Mention**       | Are principles mentioned in specs/designs?     |
| **Principle Compliance**    | Do implementation decisions follow principles? |
| **Contradiction Detection** | Are there descriptions contrary to principles? |
| **Template Sync**           | Do templates reflect latest constitution?      |

**Phase 3: Integrate Results**

Merge CLI structural results with LLM semantic results into unified validation report.

**Validation Output Format**: See `examples/validation_report.md`.

### 6. Sync Principles (sync)

Same as non-CLI version.

### 7. Version Management (bump-version)

Same as non-CLI version.

## Constitution File Structure

**Reference**: `examples/constitution_file_structure.md`

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

## Output

Depending on sub command, use the `templates/${SDD_LANG:-en}/constitution_output.md` template for output formatting.

## Quality Checks

- [ ] Language consistent (matches template language, not user's global settings)
- [ ] Template structure maintained (headings, tables, sections preserved)
- [ ] All placeholders replaced with project-specific content
- [ ] Dates replaced (`YYYY-MM-DD` -> actual date)

## Best Practices

See `references/best_practices.md` for detailed guidance.

## Notes

- Constitution file location: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`
- Keep principles few (3-7) and high-impact
- Constitution versioning follows semantic versioning
