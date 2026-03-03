---
name: generate-spec-cli-fallback
description: "Generate Abstract Specification and Technical Design Document from input content (CLI-fallback version without CLI integration). Used when sdd-cli is not available."
argument-hint: "<requirements-description>"
version: 3.0.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Specification & Design Doc Generator

Generates the following documents from input content according to the AI-SDD workflow:

1. `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md` - Abstract Specification (Specify Phase)
2. `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md` - Technical Design Document (Plan Phase)

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `examples/cli_fallback_json_output.md` - JSON output format specification

### Template Preparation Flow (Optimized)

**Phase 1: Python Script** - Execute `prepare-spec.py` to pre-load templates and references:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/generate-spec/scripts/prepare-spec.py"
```

This script:

1. Checks `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` and
   `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md` (project templates) first
2. If not found, copies from `templates/${SDD_LANG}/` to cache
3. Copies all reference files to cache
4. Exports environment variables to `$CLAUDE_ENV_FILE`:
    - `GENERATE_SPEC_SPEC_TEMPLATE` - Path to cached spec template
    - `GENERATE_SPEC_DESIGN_TEMPLATE` - Path to cached design template
    - `GENERATE_SPEC_REFERENCES` - Path to cached references

**Phase 2: Claude** - Read from cache using environment variables instead of searching files

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

### Pre-Generation Verification

Before generation, verify the following:

1. Does the `${SDD_ROOT}/` directory exist in the project?
2. If template files exist, use them

## Input

$ARGUMENTS

| Argument                   | Required | Description                                                          |
|:---------------------------|:---------|:---------------------------------------------------------------------|
| `requirements-description` | Yes      | Feature description text. Feature name is extracted from description |

## Input Examples

```
/generate-spec User authentication feature.
Supports login and logout with email and password.
Provides password reset functionality, with session management via JWT tokens.
Provides an API to check login status and middleware to protect endpoints requiring authentication.
```

## Execution Mode

**This skill operates in non-interactive mode (equivalent to `--ci` flag)**:

- ✅ Skip Vibe Coding risk assessment → Make reasonable assumptions
- ✅ Skip user questions → Automatically proceed with best guess
- ✅ Auto-approve overwrites → No confirmation prompts
- ✅ Skip spec-reviewer/prd-reviewer → Only perform automated checks
- ✅ Always generate Design Doc → No skip confirmation

## Generation Rules

### 1. Input Content Analysis

**Non-Interactive Mode**: Make reasonable assumptions for vague or unclear requirements. Do not confirm with user.

Extract/infer the following from input:

**For Spec (Abstract Specification)**:

| Extraction Item             | Description                  | Required |
|:----------------------------|:-----------------------------|:---------|
| **Feature Name**            | Identifier used for filename | Yes      |
| **Background**              | Why this feature is needed   | Yes      |
| **Purpose**                 | What to achieve              | Yes      |
| **Functional Requirements** | List of required functions   | Yes      |
| **Public API**              | Interfaces users will use    |          |
| **Data Model**              | Major types/entities         |          |
| **Behavior**                | Major use cases/sequences    |          |

**For Design Doc (Technical Design Document)**:

| Extraction Item                 | Description                                   | Required |
|:--------------------------------|:----------------------------------------------|:---------|
| **Technology Stack**            | Technologies/libraries to use                 | Yes      |
| **Architecture Proposal**       | Module structure/layer design                 | Yes      |
| **Design Decisions**            | Reasons for technology selection/alternatives |          |
| **Non-Functional Requirements** | Performance/security requirements             |          |

### 2. Existing Document Check

Check the following before generation. Both flat and hierarchical structures are supported.

**For flat structure**:

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md exist? (PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md already exist?
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md already exist?
```

**For hierarchical structure** (when placing under parent feature):

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md exist? (parent feature PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md exist? (child feature PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md already exist? (parent feature spec)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md already exist? (child feature spec)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md already exist? (parent feature design)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md already exist? (child feature design)
```

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

**Hierarchical structure usage decision**:

- Use hierarchical structure when corresponding PRD exists in hierarchical structure
- Use hierarchical structure when parent feature (category) is specified in input
- Recommended to confirm with user whether to use hierarchical structure

**If PRD exists**:

- Pre-load PRD and understand requirement IDs (UR-xxx, FR-xxx, NFR-xxx) and functional requirements
- Ensure generated spec covers PRD requirements
- Reference PRD requirement IDs in spec's "Functional Requirements" section

**If spec/design exists**:

- **Non-Interactive Mode**: Overwrite without confirmation.

## Output Format

### Phase 1: Abstract Specification (Specify Phase)

#### Template Preparation

Follow these steps to prepare the template:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` exists
2. **If exists**: Use that template
3. **If not exists**: Read `templates/${SDD_LANG:-en}/spec_template.md` from this skill directory and use it as the base
   template to generate `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md`

#### Template Application Notes

- Replace template placeholders (`{Feature Name}`, etc.) based on input content
- Sections with `<MUST>` markers are required, `<RECOMMENDED>` are recommended, `<OPTIONAL>` are optional
- Reference PRD requirement IDs (UR-xxx, FR-xxx, NFR-xxx) in functional requirements

**Save Location**:

- Flat structure: `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`
- Hierarchical structure (parent feature):
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md`
- Hierarchical structure (child feature):
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md`

### Phase 2: Technical Design Document (Plan Phase)

After abstract specification generation is complete, generate the technical design document.

#### Template Preparation

Follow these steps to prepare the template:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md` exists
2. **If exists**: Use that template
3. **If not exists**: Read `templates/${SDD_LANG:-en}/design_template.md` from this skill directory and use it as the
   base template to generate `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`

#### Template Application Notes

- Set implementation status to "Not Implemented" initially
- Design Goals, Technology Stack, Architecture, and Design Decisions are required sections
- Ensure consistency with spec

**Save Location**:

- Flat structure: `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md`
- Hierarchical structure (parent feature):
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md`
- Hierarchical structure (child feature):
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md`

**Non-Interactive Mode**: Always generate Design Doc (do not skip).

## Front Matter Generation Rules

Generated specs and design docs must include YAML front matter at the top of the file.

See `references/front_matter_spec_design.md` for full schema definition, dependency direction rules, and validation
checklist.

### Spec-Specific Field Rules

| Field        | Rule                                                                        |
|:-------------|:----------------------------------------------------------------------------|
| `id`         | `"spec-{feature-name}"`. For hierarchical: `"spec-{parent}-{feature-name}"` |
| `status`     | `"draft"` for new specs                                                     |
| `depends-on` | PRD ID (e.g., `["prd-user-auth"]`)                                          |
| `priority`   | Inherit from PRD if exists, otherwise `"medium"`                            |
| `risk`       | Inherit from PRD if exists, otherwise `"medium"`                            |

### Design Doc-Specific Field Rules

| Field         | Rule                                                                            |
|:--------------|:--------------------------------------------------------------------------------|
| `id`          | `"design-{feature-name}"`. For hierarchical: `"design-{parent}-{feature-name}"` |
| `status`      | `"draft"` for new design docs                                                   |
| `impl-status` | `"not-implemented"` for new design docs                                         |
| `depends-on`  | Spec ID (e.g., `["spec-user-auth"]`)                                            |
| `tags`        | Inherit from spec                                                               |
| `category`    | Inherit from spec                                                               |
| `priority`    | Inherit from spec                                                               |
| `risk`        | Inherit from spec                                                               |

## Generation Flow (Non-Interactive Mode)

```
1. Analyze input content
   |
2. Load project principles (Required)
   |- If CONSTITUTION.md exists:
   |   |- Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md using Read tool
   |   |- Understand principle categories (B-xxx, A-xxx, D-xxx, T-xxx)
   |- If not exists: Skip (note this in output)
   |
3. Check existing documents
   |- If PRD exists: Pre-load and understand requirements
   |- If spec/design exists: Auto-approve overwrite
   |
4. Generate and save abstract specification (Specify)
   |
5. Perform structural verification (CLI not available)
   |- Duplicate ID check
   |- Unresolved dependency check
   |- YAML front matter validation
   |- Cross-reference validation
   |
6. Generate and save Design Doc (always generate in non-interactive mode)
   |
7. Perform structural verification for Design Doc
   |
8. Generate JSON output
```

## PRD Consistency Review

If PRD exists, perform the following consistency checks on generated spec and reflect results in spec:

### Check Items

| Check Item                                | Verification Content                                                         |
|:------------------------------------------|:-----------------------------------------------------------------------------|
| **Requirement Coverage**                  | Are all PRD functional requirements (FR-xxx) covered in spec?                |
| **Requirement ID References**             | Do spec functional requirements appropriately reference PRD requirement IDs? |
| **Non-Functional Requirement Reflection** | Are PRD non-functional requirements (NFR-xxx) reflected in spec?             |
| **Terminology Consistency**               | Is the same terminology used in PRD and spec?                                |

### Handling Inconsistencies

1. **Missing requirements**: Add corresponding functional requirements to spec
2. **Missing requirement ID references**: Add corresponding requirement IDs to functional requirements
3. **Terminology inconsistency**: Unify to PRD terminology

### Documenting Consistency Review Results

Add the following to spec's end (if PRD exists):

**Reference**: `examples/prd_reference_section.md`

For hierarchical structure, parent feature PRD is
`${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md`

## Final Step: Generate JSON Output

**MANDATORY**: After spec and design generation, output JSON to stdout using Bash tool.

**Format specification**: See `examples/cli_fallback_json_output.md` > "Spec/Design Generation Output"

**Important**: Include all issues found during Structural Verification (steps 5 and 7 in Generation Flow) in
`lint_results.issues`.

**Example output with structural validation results**:

```bash
cat << 'EOF'
{
  "search_results": {
    "results": [
      {
        "file_path": "/absolute/path/.sdd/specification/user-login_spec.md",
        "file_type": "spec",
        "title": "User Login Specification",
        "feature_id": "user-login",
        "id": "spec-user-login",
        "status": "draft",
        "tags": ["auth"],
        "category": "authentication"
      },
      {
        "file_path": "/absolute/path/.sdd/specification/user-login_design.md",
        "file_type": "design",
        "title": "User Login Design",
        "feature_id": "user-login",
        "id": "design-user-login",
        "status": "draft",
        "tags": ["auth"],
        "category": "authentication"
      }
    ]
  },
  "lint_results": {
    "issues": [
      {
        "severity": "error",
        "rule": "duplicate-id",
        "file_path": "/absolute/path/.sdd/specification/legacy/user_spec.md",
        "line": 5,
        "column": 0,
        "message": "Duplicate ID 'spec-user-auth' found",
        "details": {
          "field": "id",
          "duplicate_id": "spec-user-auth",
          "other_files": ["/absolute/path/.sdd/specification/auth/user_spec.md"]
        }
      }
    ]
  },
  "generated_files": [
    "/absolute/path/.sdd/specification/user-login_spec.md",
    "/absolute/path/.sdd/specification/user-login_design.md"
  ],
  "status": "success"
}
EOF
```

**Important**:

- Replace placeholders with actual values from generated spec and design
- Use absolute paths (e.g., `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/...`)
- Extract values from YAML front matter of generated files
- Include all issues from Structural Verification in `lint_results.issues`
- If no issues found, use empty array `"issues": []`

## Post-Generation Actions

1. **Save Files**:
    - Flat structure: `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`,
      `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md`
    - Hierarchical structure (parent feature):
      `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md`,
      `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md`
    - Hierarchical structure (child feature):
      `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md`,
      `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md`

2. **Consistency Check**:
    - If PRD exists: Verify and reflect PRD <-> spec consistency
    - Verify spec <-> design consistency

## Output

Use the `templates/${SDD_LANG:-en}/spec_output.md` template for output formatting.

## Post-Generation Verification

### Automatic Verification (Performed)

The following verifications are automatically performed during generation:

- [x] **Principle Compliance Check via spec-reviewer**: Verify compliance with CONSTITUTION.md
- [x] **PRD Consistency Check**: Confirm requirement ID references and functional requirement coverage
- [x] **Template Compliance Check**: Verify presence of required sections

### Structural Verification (CLI Not Available)

Since CLI lint is not available, **verify the following structural integrity**:

#### 1. Duplicate ID Check

Use Grep to search for all `id:` entries in YAML front matter and verify no duplicates exist:

```bash
# Extract all IDs from requirement, specification directories
grep -h "^id:" ${SDD_REQUIREMENT_PATH}/**/*.md ${SDD_SPECIFICATION_PATH}/**/*.md 2>/dev/null | sort | uniq -d
```

**Expected**: No output (no duplicates)

**If duplicates found**: Report to user with file paths and ask which ID to rename

#### 2. Unresolved Dependency Check

For each generated document, verify all `depends-on` references are valid:

1. **Extract depends-on entries**:
    - Read YAML front matter from generated spec and design files
    - Parse `depends-on:` array

2. **Validate each reference**:
    - For PRD references: Check `${SDD_REQUIREMENT_PATH}/{id}.md` exists
    - For spec references: Check `${SDD_SPECIFICATION_PATH}/{id}_spec.md` exists
    - For design references: Check `${SDD_SPECIFICATION_PATH}/{id}_design.md` exists

3. **Report broken dependencies**:
    - List any `depends-on` entries pointing to non-existent files
    - Suggest creating missing dependencies or removing invalid references

#### 3. YAML Front Matter Validation

Verify YAML front matter is well-formed:

```bash
# Check if YAML can be parsed (requires yq or similar)
for file in ${SDD_SPECIFICATION_PATH}/**/*.md; do
  if ! head -20 "$file" | grep -q "^---$"; then
    echo "WARNING: Missing front matter in $file"
  fi
done
```

**Verification checklist**:

- [ ] All spec/design files have YAML front matter (`---` delimiters)
- [ ] Required fields are present: `id`, `title`, `type`, `status`
- [ ] `type` field matches file suffix (`spec` for `*_spec.md`, `design` for `*_design.md`)
- [ ] No syntax errors in YAML (proper indentation, quoted strings)

#### 4. Cross-Reference Validation

After generation, perform a quick cross-reference check:

1. **Read generated spec file** and note all mentioned requirement IDs (e.g., `UR-001`, `FR-002`)
2. **Verify these IDs exist** in the corresponding PRD file
3. **Report any missing IDs** that are referenced but not defined

**Implementation**:

- Use Grep to find all `UR-\d+`, `FR-\d+`, `NFR-\d+` patterns in spec
- Cross-check with PRD content
- Warn user if spec references non-existent requirements

### Verification Commands

```bash
# Consistency check (design <-> implementation)
/check-spec {feature-name}

# Comprehensive review (cross-document consistency + quality)
/check-spec {feature-name} --full

# Specification clarity scan
/clarify {feature-name}
```

## Serena MCP Integration (Optional)

If Serena MCP is enabled, existing codebase semantic analysis can be leveraged to enhance specification generation.

### Usage Conditions

- `serena` is configured in `.mcp.json`
- Target language's Language Server is supported

### Additional Features When Serena is Enabled

#### Specification Extraction from Existing Code

| Feature                    | Usage                                                             |
|:---------------------------|:------------------------------------------------------------------|
| `find_symbol`              | Search existing function/class definitions for API spec reference |
| `find_referencing_symbols` | Infer behavior from existing code usage patterns                  |

#### Enhanced Generation Items

1. **Existing API Reference**: Reference similar existing implementations for consistent API design suggestions
2. **Type Definition Reference**: Search existing types in project and reflect in data model
3. **Naming Convention Unification**: Analyze existing code naming patterns for new feature naming
4. **Dependency Understanding**: Identify related modules for interface design

#### Integration into Generation Flow

```
1. Analyze input content
   |
2. [When Serena enabled] Analyze existing codebase
   |- Search for similar features
   |- Understand existing types/interfaces
   |- Extract naming conventions
   |
3. Vibe Coding risk assessment
   ...
```

### Behavior When Serena is Not Configured

Even without Serena, specifications are generated based on input content and PRD.
If existing code reference is needed, recommend manual verification to user.

## Loading CONSTITUTION.md (Required)

Before spec/design generation,
**you must read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` using the Read tool**.

```
Read: ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md
```

### Post-Load Verification

After loading CONSTITUTION.md, understand the following principles and ensure spec/design compliance:

**For Abstract Specification (*_spec.md)**:

| Principle Category              | Impact on Spec                                            |
|:--------------------------------|:----------------------------------------------------------|
| Architecture Principles (A-xxx) | Architecture patterns, layer separation, interface design |
| Development Principles (D-xxx)  | Testability, modularity, requirement traceability         |
| Business Principles (B-xxx)     | Business logic reflection, domain model                   |

**For Technical Design Document (*_design.md)**:

| Principle Category              | Impact on Design                                    |
|:--------------------------------|:----------------------------------------------------|
| Technical Constraints (T-xxx)   | Technology selection, version constraints, platform |
| Architecture Principles (A-xxx) | Architecture implementation, design patterns        |
| Development Principles (D-xxx)  | Test strategy, CI/CD considerations                 |

### If CONSTITUTION.md Does Not Exist

1. **Skip principle compliance check**
2. **Note in output**: "Principle compliance check was skipped as CONSTITUTION.md does not exist"
3. **Recommend to user**: "Run `/sdd-init` or `/constitution init` to create project principles"
4. **Continue with spec/design generation** (other quality checks will still be performed)

## Principle Compliance Check

**Non-Interactive Mode**: Skip spec-reviewer and front-matter-reviewer agent calls.

**Alternative**: Perform structural verification as documented
in the "Structural Verification (CLI Not Available)" section.
