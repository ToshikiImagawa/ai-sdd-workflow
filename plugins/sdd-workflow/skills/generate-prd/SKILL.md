---
name: generate-prd
description: "Generates PRD by orchestrating sub-skills for use case diagrams, requirements analysis, and SysML diagrams. Use when user mentions PRD, product requirements, feature definition, requirement specification, or starting AI-SDD workflow."
argument-hint: "<requirements-description>"
version: 3.0.1
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash, Skill
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
- [ ] 1. Analyze input, extract feature-name
- [ ] 2. Check existing documents
- [ ] 3. Execute /generate-usecase-diagram → save as usecase_output
- [ ] 4. Execute /analyze-requirements with usecase_output → save as analysis_output
- [ ] 5. Execute /generate-requirements-diagram with analysis_output → save as diagram_output
- [ ] 6. Execute /finalize-prd with all outputs → save as complete_prd_text
- [ ] 7. Validate (Quality Checks)
- [ ] 8. Save complete_prd_text to file using Write tool
- [ ] 9. prd-reviewer (Interactive only)
- [ ] 10. front-matter-reviewer (Interactive only)
```

## Generation Flow

### Common Steps

**You MUST execute all of the following steps in order:**

1. **Analyze input** → Extract feature-name from requirements
2. **Check existing documents** → Confirm overwriting if PRD exists at `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
3. **Execute sub-skills sequentially** (do NOT stop after the first sub-skill):

    - **3a: `/generate-usecase-diagram`** → Input: requirements → Output: usecase_output (Use case diagram)
    - **3b: `/analyze-requirements`** → Input: usecase_output → Output: analysis_output (UR/FR/NFR tables)
    - **3c: `/generate-requirements-diagram`** → Input: analysis_output → Output: diagram_output (SysML diagram)
    - **3d: `/finalize-prd`** → Input: all outputs (usecase_output, analysis_output, diagram_output) → Output: complete_prd_text (Complete PRD document)

4. **Validate** → Run Quality Checks on complete_prd_text
5. **Save PRD file** → **REQUIRED**: Use the `Write` tool to save complete_prd_text to `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`

**CRITICAL**: Steps 3a-3d-5 are mandatory. The PRD file MUST be saved to disk using the Write tool.

### Mode Differences

| Step             | Interactive       | CI (`--ci`)  |
|:-----------------|:------------------|:-------------|
| Vibe Coding risk | Confirm with user | Skip         |
| Existing PRD     | Confirm overwrite | Auto-approve |
| Sub-skill flags  | None              | `--ci`       |
| **Save PRD**     | **Save**          | **Save**     |
| prd-reviewer     | Run               | Skip         |

**Sub-skill execution:**

Execute the following sub-skills **sequentially** in order. Each skill must complete before proceeding to the next:

1. **Step 3a: Generate Use Case Diagram**
   - Interactive: Execute `Skill` tool with `/generate-usecase-diagram {requirements}`
   - CI: Execute `Skill` tool with `/generate-usecase-diagram {requirements} --ci`
   - Save the output as `usecase_output`

2. **Step 3b: Analyze Requirements**
   - Interactive: Execute `Skill` tool with `/analyze-requirements {usecase_output}`
   - CI: Execute `Skill` tool with `/analyze-requirements {usecase_output} --ci`
   - Save the output as `analysis_output`

3. **Step 3c: Generate Requirements Diagram**
   - Interactive: Execute `Skill` tool with `/generate-requirements-diagram {analysis_output}`
   - CI: Execute `Skill` tool with `/generate-requirements-diagram {analysis_output} --ci`
   - Save the output as `diagram_output`

4. **Step 3d: Finalize PRD**
   - Interactive: Execute `Skill` tool with `/finalize-prd {usecase_output} {analysis_output} {diagram_output}`
   - CI: Execute `Skill` tool with `/finalize-prd {usecase_output} {analysis_output} {diagram_output} --ci`
   - Save the output as `complete_prd_text`

5. **Save PRD File** (See Post-Generation Actions section below)
   - Use the `Write` tool to save `complete_prd_text` to `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`

**IMPORTANT**: You MUST execute all 4 sub-skills (3a → 3b → 3c → 3d) and save the final PRD file. Do not stop after step 3a.

## Post-Generation Actions

### 1. Save PRD File (MANDATORY)

**CRITICAL**: The `/finalize-prd` sub-skill returns text only. This skill **MUST** save the output to a file using the `Write` tool. Do NOT skip this step.

**Required action**: Use the `Write` tool to save `complete_prd_text` (output from `/finalize-prd`) to:

- **Flat structure**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- **Hierarchical (parent)**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent}/index.md`
- **Hierarchical (child)**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent}/{feature-name}.md`

**Verification**: After saving, confirm the file exists at the expected path.

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

- [ ] Feature-name correctly extracted
- [ ] PRD follows the template structure
- [ ] All `<MUST>` sections have content
- [ ] Requirement IDs unique (UR-xxx, FR-xxx, NFR-xxx)
- [ ] Language consistent (matches template)
- [ ] Diagrams properly formatted

## Principle Compliance (Interactive Only)

> **CI Mode**: Skip this section.

After PRD generation:

1. Call prd-reviewer agent
2. Call front-matter-reviewer agent (pass PRD file path)
3. Apply approved fixes from both reviews
4. Include results in output

If CONSTITUTION.md missing: Skip check, recommend `/sdd-init`.

