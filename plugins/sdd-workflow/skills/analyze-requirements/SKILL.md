---
name: analyze-requirements
description: "Analyze and extract requirements from use case diagram. Use when extracting UR/FR/NFR from use cases or when called by generate-prd."
version: 3.0.1
license: MIT
user-invocable: true
context: fork
agent: sonnet
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Analyze Requirements

Analyzes use case diagrams or business requirements to extract structured requirements lists.

## Purpose

This skill extracts and categorizes requirements into:

- **User Requirements (UR)** - What users want the system to do
- **Functional Requirements (FR)** - Functions the system must provide
- **Non-Functional Requirements (NFR)** - Quality attributes (performance, security, etc.)

## Hybrid Approach

This skill operates in two modes:

| Mode                      | Behavior | Description                                                      |
|:--------------------------|:---------|:-----------------------------------------------------------------|
| **Interactive** (default) | Guide    | May ask clarifying questions about ambiguous requirements        |
| **CI (`--ci`)**           | Silent   | No user interaction, makes reasonable assumptions automatically  |

## Prerequisites

**Read the following references:**

- `references/usecase_diagram_guide.md` - Use case diagram notation (for parsing input)

**Read project principles if available:**

- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` - Project principles (optional, for principle alignment)

## Input

$ARGUMENTS

| Argument     | Required | Description                                                      |
|:-------------|:---------|:-----------------------------------------------------------------|
| `input-text` | Yes      | Use case diagram text, business requirements, or feature name   |
| `--ci`       | -        | CI/non-interactive mode. Skips clarifying questions             |

### Input Examples

See `examples/usecase_diagram_input.md` for detailed input formats with Mermaid diagrams.

**Quick examples:**

```
/analyze-requirements task-management
/analyze-requirements task-management --ci
```

When a feature name is provided, look for:
- `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md` - Existing PRD
- Use case diagrams within the PRD

## Generation Rules

### 1. Input Analysis

> **CI Mode**: Skip clarifying questions. Make reasonable assumptions for ambiguous items.

Parse the input to identify:

| Item | Source |
|:-----|:-------|
| **Actors** | From use case diagram or requirements text |
| **Use Cases** | From use case diagram or requirements text |
| **Relationships** | Include/extend relationships between use cases |
| **Business Context** | Background information if available |

### 2. Requirement Extraction

For each use case and context, derive:

1. **User Requirements (UR)**
   - High-level goals from user perspective
   - What value users expect
   - ID format: `UR-xxx`

2. **Functional Requirements (FR)**
   - Specific functions to fulfill user requirements
   - Derived from use cases
   - ID format: `FR-xxx`

3. **Non-Functional Requirements (NFR)**
   - Performance requirements
   - Security requirements
   - Usability requirements
   - Reliability requirements
   - ID format: `NFR-xxx`

### 3. Requirement Attributes

For each requirement, specify:

| Attribute | Values | Description |
|:----------|:-------|:------------|
| **Priority** | Must / Should / Could / Won't | MoSCoW prioritization |
| **Risk** | High / Medium / Low | Implementation risk level |
| **Verification** | Test / Analysis / Demonstration / Inspection | How to verify |

### 4. Traceability

Establish relationships between requirements:

| Relationship | From | To | Description |
|:-------------|:-----|:---|:------------|
| **derives** | FR | UR | Functional requirement derived from user requirement |
| **contains** | Parent | Child | Parent requirement contains child requirements |
| **traces** | NFR | FR | Non-functional requirement traces to functional requirement |

### 5. Validate

Check Quality Checks items before returning output.
- If issues found: Fix and repeat from step 2

## Output Format

**IMPORTANT**: This skill returns text only. It does NOT write files.

Return the following markdown structure:

```markdown
## User Requirements (UR)

| ID     | Requirement                                | Priority | Risk   |
|:-------|:-------------------------------------------|:---------|:-------|
| UR-001 | Users can efficiently manage tasks         | Must     | High   |
| UR-002 | System provides intuitive task operations  | Should   | Medium |

## Functional Requirements (FR)

| ID     | Requirement                           | Derived From | Priority | Risk   | Verification |
|:-------|:--------------------------------------|:-------------|:---------|:-------|:-------------|
| FR-001 | User can create new tasks             | UR-001       | Must     | High   | Test         |
| FR-002 | User can edit existing tasks          | UR-001       | Must     | Medium | Test         |
| FR-003 | User can delete tasks                 | UR-001       | Must     | Medium | Test         |
| FR-004 | User can mark tasks as complete       | UR-001       | Must     | Low    | Test         |

## Non-Functional Requirements (NFR)

| ID      | Requirement                          | Category    | Priority | Risk   | Verification   |
|:--------|:-------------------------------------|:------------|:---------|:-------|:---------------|
| NFR-001 | Response time under 1 second         | Performance | Should   | Medium | Demonstration  |
| NFR-002 | System available 99.9% uptime        | Reliability | Should   | High   | Analysis       |
| NFR-003 | User actions logged for audit        | Security    | Could    | Low    | Inspection     |

## Requirements Summary

| Category | Count | Must | Should | Could |
|:---------|------:|-----:|-------:|------:|
| UR       |     2 |    1 |      1 |     0 |
| FR       |     4 |    4 |      0 |     0 |
| NFR      |     3 |    0 |      2 |     1 |
| **Total**|   **9**| **5**|  **3** | **1** |
```

The caller (generate-prd or user) is responsible for saving the output to a file if needed.

## Quality Checks

Before returning output, verify:

- [ ] All use cases are covered by functional requirements
- [ ] Each FR traces to at least one UR
- [ ] Priorities are assigned consistently
- [ ] Risk levels reflect implementation complexity
- [ ] Verification methods are appropriate for requirement type
- [ ] No duplicate requirements
- [ ] IDs are unique and sequential

## Notes

### Requirements Writing

- Focus on WHAT the system must do, not HOW
- Keep requirements atomic and testable
- Avoid implementation details in requirement descriptions
- Use active voice (e.g., "System shall..." or "User can...")
- Ensure requirements are measurable where possible

### Integration

- This skill is typically called by `/generate-prd --ci` with `--ci` flag
- Output is text only; the caller is responsible for file operations
- When called standalone (Interactive mode), suggest next step: `/generate-requirements-diagram`
- In CI mode, makes reasonable assumptions for ambiguous requirements
