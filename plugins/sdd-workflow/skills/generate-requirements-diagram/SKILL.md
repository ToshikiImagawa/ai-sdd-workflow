---
name: generate-requirements-diagram
description: "Generate SysML requirements diagram from requirements analysis. Use when visualizing requirement relationships, creating traceability diagrams, or when called by generate-prd."
argument-hint: "<requirements-text> [--ci]"
license: MIT
user-invocable: true
context: fork
model: haiku
allowed-tools: Read, Glob, Grep, AskUserQuestion
disallowed-tools: Write, Edit, Bash
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
- `${CLAUDE_PLUGIN_ROOT}/shared/references/id_conventions_config.md` - PRD-level ID format resolution
  algorithm and defaults, used in Generation Rules Step 0

**Read project configuration if available:**

- `${CLAUDE_PROJECT_DIR}/.sdd-config.json` - provides `id_conventions`, used in Generation Rules Step 0

## Input

$ARGUMENTS

| Argument            | Required | Description                                         |
|:--------------------|:---------|:----------------------------------------------------|
| `requirements-text` | Yes      | Requirements analysis text OR feature name          |
| `--ci`              | -        | CI/non-interactive mode. Skips clarifying questions |

### Input Examples

**Feature name reference:** `/generate-requirements-diagram task-management`

**CI mode (called by generate-prd):** `/generate-requirements-diagram task-management --ci`

When a feature name is provided, look for:

- `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md` - Existing PRD with requirements

## Generation Rules

### 0. Resolve ID Conventions

Determine the ID format for UR/FR/NFR before reading the input, per
`${CLAUDE_PLUGIN_ROOT}/shared/references/id_conventions_config.md` § PRD-Level ID Format Resolution
(default `UR_xxx`, `FR_xxx`, `NFR_xxx`). Match requirement entries in the input against the resolved
format instead of assuming one notation, and carry each requirement's own ID through to the diagram
unchanged — never renumber or reformat an ID that the PRD already assigned.

PRD-level IDs use underscores, which is also what Mermaid's `requirementDiagram` accepts (see Step 3
rule 1). If a project has configured a format whose IDs cannot be used as Mermaid node IDs, report that
instead of silently rewriting the IDs.

### 1. Input Parsing

> **CI Mode**: Skip clarifying questions. Make reasonable assumptions for ambiguous items.

Extract requirements information:

| Item                            | Source                            |
|:--------------------------------|:----------------------------------|
| **User Requirements**           | UR entries from tables            |
| **Functional Requirements**     | FR entries with traceability      |
| **Non-Functional Requirements** | NFR entries                       |
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

1. **ID naming**: Mermaid node IDs use underscores, NOT hyphens (the PRD-level format resolved in Step 0
   already satisfies this — this rule is about Mermaid syntax, not about renaming a PRD's IDs)
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

**IMPORTANT**: This skill returns text only. It does NOT write files.

This holds even when the target document is missing the diagram section entirely (removed, or it never
had one): do not "helpfully" fill the gap by editing the document yourself with `Write` or `Edit` — those
tools are in `disallowed-tools` for exactly this reason. Return the diagram as text regardless, and leave
the decision of whether and where to write it to the caller.

Return a markdown structure with a `## Requirements Diagram (SysML)` section (containing the Mermaid
`requirementDiagram`), a `## Diagram Structure` section, and a `## Relationship Summary` table. See
`references/output_example.md` for a complete worked example.

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

**When completeness and readability conflict** (e.g. a requirement has many sub-requirements that would
push a diagram past the 10-15 guideline): completeness wins. Prefer splitting into a per-subsystem
diagram first. When splitting is not applicable (the sub-requirements are all branches of one requirement,
not a separate subsystem), it is acceptable to represent them as a single compressed node with a note —
but the output must say explicitly which sub-requirements were compressed and why, so the caller can tell
"omitted" from "combined."

### Integration

- This skill is typically called by `/generate-prd --ci` with `--ci` flag
- Output is text only; the caller is responsible for file operations
- When called standalone (Interactive mode), suggest next step: `/finalize-prd`
- In CI mode, output is optimized for pipeline consumption
