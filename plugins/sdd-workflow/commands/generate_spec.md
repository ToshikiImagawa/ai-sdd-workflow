---
description: "Generate Abstract Specification and Technical Design Document from input content"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Specification & Design Doc Generator

Generates the following documents from input content according to the AI-SDD workflow:

1. `.sdd/specification/{feature-name}_spec.md` - Abstract Specification (Specify Phase)
2. `.sdd/specification/{feature-name}_design.md` - Technical Design Document (Plan Phase)

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for specification and design document generation.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value         | Description                  |
|:-------------------------|:----------------------|:-----------------------------|
| `SDD_ROOT`          | `.sdd`                | Root directory               |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`    | PRD/Requirements directory   |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification`  | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`           | Task log directory           |

**Path Resolution Priority:**
1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or configuration file exists.

### Skills Used

This command uses the following skills:

| Skill                        | Purpose                                                                                                      |
|:-----------------------------|:-------------------------------------------------------------------------------------------------------------|
| `sdd-workflow:sdd-templates` | Generate `.sdd/SPECIFICATION_TEMPLATE.md`, `.sdd/DESIGN_DOC_TEMPLATE.md` when project templates do not exist |

**Template Preparation Flow**:

1. Use `.sdd/SPECIFICATION_TEMPLATE.md`, `.sdd/DESIGN_DOC_TEMPLATE.md` (project templates) if they exist
2. If not, use `sdd-templates` skill to generate the templates

### Pre-Generation Verification

Before generation, verify the following:

1. Does the `.sdd/` directory exist in the project?
2. If template files exist, use them

## Input

$ARGUMENTS

## Input Examples

```
/generate_spec User authentication feature.
Supports login and logout with email and password.
Provides password reset functionality, with session management via JWT tokens.
Provides an API to check login status and middleware to protect endpoints requiring authentication.
```

## Generation Rules

### 1. Vibe Coding Risk Assessment (Perform First)

Analyze input content and assess risk based on the following criteria:

| Risk   | Condition                     | Response                                                |
|:-------|:------------------------------|:--------------------------------------------------------|
| High   | No specs + vague instructions | Confirm missing information with user before generating |
| Medium | Some requirements unclear     | Clarify ambiguous points before generating              |
| Low    | Requirements clear            | Can generate as-is                                      |

**Examples of Vague Input**:

- "Make it nice," "somehow" → Confirm specific requirements
- "Improve performance" → Confirm target and goal values
- "Same as before" → Confirm reference

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
Does .sdd/requirement/{feature-name}.md exist? (PRD)
Does .sdd/specification/{feature-name}_spec.md already exist?
Does .sdd/specification/{feature-name}_design.md already exist?
```

**For hierarchical structure** (when placing under parent feature):

```
Does .sdd/requirement/{parent-feature}/index.md exist? (parent feature PRD)
Does .sdd/requirement/{parent-feature}/{feature-name}.md exist? (child feature PRD)
Does .sdd/specification/{parent-feature}/index_spec.md already exist? (parent feature spec)
Does .sdd/specification/{parent-feature}/{feature-name}_spec.md already exist? (child feature spec)
Does .sdd/specification/{parent-feature}/index_design.md already exist? (parent feature design)
Does .sdd/specification/{parent-feature}/{feature-name}_design.md already exist? (child feature design)
```

**⚠️ Note the difference in naming conventions**:

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

**If spec/design exists**: Confirm with user whether to overwrite.

## Output Format

### Phase 1: Abstract Specification (Specify Phase)

#### Template Preparation

Follow these steps to prepare the template:

1. Check if `.sdd/SPECIFICATION_TEMPLATE.md` exists
2. **If exists**: Use that template
3. **If not exists**: Use `sdd-workflow:sdd-templates` skill to generate `.sdd/SPECIFICATION_TEMPLATE.md`, then use the
   generated template

#### Template Application Notes

- Replace template placeholders (`{Feature Name}`, etc.) based on input content
- Sections with `<MUST>` markers are required, `<RECOMMENDED>` are recommended, `<OPTIONAL>` are optional
- Reference PRD requirement IDs (UR-xxx, FR-xxx, NFR-xxx) in functional requirements

**Save Location**:

- Flat structure: `.sdd/specification/{feature-name}_spec.md`
- Hierarchical structure (parent feature): `.sdd/specification/{parent-feature}/index_spec.md`
- Hierarchical structure (child feature): `.sdd/specification/{parent-feature}/{feature-name}_spec.md`

### Phase 2: Technical Design Document (Plan Phase)

After abstract specification generation is complete, generate the technical design document.

#### Template Preparation

Follow these steps to prepare the template:

1. Check if `.sdd/DESIGN_DOC_TEMPLATE.md` exists
2. **If exists**: Use that template
3. **If not exists**: Use `sdd-workflow:sdd-templates` skill to generate `.sdd/DESIGN_DOC_TEMPLATE.md`, then use the
   generated template

#### Template Application Notes

- Set implementation status to "🔴 Not Implemented" initially
- Design Goals, Technology Stack, Architecture, and Design Decisions are required sections
- Ensure consistency with spec

**Save Location**:

- Flat structure: `.sdd/specification/{feature-name}_design.md`
- Hierarchical structure (parent feature): `.sdd/specification/{parent-feature}/index_design.md`
- Hierarchical structure (child feature): `.sdd/specification/{parent-feature}/{feature-name}_design.md`

### Skip Design Doc Generation

Skip Design Doc generation and confirm with user in the following cases:

- No technical information in input at all
- Unclear whether to follow existing design patterns
- Technology selection requires investigation/consideration

## Generation Flow

```
1. Analyze input content
   ↓
2. Vibe Coding risk assessment
   ├─ High: Confirm missing info with user → Resume after response
   ├─ Medium: Confirm ambiguous points → Resume after response
   └─ Low: Proceed to next step
   ↓
3. Check existing documents
   ├─ If PRD exists: Pre-load and understand requirements
   └─ If spec/design exists: Confirm overwrite
   ↓
4. Generate and save abstract specification (Specify)
   ↓
5. PRD consistency review (if PRD exists)
   ├─ Consistent: Proceed to next step
   └─ Inconsistent: Modify spec and re-save
   ↓
6. Confirm Design Doc generation
   ├─ Technical info present: Generate and save (Plan)
   └─ No technical info: Confirm whether to skip
   ↓
7. Commit
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

```markdown
## PRD Reference

- Corresponding PRD: `.sdd/requirement/[{parent-feature}/]{feature-name}.md`
- Covered Requirements: UR-001, FR-001, FR-002, NFR-001, ...
```

※ For hierarchical structure, parent feature PRD is `.sdd/requirement/{parent-feature}/index.md`

## Post-Generation Actions

1. **Save Files**:
    - Flat structure: `.sdd/specification/{feature-name}_spec.md`, `.sdd/specification/{feature-name}_design.md`
    - Hierarchical structure (parent feature): `.sdd/specification/{parent-feature}/index_spec.md`, `.sdd/specification/{parent-feature}/index_design.md`
    - Hierarchical structure (child feature): `.sdd/specification/{parent-feature}/{feature-name}_spec.md`, `.sdd/specification/{parent-feature}/{feature-name}_design.md`

2. **Consistency Check**:
    - If PRD exists: Verify and reflect PRD ↔ spec consistency
    - Verify spec ↔ design consistency

3. **Commit**:
    - Spec only: `[spec] Add {feature-name} abstract specification`
    - Both: `[docs] Add {feature-name} abstract specification and technical design document`

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
   ↓
2. [When Serena enabled] Analyze existing codebase
   ├─ Search for similar features
   ├─ Understand existing types/interfaces
   └─ Extract naming conventions
   ↓
3. Vibe Coding risk assessment
   ...
```

### Behavior When Serena is Not Configured

Even without Serena, specifications are generated based on input content and PRD.
Existing code reference must be done manually.
