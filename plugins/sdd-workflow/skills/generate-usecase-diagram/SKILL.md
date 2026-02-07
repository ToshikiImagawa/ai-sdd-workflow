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

**When feature name is provided**, look for existing PRD at `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`.

### Input Examples

**Feature name (looks up PRD):**

```
/generate-usecase-diagram user-authentication
```

**Requirements description:**

```
/generate-usecase-diagram Users can register, login, and reset passwords. Admin can manage user accounts.
```

## Generation Flow

1. **Analyze Input**: Extract actors, use cases, and relationships
2. **Read References**: Load diagram guides for correct syntax
3. **Generate Diagram**: Create Mermaid flowchart with proper styling
4. **Validate**: Check Quality Checks items
    - If issues found: Fix and repeat from step 3
5. **Return Text**: Output diagram and documentation (no file write)

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

### Diagram Design

- Use consistent granularity within the diagram
- Keep diagram readable by limiting to 7-10 use cases per diagram
- For large systems, create separate diagrams per subsystem or feature group
- Actors represent roles (e.g., "Admin", "Guest"), not specific users

### Relationships

- **Include**: Always executed as part of the base use case (mandatory)
- **Extend**: Optional behavior that may or may not occur
- Avoid deep nesting of include/extend relationships (max 2 levels)

### Naming Conventions

- Use verb phrases for use cases (e.g., "Login", "Register Account")
- Use noun phrases for actors (e.g., "User", "System Administrator")
- Keep names concise but descriptive

### Integration

- This skill is typically called by `/generate-prd` in CI mode
- Output is text only; the caller is responsible for file operations
- When called standalone, suggest next step: `/analyze-requirements`
