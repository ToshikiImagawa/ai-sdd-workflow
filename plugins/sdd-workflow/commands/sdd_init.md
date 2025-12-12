---
description: "Initialize AI-SDD workflow in the current project. Sets up CLAUDE.md and generates document templates."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# SDD Init - AI-SDD Workflow Initializer

Initialize AI-SDD (AI-driven Specification-Driven Development) workflow in the current project.

## What This Command Does

1. **CLAUDE.md Configuration**: Add AI-SDD instructions to project's `CLAUDE.md`
2. **Project Constitution Generation**: Create `.sdd/CONSTITUTION.md` (if not exist)
3. **Template Generation**: Create document templates in `.sdd/` directory (if not exist)

## Prerequisites

**Before execution, you must read the `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command initializes the project following the sdd-workflow agent's principles.

### Configuration File (Optional)

You can customize directory names by creating `.sdd-config.json` at project root.

For configuration file details, refer to the "Project Configuration File" section in the `sdd-workflow:sdd-workflow` agent.

**Note**: If you want to use custom directory names during initialization, create `.sdd-config.json` first. The directory structure and CLAUDE.md content will be generated based on configuration values.

### Skills Used

This command uses the following skills:

| Skill                        | Purpose                                                                        |
|:-----------------------------|:-------------------------------------------------------------------------------|
| `sdd-workflow:sdd-templates` | Generate PRD, Specification, and Design Doc templates based on project context |

## Execution Flow

```
1. Check current project state
   ├─ Does CLAUDE.md exist?
   ├─ Does .sdd/ directory exist?
   └─ Does .sdd/CONSTITUTION.md exist?
   ↓
2. Configure CLAUDE.md
   ├─ If CLAUDE.md exists: Add AI-SDD Instructions section
   └─ If not exists: Create new CLAUDE.md with AI-SDD Instructions
   ↓
3. Create .sdd/ directory structure
   ├─ .sdd/requirement/
   ├─ .sdd/specification/
   └─ .sdd/task/
   ↓
4. Generate project constitution (if not exist)
   ├─ Check if .sdd/CONSTITUTION.md exists
   └─ If not exist: Generate using sdd-workflow:sdd-templates skill
   ↓
5. Check existing templates
   ├─ .sdd/PRD_TEMPLATE.md
   ├─ .sdd/SPECIFICATION_TEMPLATE.md
   └─ .sdd/DESIGN_DOC_TEMPLATE.md
   ↓
6. Generate missing templates
   └─ Use sdd-workflow:sdd-templates skill
   ↓
7. Commit changes
```

## CLAUDE.md Configuration

### AI-SDD Instructions Section

Add the following section to `CLAUDE.md`:

````markdown
## AI-SDD Instructions

This project follows AI-SDD (AI-driven Specification-Driven Development) workflow.

### Document Operations

When operating files under `.sdd/` directory, always use the `sdd-workflow:sdd-workflow`
agent to ensure proper AI-SDD workflow compliance.

**Trigger Conditions**:

- Reading or modifying files under `.sdd/`
- Creating new specifications, design docs, or requirement docs
- Implementing features that reference `.sdd/` documents

### Directory Structure

Supports both flat and hierarchical structures.

**Flat Structure (for small to medium projects)**:

    .sdd/
    ├── CONSTITUTION.md               # Project principles (top-level)
    ├── PRD_TEMPLATE.md               # PRD template for this project
    ├── SPECIFICATION_TEMPLATE.md     # Abstract specification template
    ├── DESIGN_DOC_TEMPLATE.md        # Technical design template
    ├── requirement/                  # PRD (Product Requirements Documents)
    │   └── {feature-name}.md
    ├── specification/                # Specifications and designs
    │   ├── {feature-name}_spec.md    # Abstract specification
    │   └── {feature-name}_design.md  # Technical design
    └── task/                         # Temporary task logs
        └── {ticket-number}/

**Hierarchical Structure (for medium to large projects)**:

    .sdd/
    ├── CONSTITUTION.md               # Project principles (top-level)
    ├── PRD_TEMPLATE.md               # PRD template for this project
    ├── SPECIFICATION_TEMPLATE.md     # Abstract specification template
    ├── DESIGN_DOC_TEMPLATE.md        # Technical design template
    ├── requirement/                  # PRD (Product Requirements Documents)
    │   ├── {feature-name}.md         # Top-level feature
    │   └── {parent-feature}/         # Parent feature directory
    │       ├── index.md              # Parent feature overview & requirements list
    │       └── {child-feature}.md    # Child feature requirements
    ├── specification/                # Specifications and designs
    │   ├── {feature-name}_spec.md    # Top-level feature
    │   ├── {feature-name}_design.md
    │   └── {parent-feature}/         # Parent feature directory
    │       ├── index_spec.md         # Parent feature abstract spec
    │       ├── index_design.md       # Parent feature technical design
    │       ├── {child-feature}_spec.md   # Child feature abstract spec
    │       └── {child-feature}_design.md # Child feature technical design
    └── task/                         # Temporary task logs
        └── {ticket-number}/

### File Naming Convention (Important)

**⚠️ The presence of suffixes differs between requirement and specification. Do not confuse them.**

| Directory         | File Type        | Naming Pattern                                 | Example                                   |
|:------------------|:-----------------|:-----------------------------------------------|:------------------------------------------|
| **requirement**   | All files        | `{name}.md` (no suffix)                        | `user-login.md`, `index.md`               |
| **specification** | Abstract spec    | `{name}_spec.md` (`_spec` suffix required)     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | Technical design | `{name}_design.md` (`_design` suffix required) | `user-login_design.md`, `index_design.md` |

#### Naming Pattern Quick Reference

```
# ✅ Correct Naming
requirement/auth/index.md              # Parent feature overview (no suffix)
requirement/auth/user-login.md         # Child feature requirements (no suffix)
specification/auth/index_spec.md       # Parent feature abstract spec (_spec required)
specification/auth/index_design.md     # Parent feature technical design (_design required)
specification/auth/user-login_spec.md  # Child feature abstract spec (_spec required)
specification/auth/user-login_design.md # Child feature technical design (_design required)

# ❌ Incorrect Naming (never use these)
requirement/auth/index_spec.md         # requirement doesn't need _spec
specification/auth/user-login.md       # specification requires _spec/_design
specification/auth/index.md            # specification requires _spec/_design
```

### Document Link Convention

Follow these formats for markdown links within documents:

| Link Target    | Format                                     | Link Text             | Example                                              |
|:---------------|:-------------------------------------------|:----------------------|:-----------------------------------------------------|
| **File**       | `[filename.md](path or URL)`               | Include filename      | `[user-login.md](../requirement/auth/user-login.md)` |
| **Directory**  | `[directory-name](path or URL/index.md)`   | Directory name only   | `[auth](../requirement/auth/index.md)`               |

This convention makes it visually clear whether the link target is a file or directory.

````

### Placement Rules

1. **If CLAUDE.md already has "AI-SDD" section**: Skip (already initialized)
2. **If CLAUDE.md exists but no AI-SDD section**: Append section to end
3. **If CLAUDE.md doesn't exist**: Create new file with section

## Project Constitution Generation

### What is a Project Constitution?

A Project Constitution (CONSTITUTION.md) defines **non-negotiable principles that form the foundation of all design decisions**.

| Characteristic    | Description                                                      |
|:------------------|:-----------------------------------------------------------------|
| **Non-negotiable** | Not open to debate. Changes require careful consideration       |
| **Persistent**    | Consistently applied across the entire project                   |
| **Hierarchical**  | Higher principles take precedence over lower ones                |
| **Verifiable**    | Can automatically verify spec/design compliance with principles  |

### Generation Process

1. Check if `.sdd/CONSTITUTION.md` exists
2. If not exist, generate using `sdd-workflow:sdd-templates` skill
3. Customize based on project context (language, framework, domain)

### Constitution Management

Use `/constitution` command to manage the constitution after initialization:

| Subcommand   | Purpose                                      |
|:-------------|:---------------------------------------------|
| `validate`   | Verify specs/designs comply with constitution |
| `add`        | Add new principles                            |
| `sync`       | Synchronize templates with constitution       |

## Template Generation

### Templates to Generate

| Template                  | Path                             | Purpose                       |
|:--------------------------|:---------------------------------|:------------------------------|
| **Project Constitution**  | `.sdd/CONSTITUTION.md`           | Non-negotiable principles     |
| **PRD Template**          | `.sdd/PRD_TEMPLATE.md`           | SysML-format requirements doc |
| **Spec Template**         | `.sdd/SPECIFICATION_TEMPLATE.md` | Abstract system specification |
| **Design Template**       | `.sdd/DESIGN_DOC_TEMPLATE.md`    | Technical design document     |

### Generation Process

1. **Check Existing Templates**: Skip if template already exists
2. **Analyze Project Context**:
    - Detect programming languages used
    - Identify project structure and conventions
    - Review existing documentation patterns
3. **Generate Customized Templates**:
    - Use `sdd-workflow:sdd-templates` skill
    - Customize type syntax for project language (TypeScript, Python, Go, etc.)
    - Adjust examples based on project domain

### Template Customization Points

Customize during template generation based on project analysis:

| Item                | Customization Content                                                     |
|:--------------------|:--------------------------------------------------------------------------|
| **Type Syntax**     | Adapt to project's primary language (e.g., TypeScript interfaces, Python type hints) |
| **Directory Paths** | Reflect project's actual structure in examples                            |
| **Domain Examples** | Use relevant examples based on project type (web app, CLI, library, etc.) |

## Post-Initialization Verification

After initialization, verify:

1. **CLAUDE.md**: Contains AI-SDD Instructions section
2. **Directory Structure**:
    - `.sdd/requirement/` exists
    - `.sdd/specification/` exists
    - `.sdd/task/` exists
3. **Project Constitution**: `.sdd/CONSTITUTION.md` exists
4. **Templates**: All 3 template files exist in `.sdd/`

## Output

On successful initialization, display:

````markdown
## AI-SDD Initialization Complete

### CLAUDE.md

- [x] Added AI-SDD Instructions section

### Directory Structure

- [x] Created .sdd/requirement/
- [x] Created .sdd/specification/
- [x] Created .sdd/task/

### Project Constitution

- [x] Created .sdd/CONSTITUTION.md

### Generated Templates

- [x] .sdd/PRD_TEMPLATE.md
- [x] .sdd/SPECIFICATION_TEMPLATE.md
- [x] .sdd/DESIGN_DOC_TEMPLATE.md

### Next Steps

1. Review `.sdd/CONSTITUTION.md` and customize project principles
2. Review generated templates and customize as needed
3. Use `/generate_prd` to create first PRD
4. Use `/generate_spec` to create specifications from PRD
5. Use `/constitution validate` to verify constitution compliance
````

## Commit

After successful initialization:

```
[docs] Initialize AI-SDD workflow

- Add AI-SDD Instructions to CLAUDE.md
- Create .sdd/ directory structure
- Generate project constitution (CONSTITUTION.md)
- Generate document templates
```
