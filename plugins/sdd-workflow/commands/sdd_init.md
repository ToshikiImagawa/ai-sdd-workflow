---
name: sdd_init
description: "Initialize AI-SDD workflow in the current project. Sets up CLAUDE.md and generates document templates."
---

# SDD Init - AI-SDD Workflow Initializer

Initializes the AI-SDD (AI-driven Specification-Driven Development) workflow in the current project.

## What This Command Does

1. **CLAUDE.md Configuration**: Adds AI-SDD instructions to the project's `CLAUDE.md` file
2. **Template Generation**: Creates document templates in `.docs/` directory (if not exist)

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for project initialization.

### Skills Used

This command uses the following skills:

| Skill                        | Purpose                                                                        |
|:-----------------------------|:-------------------------------------------------------------------------------|
| `sdd-workflow:sdd-templates` | Generate PRD, Specification, and Design Doc templates based on project context |

## Execution Flow

```
1. Check current project state
   ├─ Does CLAUDE.md exist?
   └─ Does .docs/ directory exist?
   ↓
2. Configure CLAUDE.md
   ├─ If CLAUDE.md exists: Add AI-SDD Instructions section
   └─ If not exists: Create new CLAUDE.md with AI-SDD Instructions
   ↓
3. Create .docs/ directory structure
   ├─ .docs/requirement-diagram/
   └─ .docs/specification/
   ↓
4. Check for existing templates
   ├─ .docs/PRD_TEMPLATE.md
   ├─ .docs/SPECIFICATION_TEMPLATE.md
   └─ .docs/DESIGN_DOC_TEMPLATE.md
   ↓
5. Generate missing templates
   └─ Use sdd-workflow:sdd-templates skill to generate
   ↓
6. Commit changes
```

## CLAUDE.md Configuration

### AI-SDD Instructions Section

Add the following section to `CLAUDE.md`:

```markdown
## AI-SDD Instructions

This project follows the AI-SDD (AI-driven Specification-Driven Development) workflow.

### Document Operations

When working with files under `.docs/` directory, you MUST use the `sdd-workflow:sdd-workflow` agent to ensure proper AI-SDD workflow compliance.

**Trigger Conditions**:
- Reading or modifying any file under `.docs/`
- Creating new specifications, designs, or requirements documents
- Implementing features that reference documents in `.docs/`

### Directory Structure

```

.docs/
├── PRD_TEMPLATE.md # PRD template for this project
├── SPECIFICATION_TEMPLATE.md # Abstract specification template
├── DESIGN_DOC_TEMPLATE.md # Technical design document template
├── requirement-diagram/ # PRD (Requirements Specification)
│ └── {feature-name}.md
└── specification/ # Specifications and Design Documents
├── {feature-name}_spec.md # Abstract specification
└── {feature-name}_design.md # Technical design document

```

### Commit Message Convention

| Prefix | Usage |
|:---|:---|
| `[docs]` | Add/update documentation |
| `[spec]` | Add/update specifications (`*_spec.md`) |
| `[design]` | Add/update design documents (`*_design.md`) |
```

### Placement Rules

1. **If CLAUDE.md already has an "AI-SDD" section**: Skip (already initialized)
2. **If CLAUDE.md exists without AI-SDD section**: Append the section at the end
3. **If CLAUDE.md does not exist**: Create new file with the section

## Template Generation

### Template Files to Generate

| Template                   | Path                              | Purpose                                    |
|:---------------------------|:----------------------------------|:-------------------------------------------|
| **PRD Template**           | `.docs/PRD_TEMPLATE.md`           | Requirements specification in SysML format |
| **Specification Template** | `.docs/SPECIFICATION_TEMPLATE.md` | Abstract system specification              |
| **Design Doc Template**    | `.docs/DESIGN_DOC_TEMPLATE.md`    | Technical design document                  |

### Generation Process

1. **Check existing templates**: Skip if template already exists
2. **Analyze project context**:
    - Detect programming language(s) used
    - Identify project structure and conventions
    - Check for existing documentation patterns
3. **Generate customized templates**:
    - Use `sdd-workflow:sdd-templates` skill
    - Customize type syntax for project's language (TypeScript, Python, Go, etc.)
    - Adjust examples to match project domain

### Template Customization Points

When generating templates, customize based on project analysis:

| Aspect              | Customization                                                                     |
|:--------------------|:----------------------------------------------------------------------------------|
| **Type Syntax**     | Match project's primary language (e.g., TypeScript interfaces, Python type hints) |
| **Directory Paths** | Reflect project's actual structure in examples                                    |
| **Domain Examples** | Use relevant examples based on project type (web app, CLI, library, etc.)         |

## Post-Initialization Verification

After initialization, verify:

1. **CLAUDE.md**: Contains AI-SDD Instructions section
2. **Directory Structure**:
    - `.docs/requirement-diagram/` exists
    - `.docs/specification/` exists
3. **Templates**: All three template files exist in `.docs/`

## Output

Upon successful initialization, display:

```markdown
## AI-SDD Initialization Complete

### CLAUDE.md
- [x] AI-SDD Instructions section added

### Directory Structure
- [x] .docs/requirement-diagram/ created
- [x] .docs/specification/ created

### Templates Generated
- [x] .docs/PRD_TEMPLATE.md
- [x] .docs/SPECIFICATION_TEMPLATE.md
- [x] .docs/DESIGN_DOC_TEMPLATE.md

### Next Steps

1. Review generated templates and customize as needed
2. Use `/generate_prd` to create your first PRD
3. Use `/generate_spec` to create specifications from PRD
4. Use the `sdd-workflow` agent for development guidance
```

## Commit

After successful initialization:

```
[docs] Initialize AI-SDD workflow

- Add AI-SDD Instructions to CLAUDE.md
- Create .docs/ directory structure
- Generate document templates
```
