---
name: sdd-init
description: "Initialize AI-SDD workflow in the current project. Sets up CLAUDE.md and generates document templates."
argument-hint: "[--ci]"
license: MIT
user-invocable: true
disable-model-invocation: true
model: haiku
allowed-tools: Read, Glob, Grep, Edit(.sdd/**), Edit(.sdd-config.json), Edit(CLAUDE.md), Edit(.claude/rules/**), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/init-structure.py" *), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/update-claude-md.py" *)
---

# SDD Init - AI-SDD Workflow Initializer

Initialize AI-SDD (AI-driven Specification-Driven Development) workflow in the current project.

## What This Command Does

1. **CLAUDE.md Configuration**: Add the minimal AI-SDD Instructions section (declaration + trigger conditions + a pointer to the detailed rule) to the project's `CLAUDE.md`
2. **Project Constitution Pointer**: This command does **not** create `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` - report that it is missing and point the user at `/constitution init`, which generates a customized one
3. **Template Generation**: Create document templates in `${SDD_ROOT}/` directory (if not exist)

> **Note**: The detailed AI-SDD guide (directory structure, file naming, doc-link convention) lives in `.claude/rules/ai-sdd-instructions.md`, a path-scoped rule that loads only when working under `.sdd/`. That file is created and version-synced automatically by the SessionStart hook (`session-start.py`), not by this command, so the always-loaded `CLAUDE.md` stays minimal. It is a single English file (agent-facing guidance, not a human-facing document) regardless of `SDD_LANG`.

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

**Note**: `.sdd-config.json` is expected to already exist when this command runs — it is created either by the
SessionStart hook (`session-start.py`) or manually by the user beforehand, never by this command itself.
`init-structure.py` (Phase 1) checks for it and **errors out if it is missing** (see Phase 1 below); this command
does not create a default one, since doing so here would duplicate the SessionStart hook's ownership of that
default and risk the two drifting out of sync. See `references/sdd_config_default.md` for the default content
the hook writes.

**Note**: The `lang` field determines the language for templates (`en` or `ja`).

**Important**: If you want to use custom directory names, create `.sdd-config.json` **before** running this command.

### Template Sources

| Template      | Source                                                                       |
|:--------------|:-----------------------------------------------------------------------------|
| Constitution  | `/constitution` skill's `templates/${SDD_LANG:-en}/constitution_template.md` |
| PRD           | `/generate-prd` skill's `templates/${SDD_LANG:-en}/prd_template.md`          |
| Specification | `/generate-spec` skill's `templates/${SDD_LANG:-en}/spec_template.md`        |
| Design Doc    | `/generate-spec` skill's `templates/${SDD_LANG:-en}/design_template.md`      |
| ADR           | this skill's `templates/${SDD_LANG:-en}/adr_template.md`                     |

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Execution Flow

**Optimized 2-Phase Execution** (reduces tool calls by 60-70%):

### Phase 1: Python Script (Static Operations)

Execute `${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/init-structure.py` to perform static file operations.

**What the script does:**

1. **Manage Configuration File**:
    - Check if `.sdd-config.json` exists
    - If not exists: Error (configuration file must be created beforehand or by session-start hook)

2. **Ensure Root Directory Exists**:
    - `mkdir -p "${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/"`
    - Note: Subdirectories (requirement, specification, adr, task) are created automatically when files are generated

3. **Copy Templates** (if not exist):
    - PRD_TEMPLATE.md (from `/generate-prd` skill)
    - SPECIFICATION_TEMPLATE.md (from `/generate-spec` skill)
    - DESIGN_DOC_TEMPLATE.md (from `/generate-spec` skill)
    - ADR_TEMPLATE.md (from this skill's `templates/${SDD_LANG:-en}/adr_template.md`)
    - Note: CONSTITUTION.md is NOT copied - use `/constitution init` to generate a customized version

4. **Ignore the Generated Cache** (idempotent):
    - Add `${SDD_ROOT}/.cache/` to `${CLAUDE_PROJECT_DIR}/.gitignore` — the cache is a generated artifact and is not meant to be committed
    - If `.gitignore` already ignores that path: leave the file untouched
    - If `.gitignore` exists without the entry: append it (existing lines are preserved, never rewritten)
    - If `.gitignore` does not exist: create it containing only that entry

5. **Cleanup**:
    - Delete `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/UPDATE_REQUIRED.md` if exists

6. **Export Environment Variables** to `$CLAUDE_ENV_FILE`:
    - `SDD_ROOT`, `SDD_LANG`, `SDD_*_DIR`, `SDD_*_PATH`

**Script execution:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/init-structure.py"`

**Note**: The script reads configuration from `.sdd-config.json`
and uses `$CLAUDE_ENV_FILE` to export variables for Claude's prompt context.

### Phase 2: Update CLAUDE.md

Execute `${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/update-claude-md.py` to automatically update CLAUDE.md.

**What the script does:**

1. **Read Plugin Version**: Extract version from `plugin.json`
2. **Load Template**: Read `templates/${SDD_LANG}/claude_md_template.md` and replace `{PLUGIN_VERSION}`
3. **Update CLAUDE.md**:
    - If not exists: Create new CLAUDE.md with AI-SDD Instructions
    - If exists without AI-SDD section: Append section
    - If exists with old version: Update section with new version
    - If exists with current version: Skip (already up to date)

**Script execution:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/sdd-init/scripts/update-claude-md.py"`

**Note**: The script automatically detects the current state and performs the appropriate operation.

## CLAUDE.md Configuration

### AI-SDD Instructions Section

Read `templates/${SDD_LANG:-en}/claude_md_template.md` and add its content to `CLAUDE.md`.

**Note**: Replace `{PLUGIN_VERSION}` in the template with the plugin version obtained in prerequisites.

### Placement Rules

1. **If CLAUDE.md already has "AI-SDD Instructions" section**:
    - Check the version in section title (e.g., `## AI-SDD Instructions (v2.2.0)`)
    - If version is older than current plugin version: Replace entire section with latest version
    - If version is same: Skip (already initialized)
2. **If CLAUDE.md exists but no AI-SDD section**: Append section to end
3. **If CLAUDE.md doesn't exist**: Create new file with section

### Migration Support

Re-running `/sdd-init` on an existing project automatically handles version upgrades:

1. **Update CLAUDE.md**: If section title version is older than current plugin version, replace entire section with latest version
2. **Add Missing Templates**: Copy the latest templates (PRD, Spec, Design, ADR) for the ones not present yet (existing templates are never overwritten, so a customized template survives re-initialization)
3. **Add the Cache Ignore Rule**: Append `${SDD_ROOT}/.cache/` to `.gitignore` if it is not ignored yet (a project initialized before this rule existed gets it on the next run; a project that already has it is left untouched)
4. **Cleanup**: Delete `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/UPDATE_REQUIRED.md`, which the SessionStart hook leaves behind when it detects a version mismatch

`${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md` and `.claude/rules/ai-sdd-instructions.md` are **not** written by this command: the SessionStart hook re-syncs both from the installed plugin at every session start (see the Note under "Read AI-SDD Principles Document").

**Detection Method**:

- CLAUDE.md has `## AI-SDD Instructions` section with older version
- OR `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md` doesn't exist (a project initialized before the `adr/` document model)

#### Migrating a v4.x Project to the v5 Document Model

v5 split what v4.x kept in a single persistent design document into a temporary draft plus a persistent decision log:

| v4.x                                                                    | v5                                                                                              |
|:------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| `${SDD_SPECIFICATION_PATH}/{feature-name}_design.md` (persistent)       | `${SDD_TASK_PATH}/{ticket-number}/design-draft.md` (temporary, deleted after implementation)     |
| Decision rationale living inside that design doc                        | `${SDD_ADR_PATH}/{feature-name}.md` (persistent, append-only decision log)                       |

Guidance to give the user when the project still has v4.x layout:

- Existing `${SDD_SPECIFICATION_PATH}/*_design.md` files **remain valid**. Read them as **supplementary input, and treat their absence as normal**. Never report one as a naming violation or propose deleting it; it may stay until its decisions have been migrated to `adr/{feature-name}.md`
- **Do not create new ones.** New technical design goes to `${SDD_TASK_PATH}/{ticket-number}/design-draft.md`
- Migration is incremental, not a bulk conversion: `/task-cleanup` appends a finished ticket's decisions and rationale to `${SDD_ADR_PATH}/{feature-name}.md` before deleting the ticket's task directory. No migration step is required before doing further work
- `ADR_TEMPLATE.md` (copied into `${SDD_ROOT}/` by Phase 1) documents the append-only entry format for the decision log. The `adr/` directory itself is created when its first file is written, exactly like `requirement/`, `specification/`, and `task/`

**Note**: After re-initialization, recommend `/recommend-front-matter` for documents under `${SDD_ROOT}/` that have no YAML front matter, or whose front matter is missing fields the current schema defines (front matter was introduced in v3.2.0).

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

**Note**: Template generation is handled by `init-structure.py` (Phase 1).
All templates are copied from skill directories if they don't already exist.

### Templates to Generate

| Template                 | Path                             | Purpose                       |
|:-------------------------|:---------------------------------|:------------------------------|
| **Project Constitution** | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`           | Non-negotiable principles     |
| **PRD Template**         | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md`           | SysML-format requirements doc |
| **Spec Template**        | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/SPECIFICATION_TEMPLATE.md` | Abstract system specification |
| **Design Template**      | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/DESIGN_DOC_TEMPLATE.md`    | Technical design document     |
| **ADR Template**         | `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md`           | Append-only decision log      |

### Generation Process (Automated by Shell Script)

The shell script:

1. **Check Existing Templates**: Skip if template already exists
2. **Copy Base Templates**: Copy from each skill's `templates/${SDD_LANG:-en}/` directory
3. **No Overwrite**: Existing templates are never overwritten (users may have customized them)

**Note**: Templates are copied as-is. For project-specific customization,
users can manually edit templates after initialization.

### Project Templates Take Precedence

Once copied into `${SDD_ROOT}/`, these files are the **project's** templates, and the skill that produces the
corresponding document reads the project copy first, falling back to its own bundled template only when the
project copy is absent:

| Project template under `${SDD_ROOT}/` | Read first by                                              |
|:--------------------------------------|:-----------------------------------------------------------|
| `PRD_TEMPLATE.md`                     | `/generate-prd` (via `prepare-prd.py`)                     |
| `SPECIFICATION_TEMPLATE.md`           | `/generate-spec` Phase 1 (via `prepare-spec.py`)           |
| `DESIGN_DOC_TEMPLATE.md`              | `/generate-spec` Phase 2 (via `prepare-spec.py`)           |
| `ADR_TEMPLATE.md`                     | `/task-cleanup`, when appending decision-log entries       |

This is why re-running `/sdd-init` never overwrites an existing template: editing the copy under
`${SDD_ROOT}/` is the supported way to adapt a document's shape to the project's conventions.

## Post-Initialization Verification

After Phase 1 and Phase 2 complete:

1. **CLAUDE.md**: Verify update script output (created/appended/updated/skipped)
2. **Templates**: Verify init-structure.py output (created templates)
3. **Configuration**: Verify `.sdd-config.json` exists
4. **Cache Ignore Rule**: Verify init-structure.py output (`.gitignore` created / appended / already present)
5. **Front Matter Recommendation**: If existing documents without YAML front matter are found under `${SDD_ROOT}/`, recommend running `/recommend-front-matter` to add structured metadata

**Note**: Both scripts output their results to stdout. Simply report what the scripts indicate.

**Important**: CONSTITUTION.md is NOT generated by `/sdd-init`. Remind users to run `/constitution init` if they need it.

## Cleanup

**Note**: Cleanup is handled by `init-structure.py` (Phase 1).

The script automatically deletes `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/UPDATE_REQUIRED.md` if it exists. This file is created by the `session-start`
hook when version mismatch is detected, and becomes unnecessary after initialization.

## Output

Use the `templates/${SDD_LANG:-en}/init_output.md` template for output formatting.
