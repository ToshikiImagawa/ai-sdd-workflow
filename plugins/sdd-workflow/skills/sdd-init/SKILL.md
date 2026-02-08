---
name: sdd-init
description: "Initialize AI-SDD workflow in the current project. Sets up CLAUDE.md and generates document templates."
version: 3.0.0
license: MIT
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# SDD Init - AI-SDD Workflow Initializer

Initialize AI-SDD (AI-driven Specification-Driven Development) workflow in the current project.

## What This Command Does

1. **CLAUDE.md Configuration**: Add AI-SDD instructions to project's `CLAUDE.md`
2. **Project Constitution Generation**: Create `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` (if not exist)
3. **Template Generation**: Create document templates in `${SDD_ROOT}/` directory (if not exist)

## Input

$ARGUMENTS

| Argument | Required | Description                                                                 |
|:---------|:---------|:----------------------------------------------------------------------------|
| `--ci`   | -        | CI/non-interactive mode. Auto-approves overwrites, skips user confirmations |

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

AI-SDD principles document path: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md`

**Note**: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md` is automatically updated at session start (via session-start hook). This command
does not need to manually copy it.

Understand AI-SDD principles.

This command initializes the project following AI-SDD principles.

### Configuration File Management

**Note**: Configuration file management is handled by `init-structure.sh` (Phase 1). The script automatically:

1. Checks if `.sdd-config.json` exists at project root
2. If exists but missing `lang` field: Adds `"lang": "en"` (v3.0.0 migration)
3. If not exists: Creates with the default configuration:
   ```json
   {
     "root": ".sdd",
     "lang": "en",
     "directories": {
       "requirement": "requirement",
       "specification": "specification",
       "task": "task"
     }
   }
   ```

**Note**: The `lang` field determines the language for templates (`en` or `ja`).

**Important**: If you want to use custom directory names, create `.sdd-config.json` **before** running this command.

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

**Optimized 2-Phase Execution** (reduces tool calls by 60-70%):

### Phase 1: Shell Script (Static Operations)

Execute `${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/init-structure.sh` to perform static file operations.

**What the script does:**

1. **Manage Configuration File**:
    - Check if `.sdd-config.json` exists
    - If exists but no `lang`: Add `lang: "en"`
    - If not exists: Create with default config

2. **Ensure Root Directory Exists**:
    - `mkdir -p "${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/"`
    - Note: Subdirectories (requirement, specification, task) are created automatically when files are generated

3. **Copy Templates** (if not exist):
    - PRD_TEMPLATE.md (from `/generate-prd` skill)
    - SPECIFICATION_TEMPLATE.md (from `/generate-spec` skill)
    - DESIGN_DOC_TEMPLATE.md (from `/generate-spec` skill)
    - Note: CONSTITUTION.md is NOT copied - use `/constitution init` to generate a customized version

4. **Cleanup**:
    - Delete `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/UPDATE_REQUIRED.md` if exists

5. **Export Environment Variables** to `$CLAUDE_ENV_FILE`:
    - `SDD_ROOT`, `SDD_LANG`, `SDD_*_DIR`, `SDD_*_PATH`

**Script execution:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/init-structure.sh"
```

**Note**: The script reads configuration from `.sdd-config.json`
and uses `$CLAUDE_ENV_FILE` to export variables for Claude's prompt context.

### Phase 2: Update CLAUDE.md

Execute `${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/update-claude-md.sh` to automatically update CLAUDE.md.

**What the script does:**

1. **Read Plugin Version**: Extract version from `plugin.json`
2. **Load Template**: Read `templates/${SDD_LANG}/claude_md_template.md` and replace `{PLUGIN_VERSION}`
3. **Update CLAUDE.md**:
    - If not exists: Create new CLAUDE.md with AI-SDD Instructions
    - If exists without AI-SDD section: Append section
    - If exists with old version: Update section with new version
    - If exists with current version: Skip (already up to date)

**Script execution:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/update-claude-md.sh"
```

**Note**: The script automatically detects the current state and performs the appropriate operation.

## CLAUDE.md Configuration

### AI-SDD Instructions Section

Read `templates/${SDD_LANG:-en}/claude_md_template.md` and add its content to `CLAUDE.md`.

**Note**: Replace `{PLUGIN_VERSION}` in the template with the plugin version obtained in prerequisites.

### Placement Rules

1. **If CLAUDE.md already has "AI-SDD Instructions" section**:
    - Check the version in section title (e.g., `## AI-SDD Instructions (v2.2.0)`)
    - If version is older than current plugin version:
        - Replace entire section with latest version
        - Generate `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md` if not exists
    - If version is same: Skip (already initialized)
2. **If CLAUDE.md exists but no AI-SDD section**: Append section to end
3. **If CLAUDE.md doesn't exist**: Create new file with section

### Migration Support (v2.2.0 -> v2.3.0+)

Projects initialized with v2.2.0 or earlier don't have `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md`.
Re-running this command will perform the following:

1. **Generate AI-SDD-PRINCIPLES.md**: Copy plugin's `AI-SDD-PRINCIPLES.md` to `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/`
2. **Update CLAUDE.md**: Update section title version and replace content with latest version

**Detection Method**:

- CLAUDE.md has `## AI-SDD Instructions` section
- AND `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md` doesn't exist
- OR a section title version is older than the current plugin version

## Project Constitution Generation

**Note**: CONSTITUTION.md is NOT generated by `/sdd-init`. Use `/constitution init` instead.

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

**Use `/constitution init` command** to generate a customized CONSTITUTION.md:

1. Analyzes project context (language, framework, domain)
2. Generates customized constitution based on analysis
3. Saves to `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`

**Do NOT manually copy** `constitution_template.md` - the template is meant to be customized for your specific project.

### Constitution Management

Use `/constitution` command to manage the constitution:

| Subcommand | Purpose                                       |
|:-----------|:----------------------------------------------|
| `init`     | Generate customized constitution file         |
| `validate` | Verify specs/designs comply with constitution |
| `add`      | Add new principles                            |
| `sync`     | Synchronize templates with constitution       |

## Template Generation

**Note**: Template generation is handled by `init-structure.sh` (Phase 1).
All templates are copied from skill directories if they don't already exist.

### Templates to Generate

| Template                 | Path                             | Purpose                       |
|:-------------------------|:---------------------------------|:------------------------------|
| **Project Constitution** | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`           | Non-negotiable principles     |
| **PRD Template**         | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md`           | SysML-format requirements doc |
| **Spec Template**        | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` | Abstract system specification |
| **Design Template**      | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`    | Technical design document     |

### Generation Process (Automated by Shell Script)

The shell script:

1. **Check Existing Templates**: Skip if template already exists
2. **Copy Base Templates**: Copy from each skill's `templates/${SDD_LANG:-en}/` directory
3. **No Overwrite**: Existing templates are never overwritten (users may have customized them)

**Note**: Templates are copied as-is. For project-specific customization,
users can manually edit templates after initialization.

## Post-Initialization Verification

After Phase 1 and Phase 2 complete:

1. **CLAUDE.md**: Verify update script output (created/appended/updated/skipped)
2. **Templates**: Verify init-structure.sh output (created templates)
3. **Configuration**: Verify `.sdd-config.json` exists

**Note**: Both scripts output their results to stdout. Simply report what the scripts indicate.

**Important**: CONSTITUTION.md is NOT generated by `/sdd-init`. Remind users to run `/constitution init` if they need it.

## Cleanup

**Note**: Cleanup is handled by `init-structure.sh` (Phase 1).

The script automatically deletes `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/UPDATE_REQUIRED.md` if it exists. This file is created by the `session-start`
hook when version mismatch is detected, and becomes unnecessary after initialization.

## Output

Use the `templates/${SDD_LANG:-en}/init_output.md` template for output formatting.
