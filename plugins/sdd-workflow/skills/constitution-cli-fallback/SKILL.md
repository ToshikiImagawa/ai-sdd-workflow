---
name: constitution-cli-fallback
description: "Define and manage non-negotiable project principles (Constitution) and verify synchronization with other documents (CLI-fallback version without CLI integration). Used when sdd-cli is not available."
argument-hint: "<subcommand> [arguments]"
version: 3.0.0
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
- `examples/cli_fallback_json_output.md` - JSON output format specification

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
/constitution init "TypeScript/React Web application"  # Initialize with context (requires context argument)
/constitution validate                  # Validate constitution compliance
/constitution add "Library-First"       # Add new principle
/constitution bump-version major        # Major version bump
```

## Execution Mode

**This skill operates in non-interactive mode**:

- ✅ `init` requires context argument → No interactive prompts
- ✅ `validate` uses LLM structural validation → No user confirmation
- ✅ `add` / `bump-version` / `update` execute without confirmation

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
    - **Context argument is required**: Use it as the project context
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

### Phase 1: Document Discovery & Structural Validation

Execute `validate-files.sh` to scan file structure:

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

**LLM Structural Validation Steps** (replacing CLI lint):

Since CLI is not available, LLM performs the following structural checks using Read, Glob, and Grep tools:

#### 1. Circular Dependency Check

**Purpose**: Detect circular references in `depends-on` chains

**Steps**:

1. **Extract all dependencies**:
    - Read YAML front matter from all discovered documents
    - Parse `depends-on:` arrays
    - Build dependency map: `{id: [dep1, dep2, ...]}`

2. **Detect cycles using depth-first search**:
    - For each document ID, traverse dependency chain
    - Track visited nodes in current path
    - If a node is revisited in same path → circular dependency detected

3. **Report circular dependencies**:
    - List all cycles found (e.g., `A → B → C → A`)
    - Suggest breaking the cycle by removing one dependency

**Example check**:

```
PRD "prd-auth" depends-on: []
Spec "spec-auth" depends-on: ["prd-auth"]
Design "design-auth" depends-on: ["spec-auth", "design-database"]
Design "design-database" depends-on: ["design-auth"]  ← CIRCULAR!
```

#### 2. Broken Link Check

**Purpose**: Verify all internal document links are valid

**Steps**:

1. **Extract internal links**:
    - Use Grep to find Markdown links: `\[.*\]\((\.\.\/|\.\/|[^http]).*\.md\)`
    - Parse relative paths from current document location

2. **Verify target files exist**:
    - Resolve relative path to absolute path
    - Check if file exists using Glob or Read
    - Handle both flat and hierarchical structures

3. **Report broken links**:
    - List source file, link text, and broken target path
    - Suggest fixing the link or removing it

**Example check**:

```bash
# Find all markdown links
grep -r "\[.*\](\.\.\/.*\.md)" ${SDD_ROOT}
# Verify each target exists
```

#### 3. Duplicate ID Check

**Purpose**: Ensure all document IDs are unique

**Steps**:

1. **Extract all IDs**:
   ```bash
   grep -h "^id:" ${SDD_REQUIREMENT_PATH}/**/*.md ${SDD_SPECIFICATION_PATH}/**/*.md | sort
   ```

2. **Detect duplicates**:
   ```bash
   grep -h "^id:" ${SDD_REQUIREMENT_PATH}/**/*.md ${SDD_SPECIFICATION_PATH}/**/*.md | sort | uniq -d
   ```

3. **Report duplicate IDs**:
    - List duplicate ID value
    - List all files using that ID
    - Suggest renaming one of them

**Example output**:

```
DUPLICATE ID: "spec-user-auth"
  Found in: specification/auth/user_spec.md
  Found in: specification/legacy/user_spec.md
  → Rename one to "spec-user-auth-v2" or "spec-legacy-user-auth"
```

#### 4. Orphan Reference Check

**Purpose**: Find `depends-on` entries pointing to non-existent documents

**Steps**:

1. **Collect all existing IDs**:
    - Extract `id:` fields from all documents
    - Build a set of valid IDs

2. **Check all dependencies**:
    - For each document, read `depends-on:` array
    - Verify each referenced ID exists in valid IDs set

3. **Report orphaned references**:
    - List document with orphaned reference
    - List the non-existent ID
    - Suggest creating the missing document or removing the reference

**Example output**:

```
ORPHAN REFERENCE in specification/auth/login_design.md:
  depends-on: ["spec-session-management"]
  But "spec-session-management" does not exist
  → Create specification/session/session-management_spec.md
  → Or remove from depends-on array
```

**Structural Validation Summary**:

After performing all checks, provide a summary:

```
Structural Validation Results:
✓ Circular dependencies: 0 found
✗ Broken links: 2 found
✓ Duplicate IDs: 0 found
✗ Orphan references: 1 found

Details:
- Broken link: specification/auth/login_spec.md → ../requirement/nonexistent.md
- Broken link: requirement/auth.md → ./old-api.md
- Orphan reference: specification/auth/login_design.md → spec-session-management
```

### Phase 2: Content Validation

Read files from discovery results and validate content

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

### Phase 3: Generate JSON Output (validate subcommand only)

**MANDATORY**: After validation, output JSON to stdout using Bash tool.

**Format specification**: See `examples/cli_fallback_json_output.md` > "Constitution Validation Output"

**Important**: Include all issues found during LLM Structural Validation Steps (Phase 1) in `lint_results.issues`.

**Example output with validation results**:

```bash
cat << 'EOF'
{
  "search_results": {
    "results": [
      {
        "file_path": "/absolute/path/.sdd/CONSTITUTION.md",
        "file_type": "constitution",
        "title": "Project Constitution",
        "id": "constitution-v1",
        "status": "active"
      }
    ]
  },
  "lint_results": {
    "issues": [
      {
        "severity": "error",
        "rule": "circular-dependency",
        "file_path": "/absolute/path/.sdd/specification/auth/login_design.md",
        "line": 0,
        "column": 0,
        "message": "Circular dependency detected: design-auth → design-database → design-auth",
        "details": {
          "field": "depends-on",
          "cycle": ["design-auth", "design-database", "design-auth"]
        }
      },
      {
        "severity": "warning",
        "rule": "broken-link",
        "file_path": "/absolute/path/.sdd/requirement/auth.md",
        "line": 15,
        "column": 0,
        "message": "Broken internal link: ../old-api.md does not exist",
        "details": {
          "field": "link",
          "target": "../old-api.md"
        }
      }
    ]
  },
  "validated_files": [
    "/absolute/path/.sdd/CONSTITUTION.md",
    "/absolute/path/.sdd/requirement/auth.md",
    "/absolute/path/.sdd/specification/auth/login_spec.md",
    "/absolute/path/.sdd/specification/auth/login_design.md"
  ],
  "status": "success"
}
EOF
```

**Important**:

- Replace placeholders with actual values from validated documents
- Use absolute paths
- Include all issues from LLM Structural Validation Steps in `lint_results.issues`
- If no issues found, use empty array `"issues": []`
- `search_results` contains all documents that were validated

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
