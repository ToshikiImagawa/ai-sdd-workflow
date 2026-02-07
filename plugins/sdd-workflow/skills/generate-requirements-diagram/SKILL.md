---
name: generate-requirements-diagram
description: "Generate SysML requirements diagram from requirements analysis. Use when visualizing requirement relationships, creating traceability diagrams, or when called by generate-prd."
version: 3.0.1
license: MIT
user-invocable: true
context: fork
agent: sonnet
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Generate Requirements Diagram

Generates SysML requirements diagrams in Mermaid format from requirements analysis.

## Purpose

This skill creates SysML requirements diagrams that visualize:

- Requirement hierarchy and relationships
- Requirement types (functional, performance, interface, etc.)
- Traceability between requirements
- Risk levels and verification methods

## Hybrid Approach

This skill operates in two modes:

| Mode                      | Behavior | Description                                                  |
|:--------------------------|:---------|:-------------------------------------------------------------|
| **Interactive** (default) | Guide    | May ask clarifying questions, provides detailed output       |
| **CI (`--ci`)**           | Silent   | No user interaction, concise output for pipeline integration |

## Prerequisites

**Read the following reference guides before generation:**

- `references/mermaid_notation_rules.md` - Mermaid notation rules for requirements diagrams
- `references/requirements_diagram_components.md` - SysML requirements diagram component definitions

## Input

$ARGUMENTS

| Argument            | Required | Description                                         |
|:--------------------|:---------|:----------------------------------------------------|
| `requirements-text` | Yes      | Requirements analysis text OR feature name          |
| `--ci`              | -        | CI/non-interactive mode. Skips clarifying questions |

### Input Examples

**Feature name reference:**

```
/generate-requirements-diagram task-management
```

**CI mode (called by generate-prd):**

```
/generate-requirements-diagram task-management --ci
```

When a feature name is provided, look for:

- `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md` - Existing PRD with requirements

## Generation Rules

### 1. Input Parsing

> **CI Mode**: Skip clarifying questions. Make reasonable assumptions for ambiguous items.

Extract requirements information:

| Item                            | Source                            |
|:--------------------------------|:----------------------------------|
| **User Requirements**           | UR-xxx entries from tables        |
| **Functional Requirements**     | FR-xxx entries with traceability  |
| **Non-Functional Requirements** | NFR-xxx entries                   |
| **Relationships**               | Derived from, traces to, contains |

### 2. Diagram Generation

Follow these rules when generating the requirements diagram:

1. **Use requirementDiagram syntax** (native Mermaid support)
2. **Apply dark theme** with `%%{init: {'theme': 'dark'}}%%`
3. **Use correct requirement types**:
    - `requirement` - General requirement
    - `functionalRequirement` - Functional requirement
    - `performanceRequirement` - Performance requirement
    - `interfaceRequirement` - Interface requirement
    - `designConstraint` - Design constraint
4. **Use correct relationships**:
    - `contains` - Parent contains child
    - `derives` - Derived from another requirement
    - `satisfies` - Element satisfies requirement
    - `verifies` - Test verifies requirement
    - `refines` - Refines to more detail
    - `traces` - General traceability

### 3. Syntax Rules

**CRITICAL: Follow these Mermaid requirementDiagram syntax rules:**

1. **ID naming**: Use underscores, NOT hyphens
    - ❌ `id: FR-001`
    - ✅ `id: FR_001`

2. **Text quoting**: Always quote text values
    - ❌ `text: User can create tasks`
    - ✅ `text: "User can create tasks"`

3. **Requirement names**: Use underscores or camelCase
    - ❌ `requirement Task Management`
    - ✅ `requirement Task_Management`

4. **Attribute values**: Use lowercase
    - ❌ `risk: High`
    - ✅ `risk: high`

5. **Relationship syntax**: Use correct arrow format
    - `A - contains -> B`
    - `A - derives -> B`

### 4. Validate

Check Quality Checks items before returning output.

- If issues found: Fix and repeat from step 2

## Output Format

Use the `templates/${SDD_LANG:-en}/requirements_diagram_output.md` template for output formatting.

**Read the output template before returning results.**

## Output

**IMPORTANT: This skill returns TEXT only. It does NOT write files.**

The output consists of:

1. **Mermaid requirementDiagram code block** - The SysML requirements diagram
2. **Diagram Structure** - Hierarchical view of requirements
3. **Relationship Summary** - Table of all relationships with rationale

The caller (generate-prd or user) is responsible for saving the output to a file if needed.

## Quality Checks

Before returning output, verify:

- [ ] All requirements from input are represented
- [ ] Requirement IDs use underscores (not hyphens)
- [ ] Text values are properly quoted
- [ ] Relationships are correctly specified
- [ ] Mermaid syntax is valid (no errors)
- [ ] Risk levels are lowercase
- [ ] Verification methods are valid values

## Verification Method Reference

| Value           | Meaning           | When to Use                          |
|:----------------|:------------------|:-------------------------------------|
| `analysis`      | Static analysis   | Design review, code analysis         |
| `inspection`    | Manual review     | Document review, code review         |
| `test`          | Automated testing | Unit, integration, E2E tests         |
| `demonstration` | Live demo         | User acceptance, manual verification |

## Notes

### Diagram Design

- Keep diagram readable by limiting to 10-15 requirements per diagram
- For large systems, create separate diagrams per subsystem
- Use consistent naming conventions throughout
- Ensure all functional requirements derive from user requirements
- Non-functional requirements should trace to affected functional requirements

### Integration

- This skill is typically called by `/generate-prd --ci` with `--ci` flag
- Output is text only; the caller is responsible for file operations
- When called standalone (Interactive mode), suggest next step: `/finalize-prd`
- In CI mode, output is optimized for pipeline consumption
