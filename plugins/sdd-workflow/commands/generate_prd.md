---
description: "Generate PRD (Requirements Specification) in SysML requirements diagram format from business requirements"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Generate PRD - Requirements Specification Generation

Generates PRD (Requirements Specification) from input business requirements according to the AI-SDD workflow.

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for PRD generation.

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

| Skill                        | Purpose                                                              |
|:-----------------------------|:---------------------------------------------------------------------|
| `sdd-workflow:sdd-templates` | Generate `.sdd/PRD_TEMPLATE.md` when project template does not exist |

**Template Preparation Flow**:

1. Use `.sdd/PRD_TEMPLATE.md` (project template) if it exists
2. If not, use `sdd-templates` skill to generate the template

### PRD / Requirements Diagram Positioning (Reference)

**Abstraction Level: Highest** | **Focus: What to build, why to build it**

| Item                  | Details                                                                                                      |
|:----------------------|:-------------------------------------------------------------------------------------------------------------|
| **Purpose**           | Define high-level product requirements (business value)                                                      |
| **Content**           | User requirements, functional requirements, non-functional requirements in SysML requirements diagram format |
| **Technical Details** | **Not included**                                                                                             |
| **SysML Elements**    | Requirements Diagram (req)                                                                                   |

### Document Dependencies

```
CONSTITUTION.md → PRD (Requirements Diagram) → *_spec.md → *_design.md → task/ → Implementation
```

PRD is created following `CONSTITUTION.md` principles and serves as the foundation for subsequent specifications and design documents.

## Input

$ARGUMENTS

### Input Examples

```
/generate_prd A feature for users to manage tasks.
Available only to logged-in users.
Supports task creation, editing, deletion, and completion, with due date and priority settings.
Sends email notifications for tasks nearing their due date.
```

## Generation Rules

### 1. Vibe Coding Risk Assessment (Perform First)

Analyze input content and assess risk based on the following criteria:

| Risk   | Condition                   | Response                                         |
|:-------|:----------------------------|:-------------------------------------------------|
| High   | Business requirements vague | Confirm missing info with user before generating |
| Medium | Some requirements unclear   | Clarify ambiguous points before generating       |
| Low    | Requirements clear          | Can generate as-is                               |

**Examples of Vague Input**:

- "Add a useful feature" → Confirm specific functionality
- "Improve user experience" → Confirm improvement target and goals
- "Same feature as competitors" → Confirm specific feature specifications

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

**⚠️ Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

**Hierarchical structure usage decision**:

- Use hierarchical structure when parent feature (category) is specified in input, or when existing hierarchical
  structure exists
- Recommended to confirm with user whether to use hierarchical structure

**If PRD exists**: Confirm with user whether to overwrite.

**If spec/design exists**:

- After PRD generation, verify no impact on consistency with existing spec/design
- If requirement IDs are added/changed, notify that spec/design may need updates

## Output Format

### Template Preparation

Follow these steps to prepare the template:

1. Check if `.sdd/PRD_TEMPLATE.md` exists
2. **If exists**: Use that template
3. **If not exists**: Use `sdd-workflow:sdd-templates` skill to generate `.sdd/PRD_TEMPLATE.md`, then use the generated
   template

### Template Application Notes

- Replace template placeholders (`{Feature Name}`, `{Requirement Name}`, etc.) based on input content
- Sections with `<MUST>` markers are required, `<RECOMMENDED>` are recommended, `<OPTIONAL>` are optional
- Use SysML requirementDiagram syntax for requirements diagrams
- Manage requirement IDs (UR-xxx, FR-xxx, NFR-xxx) uniquely

**Save Location**:

- Flat structure: `.sdd/requirement/{feature-name}.md`
- Hierarchical structure (parent feature): `.sdd/requirement/{parent-feature}/index.md`
- Hierarchical structure (child feature): `.sdd/requirement/{parent-feature}/{feature-name}.md`

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
   ├─ If PRD exists: Confirm overwrite
   └─ If spec/design exists: Understand impact scope
   ↓
5. Generate and save PRD
   ↓
6. Principle compliance check with prd-reviewer (Required)
   ├─ Explicitly call prd-reviewer agent using Task tool
   │  Example: Task(subagent_type="sdd-workflow:prd-reviewer", prompt=".sdd/requirement/{feature-name}.md")
   ├─ Check CONSTITUTION.md compliance
   ├─ On violation detection: Attempt auto-fix
   ├─ After fix, re-check
   └─ Retrieve review results and include in next step output
   ↓
7. Check consistency with existing spec/design
   ├─ If spec/design exists: Verify consistency
   └─ Updates needed: Notify recommendation to update spec/design
   ↓
8. Propose next steps
   - Create abstract specification with /generate_spec
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

1. **Spec needs update**: Regenerate with `/generate_spec` or update manually
2. **Design needs update**: Check if spec changes require design decision revision
3. **Impact Scope Notification**: Clearly indicate to user which documents need updates

## Post-Generation Actions

1. **Save File**:
    - Flat structure: `.sdd/requirement/{feature-name}.md`
    - Hierarchical structure: `.sdd/requirement/{parent-feature}/index.md` or
      `.sdd/requirement/{parent-feature}/{feature-name}.md`

2. **Consistency Check**:
    - If existing spec/design exists: Verify impact and notify if updates needed

3. **Next Steps**:
    - Create abstract specification and technical design document with `/generate_spec`
    - Reference PRD requirement IDs in specification
    - If existing spec exists, recommend update

## Loading CONSTITUTION.md (Required)

Before PRD generation, **you must read `.sdd/CONSTITUTION.md` using the Read tool**.

```
Read: .sdd/CONSTITUTION.md
```

### Post-Load Verification

After loading CONSTITUTION.md, understand the following principles and ensure PRD compliance:

| Principle Category        | Impact on PRD                                              |
|:--------------------------|:-----------------------------------------------------------|
| Business Principles (B-xxx) | Directly reflected in background/purpose, user requirements |
| Architecture Principles (A-xxx) | Documented as constraints (no technical details)       |
| Development Principles (D-xxx) | Affects verifymethod selection                         |
| Technical Constraints (T-xxx) | Documented as constraints (from feasibility perspective) |

### If CONSTITUTION.md Does Not Exist

- Skip principle check
- Note in output: "Principle check was not performed as CONSTITUTION.md does not exist"

## Principle Compliance Check with prd-reviewer (Required)

After PRD generation, **you must call the `prd-reviewer` agent using the Task tool to check principle compliance**.

### Check Flow

```
1. Explicitly call prd-reviewer agent using Task tool
   Example: Task(
     subagent_type="sdd-workflow:prd-reviewer",
     prompt=".sdd/requirement/{feature-name}.md"
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

**Important**: This check cannot be omitted. **You must execute prd-reviewer using the Task tool.**

### Check Result Output (Required)

**Upon PRD generation completion, you must output the following check result section. This section cannot be omitted.**

```markdown
## CONSTITUTION.md Compliance Check Results

**Check Execution Time**: YYYY-MM-DD HH:MM:SS
**Review Agent**: prd-reviewer
**Target File**: .sdd/requirement/{feature-name}.md

### Compliance Status Summary

| Principle Category | Compliance Status | Details |
|:---|:---|:---|
| Business Principles (B-xxx) | 🟢 Compliant / 🟡 Partially Compliant / 🔴 Violation | Compliant: X items, Violations: Y items |
| Architecture Principles (A-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |
| Development Principles (D-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |
| Technical Constraints (T-xxx) | 🟢 / 🟡 / 🔴 | Compliant: X items, Violations: Y items |

### Fix Summary

- **Auto-fixes applied**: {count} items
- **Manual fixes required**: {count} items

### 🔴 Violations (if any)

**[If violations exist]**

#### Principle: {Principle ID} - {Principle Name}

**Violation Details**:
- {Specific violation content}

**Recommended Actions**:
- [ ] {Fix method}

---

**[If violations exist, explicitly display warning to user]**

⚠️ **Warning**: CONSTITUTION.md violations detected in PRD.
Please implement the recommended actions above and re-run `/generate_prd` or fix manually.
If you proceed to `/generate_spec` without resolving violations, they may propagate to specification and design documents.

```

**Feedback Loop on Violation Detection**:

1. If violations detected, explicitly display the above warning to user
2. Clearly document auto-fixed items
3. Present manual fix items as specific actions
4. Encourage user to resolve before proceeding to next step (`/generate_spec`)

## Notes

- PRD should **NOT include technical details** (that is the role of `*_spec.md` and `*_design.md`)
- Manage requirement IDs uniquely so they can be referenced in subsequent documents
- Classify priorities using MoSCoW method (Must/Should/Could/Won't)
- Maintain high abstraction level and focus on "what" and "why"
