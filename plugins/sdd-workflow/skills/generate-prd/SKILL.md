---
name: generate-prd
description: "Generates complete PRD document from business requirements. Creates use case diagrams, requirements analysis (UR/FR/NFR), SysML diagrams, and complete PRD file. Use when user mentions PRD, product requirements, feature definition, requirement specification, or starting AI-SDD workflow."
argument-hint: "<requirements-description> [--ci] [--amend]"
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/**), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/generate-prd/scripts/prepare-prd.py" *)
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

**PRD writes are human-directed, not inferred**: This skill's PRD writes (Step 10) are authored directly from the
`requirements` input the user provided — this is the intended, human-initiated path for creating/updating a PRD,
and is compatible with AI-SDD-PRINCIPLES.md § Document Update Triggers ("Updating `requirement/` (PRD) — Never
Automated"). Never repurpose this skill to reconcile the PRD backward from a spec/design/implementation
contradiction — the "Consistency Check" in Post-Generation Actions only recommends downstream updates
(`/generate-spec`), it must never edit the PRD itself.

**`--amend` is an addition mode, not a reconciliation mode**: `--amend` lets a human append newly-provided
requirements to an existing PRD without a full overwrite (see Step 3.5). The `requirements` input passed with
`--amend` must be a human describing NEW requirements to add — never a summary of what a spec/design/
implementation already does. Do not invoke `--amend` from `doc-consistency-checker`'s automated PRD-contradiction
detection, `plan-refactor`, or any other flow that derives PRD content by reconciling it backward from downstream
artifacts; those flows must stop at reporting the contradiction and let a human write the `--amend` input
themselves. This carries the same enforcement strength as the no-full-overwrite-inference rule above.

**Load PRD template** (in order):

1. `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` — Project-specific template
2. `templates/${SDD_LANG:-en}/prd_template.md` — Fallback default

**Load if exists:**

- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` — For principle compliance check

**Read project configuration if available:**

- `${CLAUDE_PROJECT_DIR}/.sdd-config.json` — provides `id_conventions`, used in Step 5 (Resolve ID Conventions)

## Input

$ARGUMENTS

| Argument       | Required | Description                               |
|:---------------|:---------|:------------------------------------------|
| `requirements` | Yes      | Business requirements text (for `--amend`, describe only the NEW requirements to add) |
| `--ci`         | No       | CI mode: no questions, skips prd-reviewer |
| `--amend`      | No       | Amend mode: append the new requirements to an existing PRD instead of regenerating it. Requires an existing PRD (Step 3) |

**Examples:**

- `/generate-prd A feature for users to manage tasks. Supports creation, editing, deletion.`
- `/generate-prd A feature for users to manage tasks. --ci`
- `/generate-prd Add a due-date reminder notification to task management. --amend`

## Progress Checklist

Use `templates/${SDD_LANG:-en}/progress_checklist.md` to track progress.

## Generation Flow

**You MUST execute all of the following steps in order to generate a complete PRD file:**

### Step 1: Prerequisites

**Phase 1: Python Script** - Execute `prepare-prd.py` to pre-load templates and references by running
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/generate-prd/scripts/prepare-prd.py"`.

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
| `usecase_diagram_guide.md`            | Use case diagram notation                |
| `mermaid_notation_rules.md`           | Mermaid syntax rules                     |
| `requirements_diagram_components.md`  | SysML requirements diagram components    |
| `front_matter_prd.md`                 | PRD front matter schema                  |
| `id_conventions_config.md`            | PRD-level ID format resolution algorithm and defaults (Step 5) |

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

| Mode        | If PRD exists           | If PRD does not exist                                                            |
|:------------|:------------------------|:----------------------------------------------------------------------------------|
| Interactive | Ask user to confirm overwrite | Proceed to generate a new PRD                                              |
| CI (`--ci`) | Auto-approve overwrite  | Proceed to generate a new PRD                                                     |
| `--amend`   | Proceed to Step 3.5     | **Error**: `--amend` requires an existing PRD. Stop and tell the user to run `/generate-prd` without `--amend` first |

### Step 3.5: Load Existing PRD (`--amend` Only)

Skip this step unless `--amend` is specified.

1. Read the existing PRD file in full — it is the base that new content will be appended to. Do not modify its
   existing prose, tables, or diagram nodes.
2. Extract every requirement `id:` in the requirements diagram (§3.1), grouped by ID prefix (`UR`, `FR`, `NFR`,
   `IR`, `DC`, or a project-specific prefix from `.sdd-config.json`'s `id_conventions`). Track sub-requirement IDs
   (e.g. `FR_001_02`) under their parent separately, so a new top-level requirement and a new sub-requirement of an
   existing parent are numbered independently.
3. For each prefix, record the highest existing numeric suffix. New requirements in that prefix continue from
   `max + 1`, zero-padded to the same width as the existing IDs (default 3 digits: `UR_005`). A prefix with no
   existing entries starts at `001`.
4. Note the existing use case diagram's actors/use cases and the existing requirements diagram's nodes/relationships
   — Steps 4–6 add to these, and must never replace, renumber, or restate them.

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

> **Amend Mode (`--amend`)**: Generate only the actors/use cases introduced by the new requirements. Do not
> regenerate or restate actors/use cases already present in the existing PRD (Step 3.5).

### Step 5: Analyze Requirements

Extract structured requirements from the use case diagram and business context.

**Resolve ID conventions** before assigning any ID, per `id_conventions_config.md` § PRD-Level ID Format
Resolution (default `UR_xxx`, `FR_xxx`, `NFR_xxx`). Use the resolved format consistently for every ID produced
below and in Step 6.

**Generate three requirement tables:**

1. **User Requirements (UR)**: High-level goals from user perspective
   - ID format: from above (`id_conventions.prd_user`)
   - Include: ID, Requirement, Priority, Risk

2. **Functional Requirements (FR)**: Specific functions to fulfill user requirements
   - ID format: from above (`id_conventions.prd_functional`)
   - Include: ID, Requirement, Derived From (matching UR ID format above), Priority, Risk, Verification

3. **Non-Functional Requirements (NFR)**: Quality attributes
   - ID format: from above (`id_conventions.prd_nonfunctional`)
   - Include: ID, Requirement, Category, Priority, Risk, Verification

**Requirements Summary table:**
- Count by category (UR/FR/NFR)
- Count by priority (Must/Should/Could)

> **Amend Mode (`--amend`)**: Generate only the new UR/FR/NFR entries for the requirements given in this
> invocation. Assign IDs continuing from the maximums recorded in Step 3.5 — never renumber, edit, or remove an
> existing requirement.

### Step 6: Generate Requirements Diagram

Generate a SysML requirements diagram in Mermaid `requirementDiagram` format.

**Critical syntax rules:**
- Use underscores in IDs, NOT hyphens (e.g., `UR_001`, not `UR-001`)
- Quote all text values (e.g., `text: "User can create tasks"`)
- Use lowercase for attributes (e.g., `risk: high`, not `risk: High`)
- Use correct requirement types: `requirement`, `functionalRequirement`, `performanceRequirement`
- Use correct relationships: `contains`, `derives`, `traces`

> **Amend Mode (`--amend`)**: Generate only the new nodes and relationships for the requirements produced in
> Step 5. Existing nodes and relationships from Step 3.5 carry through unchanged — do not regenerate them.

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

> **Amend Mode (`--amend`)**: Delegate to `finalize-prd --amend`, passing the existing PRD text loaded in
> Step 3.5 alongside the new artifacts from Steps 4–6. The result is the existing PRD with the new content
> appended — never a from-scratch regeneration.

### Step 8: Add YAML Front Matter

Generate YAML front matter following `references/front_matter_prd.md` schema. See
`templates/${SDD_LANG:-en}/front_matter_example.md` for a concrete example.

| Field         | Rule                                                                                                                       |
|:--------------|:-----------------------------------------------------------------------------------------------------------------------------|
| `sdd-version` | Set to the sdd-workflow plugin's current version — read `version` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` |

> **Amend Mode (`--amend`)**: Keep every existing front matter field as-is except `updated` (today's date) and
> `sdd-version` (refresh to the current plugin version). Do not regenerate `id`, `created`, `priority`, `risk`,
> `tags`, `category`, or `depends-on`.

### Step 9: Validate

Check Quality Checks items before saving.

### Step 10: Save PRD File

**MANDATORY**: Use the `Write` tool to save the complete PRD to:

- **Flat structure**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- **Hierarchical (parent)**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent}/index.md`
- **Hierarchical (child)**: `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent}/{feature-name}.md`

After saving, confirm the file exists at the expected path. In `--amend` mode, the saved content is the merged
PRD produced by Step 7 (existing content plus new additions), not a freshly regenerated document.

### Mode Differences

| Step                  | Interactive       | CI (`--ci`)     | `--amend`                                          |
|:-----------------------|:------------------|:----------------|:-----------------------------------------------------|
| Vibe Coding risk       | Confirm with user | Skip            | Confirm with user (applies to the new requirements)  |
| Existing PRD           | Confirm overwrite | Auto-approve    | Required — error if missing (Step 3.5)               |
| Clarifying questions   | Ask if needed     | Skip            | Ask if needed                                        |
| Use case diagram       | Full regenerate   | Full regenerate | Additions only (Step 4)                              |
| Requirements analysis  | Full regenerate   | Full regenerate | New UR/FR/NFR only, continued IDs (Step 5)           |
| Requirements diagram   | Full regenerate   | Full regenerate | New nodes/relationships only (Step 6)                |
| **Save PRD file**      | **Save**          | **Save**        | **Save (merged/appended content)**                   |
| prd-reviewer           | Run               | Skip            | Run                                                   |
| front-matter-reviewer  | Run               | Skip            | Run                                                   |

## Post-Generation Actions

### 1. Principle Compliance (Interactive Only)

> **CI Mode**: Skip this section.

After PRD generation:

1. Call prd-reviewer agent to check compliance with CONSTITUTION.md
2. Call front-matter-reviewer agent (pass PRD file path)
3. Apply approved fixes from both reviews
4. Include results in output

**If agent delegation is unavailable in the current execution environment**, do not silently skip these
reviews or report them as completed. State explicitly in the output that principle/front-matter review
was not performed and why, and list it as a manual review item for a human to run separately.

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
- [ ] Requirement IDs are unique (format resolved in Step 5)
- [ ] All FRs trace to at least one UR
- [ ] Priority and risk values are valid
- [ ] Verification methods are specified for all requirements
- [ ] Language is consistent throughout (matches template)
- [ ] No `<MUST>`, `<RECOMMENDED>`, `<OPTIONAL>` markers in final output
- [ ] (`--amend` only) Every pre-existing requirement ID, section, and diagram node is unchanged from Step 3.5
- [ ] (`--amend` only) New requirement IDs continue from the existing PRD's maximum per prefix, with no collisions

## Principle Compliance (Interactive Only)

> **CI Mode**: Skip this section.

After PRD generation:

1. Call prd-reviewer agent
2. Call front-matter-reviewer agent (pass PRD file path)
3. Apply approved fixes from both reviews
4. Include results in output

**If agent delegation is unavailable in the current execution environment**, do not silently skip these
reviews or report them as completed. State explicitly in the output that principle/front-matter review
was not performed and why, and list it as a manual review item for a human to run separately.

If CONSTITUTION.md missing: Skip check, recommend `/sdd-init`.

