---
name: generate-prd
description: "Generate PRD (Requirements Specification) in SysML requirements diagram format from business requirements"
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
---

# Generate PRD - Requirements Specification Generation

Generates PRD (Requirements Specification) from input business requirements according to the AI-SDD workflow.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

**Read the following diagram reference guides:**

- `references/usecase_diagram_guide.md` - Use case diagram notation guide for mermaid (flowchart-based)
- `references/mermaid_notation_rules.md` - Requirements diagram notation rules for mermaid
- `references/requirements_diagram_components.md` - Requirements diagram component definitions

### Template Preparation Flow (Optimized)

**Phase 1: Shell Script** - Execute `prepare-prd.sh` to pre-load templates and references:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/generate-prd/scripts/prepare-prd.sh"
```

This script:
1. Checks `.sdd/PRD_TEMPLATE.md` (project template) first
2. If not found, copies `templates/${SDD_LANG}/prd_template.md` to cache
3. Copies all reference files to cache
4. Exports environment variables to `$CLAUDE_ENV_FILE`:
   - `GENERATE_PRD_TEMPLATE` - Path to cached template
   - `GENERATE_PRD_REFERENCES` - Path to cached references

**Phase 2: Claude** - **MUST read template from cache before generation**

**CRITICAL**: You must explicitly read the template using Read tool. The `prepare-prd.sh` script only prepares the cache - it does NOT automatically inject the template content. Follow the "Template Loading (Required)" section in this document.

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

| Argument                   | Required | Description                                                                                    |
|:---------------------------|:---------|:-----------------------------------------------------------------------------------------------|
| `requirements-description` | Yes      | Business requirements description text. Feature name is extracted from description             |
| `--ci`                     | -        | CI/non-interactive mode. Skips Vibe Coding check, auto-approves overwrites, skips prd-reviewer |

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
Does .sdd/requirement/{feature-name}.md already exist? (PRD)
Does .sdd/specification/{feature-name}_spec.md already exist? (spec)
Does .sdd/specification/{feature-name}_design.md already exist? (design)
```

**For hierarchical structure** (when placing under parent feature):

```
Does .sdd/requirement/{parent-feature}/index.md already exist? (parent feature PRD)
Does .sdd/requirement/{parent-feature}/{feature-name}.md already exist? (child feature PRD)
Does .sdd/specification/{parent-feature}/index_spec.md already exist? (parent feature spec)
Does .sdd/specification/{parent-feature}/{feature-name}_spec.md already exist? (child feature spec)
Does .sdd/specification/{parent-feature}/index_design.md already exist? (parent feature design)
Does .sdd/specification/{parent-feature}/{feature-name}_design.md already exist? (child feature design)
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

## Output Format

### Template Loading (Required)

**Before PRD generation, you MUST load the template** using one of the following methods:

**Method 1: Use cached template (Recommended - if prepare-prd.sh was executed)**:
```
Read: ${GENERATE_PRD_TEMPLATE}
```

**Method 2: Manual template selection (if cache not available)**:
1. Check if `.sdd/PRD_TEMPLATE.md` exists
2. **If exists**: Read `.sdd/PRD_TEMPLATE.md` using Read tool
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

- Flat structure: `.sdd/requirement/{feature-name}.md`
- Hierarchical structure (parent feature): `.sdd/requirement/{parent-feature}/index.md`
- Hierarchical structure (child feature): `.sdd/requirement/{parent-feature}/{feature-name}.md`

## Generation Flow

```
1. Analyze input content
   |
2. Load PRD template (Required)
   |- Read template using Method 1 or Method 2 (see "Template Loading" section)
   |- Verify template language matches SDD_LANG
   |- Understand template structure (<MUST>, <RECOMMENDED>, <OPTIONAL> sections)
   |
3. Load project principles (Required)
   |- If CONSTITUTION.md exists:
   |   |- Read .sdd/CONSTITUTION.md using Read tool
   |   |- Understand principle categories (B-xxx, A-xxx, D-xxx, T-xxx)
   |- If not exists: Skip (note this in output)
   |
4. Vibe Coding risk assessment (skip if --ci)
   |- High: Confirm missing info with user -> Resume after response
   |- Medium: Confirm ambiguous points -> Resume after response
   |- Low: Proceed to next step
   |
5. Check existing documents
   |- If PRD exists: Confirm overwrite (auto-approve if --ci)
   |- If spec/design exists: Understand impact scope
   |
6. Generate PRD following loaded template
   |- Replace placeholders with analyzed content
   |- Maintain template structure and formatting
   |- Ensure language consistency with template
   |
7. Save PRD to appropriate location
   |
8. Principle compliance check with prd-reviewer (skip if --ci)
   |- Call prd-reviewer agent
   |- Check CONSTITUTION.md compliance
   |- On violation detection: Review fix proposals and apply approved fixes (main agent)
   |- After fix, re-check
   |
7. Check consistency with existing spec/design
   |- If spec/design exists: Verify consistency
   |- Updates needed: Notify recommendation to update spec/design
   |
8. Propose next steps
   - Create abstract specification with /generate-spec
   - If existing spec exists, recommend update
```

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
    - Flat structure: `.sdd/requirement/{feature-name}.md`
    - Hierarchical structure: `.sdd/requirement/{parent-feature}/index.md` or
      `.sdd/requirement/{parent-feature}/{feature-name}.md`

2. **Consistency Check**:
    - If existing spec/design exists: Verify impact and notify if updates needed

## Output

Use the `templates/${SDD_LANG:-en}/prd_output.md` template for output formatting.

## Loading CONSTITUTION.md (Required)

Before PRD generation, **you must read `.sdd/CONSTITUTION.md` using the Read tool**.

```
Read: .sdd/CONSTITUTION.md
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

## Principle Compliance Check with prd-reviewer (Required)

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

- [x] **Principle Compliance Check via prd-reviewer**: Verify compliance with CONSTITUTION.md
- [x] **Existing spec/design Consistency Check**: Understand impact scope

### Verification Commands

```bash
# PRD quality check (CONSTITUTION.md compliance, completeness, clarity)
/check-spec {feature-name} --full

# Specification clarity scan
/clarify {feature-name}
```

## Notes

- PRD should **NOT include technical details** (that is the role of `*_spec.md` and `*_design.md`)
- Manage requirement IDs uniquely so they can be referenced in subsequent documents
- Classify priorities using MoSCoW method (Must/Should/Could/Won't)
- Maintain high abstraction level and focus on "what" and "why"
