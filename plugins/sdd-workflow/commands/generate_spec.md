---
name: generate_spec
description: "Generate Abstract Specification and Technical Design Document from input content"
---

# Specification & Design Doc Generator

Generates the following documents from input content according to the AI-SDD workflow:

1. `.docs/specification/{feature-name}_spec.md` - Abstract Specification (Specify Phase)
2. `.docs/specification/{feature-name}_design.md` - Technical Design Document (Plan Phase)

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for specification and design document generation.

### Skills Used

This command uses the following skills:

| Skill | Purpose |
|:---|:---|
| `sdd-workflow:sdd-templates` | Specification and design document template reference (fallback when project templates do not exist) |

**Template Priority**:
1. Use `.docs/SPECIFICATION_TEMPLATE.md`, `.docs/DESIGN_DOC_TEMPLATE.md` (project templates) if they exist
2. If not, reference `sdd-templates` skill templates

### Pre-Generation Verification

Before generation, verify the following:

1. Does the `.docs/` directory exist in the project?
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

| Risk | Condition | Response |
|:---|:---|:---|
| High | No specs + vague instructions | Confirm missing information with user before generating |
| Medium | Some requirements unclear | Clarify ambiguous points before generating |
| Low | Requirements clear | Can generate as-is |

**Examples of Vague Input**:

- "Make it nice," "somehow" → Confirm specific requirements
- "Improve performance" → Confirm target and goal values
- "Same as before" → Confirm reference

### 2. Input Content Analysis

Extract/infer the following from input:

**For Spec (Abstract Specification)**:

| Extraction Item | Description | Required |
|:---|:---|:---|
| **Feature Name** | Identifier used for filename | Yes |
| **Background** | Why this feature is needed | Yes |
| **Purpose** | What to achieve | Yes |
| **Functional Requirements** | List of required functions | Yes |
| **Public API** | Interfaces users will use | |
| **Data Model** | Major types/entities | |
| **Behavior** | Major use cases/sequences | |

**For Design Doc (Technical Design Document)**:

| Extraction Item | Description | Required |
|:---|:---|:---|
| **Technology Stack** | Technologies/libraries to use | Yes |
| **Architecture Proposal** | Module structure/layer design | Yes |
| **Design Decisions** | Reasons for technology selection/alternatives | |
| **Non-Functional Requirements** | Performance/security requirements | |

### 3. Missing Information Confirmation

If important items cannot be determined from input, **confirm with user before generation**:

- Feature name unclear
- Required extraction items cannot be inferred from input
- No technology stack specified (confirm whether to follow existing patterns)
- Ambiguous business rules or edge cases

### 4. Existing Document Check

Check the following before generation:

```
Does .docs/requirement-diagram/{feature-name}.md exist? (PRD)
Does .docs/specification/{feature-name}_spec.md already exist?
Does .docs/specification/{feature-name}_design.md already exist?
```

**If PRD exists**:

- Pre-load PRD and understand requirement IDs (UR-xxx, FR-xxx, NFR-xxx) and functional requirements
- Ensure generated spec covers PRD requirements
- Reference PRD requirement IDs in spec's "Functional Requirements" section

**If spec/design exists**: Confirm with user whether to overwrite.

## Output Format

### Phase 1: Abstract Specification (Specify Phase)

If a template (`.docs/SPECIFICATION_TEMPLATE.md`) exists in the project, follow it.
Otherwise, generate with the following structure:

```markdown
# {Feature Name} Specification

## Background

Why this feature is needed

## Overview

What to achieve

## Functional Requirements

- Requirement 1
- Requirement 2

## API

Public interface definitions

## Data Model

Major type definitions
```

**Save Location**: `.docs/specification/{feature-name}_spec.md`

### Phase 2: Technical Design Document (Plan Phase)

After abstract specification generation is complete, generate the technical design document.
If a template (`.docs/DESIGN_DOC_TEMPLATE.md`) exists in the project, follow it.

**Content to Include in Design Doc**:

| Section | Content | Required |
|:---|:---|:---|
| Implementation Status | Initially Not Implemented | Yes |
| Design Goals | Technical goals to achieve | Yes |
| Technology Stack | Technologies and selection rationale | Yes |
| Architecture | System diagram/module breakdown | Yes |
| Design Decisions | Decisions/options/rationale | Yes |
| Data Model | Specific type definitions | |
| Interface Definitions | Interface definitions for each layer | |
| Testing Strategy | Test levels/coverage targets | |

**Save Location**: `.docs/specification/{feature-name}_design.md`

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

| Check Item | Verification Content |
|:---|:---|
| **Requirement Coverage** | Are all PRD functional requirements (FR-xxx) covered in spec? |
| **Requirement ID References** | Do spec functional requirements appropriately reference PRD requirement IDs? |
| **Non-Functional Requirement Reflection** | Are PRD non-functional requirements (NFR-xxx) reflected in spec? |
| **Terminology Consistency** | Is the same terminology used in PRD and spec? |

### Handling Inconsistencies

1. **Missing requirements**: Add corresponding functional requirements to spec
2. **Missing requirement ID references**: Add corresponding requirement IDs to functional requirements
3. **Terminology inconsistency**: Unify to PRD terminology

### Documenting Consistency Review Results

Add the following to spec's end (if PRD exists):

```markdown
## PRD Reference

- Corresponding PRD: `.docs/requirement-diagram/{feature-name}.md`
- Covered Requirements: UR-001, FR-001, FR-002, NFR-001, ...
```

## Post-Generation Actions

1. **Save Files**:
    - `.docs/specification/{feature-name}_spec.md`
    - `.docs/specification/{feature-name}_design.md` (if generated)

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

| Feature | Usage |
|:---|:---|
| `find_symbol` | Search existing function/class definitions for API spec reference |
| `find_referencing_symbols` | Infer behavior from existing code usage patterns |

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
