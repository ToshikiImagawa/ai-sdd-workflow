---
name: finalize-prd
description: "Finalize and integrate PRD from all artifacts. Use when combining use case diagrams, requirements analysis, and requirements diagrams into a complete PRD, or when called by generate-prd."
argument-hint: "<feature-name> [--ci] [--amend]"
license: MIT
user-invocable: true
context: fork
model: sonnet
allowed-tools: Read, Glob, Grep, AskUserQuestion
disallowed-tools: Write, Edit, Bash
---

# Finalize PRD

Integrates all generated artifacts (use case diagram, requirements analysis, requirements diagram) into a complete PRD
document.

## Purpose

This skill combines:

- Use case diagrams
- Requirements analysis (UR/FR/NFR tables)
- SysML requirements diagrams

Into a cohesive PRD document following the PRD template structure.

## Hybrid Approach

This skill operates in two modes:

| Mode                      | Behavior | Description                                                  |
|:--------------------------|:---------|:-------------------------------------------------------------|
| **Interactive** (default) | Guide    | May ask clarifying questions, provides detailed output       |
| **CI (`--ci`)**           | Silent   | No user interaction, concise output for pipeline integration |

## Prerequisites

**Read the following prerequisite references before execution:**

| File                                                    | Purpose                                  |
|:--------------------------------------------------------|:-----------------------------------------|
| `references/prerequisites_directory_paths.md`           | Resolve `${SDD_*}` environment variables |
| `references/id_conventions_config.md`                   | PRD-level ID format resolution algorithm and defaults (Integration Rule 5) |

**Load PRD template** (in order):

1. `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` — Project-specific template
2. `templates/${SDD_LANG:-en}/prd_template.md` — Fallback default

**Load if exists:**

- `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md` — For principle compliance

**Read project configuration if available:**

- `${CLAUDE_PROJECT_DIR}/.sdd-config.json` — provides `id_conventions`, used in Integration Rule 5 (ID Consistency)

## Input

$ARGUMENTS

| Argument            | Required      | Description                                                    |
|:--------------------|:--------------|:-----------------------------------------------------------------|
| `feature-name`      | Yes           | Feature name for the PRD                                       |
| `usecase-text`      | Yes           | Use case diagram output from generate-usecase-diagram (new actors/use cases only, when `--amend`) |
| `analysis-text`     | Yes           | Requirements analysis output from analyze-requirements (new UR/FR/NFR only, when `--amend`) |
| `diagram-text`      | Yes           | Requirements diagram output from generate-requirements-diagram (new nodes/relationships only, when `--amend`) |
| `--ci`              | -             | CI/non-interactive mode. Skips clarifying questions            |
| `--amend`           | -             | Amend mode: merge the artifacts above into `existing-prd-text` instead of building a PRD from scratch |
| `existing-prd-text` | When `--amend` | Full text of the existing PRD to append to                    |

> **Required input missing**: `usecase-text` / `analysis-text` / `diagram-text` are marked Required above because
> they are the actual new content to integrate — if any is empty, a placeholder, or absent despite the caller
> claiming to invoke this skill, that is a caller error, not something to fill in by inference. Do not invent
> UR/FR/NFR content to compensate for missing input. Report the missing input in the output instead, and in
> `--amend` mode return `existing-prd-text` unchanged rather than fabricating new requirements.

### Input Format

The skill receives structured text blocks from previous skills. See `references/input_format.md` for the exact shape.

## Integration Rules

### 1. Template Loading

> **CI Mode**: Skip clarifying questions. Make reasonable assumptions for ambiguous items.

Load the PRD template in this order:

1. `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/PRD_TEMPLATE.md` (if exists)
2. `templates/${SDD_LANG:-en}/prd_template.md` (fallback)

### 2. Content Integration

Map input artifacts to template sections:

| Input                | Template Section               | Notes                               |
|:---------------------|:-------------------------------|:------------------------------------|
| Use case diagram     | 2.1-2.2 Use Case Diagram       | Overview and detailed sections      |
| Actors table         | (included in use case section) | Merge into diagram section          |
| Use Cases table      | 2.3 Function List              | Convert to text format              |
| UR table             | 4.x Detailed Requirements      | User requirements section           |
| FR table             | 4.1 Functional Requirements    | Expand to detailed descriptions     |
| NFR table            | 4.2-4.4 Non-Functional         | Performance, interface, constraints |
| Requirements diagram | 3.1 Requirements Diagram       | Overall SysML diagram               |
| Relationships        | (within diagram)               | Contains, derives, traces           |

### 3. Section Markers

Preserve template section markers:

| Marker          | Meaning     | Handling                  |
|:----------------|:------------|:--------------------------|
| `<MUST>`        | Required    | Must include content      |
| `<RECOMMENDED>` | Recommended | Include if data available |
| `<OPTIONAL>`    | Optional    | Include if relevant       |

### 4. Language Consistency

**CRITICAL: Match template language**

- If template is English, entire PRD must be in English
- If template is Japanese, entire PRD must be in Japanese
- Do NOT mix languages

### 5. ID Consistency

Ensure requirement IDs are consistent. Resolve each type's ID format per `id_conventions_config.md` § PRD-Level
ID Format Resolution (default `UR_xxx`, `FR_xxx`, `NFR_xxx`, `IR_xxx`, `DC_xxx`).

> **Amend Mode (`--amend`)**: New IDs must continue from the existing PRD's maximum per prefix (the caller —
> `generate-prd` Step 3.5 — computes and passes this). Never renumber or reuse an existing ID.

### 6. Validate

Check Quality Checks items before returning output.

- If issues found: Fix and repeat from step 2

### 7. Amend Mode Integration (`--amend`)

When `--amend` is set, `existing-prd-text` is the current PRD in full. Build the output by taking that text
verbatim and inserting only the new content — never regenerate or rewrite sections that already exist.

> Reminder: the caller-error rule under **## Input** above still applies here. If `usecase-text` / `analysis-text` /
> `diagram-text` were empty or absent, do not invent rows to insert into the tables below — return
> `existing-prd-text` unchanged.

| Insertion                                    | Where                                                                                        |
|:-----------------------------------------------|:------------------------------------------------------------------------------------------------|
| New UR/FR/NFR rows                             | §4 (Detailed Requirements) is prose, not a table (see `templates/{en,ja}/prd_template.md`: `### FR_001: {name}` headings) — append each new requirement as a new `### {ID}: {name}` subsection under the matching §4.x heading, matching the style of existing entries |
| New requirements diagram nodes & relationships | Appended inside the existing `requirementDiagram` Mermaid block, before its closing code fence |
| New actors/use cases (if any)                  | Appended inside the existing use case diagram's `subgraph` and tables. If the caller does not specify which existing use case a new `<<include>>`/`<<extend>>` relationship should attach to, default to the use case within the same functional category/`subgraph`, and state that judgment call in the output rather than silently guessing |
| Front matter                                   | Preserve every existing field except `updated` (today) and `sdd-version` (current plugin version) |

Everything else in `existing-prd-text` — prose, existing IDs, existing diagram nodes, existing front matter
fields — must come through byte-for-byte unchanged. If the caller did not pass `existing-prd-text`, this is a
caller error; do not attempt to reconstruct the existing PRD from memory.

If an input artifact carries an attribute that has no corresponding slot in the existing PRD's structure (e.g.
a `Priority` value when the existing §4 entries are prose that doesn't surface priority per-item), do not drop
it silently — surface it inline in the new subsection's prose (e.g. as a `- Priority: ...` bullet) instead of
omitting it.

## Front Matter Generation Rules

Generated PRDs must include YAML front matter at the top of the file.

See `references/front_matter_prd.md` for full schema definition, dependency direction rules,
and validation checklist.

### Common Field Rule

| Field         | Rule                                                                                                                       |
|:--------------|:-----------------------------------------------------------------------------------------------------------------------------|
| `sdd-version` | Set to the sdd-workflow plugin's current version — read `version` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` |

> **Amend Mode (`--amend`)**: Do not regenerate any field below. Keep the existing PRD's front matter values as-is
> except `updated` (today) and `sdd-version` (refresh per the rule above).

### PRD-Specific Field Rules

| Field        | Rule                                                                           |
|:-------------|:-------------------------------------------------------------------------------|
| `id`         | `"prd-{feature-name}"`. For hierarchical: `"prd-{parent}-{feature-name}"`      |
| `status`     | `"draft"` for new PRDs                                                         |
| `depends-on` | Parent PRD ID if hierarchical (e.g., `["prd-auth"]`). Empty for top-level PRDs |
| `priority`   | `"medium"` unless explicitly specified in input                                |
| `risk`       | `"medium"` unless explicitly specified in input                                |
| `tags`       | Extract relevant keywords from requirements                                    |
| `category`   | Infer from requirements (e.g., `"authentication"`, `"payment"`)                |

## Output

**IMPORTANT: This skill returns TEXT only. It does NOT write files.**

The output is a complete PRD document text that:

1. Follows the PRD template structure
2. Integrates all input artifacts
3. Maintains consistent formatting
4. Preserves traceability between requirements
5. Uses consistent language throughout

The caller (generate-prd) is responsible for:

- Saving the output to `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md`
- Running prd-reviewer for compliance check

> **Amend Mode (`--amend`)**: The returned text is the full merged PRD (existing content + new insertions from
> Rule 7 above), ready for the caller to save in place — not just the new fragment.

## Quality Checks

Before returning output, verify:

- [ ] All `<MUST>` sections have content
- [ ] Use case diagram is properly formatted
- [ ] Requirements diagram is properly formatted
- [ ] All requirement IDs are unique
- [ ] Traceability is maintained (FR → UR)
- [ ] Language is consistent throughout
- [ ] Template structure is preserved
- [ ] (`--amend` only) `existing-prd-text` content is preserved unchanged outside the insertion points listed in Rule 7

## Notes

### PRD Finalization

- Remove `<MUST>`, `<RECOMMENDED>`, `<OPTIONAL>` markers from final output
- Add glossary entries for any domain-specific terms
- Include out of scope section even if empty (prevents scope creep)
- Ensure all requirements have verification methods specified

### Integration

- This skill is typically called by `/generate-prd --ci` with `--ci` flag
- Output is text only; the caller is responsible for file operations
- Receives output from all previous skills in the workflow
- In CI mode, output is optimized for pipeline consumption
