---
name: checklist
description: "Generate quality assurance checklists from specifications and plans with structured IDs and categories"
argument-hint: "<feature-name> [ticket-number]"
arguments: [feature-name, ticket-number]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit(.sdd/**)
---

# Checklist - Quality Checklist Generation

Automatically generates comprehensive quality assurance checklists from specifications, the technical design
draft, and task breakdowns.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
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
| `ticket-number` | -        | Used for the output directory name and to locate the design draft. Uses feature-name if omitted |

### Input Format

Usage: `/checklist {feature-name} {ticket-number}`. `ticket-number` may also be passed as a flag; both
spellings — `--ticket {number}` and `--ticket={number}` — are accepted and mean the same thing.

**When `ticket-number` is omitted**, `feature-name` becomes the ticket directory name: the design draft and
task breakdown are looked up under `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{feature-name}/`, and the
checklist is written to `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{feature-name}/checklist.md` — **not**
`task/{ticket-number}/checklist.md`. State the resolved ticket directory in the output. If that directory
holds neither `design-draft.md` nor `tasks.md`, say so instead of generating quietly from the remaining
inputs: name the omitted `ticket-number` as the likely cause (the rest of the workflow writes under a ticket
directory, so the checklist would land away from it) and offer re-running as
`/checklist {feature-name} {ticket-number}`. A v4.x persistent design doc (see "Load Source Documents" below)
still supplies the design items when the project has one, but it lives under `specification/` and is resolved
from `feature-name`, so it neither confirms nor corrects the resolved ticket directory — report the
resolution either way.

### Input Examples

| Example                                | Description                     |
|:----------------------------------------|:---------------------------------|
| `/checklist user-auth TICKET-123`       | Standard usage                   |
| `/checklist task-management`            | Uses feature-name as ticket dir  |
| `/checklist auth/user-login TICKET-789` | For hierarchical structure       |

## Processing Flow

### 1. Load Source Documents

Both flat and hierarchical structures are supported.

**For flat structure**:

| File                                                                     | Required   |
|:--------------------------------------------------------------------------|:-----------|
| `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md` (PRD)  | if exists  |
| `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}.md` **or** `{feature-name}_spec.md` | required (either form) |
| `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/design-draft.md`        | if exists  |
| `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md` (v4.x persistent design doc) | if exists  |
| `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/tasks.md`               | if exists  |

**For hierarchical structure** (when argument contains `/`):

| File                                                                                          | Required  |
|:------------------------------------------------------------------------------------------------|:----------|
| `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md` (parent feature PRD) | if exists |
| `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md` (child feature PRD) | if exists |
| `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index.md` **or** `index_spec.md` (parent feature spec) | if exists |
| `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}.md` **or** `{feature-name}_spec.md` (child feature spec) | required (either form) |
| `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/design-draft.md` (design draft)                | if exists |
| `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md` (parent feature v4.x persistent design doc) | if exists |
| `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md` (child feature v4.x persistent design doc) | if exists |
| `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/tasks.md`                                      | if exists |

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` suffix optional (`index_spec.md`, `{feature-name}_spec.md`, or no suffix) —
  either form satisfies the rows marked "required (either form)" above
- **Under task**: Design draft uses the fixed filename `design-draft.md`. It is ticket-scoped, so its path is
  the same in both flat and hierarchical structures

**When the design draft is absent**: `design-draft.md` is a temporary document deleted once implementation
completes, so treat it as an optional input. Continue with the abstract spec (and PRD/tasks.md when present),
and limit design-review items to what the spec supports — do not stop, and do not prompt for regeneration.

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may
still contain these. They **remain valid** — read them as **supplementary input, and treat their absence as
normal**. Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and
never report an existing one as a naming violation or propose deleting it; it may stay until its decisions
have been migrated to `adr/{feature}.md`. When `design-draft.md` is absent but such a file exists, derive the
Design Review items from it instead of narrowing them to what the spec supports. Their path follows the
spec's flat/hierarchical structure (parent features use `index_design.md`) and is resolved from
`feature-name`, not from `ticket-number`.

### 2. Extract Verification Points

From each document, extract checkable items:

**From PRD** (if exists):

| Extract Item                          | Purpose                     |
|:--------------------------------------|:----------------------------|
| Functional Requirements (FR-xxx)      | Verify feature completeness |
| Non-Functional Requirements (NFR-xxx) | Verify quality attributes   |
| Acceptance Criteria                   | Verify business value       |

**From Abstract Specification**:

| Extract Item       | Purpose                         |
|:-------------------|:--------------------------------|
| Public APIs        | Verify interface implementation |
| Data Models        | Verify type definitions         |
| Behavior Contracts | Verify sequence flows           |
| Constraints        | Verify edge case handling       |

**From Technical Design** (the design draft, or a v4.x persistent design doc when the project has one;
skip these items when neither exists):

| Extract Item       | Purpose                       |
|:-------------------|:------------------------------|
| Module Structure   | Verify architecture alignment |
| Technology Stack   | Verify dependencies           |
| Design Decisions   | Verify rationale documented   |
| Integration Points | Verify external connections   |

**From Task Breakdown** (if exists):

| Extract Item        | Purpose                      |
|:--------------------|:-----------------------------|
| Completion Criteria | Verify task-level acceptance |
| Dependencies        | Verify implementation order  |
| Test Requirements   | Verify test coverage         |

### 3. Generate Checklist Items

Transform extracted points into actionable checklist items:

**Basis disclosure (required per item)**: State which document and which specific statement each item
was derived from (e.g. "spec §4.2 FR-003", "design §6 Architecture"). An item may legitimately be
synthesized from a general QA concern implied by an implementation component's existence rather than
quoted from a document (e.g. "config input fallback behavior" inferred from a config-loading module) —
that is not fabrication, but say so explicitly ("synthesized from: ...") instead of implying it was
extracted verbatim. This basis line is what lets a reviewer tell "extracted" apart from "invented."

**ID Assignment Format**: `CHK-{category}{nn}` (e.g., `CHK-101`, `CHK-102`, ... for Category 1;
`CHK-201`, `CHK-202`, ... for Category 2; `CHK-301`, `CHK-302`, ... for Category 3)

| Category Number | Category Name         |
|:----------------|:----------------------|
| 1               | Requirements Review   |
| 2               | Specification Review  |
| 3               | Design Review         |
| 4               | Implementation Review |
| 5               | Testing Review        |
| 6               | Documentation Review  |
| 7               | Security Review       |
| 8               | Performance Review    |
| 9               | Deployment Review     |

**Categories**:

| Category                  | Purpose                           | Examples                                       |
|:--------------------------|:----------------------------------|:-----------------------------------------------|
| **Requirements Review**   | Verify all requirements addressed | FR-xxx coverage, NFR-xxx validation            |
| **Specification Review**  | Verify spec completeness          | API signatures, data models                    |
| **Design Review**         | Verify design quality             | Architecture patterns, tech stack              |
| **Implementation Review** | Verify code quality               | Code structure, naming conventions             |
| **Testing Review**        | Verify test adequacy              | Unit tests, integration tests, edge cases      |
| **Documentation Review**  | Verify documentation              | Code comments, design docs, README             |
| **Security Review**       | Verify security measures          | Authentication, authorization, data validation |
| **Performance Review**    | Verify performance                | Response times, resource usage                 |
| **Deployment Review**     | Verify deployment readiness       | Configuration, migrations, rollback plan       |

### 4. Organize by Priority

Assign priority levels:

| Priority        | Mark | Criteria                 | When to Check      |
|:----------------|:-----|:-------------------------|:-------------------|
| **P1 - High**   | P1   | Must pass before merge   | Before PR creation |
| **P2 - Medium** | P2   | Should pass before merge | During PR review   |
| **P3 - Low**    | P3   | Nice to have             | Opportunistic      |

**Assign a priority to every item, in every category** — including any category you add beyond the
standard nine (e.g. a principle-compliance category). An item without a priority leaves the reader
unable to judge sequencing, regardless of which category it sits in.

**Priority-scheme origin (required)**: when you state that the priority scheme "matches the SKILL.md
definition" or similar, that statement must follow an actual comparison, not a copy of this reminder.
Name the documents you compared (this SKILL.md body vs. the template) and say explicitly whether they
agreed or you found and resolved a discrepancy — a bare restatement of "matches the definition" without
that comparison record does not satisfy this.

## Output Format

### Checklist Document

For a complete checklist example with all categories (CHK-101 through CHK-903), priority levels, and completion criteria, see:

**Reference**: `examples/checklist_full_example.md`

The example includes 9 categories (Requirements, Specification, Design, Implementation, Testing, Documentation, Security, Performance, Deployment) with 60 total items across P1/P2/P3 priority levels.

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/checklist.md`

## Checklist Template Integration

This command uses the template from `templates/${SDD_LANG:-en}/checklist_template.md` (within this skill directory) as a base and customizes it
based on:

- Project-specific requirements
- Programming language conventions
- Technology stack
- Team standards

## Update Existing Checklist

To update an existing checklist after spec changes, run `/checklist user-auth TICKET-123 --update`.

This will:

1. Load existing checklist
2. Compare with current specs
3. Add new items
4. Mark obsolete items
5. Preserve completion status

## Export Formats

### GitHub Issues

Run `/checklist user-auth TICKET-123 --export github-issues` to create individual GitHub issues for P1 items.

### Notion/Linear

Run `/checklist user-auth TICKET-123 --export csv` to export the checklist as CSV for import to project management
tools.

## Best Practices

| Practice             | Benefit                                                 |
|:---------------------|:--------------------------------------------------------|
| **Generate early**   | Use checklist as implementation guide                   |
| **Update regularly** | Keep in sync with spec changes                          |
| **Track completion** | Mark items as they're verified                          |
| **Customize**        | Add project-specific items                              |
| **Archive**          | Keep checklist with implementation for future reference |

## Integration with Other Commands

The checklist fits into the overall workflow as follows: `/generate-spec {description} --ticket {ticket}` ->
`/task-breakdown {feature} {ticket}` -> `/checklist {feature} {ticket}` (generate checklist) ->
`/implement {feature} {ticket}` (use checklist during implementation) -> review against checklist before PR.
All four steps share the same `{ticket}`, so they read and write the same `task/{ticket}/` directory.

## Notes

- Checklist items are derived from specifications, not invented
- IDs (CHK-101, CHK-201, etc.) are stable across updates and organized by category
- Priority levels (P1, P2, P3) can be customized per project
- Some items may require manual verification
- Automated checks should be integrated into CI/CD where possible
- Archive checklist with task logs for future reference
