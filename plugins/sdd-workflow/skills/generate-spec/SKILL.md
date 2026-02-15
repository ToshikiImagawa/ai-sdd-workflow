---
name: generate-spec
description: "Generate Abstract Specification and Technical Design Document from input content"
argument-hint: "<requirements-description>"
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
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

### Template Preparation Flow (Optimized)

**Phase 1: Shell Script** - Execute `prepare-spec.sh` to pre-load templates and references:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/generate-spec/scripts/prepare-spec.sh"
```

This script:
1. Checks `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` and `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md` (project templates) first
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

| Argument                   | Required | Description                                                                                                                  |
|:---------------------------|:---------|:-----------------------------------------------------------------------------------------------------------------------------|
| `requirements-description` | Yes      | Feature description text. Feature name is extracted from description                                                         |
| `--ci`                     | -        | CI/non-interactive mode. Skips Vibe Coding check, auto-approves overwrites, skips spec-reviewer, always generates Design Doc |

## Input Examples

```
/generate-spec User authentication feature.
Supports login and logout with email and password.
Provides password reset functionality, with session management via JWT tokens.
Provides an API to check login status and middleware to protect endpoints requiring authentication.
```

## Generation Rules

### 1. Vibe Coding Risk Assessment (Perform First)

> **CI Mode**: If `--ci` flag is specified, skip this section entirely and proceed to step 4.

Analyze input content and assess risk based on the following criteria:

| Risk   | Condition                     | Response                                                |
|:-------|:------------------------------|:--------------------------------------------------------|
| High   | No specs + vague instructions | Confirm missing information with user before generating |
| Medium | Some requirements unclear     | Clarify ambiguous points before generating              |
| Low    | Requirements clear            | Can generate as-is                                      |

**Examples of Vague Input**:

- "Make it nice," "somehow" -> Confirm specific requirements
- "Improve performance" -> Confirm target and goal values
- "Same as before" -> Confirm reference

### 2. Input Content Analysis

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

### 3. Missing Information Confirmation

If important items cannot be determined from input, **confirm with user before generation**:

- Feature name unclear
- Required extraction items cannot be inferred from input
- No technology stack specified (confirm whether to follow existing patterns)
- Ambiguous business rules or edge cases

### 4. Existing Document Check

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

- **CI Mode (`--ci`)**: Overwrite without confirmation.
- **Interactive**: Confirm with user whether to overwrite.

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
- Hierarchical structure (parent feature): `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md`
- Hierarchical structure (child feature): `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md`

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
- Hierarchical structure (parent feature): `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md`
- Hierarchical structure (child feature): `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md`

### Skip Design Doc Generation

> **CI Mode**: If `--ci` flag is specified, always generate Design Doc (do not skip).

Skip Design Doc generation and confirm with user in the following cases:

- No technical information in input at all
- Unclear whether to follow existing design patterns
- Technology selection requires investigation/consideration

## Generation Flow

```
1. Analyze input content
   |
2. Load project principles (Required)
   |- If CONSTITUTION.md exists:
   |   |- Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md using Read tool
   |   |- Understand principle categories (B-xxx, A-xxx, D-xxx, T-xxx)
   |- If not exists: Skip (note this in output)
   |
3. Vibe Coding risk assessment (skip if --ci)
   |- High: Confirm missing info with user -> Resume after response
   |- Medium: Confirm ambiguous points -> Resume after response
   |- Low: Proceed to next step
   |
4. Check existing documents
   |- If PRD exists: Pre-load and understand requirements
   |- If spec/design exists: Confirm overwrite (auto-approve if --ci)
   |
5. Generate and save abstract specification (Specify)
   |
6. Spec principle compliance check with spec-reviewer (skip if --ci)
   |- Call spec-reviewer agent (--summary option)
   |- **Target**: {feature-name}_spec.md only (Design Doc not yet generated)
   |- Check CONSTITUTION.md compliance (Architecture/Development principles focus)
   |- On violation detection: Review fix proposals and apply approved fixes (main agent)
   |- After fix, re-check
   |
7. Confirm Design Doc generation (always generate if --ci)
   |- Technical info present: Generate and save (Plan)
   |- No technical info: Confirm whether to skip
   |
8. Design Doc principle compliance check with spec-reviewer (skip if --ci)
   |- Call spec-reviewer agent (--summary option)
   |- **Target**: {feature-name}_design.md only (Spec already checked in step 6)
   |- Check CONSTITUTION.md compliance (Technical constraints/Architecture focus)
   |- On violation detection: Review fix proposals and apply approved fixes (main agent)
   |- After fix, re-check
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

For hierarchical structure, parent feature PRD is `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md`

## Post-Generation Actions

1. **Save Files**:
    - Flat structure: `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`, `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md`
    - Hierarchical structure (parent feature): `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md`,
      `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md`
    - Hierarchical structure (child feature): `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md`,
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

Before spec/design generation, **you must read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` using the Read tool**.

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

## Principle Compliance Check with spec-reviewer (Required)

> **CI Mode**: If `--ci` flag is specified, skip principle compliance check.

After spec and design generation, **you must call the `spec-reviewer` agent to check principle compliance**.

### Check Flow

```
1. Call spec-reviewer agent
   |
2. Execute CONSTITUTION.md compliance check
   |
3. If violations detected:
   |- Review fix proposals from spec-reviewer
   |- Apply approved fixes using Edit tool (main agent)
   |- Report non-applicable fixes to user
   |
4. After fix, re-check to verify
   |
5. Include check results in output
```

### Abstract Specification Check Result Output

Include the following after spec generation:

**Reference**: `examples/compliance_check_spec.md`

### Technical Design Document Check Result Output

Include the following after design doc generation:

**Reference**: `examples/compliance_check_design.md`
