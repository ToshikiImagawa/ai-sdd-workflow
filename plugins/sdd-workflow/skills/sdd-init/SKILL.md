---
name: sdd-init
description: "Initialize AI-SDD workflow in the current project. Sets up CLAUDE.md and generates document templates."
version: 3.0.0
license: MIT
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# SDD Init - AI-SDD Workflow Initializer

Initialize AI-SDD (AI-driven Specification-Driven Development) workflow in the current project.

## What This Command Does

1. **CLAUDE.md Configuration**: Add AI-SDD instructions to project's `CLAUDE.md`
2. **Project Constitution Generation**: Create `.sdd/CONSTITUTION.md` (if not exist)
3. **Template Generation**: Create document templates in `.sdd/` directory (if not exist)

## Prerequisites

### 1. Get Plugin Version

Read version from plugin's `plugin.json`.

**plugin.json path** (search in the following order and use the first file found):

1. `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json` (Claude Code environment variable)
2. `plugins/sdd-workflow/.claude-plugin/plugin.json` (from project root - for plugin development)

Steps:

1. Read `plugin.json`
2. Get the `version` field value (e.g., `"2.3.0"`)
3. Use this version as `{PLUGIN_VERSION}` in subsequent processing

**Important**: The CLAUDE.md section title must include this version (e.g., `## AI-SDD Instructions (v2.3.0)`)

### 2. Read AI-SDD Principles Document

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `.sdd/AI-SDD-PRINCIPLES.md`

**Note**: `.sdd/AI-SDD-PRINCIPLES.md` is automatically updated at session start (via session-start hook). This command
does not need to manually copy it.

Understand AI-SDD principles.

This command initializes the project following AI-SDD principles.

### Configuration File (Optional)

You can customize directory names by creating `.sdd-config.json` at project root.

For configuration file details, refer to the "Project Configuration File" section in the AI-SDD principles document.

**Note**: If you want to use custom directory names during initialization, create `.sdd-config.json` first. The
directory structure and CLAUDE.md content will be generated based on configuration values.

### Template Sources

| Template      | Source                                                                       |
|:--------------|:-----------------------------------------------------------------------------|
| Constitution  | `/constitution` skill's `templates/${SDD_LANG:-en}/constitution_template.md` |
| PRD           | `/generate-prd` skill's `templates/${SDD_LANG:-en}/prd_template.md`          |
| Specification | `/generate-spec` skill's `templates/${SDD_LANG:-en}/spec_template.md`        |
| Design Doc    | `/generate-spec` skill's `templates/${SDD_LANG:-en}/design_template.md`      |

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Execution Flow

```
1. Check current project state
   |- Does CLAUDE.md exist?
   |- Does .sdd/ directory exist?
   |- Does .sdd/CONSTITUTION.md exist?
   |
2. Configure CLAUDE.md
   |- If CLAUDE.md exists: Add AI-SDD Instructions section
   |- If not exists: Create new CLAUDE.md with AI-SDD Instructions
   |
3. Create .sdd/ directory structure
   |- .sdd/requirement/
   |- .sdd/specification/
   |- .sdd/task/
   |
4. Generate project constitution (if not exist)
   |- Check if .sdd/CONSTITUTION.md exists
   |- If not exist: Generate using /constitution skill's templates/${SDD_LANG:-en}/constitution_template.md
   |
5. Check existing templates
   |- .sdd/PRD_TEMPLATE.md
   |- .sdd/SPECIFICATION_TEMPLATE.md
   |- .sdd/DESIGN_DOC_TEMPLATE.md
   |
6. Generate missing templates
   |- Use each skill's templates/${SDD_LANG:-en}/ directory as base
```

## CLAUDE.md Configuration

### AI-SDD Instructions Section

Read `templates/${SDD_LANG:-en}/claude_md_template.md` and add its content to `CLAUDE.md`.

**Note**: Replace `{PLUGIN_VERSION}` in the template with the plugin version obtained in prerequisites.

### Placement Rules

1. **If CLAUDE.md already has "AI-SDD Instructions" section**:
    - Check the version in section title (e.g., `## AI-SDD Instructions (v2.2.0)`)
    - If version is older than current plugin version:
        - Replace entire section with latest version
        - Generate `.sdd/AI-SDD-PRINCIPLES.md` if not exists
    - If version is same: Skip (already initialized)
2. **If CLAUDE.md exists but no AI-SDD section**: Append section to end
3. **If CLAUDE.md doesn't exist**: Create new file with section

### Migration Support (v2.2.0 -> v2.3.0+)

Projects initialized with v2.2.0 or earlier don't have `.sdd/AI-SDD-PRINCIPLES.md`.
Re-running this command will perform the following:

1. **Generate AI-SDD-PRINCIPLES.md**: Copy plugin's `AI-SDD-PRINCIPLES.md` to `.sdd/`
2. **Update CLAUDE.md**: Update section title version and replace content with latest version

**Detection Method**:

- CLAUDE.md has `## AI-SDD Instructions` section
- AND `.sdd/AI-SDD-PRINCIPLES.md` doesn't exist
- OR section title version is older than current plugin version

## Project Constitution Generation

### What is a Project Constitution?

A Project Constitution (CONSTITUTION.md) defines **non-negotiable principles that form the foundation of all design
decisions**.

| Characteristic     | Description                                                     |
|:-------------------|:----------------------------------------------------------------|
| **Non-negotiable** | Not open to debate. Changes require careful consideration       |
| **Persistent**     | Consistently applied across the entire project                  |
| **Hierarchical**   | Higher principles take precedence over lower ones               |
| **Verifiable**     | Can automatically verify spec/design compliance with principles |

### Generation Process

1. Check if `.sdd/CONSTITUTION.md` exists
2. If not exist, read `/constitution` skill's `templates/${SDD_LANG:-en}/constitution_template.md` and generate
3. Customize based on project context (language, framework, domain)

### Constitution Management

Use `/constitution` command to manage the constitution after initialization:

| Subcommand | Purpose                                       |
|:-----------|:----------------------------------------------|
| `validate` | Verify specs/designs comply with constitution |
| `add`      | Add new principles                            |
| `sync`     | Synchronize templates with constitution       |

## Template Generation

### Templates to Generate

| Template                 | Path                             | Purpose                       |
|:-------------------------|:---------------------------------|:------------------------------|
| **Project Constitution** | `.sdd/CONSTITUTION.md`           | Non-negotiable principles     |
| **PRD Template**         | `.sdd/PRD_TEMPLATE.md`           | SysML-format requirements doc |
| **Spec Template**        | `.sdd/SPECIFICATION_TEMPLATE.md` | Abstract system specification |
| **Design Template**      | `.sdd/DESIGN_DOC_TEMPLATE.md`    | Technical design document     |

### Generation Process

1. **Check Existing Templates**: Skip if template already exists
2. **Analyze Project Context**:
    - Detect programming languages used
    - Identify project structure and conventions
    - Review existing documentation patterns
3. **Generate Customized Templates**:
    - Read base templates from each skill's `templates/${SDD_LANG:-en}/` directory
    - Customize type syntax for project language (TypeScript, Python, Go, etc.)
    - Adjust examples based on project domain

### Template Customization Points

Customize during template generation based on project analysis:

| Item                | Customization Content                                                                |
|:--------------------|:-------------------------------------------------------------------------------------|
| **Type Syntax**     | Adapt to project's primary language (e.g., TypeScript interfaces, Python type hints) |
| **Directory Paths** | Reflect project's actual structure in examples                                       |
| **Domain Examples** | Use relevant examples based on project type (web app, CLI, library, etc.)            |

## Post-Initialization Verification

After initialization, verify:

1. **CLAUDE.md**: Contains AI-SDD Instructions section
2. **Directory Structure**:
    - `.sdd/requirement/` exists
    - `.sdd/specification/` exists
    - `.sdd/task/` exists
3. **Project Constitution**: `.sdd/CONSTITUTION.md` exists
4. **Templates**: All 3 template files exist in `.sdd/`

## Cleanup

After initialization is complete, perform the following cleanup:

1. **Delete warning file**: Delete `.sdd/UPDATE_REQUIRED.md` if it exists
    - This file is created by the `session-start` hook when version mismatch is detected
    - It becomes unnecessary after initialization is complete

## Output

Use the `templates/${SDD_LANG:-en}/init_output.md` template for output formatting.
