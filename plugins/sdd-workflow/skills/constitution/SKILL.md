---
name: constitution
description: "Define and manage non-negotiable project principles (Constitution) and verify synchronization with other documents"
argument-hint: "<subcommand> [arguments]"
license: MIT
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Skill, Edit(.sdd/**), Edit(CLAUDE.md), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/constitution/scripts/validate-files.py" *)
---

# Constitution - Project Principles Management

Define the project's non-negotiable principles (Constitution)
and verify that all specifications and design documents comply with them.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read only these sections of the AI-SDD principles document (not the whole file): § Recommended Directory Structure, § Importance of CONSTITUTION.md Compliance Check
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

| Example                                                 | Description                                |
|:----------------------------------------------------------|:--------------------------------------------|
| `/constitution init`                                       | Initialize constitution file (interactive)  |
| `/constitution init "TypeScript/React Web application"`    | Initialize with context (non-interactive)   |
| `/constitution validate`                                    | Validate constitution compliance            |
| `/constitution add "Library-First"`                         | Add new principle                           |
| `/constitution bump-version major`                          | Major version bump                          |

## Processing Flow

### 1. Initialize (init)

Create a constitution file in the project by running `/constitution init`.

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

- `SDD_LANG=en` (or unset) → All content in English (use `templates/en/`)
- `SDD_LANG=ja` → All content in Japanese (use `templates/ja/`)
- The template language is the authoritative source for the output language — never override it with user preferences or
  global CLAUDE.md settings

**Content**: Template customized for the project

### 2. Add Principle (add)

Add a new principle to a constitution by running `/constitution add "Library-First"`.

**Process**:

1. Confirm principle details with the user
2. Add to the appropriate category
3. Bump version per the "Version Bump Rules" in §4
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

**Interactive Prompts**: See `examples/update_interactive_session.md` for an example interactive session.

**Version Bump Rules**:

| Change Type                | Version Impact                           |
|:---------------------------|:-----------------------------------------|
| Add principle              | MINOR (x.Y.z) or MAJOR (X.y.z)           |
| Modify principle           | MINOR (x.Y.z) or MAJOR (X.y.z)           |
| Remove principle           | MINOR (x.Y.z) or MAJOR (X.y.z)           |
| Change principle priority  | MINOR (x.Y.z) or MAJOR (X.y.z)           |
| Update enforcement         | MINOR (x.Y.z)                            |
| Clarify principle (meaning unchanged) | PATCH (x.y.Z)         |
| Fix typo / wording / link  | PATCH (x.y.Z)                            |

Where a row shows MINOR or MAJOR, it is MAJOR only if the change makes existing implementations violations;
otherwise MINOR (see the rule below).

This table enumerates the same change types as the "Semantic Versioning" table in §7 (Version Management),
and the two must agree row for row. The split follows one rule: **does the change make existing
implementations violations?** Judge by impact, not by size of the wording change.

- **MAJOR** — a breaking change: specs, designs, or code that already comply start to violate (§7's
  "Conditions for Major Version Bump"). Removal, change of meaning, a new principle, or wider scope all count,
  but only where they create violations.
- **MINOR** — a feature addition or update that leaves existing implementations compliant: a new principle
  (see the "Add Principle (add)" flow in §2), broader or clearer scope, added process rules, a new/updated
  enforcement mechanism, or a relaxation that changes meaning but violates nothing.
- **PATCH** — a fix that does not change meaning: typos, wording, link fixes.

State the impact on existing implementations, and why, in the amendment PR so a reviewer (or the team's agreed review mechanism) can confirm the bump.

### 5. Validate (validate)

Verify all specifications and design documents comply with constitution by running `/constitution validate`.

**Optimized Execution Flow**:

**Phase 1: Shell Script** - Execute `python3 "${CLAUDE_PLUGIN_ROOT}/skills/constitution/scripts/validate-files.py"` to
scan file structure.

This script:

1. Scans all requirement files (`${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/**/*.md`)
2. Scans all specification files (every `.md` under `${SDD_SPECIFICATION_PATH}` except `*_design.md` — the
   `_spec` suffix is optional there)
3. Scans v4.x persistent design docs (`*_design.md`) separately, where a project still has them
4. Generates file lists and summary JSON
5. Exports environment variables to `$CLAUDE_ENV_FILE`:
    - `CONSTITUTION_REQUIREMENT_FILES` - List of requirement files
    - `CONSTITUTION_SPEC_FILES` - List of spec files
    - `CONSTITUTION_DESIGN_FILES` - List of design files
    - `CONSTITUTION_SUMMARY` - JSON summary with file counts

**Phase 2: Claude** - Read files from pre-scanned lists and validate content

**Validation Targets**:

- `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/**/*.md` (PRDs)
- `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/**/*.md` (abstract specs, suffix optional)
- `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/**/*_design.md` (v4.x persistent design docs, when present)
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`
- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md`

Not scanned by this skill: `${SDD_TASK_PATH}/{ticket-number}/design-draft.md` (temporary, deleted after
implementation) and `${SDD_ADR_PATH}/**/*.md`. Principle compliance for those is reviewed while the ticket is
open, not by this validation pass.

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

3. **Update ADR Template** (`${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md`):
    - Add a principle reference to the entry format, so an entry's `Rationale` states the principle the
      decision rests on
    - Sync terminology
    - Keep the required entry items (`Decision` / `Rationale` / `Rejected alternatives`) intact — skills read
      them mechanically
    - Sync touches the **template only**. Recorded entries in `${SDD_ADR_PATH}/{feature-name}.md` are
      append-only and are never rewritten by a sync

4. **Update Task Templates**:
    - Add compliance verification tasks
    - Update completion criteria
    - Reference relevant principles

5. **Update Checklist Template**:
    - Add principle verification items
    - Update priorities
    - Sync quality gates

**Output**: See `examples/sync_report.md` for an example sync report.

### 7. Version Management (bump-version)

Update constitution version by running `/constitution bump-version {major|minor|patch}` (e.g.
`/constitution bump-version major` for a breaking change, `minor` to add a principle, `patch` for a typo fix).

**Semantic Versioning**:

| Version Type | Use Case                                                                    | Example        |
|:-------------|:----------------------------------------------------------------------------|:---------------|
| Major        | Breaking change that makes existing implementations violations (removal, change of meaning, new principle, or wider scope, only where it creates violations) | 1.0.0 -> 2.0.0 |
| Minor        | Feature addition/update (new principle, broader or clearer scope, added process rules, enforcement mechanism, relaxation that leaves existing implementations compliant) | 1.0.0 -> 1.1.0 |
| Patch        | Fix that does not change meaning (typo, wording, link) | 1.0.0 -> 1.0.1 |

This mirrors the "Version Bump Rules" table in §4 (Update Constitution); keep the two in sync when either
changes.

## Constitution File Structure

For a complete constitution file example with all categories (Business, Architecture, Development Methodology, Technical
Constraints), principle hierarchy, verification items, and change history, see:

**Reference**: `examples/constitution_file_structure.md`

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

## Output

Depending on sub command, use the `templates/${SDD_LANG:-en}/constitution_output.md` template for output formatting.

## Quality Checks

- [ ] Language consistent (matches template language, not user's global settings)
- [ ] Template structure maintained (headings, tables, sections preserved)
- [ ] All placeholders replaced with project-specific content
- [ ] Dates replaced (`YYYY-MM-DD` → actual date)

## Constitution and Other Documents

### Documents to Synchronize

| Document                                                      | Sync Content                          |
|:--------------------------------------------------------------|:--------------------------------------|
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` | Add principle reference sections      |
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`    | Add principle compliance checklist    |
| `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md`           | Add principle reference to the entry format |
| Abstract specs under `specification/` (suffix optional)       | Design based on principles            |
| `task/{ticket-number}/design-draft.md`                        | Explicitly state principle compliance |
| `adr/{feature-name}.md`                                       | State the principle a decision rests on in its `Rationale` |

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

The change process follows these steps in order: propose change (discuss in Issue, etc.) -> team approval -> update
constitution file -> bump version -> update affected documents -> verify with `/constitution validate`.

### Conditions for Major Version Bump

Major version bump is required only when the change makes existing implementations violations, for example:

- Removal of an existing principle that makes existing implementations violations
- Change to an existing principle's meaning or priority that makes existing implementations violations
- A new principle or wider scope that makes existing implementations violations
- Breaking changes affecting existing specs/designs

## Best Practices

See `references/best_practices.md` for detailed guidance on:

- When to create a constitution
- Principle design guidelines (good vs. bad principles)
- Constitution vs. style guide comparison
- Advanced features (principle templates, constitution as code)

## AI-SDD Workflow Integration

Constitution principles are checked at each level of the AI-SDD workflow, in this order: Constitution
(Project-Level Principles) -> PRD (Business Requirements) -> Specification (Logical Design) -> Design Document
(Technical Implementation) -> Implementation (Code).

## Notes

- Constitution file location: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`
- Keep principles few (3-7) and high-impact
- Constitution versioning follows semantic versioning
- See `references/best_practices.md` for additional recommendations
