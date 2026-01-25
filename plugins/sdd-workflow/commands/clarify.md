---
description: "Analyze specifications and generate clarification questions to eliminate ambiguity before implementation"
argument-hint: "[spec-file-path]"
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Clarify - Specification Clarification

Scans specifications across 9 key categories and generates targeted clarification questions to eliminate ambiguity
before implementation.

## Prerequisites

### Plugin Update Check

**Before execution, check if `.sdd/UPDATE_REQUIRED.md` exists.**

If this file exists, the AI-SDD plugin needs to be updated. Display a warning to the user and prompt them to run the following command:

```
/sdd_init
```

### AI-SDD Principles Document

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `.sdd/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles.

This command follows AI-SDD principles for specification clarification.

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

### Relationship to Vibe Detector Skill

This command is complementary to the `vibe-detector` skill:

| Tool              | Purpose                                     | When to Use                    |
|:------------------|:--------------------------------------------|:-------------------------------|
| **vibe-detector** | Detects vague instructions in user requests | During task initiation         |
| **clarify**       | Scans existing specs for ambiguity and gaps | Before implementation planning |

## Input

$ARGUMENTS

### Input Examples

```
/clarify user-auth
/clarify task-management
/clarify auth/user-login  # For hierarchical structure
```

## Processing Flow

### 1. Load Target Specifications

Both flat and hierarchical structures are supported.

**For flat structure**:

```
Load .sdd/requirement/{feature-name}.md (PRD, if exists)
Load .sdd/specification/{feature-name}_spec.md (if exists)
Load .sdd/specification/{feature-name}_design.md (if exists)
```

**For hierarchical structure** (when argument contains `/`):

```
Load .sdd/requirement/{parent-feature}/index.md (parent feature PRD, if exists)
Load .sdd/requirement/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load .sdd/specification/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load .sdd/specification/{parent-feature}/{feature-name}_spec.md (child feature spec, if exists)
Load .sdd/specification/{parent-feature}/index_design.md (parent feature design, if exists)
Load .sdd/specification/{parent-feature}/{feature-name}_design.md (child feature design, if exists)
```

**⚠️ Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

### 2. Nine Category Analysis

Analyze specifications across these categories:

| Category                           | Analysis Focus                       | Examples of Ambiguity                   |
|:-----------------------------------|:-------------------------------------|:----------------------------------------|
| **1. Functional Scope**            | What the feature does vs doesn't do  | Edge cases, boundary conditions         |
| **2. Data Model**                  | Data structures, types, constraints  | Field nullability, validation rules     |
| **3. Flow & Behavior**             | State transitions, error handling    | Rollback behavior, retry logic          |
| **4. Non-Functional Requirements** | Performance, security, scalability   | Response time requirements, rate limits |
| **5. Integrations**                | External system dependencies         | Authentication methods, API versions    |
| **6. Edge Cases**                  | Boundary conditions, error scenarios | Empty states, network failures          |
| **7. Constraints**                 | Technical limitations, trade-offs    | Browser support, data size limits       |
| **8. Terminology**                 | Domain-specific terms                | Consistent naming, acronym definitions  |
| **9. Completion Signals**          | "Done" criteria, success metrics     | Acceptance criteria, test coverage      |

### 3. Classify Clarity Level

For each category, classify clarity as:

| Level       | Criteria                               | Example                             |
|:------------|:---------------------------------------|:------------------------------------|
| **Clear**   | Fully specified with explicit examples | "Return 404 when user ID not found" |
| **Partial** | Concept exists but details missing     | "Handle errors appropriately"       |
| **Missing** | Not mentioned in specifications        | No mention of authentication flow   |

### 4. Generate Clarification Questions

Generate up to 5 high-impact questions prioritizing:

**Selection Criteria**:

1. **Impact**: Would ambiguity cause major implementation divergence?
2. **Frequency**: Will this decision affect multiple modules?
3. **Risk**: Could wrong assumptions require significant rework?

**Question Format**:

````markdown
### Q{n}: {Category} - {Question Title}

**Context**: {Brief explanation of why this matters}

**Question**: {Specific question requiring user decision}

**Examples to Consider**:
- Option A: {Example}
- Option B: {Example}

**Current Specification State**: Clear / Partial / Missing
````

### 5. Integrate Answers

After receiving user answers:

1. **Update Specifications**: Integrate answers into appropriate `*_spec.md` or `*_design.md`
2. **Mark Resolved**: Track which questions have been addressed
3. **Generate Diff**: Show what was added to specifications

## Output

Use the output-templates skill to display specification clarification report.

## Integration Mode

When user provides answers, use `--integrate` flag:

```
/clarify user-auth --integrate
```

This will:

1. Prompt for answers to each question
2. Update specifications incrementally
3. Show diffs of changes

## Best Practices

### When to Use This Command

| Scenario                               | Recommended Action                                |
|:---------------------------------------|:--------------------------------------------------|
| **Before task breakdown**              | Run `/clarify` to catch ambiguities early         |
| **After receiving vague requirements** | Use with `/generate_spec` to build complete specs |
| **During spec review**                 | Verify all 9 categories are addressed             |
| **Before implementation**              | Final check to ensure no hidden assumptions       |

### Complementary Commands

```
/clarify {feature}           # Identify ambiguities
↓
(Update specs with answers)
↓
/check_spec {feature}        # Verify consistency
↓
/task_breakdown {feature}    # Generate tasks
```

## Advanced Options

### Focus on Specific Categories

```
/clarify user-auth --categories flow,integrations,edge-cases
```

### Specify Output Detail Level

```
/clarify user-auth --detail minimal    # Top 3 questions only
/clarify user-auth --detail standard   # Top 5 questions (default)
/clarify user-auth --detail comprehensive  # All identified issues
```

## Post-Clarification Verification

### Automatic Verification (Performed)

The following verifications are automatically performed during clarification:

- [x] **Nine Category Scan**: Comprehensively detect ambiguities across functional scope, data model, flow, etc.
- [x] **Clarity Score Calculation**: Classify items as Clear/Partial/Missing and calculate overall score
- [x] **Question Prioritization**: Select questions based on impact, risk, and blocker status


### Verification Commands

```bash
# Re-scan to verify clarity improvements
/clarify {feature-name}

# Consistency check (verify updated specifications)
/check_spec {feature-name} --full
```

### Implementation Readiness Criteria

| Clarity Score | Recommended Action |
|:---|:---|
| 80% or above | Ready for implementation |
| 60-79% | Recommended to resolve Partial items |
| Below 60% | Further clarification required before implementation |

## Notes

- Questions are generated based on specification analysis, not assumptions
- Prioritize questions that would cause most implementation uncertainty
- Some ambiguity is acceptable for low-risk, low-impact decisions
- Re-run after major specification updates to catch new ambiguities
- Works best when combined with vibe-detector skill during task initiation