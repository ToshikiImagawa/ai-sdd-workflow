---
name: generate-prd
description: "Generates complete PRD document from business requirements. Creates use case diagrams, requirements analysis (UR/FR/NFR), SysML diagrams, and complete PRD file. Use when user mentions PRD, product requirements, feature definition, requirement specification, or starting AI-SDD workflow."
argument-hint: "<requirements-description> [--ci]"
version: 3.1.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
---

# Generate PRD

Generates PRD from business requirements by orchestrating sub-skills.

## Prerequisites

**Read before execution:**

| File                                          | Purpose                                  |
|:----------------------------------------------|:-----------------------------------------|
| `references/prerequisites_directory_paths.md` | Resolve `${SDD_*}` environment variables |
| `references/prerequisites_principles.md`      | Load AI-SDD principles                   |
| `references/prerequisites_plugin_update.md`   | Check plugin version compatibility       |

**Load PRD template** (in order):

1. `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` — Project-specific template
2. `templates/${SDD_LANG:-en}/prd_template.md` — Fallback default

**Load if exists:**

- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` — For principle compliance check

## Input

$ARGUMENTS

| Argument       | Required | Description                               |
|:---------------|:---------|:------------------------------------------|
| `requirements` | Yes      | Business requirements text                |
| `--ci`         | No       | CI mode: no questions, skips prd-reviewer |

**Examples:**

```
/generate-prd A feature for users to manage tasks. Supports creation, editing, deletion.
/generate-prd A feature for users to manage tasks. --ci
```

## Progress Checklist

Copy to track progress:

```
PRD Generation:
- [ ] 1. Read prerequisites and templates
- [ ] 2. Analyze input, extract feature-name
- [ ] 3. Check existing PRD documents (confirm overwrite if needed)
- [ ] 4. Generate Use Case Diagram (Mermaid flowchart)
- [ ] 5. Analyze Requirements (extract UR/FR/NFR tables)
- [ ] 6. Generate Requirements Diagram (SysML diagram)
- [ ] 7. Integrate all sections into complete PRD
- [ ] 8. Add YAML front matter
- [ ] 9. Validate (Quality Checks)
- [ ] 10. Save PRD file using Write tool
- [ ] 11. prd-reviewer (Interactive only)
- [ ] 12. front-matter-reviewer (Interactive only)
```

## Generation Flow

**You MUST execute all of the following steps in order to generate a complete PRD file:**

### Step 1: Prerequisites

**Phase 1: Python Script** - Execute `prepare-prd.py` to pre-load templates and references:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/generate-prd/scripts/prepare-prd.py"
```

This script:
1. Checks `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` (project template) first
2. If not found, copies from `templates/${SDD_LANG}/` to cache
3. Copies all reference files to cache
4. Exports environment variables to `$CLAUDE_ENV_FILE`:
   - `GENERATE_PRD_TEMPLATE` - Path to cached PRD template
   - `GENERATE_PRD_REFERENCES` - Path to cached references
   - `GENERATE_PRD_CACHE_DIR` - Path to cache directory

**Phase 2: Read from Cache** - Use environment variables to access pre-loaded files:

Read the following files from `$GENERATE_PRD_REFERENCES`:

| File                                  | Purpose                                  |
|:--------------------------------------|:-----------------------------------------|
| `prerequisites_directory_paths.md`    | Resolve `${SDD_*}` environment variables |
| `prerequisites_principles.md`         | Load AI-SDD principles                   |
| `prerequisites_plugin_update.md`      | Check plugin version compatibility       |
| `../../../shared/references/usecase_diagram_guide.md` | Use case diagram notation |
| `../../../shared/references/mermaid_notation_rules.md` | Mermaid syntax rules |
| `../../../shared/references/requirements_diagram_components.md` | SysML requirements diagram components |
| `../../../shared/references/front_matter_prd.md` | PRD front matter schema |

**Load PRD template** from `$GENERATE_PRD_TEMPLATE`

**Load if exists:**

- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` — For principle compliance check

### Step 2: Analyze Input

Extract the following from requirements description:

- **Feature name**: Identifier used for filename (e.g., "task-management", "user-authentication")
- **Actors**: Users, roles, or external systems interacting with the feature
- **Use cases**: Main functions users want to perform
- **Business context**: Why this feature is needed

> **CI Mode**: Skip Vibe Coding risk assessment. Make reasonable assumptions for ambiguous requirements.
> **Interactive Mode**: If requirements are vague, ask clarifying questions using AskUserQuestion.

### Step 3: Check Existing PRD

Check if PRD already exists at `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`

| Mode        | If PRD exists           | Action                       |
|:------------|:------------------------|:-----------------------------|
| Interactive | Ask user                | Confirm overwrite            |
| CI (`--ci`) | Auto-approve            | Proceed with overwrite       |

### Step 4: Generate Use Case Diagram

Generate a Mermaid flowchart representing actors, use cases, and system boundaries.

**Requirements:**
- Use `flowchart LR` format
- Apply dark theme: `%%{init: {'theme': 'dark'}}%%`
- Define actors with `((Actor))` notation
- Define use cases within `subgraph` (system boundary)
- Use consistent styling (see mermaid_notation_rules.md)

**Output sections:**
- Use Case Diagram (Mermaid code block)
- Actors table
- Use Cases table

### Step 5: Analyze Requirements

Extract structured requirements from the use case diagram and business context.

**Generate three requirement tables:**

1. **User Requirements (UR)**: High-level goals from user perspective
   - ID format: `UR-xxx`
   - Include: ID, Requirement, Priority, Risk

2. **Functional Requirements (FR)**: Specific functions to fulfill user requirements
   - ID format: `FR-xxx`
   - Include: ID, Requirement, Derived From (UR-xxx), Priority, Risk, Verification

3. **Non-Functional Requirements (NFR)**: Quality attributes
   - ID format: `NFR-xxx`
   - Include: ID, Requirement, Category, Priority, Risk, Verification

**Requirements Summary table:**
- Count by category (UR/FR/NFR)
- Count by priority (Must/Should/Could)

### Step 6: Generate Requirements Diagram

Generate a SysML requirements diagram in Mermaid `requirementDiagram` format.

**Critical syntax rules:**
- Use underscores in IDs, NOT hyphens (e.g., `UR_001`, not `UR-001`)
- Quote all text values (e.g., `text: "User can create tasks"`)
- Use lowercase for attributes (e.g., `risk: high`, not `risk: High`)
- Use correct requirement types: `requirement`, `functionalRequirement`, `performanceRequirement`
- Use correct relationships: `contains`, `derives`, `traces`

### Step 7: Integrate Into Complete PRD

Combine all generated sections following the PRD template structure:

| Generated Section          | Template Section               |
|:---------------------------|:-------------------------------|
| Use Case Diagram           | 2.1-2.2 Use Case Diagram       |
| Actors/Use Cases tables    | 2.3 Function List              |
| UR table                   | 4.x Detailed Requirements      |
| FR table                   | 4.1 Functional Requirements    |
| NFR table                  | 4.2-4.4 Non-Functional         |
| Requirements Diagram       | 3.1 Requirements Diagram       |

**Language consistency:**
- Match the PRD template language (English or Japanese)
- Do NOT mix languages

### Step 8: Add YAML Front Matter

Generate YAML front matter following `references/front_matter_prd.md` schema:

```yaml
---
id: "prd-{feature-name}"
title: "{Feature Title}"
type: "prd"
status: "draft"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
depends-on: []  # Parent PRD if hierarchical
priority: "medium"  # or extract from requirements
risk: "medium"  # or extract from requirements
tags: ["{tag1}", "{tag2}"]
category: "{category}"
---
```

### Step 9: Validate

Check Quality Checks items before saving.

### Step 10: Save PRD File

**MANDATORY**: Use the `Write` tool to save the complete PRD to:

- **Flat structure**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- **Hierarchical (parent)**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent}/index.md`
- **Hierarchical (child)**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent}/{feature-name}.md`

After saving, confirm the file exists at the expected path.

### Mode Differences

| Step                 | Interactive       | CI (`--ci`)  |
|:---------------------|:------------------|:-------------|
| Vibe Coding risk     | Confirm with user | Skip         |
| Existing PRD         | Confirm overwrite | Auto-approve |
| Clarifying questions | Ask if needed     | Skip         |
| **Save PRD file**    | **Save**          | **Save**     |
| prd-reviewer         | Run               | Skip         |
| front-matter-reviewer| Run               | Skip         |

## Post-Generation Actions

### 1. Principle Compliance (Interactive Only)

> **CI Mode**: Skip this section.

After PRD generation:

1. Call prd-reviewer agent to check compliance with CONSTITUTION.md
2. Call front-matter-reviewer agent (pass PRD file path)
3. Apply approved fixes from both reviews
4. Include results in output

If CONSTITUTION.md missing: Skip check, recommend `/sdd-init`.

### 2. Consistency Check

If existing spec/design exists:

| Check                | Action                       |
|:---------------------|:-----------------------------|
| New requirements     | Verify reflected in spec     |
| Changed requirements | Verify spec/design updated   |
| ID changes           | Verify spec references match |

If updates needed, recommend `/generate-spec`.

## Output

Use `templates/${SDD_LANG:-en}/prd_output.md` for output formatting.

## Quality Checks

Before saving the PRD file, verify:

- [ ] Feature-name correctly extracted from requirements
- [ ] YAML front matter is valid and complete
- [ ] PRD follows the template structure
- [ ] All `<MUST>` sections have content
- [ ] Use case diagram is valid Mermaid flowchart
- [ ] Requirements diagram is valid Mermaid requirementDiagram
- [ ] Requirement IDs are unique (UR-xxx, FR-xxx, NFR-xxx)
- [ ] All FRs trace to at least one UR
- [ ] Priority and risk values are valid
- [ ] Verification methods are specified for all requirements
- [ ] Language is consistent throughout (matches template)
- [ ] No `<MUST>`, `<RECOMMENDED>`, `<OPTIONAL>` markers in final output

## Principle Compliance (Interactive Only)

> **CI Mode**: Skip this section.

After PRD generation:

1. Call prd-reviewer agent
2. Call front-matter-reviewer agent (pass PRD file path)
3. Apply approved fixes from both reviews
4. Include results in output

If CONSTITUTION.md missing: Skip check, recommend `/sdd-init`.

