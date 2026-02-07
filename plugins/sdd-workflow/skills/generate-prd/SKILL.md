---
name: generate-prd
description: "Generate PRD (Requirements Specification) in SysML requirements diagram format from business requirements"
version: 3.0.1
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash, Skill
---

# Generate PRD - Requirements Specification Generation

Generates PRD (Requirements Specification) from input business requirements according to the AI-SDD workflow.

## Hybrid Approach

This skill operates in two modes:

| Mode                      | Behavior | Description                                                                              |
|:--------------------------|:---------|:-----------------------------------------------------------------------------------------|
| **Interactive** (default) | Guide    | Each sub-skill is independent, user invokes sequentially. This skill proposes next steps |
| **CI (`--ci`)**           | Wrapper  | This skill automatically executes sub-skills via Skill tool                              |

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Template Preparation Flow (Optimized)

**Phase 1: Shell Script** - Execute `prepare-prd.sh` to pre-load templates and references:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/generate-prd/scripts/prepare-prd.sh"
```

This script:

1. Checks `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` (project template) first
2. If not found, copies `templates/${SDD_LANG}/prd_template.md` to cache
3. Copies all reference files to cache
4. Exports environment variables to `$CLAUDE_ENV_FILE`:
    - `GENERATE_PRD_TEMPLATE` - Path to cached template
    - `GENERATE_PRD_REFERENCES` - Path to cached references

**Phase 2: Claude** - **MUST read template from cache before generation**

**CRITICAL**: You must explicitly read the template using Read tool. The `prepare-prd.sh` script only prepares the
cache - it does NOT automatically inject the template content. Follow the "Template Loading (Required)" section in this
document.

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

### PRD / Requirements Diagram Positioning (Reference)

**Abstraction Level: Highest** | **Focus: What to build, why to build it**

| Item                  | Details                                                                                                      |
|:----------------------|:-------------------------------------------------------------------------------------------------------------|
| **Purpose**           | Define high-level product requirements (business value)                                                      |
| **Content**           | User requirements, functional requirements, non-functional requirements in SysML requirements diagram format |
| **Technical Details** | **Not included**                                                                                             |
| **SysML Elements**    | Requirements Diagram (req)                                                                                   |

### Document Dependencies

See `references/document_dependencies.md` for the document dependency chain and direction meaning.

PRD is created following `CONSTITUTION.md` principles and serves as the foundation for subsequent specifications and
design documents.

## Input

$ARGUMENTS

| Argument                   | Required | Description                                                                        |
|:---------------------------|:---------|:-----------------------------------------------------------------------------------|
| `requirements-description` | Yes      | Business requirements description text. Feature name is extracted from description |
| `--ci`                     | -        | CI/non-interactive mode. Executes all sub-skills automatically, skips prd-reviewer |

### Input Examples

```
/generate-prd A feature for users to manage tasks.
Available only to logged-in users.
Supports task creation, editing, deletion, and completion, with due date and priority settings.
Sends email notifications for tasks nearing their due date.
```

## Generation Rules

### 1. Vibe Coding Risk Assessment (Perform First)

> **CI Mode**: If `--ci` flag is specified, skip this section entirely and proceed to step 4.

Analyze input content and assess risk based on the following criteria:

| Risk   | Condition                   | Response                                         |
|:-------|:----------------------------|:-------------------------------------------------|
| High   | Business requirements vague | Confirm missing info with user before generating |
| Medium | Some requirements unclear   | Clarify ambiguous points before generating       |
| Low    | Requirements clear          | Can generate as-is                               |

**Examples of Vague Input**:

- "Add a useful feature" -> Confirm specific functionality
- "Improve user experience" -> Confirm improvement target and goals
- "Same feature as competitors" -> Confirm specific feature specifications

### 2. Input Content Analysis

Extract/infer the following from input:

| Extraction Item                 | Description                                | Required |
|:--------------------------------|:-------------------------------------------|:---------|
| **Feature Name**                | Identifier used for filename               | Yes      |
| **Background/Purpose**          | Why this feature is needed, business value | Yes      |
| **User Requirements**           | What end users want                        | Yes      |
| **Functional Requirements**     | Functions the system should provide        | Yes      |
| **Non-Functional Requirements** | Performance, security, availability, etc.  |          |
| **Constraints**                 | Technical/business constraints             |          |
| **Preconditions**               | Assumptions for feature operation          |          |

### 3. Missing Information Confirmation

If important items cannot be determined from input, **confirm with user before generation**:

- Feature name unclear
- Business value/purpose unclear
- User requirements subject (who will use it) unclear
- Success criteria/goals unclear

### 4. Existing Document Check

Check the following before generation. Both flat and hierarchical structures are supported.

**For flat structure**:

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md already exist? (PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md already exist? (spec)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md already exist? (design)
```

**For hierarchical structure** (when placing under parent feature):

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md already exist? (parent feature PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md already exist? (child feature PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md already exist? (parent feature spec)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md already exist? (child feature spec)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md already exist? (parent feature design)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md already exist? (child feature design)
```

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

**Hierarchical structure usage decision**:

- Use hierarchical structure when parent feature (category) is specified in input, or when existing hierarchical
  structure exists
- Recommended to confirm with user whether to use hierarchical structure

**If PRD exists**:

- **CI Mode (`--ci`)**: Overwrite without confirmation.
- **Interactive**: Confirm with user whether to overwrite.

**If spec/design exists**:

- After PRD generation, verify no impact on consistency with existing spec/design
- If requirement IDs are added/changed, notify that spec/design may need updates

## Generation Flow

### Interactive Mode (Default)

```
1. Analyze input content
   |
2. Load PRD template (Required)
   |- Read template using cached or manual method
   |- Verify template language matches SDD_LANG
   |
3. Load project principles (Required)
   |- If CONSTITUTION.md exists: Read and understand principles
   |- If not exists: Skip (note in output)
   |
4. Vibe Coding risk assessment
   |- High/Medium: Confirm with user
   |- Low: Proceed
   |
5. Check existing documents
   |- If PRD exists: Confirm overwrite
   |- If spec/design exists: Understand impact scope
   |
6. Generate PRD text content (without full diagrams)
   |- Generate basic structure following template
   |- Include placeholder sections for diagrams
   |
7. Save PRD to ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md
   |
8. Principle compliance check with prd-reviewer
   |- Call prd-reviewer agent
   |- Apply approved fixes
   |
9. **Propose next steps to user**:
   |- "To add use case diagram: `/generate-usecase-diagram {feature-name}`"
   |- "To analyze requirements: `/analyze-requirements {feature-name}`"
   |- "To add requirements diagram: `/generate-requirements-diagram {feature-name}`"
   |- "To create complete PRD: `/generate-prd {requirements} --ci`"
```

### CI Mode (`--ci`)

```
1. Analyze input content
   |
2. Load PRD template (Required)
   |
3. Load project principles (if exists)
   |
4. Check existing documents (auto-approve overwrite)
   |
5. Execute sub-skills via Skill tool:
   |
   ├── Skill: /generate-usecase-diagram {requirements}
   │   → Returns: Use case diagram Mermaid text
   │
   ├── Skill: /analyze-requirements {usecase-text}
   │   → Returns: Requirements analysis (UR/FR/NFR tables)
   │
   ├── Skill: /generate-requirements-diagram {analysis-text}
   │   → Returns: SysML requirements diagram Mermaid text
   │
   └── Skill: /finalize-prd {feature-name} {all-texts}
       → Returns: Complete integrated PRD text
   |
6. Save complete PRD to ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md
   |
7. Skip prd-reviewer (CI mode)
   |
8. Output completion summary
```

## Output Format

### Template Loading (Required)

**Before PRD generation, you MUST load the template** using one of the following methods:

**Method 1: Use cached template (Recommended - if prepare-prd.sh was executed)**:

```
Read: ${GENERATE_PRD_TEMPLATE}
```

**Method 2: Manual template selection (if cache not available)**:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` exists
2. **If exists**: Read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` using Read tool
3. **If not exists**: Read `templates/${SDD_LANG:-en}/prd_template.md` from this skill directory using Read tool

**Verification after loading**:

- Confirm template language matches `SDD_LANG` environment variable
- If mismatch detected, reload correct template

### Template Application Notes

**IMPORTANT: You must strictly follow the loaded template structure and language**

1. **Structure Compliance**:
    - Preserve all `<MUST>` sections from template
    - Include `<RECOMMENDED>` sections whenever possible
    - Add `<OPTIONAL>` sections as needed
    - Maintain template's section order and hierarchy

2. **Placeholder Replacement**:
    - Replace `{Feature Name}`, `{Requirement Name}`, etc. with actual content from input
    - Preserve template formatting (headers, tables, code blocks)

3. **Language Consistency**:
    - **CRITICAL**: Generate PRD in the same language as the loaded template
    - Do not mix languages - if template is in English, entire PRD must be in English
    - If template is in Japanese, entire PRD must be in Japanese

4. **Diagram Compliance**:
    - Use SysML requirementDiagram syntax as shown in template
    - Follow template's diagram structure examples

5. **Requirement ID Management**:
    - Manage requirement IDs (UR-xxx, FR-xxx, NFR-xxx, etc.) uniquely
    - Follow template's ID naming conventions

**Save Location**:

- Flat structure: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- Hierarchical structure (parent feature): `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md`
- Hierarchical structure (child feature):
  `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md`

## Consistency Check with Existing spec/design

If existing spec/design exists, verify the following after PRD generation:

### Check Items

| Check Item                     | Verification Content                                        |
|:-------------------------------|:------------------------------------------------------------|
| **New Requirement Addition**   | Are requirements added in PRD reflected in spec?            |
| **Requirement Changes**        | Are requirements changed in PRD reflected in spec/design?   |
| **Requirement Deletion**       | Are requirements deleted from PRD removed from spec/design? |
| **Requirement ID Consistency** | Do requirement ID references in spec match PRD?             |

### Handling When Updates Needed

1. **Spec needs update**: Regenerate with `/generate-spec` or recommend manual update to user
2. **Design needs update**: Check if spec changes require design decision revision
3. **Impact Scope Notification**: Clearly indicate to user which documents need updates

## Post-Generation Actions

1. **Save File**:
    - Flat structure: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
    - Hierarchical structure: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md` or
      `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md`

2. **Consistency Check**:
    - If existing spec/design exists: Verify impact and notify if updates needed

## Output

Use the `templates/${SDD_LANG:-en}/prd_output.md` template for output formatting.

## Loading CONSTITUTION.md (Required)

Before PRD generation, **you must read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` using the Read tool**.

```
Read: ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md
```

### Post-Load Verification

After loading CONSTITUTION.md, understand the following principles and ensure PRD compliance:

| Principle Category              | Impact on PRD                                               |
|:--------------------------------|:------------------------------------------------------------|
| Business Principles (B-xxx)     | Directly reflected in background/purpose, user requirements |
| Architecture Principles (A-xxx) | Documented as constraints (no technical details)            |
| Development Principles (D-xxx)  | Affects verifymethod selection                              |
| Technical Constraints (T-xxx)   | Documented as constraints (from feasibility perspective)    |

### If CONSTITUTION.md Does Not Exist

1. **Skip principle compliance check**
2. **Note in output**: "Principle compliance check was skipped as CONSTITUTION.md does not exist"
3. **Recommend to user**: "Run `/sdd-init` or `/constitution init` to create project principles"
4. **Continue with PRD generation** (other quality checks will still be performed)

## Principle Compliance Check with prd-reviewer (Interactive Mode Only)

> **CI Mode**: If `--ci` flag is specified, skip principle compliance check.

After PRD generation, **you must call the `prd-reviewer` agent to check principle compliance**.

### Check Flow

```
1. Call prd-reviewer agent
   |
2. Execute CONSTITUTION.md compliance check
   |
3. If violations detected:
   |- Review fix proposals from prd-reviewer
   |- Apply approved fixes using Edit tool (main agent)
   |- Report non-applicable fixes to user
   |
4. After fix, re-check to verify
   |
5. Include check results in output
```

### Check Result Output

Include the following in output upon generation completion:

```markdown
### CONSTITUTION.md Compliance Check Results

| Principle Category      | Compliance Status                         |
|:------------------------|:------------------------------------------|
| Business Principles     | Compliant / Violation                     |
| Architecture Principles | Compliant / Violation                     |
| Development Principles  | Compliant / Violation                     |
| Technical Constraints   | Compliant / Violation                     |

**Fix proposals applied**: {count} items
**Fixes requiring discussion**: {count} items (see details above)
```

## Post-Generation Verification

### Automatic Verification (Performed)

The following verifications are automatically performed during generation:

- [x] **Principle Compliance Check via prd-reviewer**: Verify compliance with CONSTITUTION.md (Interactive mode)
- [x] **Existing spec/design Consistency Check**: Understand impact scope

### Verification Commands

```bash
# PRD quality check (CONSTITUTION.md compliance, completeness, clarity)
/check-spec {feature-name} --full

# Specification clarity scan
/clarify {feature-name}
```

## Sub-Skills Reference

This skill can delegate to the following sub-skills:

| Skill                            | Purpose                   | Context | Output              |
|:---------------------------------|:--------------------------|:--------|:--------------------|
| `/generate-usecase-diagram`      | Generate use case diagram | fork    | Mermaid text        |
| `/analyze-requirements`          | Extract UR/FR/NFR         | fork    | Requirements tables |
| `/generate-requirements-diagram` | Generate SysML diagram    | fork    | Mermaid text        |
| `/finalize-prd`                  | Integrate all artifacts   | fork    | Complete PRD text   |

## Notes

- PRD should **NOT include technical details** (that is the role of `*_spec.md` and `*_design.md`)
- Manage requirement IDs uniquely so they can be referenced in subsequent documents
- Classify priorities using MoSCoW method (Must/Should/Could/Won't)
- Maintain high abstraction level and focus on "what" and "why"
- In Interactive mode, user can selectively run sub-skills for incremental updates
- In CI mode, all sub-skills are executed automatically for complete PRD generation
