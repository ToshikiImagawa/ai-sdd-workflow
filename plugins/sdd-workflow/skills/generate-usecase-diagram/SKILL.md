---
name: generate-usecase-diagram
description: "Generate use case diagram in Mermaid format from business requirements. Use when user needs to visualize actors, use cases, and system boundaries for a feature or when PRD diagrams are requested."
version: 3.0.1
license: MIT
user-invocable: true
context: fork
agent: sonnet
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Generate Use Case Diagram

Generates a use case diagram in Mermaid flowchart format from business requirements or feature name.

## Prerequisites

**Read the following reference guides before generation:**

- `references/usecase_diagram_guide.md` - Use case diagram notation and examples
- `references/mermaid_notation_rules.md` - Mermaid flowchart syntax and styling

## Input

$ARGUMENTS

| Argument                   | Required | Description                                |
|:---------------------------|:---------|:-------------------------------------------|
| `requirements-description` | Yes      | Business requirements text OR feature name |

**When feature name is provided**, look for existing PRD at `.sdd/requirement/{feature-name}.md`.

## Generation Flow

1. **Analyze Input**: Extract actors, use cases, and relationships
2. **Read References**: Load diagram guides for correct syntax
3. **Generate Diagram**: Create a Mermaid flowchart with proper styling
4. **Return Text**: Output diagram and documentation (no file write)

## Output Format

Use the `templates/${SDD_LANG:-en}/usecase_output.md` template for output formatting.

**Read the output template before returning results.**

## Quality Checks

Before returning, verify:

- [ ] All actors from requirements are represented
- [ ] All major functions are captured as use cases
- [ ] System boundary defined
- [ ] Mermaid syntax is valid
- [ ] Consistent styling applied

## Notes

- Use consistent granularity within the diagram
- Actors represent roles, not specific users
- Include = always executed, Extend = optional behavior
