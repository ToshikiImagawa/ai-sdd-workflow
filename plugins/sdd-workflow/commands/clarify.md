---
description: "Analyze specifications and generate clarification questions to eliminate ambiguity before implementation"
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

**Read the AI-SDD principles document.**

AI-SDD principles document path (search in the following order and use the first file found):
1. `.sdd/AI-SDD-PRINCIPLES.md` (from project root - for plugin users)
2. `../AI-SDD-PRINCIPLES.md` (relative path from this file - for plugin development)
3. `plugins/sdd-workflow/AI-SDD-PRINCIPLES.md` (from project root - for plugin development)

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

## Output Format

### Initial Clarification Report

````markdown
# Specification Clarification Report

## Target Documents

- `.sdd/requirement/[{parent-feature}/]{feature-name}.md` (PRD, if exists)
- `.sdd/specification/[{parent-feature}/]{feature-name}_spec.md`
- `.sdd/specification/[{parent-feature}/]{feature-name}_design.md`

※ For hierarchical structure, parent feature uses `index.md`, `index_spec.md`, `index_design.md`

## Category Analysis Summary

| Category | Clear | Partial | Missing | Priority |
|:---|:---|:---|:---|:---|
| Functional Scope | ✓ | | | Low |
| Data Model | | ✓ | | High |
| Flow & Behavior | | | ✓ | High |
| Non-Functional Requirements | ✓ | | | Low |
| Integrations | | ✓ | | Medium |
| Edge Cases | | | ✓ | High |
| Constraints | ✓ | | | Low |
| Terminology | ✓ | | | Low |
| Completion Signals | | ✓ | | Medium |

## High-Priority Clarification Questions

### Q1: Data Model - User Status Field Nullability

**Context**: The specification mentions a `status` field in the User model but doesn't specify if it can be null or what the default value should be.

**Question**: Should the `status` field allow null values? If not, what should be the default value for new users?

**Examples to Consider**:
- Option A: Required field, default to "active"
- Option B: Required field, default to "pending"
- Option C: Optional field, null means "unverified"

**Current Specification State**: Partial (mentioned but details missing)

**Impact**: High - Affects database schema, validation logic, and API responses

---

### Q2: Flow & Behavior - Authentication Failure Retry Logic

**Context**: The spec describes authentication but doesn't specify behavior when authentication fails.

**Question**: What should happen after failed authentication attempts? Should there be rate limiting or account locking?

**Examples to Consider**:
- Option A: No retry limit, allow indefinite attempts
- Option B: Lock account after 5 failed attempts for 15 minutes
- Option C: Exponential backoff: 1s, 5s, 15s, then lock

**Current Specification State**: Missing

**Impact**: High - Security and user experience implications

---

{Continue for up to 5 questions}

## Recommendations

1. **Immediate Action Required**: Address Q1, Q2 (High Impact)
2. **Before Implementation**: Clarify Q3, Q4 (Medium Impact)
3. **Nice to Have**: Q5 (Low Impact, can be decided during implementation)

## Next Steps

1. Review questions with stakeholders
2. Update specifications with answers using `/clarify {feature-name} --integrate`
3. Re-run `/check_spec {feature-name}` to verify consistency
````

### After Integration

````markdown
# Clarification Integration Complete

## Updated Documents

- Updated `.sdd/specification/[{path}/]{feature-name}_spec.md`
  - Added: User.status field nullability and default value
  - Added: Authentication retry logic specification

- Updated `.sdd/specification/[{path}/]{feature-name}_design.md`
  - Added: Rate limiting implementation approach
  - Added: Database schema constraints for status field

## Changes Summary

### Q1 Resolution: User Status Field
```diff
+ ### User Model
+
+ - `status`: Required field (string), default: "active"
+ - Allowed values: "active", "inactive", "suspended"
+ - Cannot be null
```

### Q2 Resolution: Authentication Retry Logic
```diff
+ ### Authentication Error Handling
+
+ Failed authentication attempts trigger progressive rate limiting:
+ 1. First 3 attempts: Immediate retry allowed
+ 2. Attempts 4-5: 5-second delay required
+ 3. After 5 failures: Account locked for 15 minutes
+ 4. After lock expires: Counter resets
```

## Remaining Ambiguities

- Q3: Edge case handling for concurrent sessions (Medium priority)
- Q5: Performance requirements for bulk operations (Low priority)

## Recommended Next Steps

1. Run `/task_breakdown {feature-name}` to generate implementation tasks
2. Address remaining ambiguities during implementation if needed
````

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

## Notes

- Questions are generated based on specification analysis, not assumptions
- Prioritize questions that would cause most implementation uncertainty
- Some ambiguity is acceptable for low-risk, low-impact decisions
- Re-run after major specification updates to catch new ambiguities
- Works best when combined with vibe-detector skill during task initiation