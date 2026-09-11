---
name: clarify
description: "Analyze specifications and generate clarification questions to eliminate ambiguity before implementation"
argument-hint: "<feature-name> [ticket-number] [--interactive]"
arguments: [feature-name, ticket-number]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/**)
disallowed-tools: Bash
---

# Clarify - Specification Clarification

Scans specifications across 9 key categories and generates targeted clarification questions to eliminate ambiguity
before implementation.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

**PRD is out of scope for edits**: Although `allowed-tools` grants `Edit(.sdd/**)`, this skill only edits
`*_spec.md` / `task/{ticket-number}/design-draft.md`. Never write to `requirement/**` — see
AI-SDD-PRINCIPLES.md § Document Update
Triggers ("Updating `requirement/` (PRD) — Never Automated").

### Relationship to Vibe Detector Skill

This command is complementary to the `vibe-detector` skill:

| Tool              | Purpose                                     | When to Use                    |
|:------------------|:--------------------------------------------|:-------------------------------|
| **vibe-detector** | Detects vague instructions in user requests | During task initiation         |
| **clarify**       | Scans existing specs for ambiguity and gaps | Before implementation planning |

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

- `feature-name`: $feature-name
- `ticket-number`: $ticket-number

Full argument string: $ARGUMENTS

> **Fallback**: If a value above is empty, remains a literal `$` placeholder, or starts with `--`
> (a flag captured positionally), treat that argument as omitted and interpret the full argument
> string instead. Ask the user interactively when a required argument is missing.

| Argument        | Required | Description                                                        |
|:----------------|:---------|:-------------------------------------------------------------------|
| `feature-name`  | Yes      | Target feature name or path (e.g., `user-auth`, `auth/user-login`) |
| `ticket-number` | -        | Locates the design draft `task/{ticket-number}/design-draft.md`. Omit to analyze the PRD, the spec, and any v4.x persistent design doc only |
| `--interactive` | -        | Interactive mode: Answer questions one at a time                   |

`ticket-number` may be passed positionally (`/clarify {feature-name} {ticket-number}`) or as a flag; both
spellings — `--ticket {number}` and `--ticket={number}` — are accepted and mean the same thing.

**When `ticket-number` is omitted**, no design draft is looked up at all: the analysis runs on the PRD, the
abstract spec, and any v4.x persistent design doc (resolved from `feature-name`, so it is still consulted),
and design-level categories are otherwise limited to what those documents express. This is a supported
mode, not an error — but state it in the output ("no `ticket-number` given, so
`task/{ticket-number}/design-draft.md` was not consulted") so the reduced coverage is visible. When a
`ticket-number` *is* given and the draft is missing there, that is also normal (the draft is deleted once
implementation completes) — report the resolved path and continue rather than prompting for regeneration.

### Input Examples

**Reference**: `references/command_examples.md`

## Processing Flow

### 1. Load Target Specifications

Both flat and hierarchical structures are supported.

See `references/target_specification_loading.md` for the list of paths to load, including how the design draft
is resolved and what to do when it is absent.

In addition to the paths listed there, load the v4.x persistent design doc when the project has one:
`${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/[{parent-feature}/]{feature-name}_design.md` (parent
features use `index_design.md`). Its path follows the spec's flat/hierarchical structure and is resolved from
`feature-name`, not from `ticket-number`.

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may
still contain these. They **remain valid** — read them as **supplementary input, and treat their absence as
normal**. Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and
never report an existing one as a naming violation or propose deleting it; it may stay until its decisions
have been migrated to `adr/{feature}.md`. When `task/{ticket-number}/design-draft.md` is absent (or
`ticket-number` was omitted) but such a file exists, analyze the design-level categories against it instead
of limiting them to what the spec expresses.

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` suffix optional (`index_spec.md`, `{feature-name}_spec.md`, or no suffix).
  A `_design.md` sibling here is a v4.x persistent design doc — still valid, see above
- **Under task**: Design draft uses the fixed filename `design-draft.md`

### 2. Nine Category Analysis

Analyze specifications across 9 key categories. See `references/nine_category_analysis.md` for:

- Full category definitions and analysis focus
- Clarity level classification (Clear / Partial / Missing)
- Question prioritization criteria
- Question format template

### 3. Generate Clarification Questions

Based on category analysis, generate up to 5 high-impact questions using the format in
`references/nine_category_analysis.md`.

### 4. Integrate Answers

After receiving user answers, the **main agent (this skill)** applies the integration:

1. **Review Integration Proposals**: Review proposals from `clarification-assistant` agent output
2. **Update Specifications**: Apply approved changes to the appropriate `*_spec.md` or
   `task/{ticket-number}/design-draft.md` using Edit/Write tools (never `requirement/**` — see Prerequisites).
   When the design draft is absent, integrate design-related answers into the `*_spec.md` only where they
   belong at the abstract level; otherwise report them as findings rather than recreating the draft. A v4.x
   persistent design doc is a **read-only** supplementary input here — it may inform the analysis, but never
   receives integration edits; report answers that belong to it as findings instead
3. **Mark Resolved**: Track which questions have been addressed
4. **Generate Diff**: Show what was added to specifications

**Note**: The `clarification-assistant` agent outputs integration proposals (target file, section, content). This skill
applies the actual edits.

## Output

Use the `templates/${SDD_LANG:-en}/clarification_output.md` template for output formatting.

## Integration Mode

When user provides answers, use the `--integrate` flag (e.g. `/clarify user-auth --integrate`).

This will:

1. Prompt for answers to each question
2. Update specifications incrementally
3. Show diffs of changes

## Best Practices

### When to Use This Command

| Scenario                               | Recommended Action                                |
|:---------------------------------------|:--------------------------------------------------|
| **Before task breakdown**              | Run `/clarify` to catch ambiguities early         |
| **After receiving vague requirements** | Use with `/generate-spec` to build complete specs |
| **During spec review**                 | Verify all 9 categories are addressed             |
| **Before implementation**              | Final check to ensure no hidden assumptions       |

### Complementary Commands

See `references/complementary_commands.md` for the recommended command sequence around `/clarify`.

## Advanced Options

### Focus on Specific Categories

Use `--categories` with a comma-separated list, e.g. `/clarify user-auth --categories flow,integrations,edge-cases`.

### Specify Output Detail Level

Use `--detail` with one of the following values:

| Value           | Effect                        |
|:-----------------|:------------------------------|
| `minimal`        | Top 3 questions only          |
| `standard`       | Top 5 questions (default)     |
| `comprehensive`  | All identified issues         |

## Post-Clarification Verification

### Automatic Verification (Performed)

The following verifications are automatically performed during clarification:

- [x] **Nine Category Scan**: Comprehensively detect ambiguities across functional scope, data model, flow, etc.
- [x] **Clarity Score Calculation**: Classify items as Clear/Partial/Missing and calculate overall score
- [x] **Question Prioritization**: Select questions based on impact, risk, and blocker status

### Verification Commands

**Reference**: `references/verification_commands.md`

### Implementation Readiness Criteria

| Clarity Score | Recommended Action                                   |
|:--------------|:-----------------------------------------------------|
| 80% or above  | Ready for implementation                             |
| 60-79%        | Recommended to resolve Partial items                 |
| Below 60%     | Further clarification required before implementation |

## Notes

- Questions are generated based on specification analysis, not assumptions
- Prioritize questions that would cause most implementation uncertainty
- Some ambiguity is acceptable for low-risk, low-impact decisions
- Re-run after major specification updates to catch new ambiguities
- Works best when combined with vibe-detector skill during task initiation
