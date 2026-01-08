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

| Environment Variable     | Default Value        | Description                    |
|:-------------------------|:---------------------|:-------------------------------|
| `SDD_ROOT`               | `.sdd`               | Root directory                 |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | PRD/Requirements directory     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`          | Task log directory             |

**Path Resolution Priority:**

1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or
configuration file exists.

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
2. Load project principles (Required)
   ├─ If CONSTITUTION.md exists:
   │   └─ Read .sdd/CONSTITUTION.md using Read tool
   │   └─ Understand principle categories (B-xxx, A-xxx, D-xxx, T-xxx)
   └─ If not exists: Skip (note this in output)
   ↓
3. Vibe Coding risk assessment
   ├─ High: Confirm missing info with user → Resume after response
   ├─ Medium: Confirm ambiguous points → Resume after response
   └─ Low: Proceed to next step
   ↓
4. Check existing documents
   ├─ If PRD exists: Pre-load and understand requirements
   └─ If spec/design exists: Confirm overwrite
   ↓
5. Generate and save abstract specification (Specify)
   ↓
6. Spec principle compliance check with spec-reviewer (Required)
   ├─ Explicitly call spec-reviewer agent using Task tool
   │  Example: Task(subagent_type="sdd-workflow:spec-reviewer", prompt=".sdd/specification/{feature-name}_spec.md")
   ├─ Check CONSTITUTION.md compliance (Architecture/Development principles focus)
   ├─ On violation detection: Attempt auto-fix
   ├─ After fix, re-check
   └─ Retrieve review results and include in next step output
   ↓
7. Confirm Design Doc generation
   ├─ Technical info present: Generate and save (Plan)
   └─ No technical info: Confirm whether to skip
   ↓
8. Design Doc principle compliance check with spec-reviewer (When design generated, Required)
   ├─ Explicitly call spec-reviewer agent using Task tool
   │  Example: Task(subagent_type="sdd-workflow:spec-reviewer", prompt=".sdd/specification/{feature-name}_design.md")
   ├─ Check CONSTITUTION.md compliance (Technical constraints/Architecture focus)
   ├─ On violation detection: Attempt auto-fix
   ├─ After fix, re-check
   └─ Retrieve review results and include in next step output
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

````markdown
## PRD Reference

- Corresponding PRD: `.sdd/requirement/[{parent-feature}/]{feature-name}.md`
- Covered Requirements: UR-001, FR-001, FR-002, NFR-001, ...
````

※ For hierarchical structure, parent feature PRD is `.sdd/requirement/{parent-feature}/index.md`

## Post-Generation Actions

1. **Save Files**:
    - Flat structure: `.sdd/specification/{feature-name}_spec.md`, `.sdd/specification/{feature-name}_design.md`
    - Hierarchical structure (parent feature): `.sdd/specification/{parent-feature}/index_spec.md`,
      `.sdd/specification/{parent-feature}/index_design.md`
    - Hierarchical structure (child feature): `.sdd/specification/{parent-feature}/{feature-name}_spec.md`,
      `.sdd/specification/{parent-feature}/{feature-name}_design.md`

2. **Consistency Check**:
    - If PRD exists: Verify and reflect PRD ↔ spec consistency
    - Verify spec ↔ design consistency

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

## Loading CONSTITUTION.md (Required)

Before spec/design generation, **you must read `.sdd/CONSTITUTION.md` using the Read tool**.

```
Read: .sdd/CONSTITUTION.md
```

### Post-Load Verification

After loading CONSTITUTION.md, understand the following principles and ensure spec/design compliance:

**For Abstract Specification (*_spec.md)**:

| Principle Category          | Impact on Spec                                           |
|:----------------------------|:---------------------------------------------------------|
| Architecture Principles (A-xxx) | Architecture patterns, layer separation, interface design |
| Development Principles (D-xxx)  | Testability, modularity, requirement traceability        |
| Business Principles (B-xxx)     | Business logic reflection, domain model                  |

**For Technical Design Document (*_design.md)**:

| Principle Category          | Impact on Design                                         |
|:----------------------------|:---------------------------------------------------------|
| Technical Constraints (T-xxx)   | Technology selection, version constraints, platform      |
| Architecture Principles (A-xxx) | Architecture implementation, design patterns             |
| Development Principles (D-xxx)  | Test strategy, CI/CD considerations                      |

### If CONSTITUTION.md Does Not Exist

- Skip principle check
- Note in output: "Principle check was not performed as CONSTITUTION.md does not exist"

## Principle Compliance Check with spec-reviewer (Required)

After spec and design generation, **you must call the `spec-reviewer` agent using the Task tool to check principle compliance**.

### Check Flow

```
1. Explicitly call spec-reviewer agent using Task tool
   [After spec generation]
   Example: Task(
     subagent_type="sdd-workflow:spec-reviewer",
     prompt=".sdd/specification/{feature-name}_spec.md"
   )

   [After design generation]
   Example: Task(
     subagent_type="sdd-workflow:spec-reviewer",
     prompt=".sdd/specification/{feature-name}_design.md"
   )
   ↓
2. Execute CONSTITUTION.md compliance check
   ↓
3. If violations detected:
   ├─ Auto-fixable: Apply fix using Edit tool
   └─ Not auto-fixable: Report locations needing manual fix
   ↓
4. After fix, re-check to verify
   ↓
5. Retrieve review results and must include in output (see next section)
```

**Important**: This check cannot be omitted. **After both spec and design generation, you must execute spec-reviewer using the Task tool.**

### Check Result Output (Required)

**Upon spec/design generation completion, you must output the following check result section. This section cannot be omitted.**

```markdown
## CONSTITUTION.md Compliance Check Results

**Check Execution Time**: YYYY-MM-DD HH:MM:SS
**Review Agent**: spec-reviewer

### spec Check Results

**Target File**: .sdd/specification/{feature-name}_spec.md

#### Compliance Status Summary

| Principle Category | Compliance Status | Details |
|:---|:---|:---|
| Business Principles (B-xxx) | 🟢 Compliant / 🟡 Partially Compliant / 🔴 Violation | Compliant: X items, Violations: Y items |
| Architecture Principles (A-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |
| Development Principles (D-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |
| Technical Constraints (T-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |

#### Fix Summary

- **Auto-fixes applied**: {count} items
- **Manual fixes required**: {count} items

---

### design Check Results (if generated)

**Target File**: .sdd/specification/{feature-name}_design.md

#### Compliance Status Summary

| Principle Category | Compliance Status | Details |
|:---|:---|:---|
| Business Principles (B-xxx) | 🟢 Compliant / 🟡 Partially Compliant / 🔴 Violation | Compliant: X items, Violations: Y items |
| Architecture Principles (A-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |
| Development Principles (D-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |
| Technical Constraints (T-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |

#### Fix Summary

- **Auto-fixes applied**: {count} items
- **Manual fixes required**: {count} items

---

### 🔴 Violations (if any)

**[If violations exist]**

#### Principle: {Principle ID} - {Principle Name}

**Violated File**: {spec or design}
**Violation Details**:
- {Specific violation content}

**Recommended Actions**:
- [ ] {Fix method}

---

**[If violations exist, explicitly display warning to user]**

⚠️ **Warning**: CONSTITUTION.md violations detected in spec/design documents.
Please implement the recommended actions above and re-run `/generate_spec` or fix manually.
If you proceed to implementation without resolving violations, they may be flagged during code review.

```

**Feedback Loop on Violation Detection**:

1. If violations detected, explicitly display the above warning to user
2. Clearly document auto-fixed items
3. Present manual fix items as specific actions
4. Encourage user to resolve before proceeding to next step (task breakdown/implementation)
