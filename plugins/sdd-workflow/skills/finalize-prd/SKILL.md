---
name: finalize-prd
description: "Finalize and integrate PRD from all artifacts. Use when combining use case diagrams, requirements analysis, and requirements diagrams into a complete PRD, or when called by generate-prd."
version: 3.0.1
license: MIT
user-invocable: true
context: fork
agent: sonnet
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Finalize PRD

Integrates all generated artifacts (use case diagram, requirements analysis, requirements diagram) into a complete PRD
document.

## Purpose

This skill combines:

- Use case diagrams
- Requirements analysis (UR/FR/NFR tables)
- SysML requirements diagrams

Into a cohesive PRD document following the PRD template structure.

## Hybrid Approach

This skill operates in two modes:

| Mode                      | Behavior | Description                                                  |
|:--------------------------|:---------|:-------------------------------------------------------------|
| **Interactive** (default) | Guide    | May ask clarifying questions, provides detailed output       |
| **CI (`--ci`)**           | Silent   | No user interaction, concise output for pipeline integration |

## Prerequisites

**Read the following prerequisite references before execution:**

| File                                                    | Purpose                                  |
|:--------------------------------------------------------|:-----------------------------------------|
| `../shared/references/prerequisites_directory_paths.md` | Resolve `${SDD_*}` environment variables |

**Load PRD template** (in order):

1. `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` — Project-specific template
2. `templates/${SDD_LANG:-en}/prd_template.md` — Fallback default

**Load if exists:**

- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` — For principle compliance

## Input

$ARGUMENTS

| Argument        | Required | Description                                                    |
|:----------------|:---------|:---------------------------------------------------------------|
| `feature-name`  | Yes      | Feature name for the PRD                                       |
| `usecase-text`  | Yes      | Use case diagram output from generate-usecase-diagram          |
| `analysis-text` | Yes      | Requirements analysis output from analyze-requirements         |
| `diagram-text`  | Yes      | Requirements diagram output from generate-requirements-diagram |
| `--ci`          | -        | CI/non-interactive mode. Skips clarifying questions            |

### Input Format

The skill receives structured text blocks from previous skills:

```
/finalize-prd task-management

## Use Case Diagram
{usecase diagram from generate-usecase-diagram}

## Requirements Analysis
{analysis from analyze-requirements}

## Requirements Diagram
{diagram from generate-requirements-diagram}
```

## Integration Rules

### 1. Template Loading

> **CI Mode**: Skip clarifying questions. Make reasonable assumptions for ambiguous items.

Load the PRD template in this order:

1. `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` (if exists)
2. `templates/${SDD_LANG:-en}/prd_template.md` (fallback)

### 2. Content Integration

Map input artifacts to template sections:

| Input                | Template Section               | Notes                               |
|:---------------------|:-------------------------------|:------------------------------------|
| Use case diagram     | 2.1-2.2 Use Case Diagram       | Overview and detailed sections      |
| Actors table         | (included in use case section) | Merge into diagram section          |
| Use Cases table      | 2.3 Function List              | Convert to text format              |
| UR table             | 4.x Detailed Requirements      | User requirements section           |
| FR table             | 4.1 Functional Requirements    | Expand to detailed descriptions     |
| NFR table            | 4.2-4.4 Non-Functional         | Performance, interface, constraints |
| Requirements diagram | 3.1 Requirements Diagram       | Overall SysML diagram               |
| Relationships        | (within diagram)               | Contains, derives, traces           |

### 3. Section Markers

Preserve template section markers:

| Marker          | Meaning     | Handling                  |
|:----------------|:------------|:--------------------------|
| `<MUST>`        | Required    | Must include content      |
| `<RECOMMENDED>` | Recommended | Include if data available |
| `<OPTIONAL>`    | Optional    | Include if relevant       |

### 4. Language Consistency

**CRITICAL: Match template language**

- If template is English, entire PRD must be in English
- If template is Japanese, entire PRD must be in Japanese
- Do NOT mix languages

### 5. ID Consistency

Ensure requirement IDs are consistent:

| ID Format | Type                       | Example |
|:----------|:---------------------------|:--------|
| `UR-xxx`  | User Requirement           | UR-001  |
| `FR-xxx`  | Functional Requirement     | FR-001  |
| `NFR-xxx` | Non-Functional Requirement | NFR-001 |
| `PR-xxx`  | Performance Requirement    | PR-001  |
| `IR-xxx`  | Interface Requirement      | IR-001  |
| `DC-xxx`  | Design Constraint          | DC-001  |

### 6. Validate

Check Quality Checks items before returning output.

- If issues found: Fix and repeat from step 2

## Output

**IMPORTANT: This skill returns TEXT only. It does NOT write files.**

The output is a complete PRD document text that:

1. Follows the PRD template structure
2. Integrates all input artifacts
3. Maintains consistent formatting
4. Preserves traceability between requirements
5. Uses consistent language throughout

The caller (generate-prd) is responsible for:

- Saving the output to `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- Running prd-reviewer for compliance check

## Quality Checks

Before returning output, verify:

- [ ] All `<MUST>` sections have content
- [ ] Use case diagram is properly formatted
- [ ] Requirements diagram is properly formatted
- [ ] All requirement IDs are unique
- [ ] Traceability is maintained (FR → UR)
- [ ] Language is consistent throughout
- [ ] Template structure is preserved

## Notes

### PRD Finalization

- Remove `<MUST>`, `<RECOMMENDED>`, `<OPTIONAL>` markers from final output
- Add glossary entries for any domain-specific terms
- Include out of scope section even if empty (prevents scope creep)
- Ensure all requirements have verification methods specified

### Integration

- This skill is typically called by `/generate-prd --ci` with `--ci` flag
- Output is text only; the caller is responsible for file operations
- Receives output from all previous skills in the workflow
- In CI mode, output is optimized for pipeline consumption
