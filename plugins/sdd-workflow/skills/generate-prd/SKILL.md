---
name: generate-prd
description: "Generates PRD by orchestrating sub-skills for use case diagrams, requirements analysis, and SysML diagrams. Use when user mentions PRD, product requirements, feature definition, requirement specification, or starting AI-SDD workflow."
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
- [ ] 3. /generate-usecase-diagram
- [ ] 4. /analyze-requirements
- [ ] 5. /generate-requirements-diagram
- [ ] 6. /finalize-prd
- [ ] 7. Validate (Quality Checks)
- [ ] 8. Save PRD file
- [ ] 9. prd-reviewer (Interactive only)
```

## Generation Flow

### Common Steps

1. **Analyze input** → Extract feature-name
2. **Check existing documents** → Confirm overwriting if it exists
3. **Execute sub-skills** (all run in `context: fork`):
    
    | Step | Skill                            | Input           | Output            |
    |:-----|:---------------------------------|:----------------|:------------------|
    | 3a   | `/generate-usecase-diagram`      | requirements    | Use case diagram  |
    | 3b   | `/analyze-requirements`          | usecase-output  | UR/FR/NFR tables  |
    | 3c   | `/generate-requirements-diagram` | analysis-output | SysML diagram     |
    | 3d   | `/finalize-prd`                  | all outputs     | Complete PRD text |

4. **Validate** → Quality Checks
5. **Save** → `${SDD_REQUIREMENT_PATH}/{feature-name}.md`

### Mode Differences

| Step             | Interactive       | CI (`--ci`)  |
|:-----------------|:------------------|:-------------|
| Vibe Coding risk | Confirm with user | Skip         |
| Existing PRD     | Confirm overwrite | Auto-approve |
| Sub-skill flags  | None              | `--ci`       |
| prd-reviewer     | Run               | Skip         |

**Sub-skill execution:**

- Interactive: `Skill: /generate-usecase-diagram {requirements}`
- CI: `Skill: /generate-usecase-diagram {requirements} --ci`

## Output

**This skill writes files (sub-skills return text only).**

Save location:

- `${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- Hierarchical: `${SDD_REQUIREMENT_PATH}/{parent}/{feature-name}.md`

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
2. Apply approved fixes
3. Include results in output

If CONSTITUTION.md missing: Skip check, recommend `/sdd-init`.

## Consistency Check

If existing spec/design exists:

| Check                | Action                       |
|:---------------------|:-----------------------------|
| New requirements     | Verify reflected in spec     |
| Changed requirements | Verify spec/design updated   |
| ID changes           | Verify spec references match |

If updates needed, recommend `/generate-spec`.
