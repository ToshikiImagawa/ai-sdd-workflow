---
name: task-breakdown
description: "Break down tasks from technical design document, generating a list of independently testable small tasks"
argument-hint: "<feature-name> <ticket-number>"
arguments: [feature-name, ticket-number]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/**)
---

# Task Breakdown

Loads the technical design (`task/{ticket-number}/design-draft.md`, or the spec's persistent
`{feature-name}_design.md` when this generation has no task-scoped draft) and breaks it down into
independently testable small tasks.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Tasks Phase Positioning (Reference)

| Phase     | Purpose                                                   | Deliverables  |
|:----------|:----------------------------------------------------------|:--------------|
| **Tasks** | Break down design into independently testable small tasks | Under `task/` |

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

| Argument | Required | Description |
|:--|:--|:--|
| `feature-name` | Yes | Target feature name or path (e.g., `user-auth`, `auth/user-login`). PRD and spec paths are resolved from this value |
| `ticket-number` | Yes | Ticket number (e.g., `TICKET-123`). Locates both the design draft to read and the `tasks.md` to write. Accepted positionally, or as a flag in either form: `--ticket <number>` and `--ticket=<number>` |
| `--ci` | - | CI/non-interactive mode. Exits with an error instead of prompting when the ticket number or the design draft is missing |

`ticket-number` is required because the design draft and `tasks.md` both live under
`${SDD_TASK_PATH}/{ticket-number}/`. This matches `/generate-spec`, which requires `--ticket` to decide
where to write the draft.

**Ticket argument forms**: **both `--ticket <number>` (space) and `--ticket=<number>` (equals sign) are
accepted**, and so is the bare positional form. A flag form does not consume the positional slot —
`/task-breakdown user-auth --ticket=123` still resolves `feature-name` to `user-auth`. Strip the
`--ticket`/`--ticket=` prefix before using the value.

**When the ticket number is missing**:

- **Interactive**: ask for it with `AskUserQuestion` before loading any document (offer the branch name or the
  current issue as a hint). Nothing is read or written until it is resolved
- **`--ci` mode**: do not ask. Stop with an error naming the missing argument and the fix
  (`/task-breakdown {feature-name} --ticket=<number>`), and write no files

### Input Examples

- `/task-breakdown user-auth TICKET-123`
- `/task-breakdown auth/user-login TICKET-123`
- `/task-breakdown user-auth --ticket TICKET-123`
- `/task-breakdown user-auth --ticket=TICKET-123`

## Front Matter Generation Rules

Generated task breakdown files must include YAML front matter at the top of the file.

See `references/front_matter_task.md` for full schema definition, dependency direction rules, and validation checklist.

### Task-Specific Field Rules

| Field | Rule |
|:------|:-----|
| `id` | `"task-{feature-name}"`. For hierarchical: `"task-{parent}-{feature-name}"` |
| `status` | `"pending"` for new task breakdowns |
| `depends-on` | Design draft ID, which is ticket-scoped (e.g., `["design-TICKET-123"]`) |
| `ticket` | Ticket number from input argument |
| `tags` | Inherit from design draft |
| `category` | Inherit from design draft |
| `priority` | Inherit from design draft |

## Processing Flow

### 1. Load Related Documents

**Design source (required)**:

- Load `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/design-draft.md` if it exists. This is
  **ticket-scoped with a fixed filename**, so its path does not vary with the spec's flat/hierarchical
  structure.
- If it does not exist, this project's generation may have no task-scoped design-draft concept at all
  (the design is persisted directly alongside the spec instead). Fall back to the spec's persistent design
  sibling instead: `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md` (flat), or
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md`
  (hierarchical, when `feature-name` contains `/`).
- If neither exists, this is a missing design draft — see the fallback flow below.

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may
still contain these. They **remain valid** — read them as **supplementary input, and treat their absence as
normal**. Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and
never report an existing one as a naming violation or propose deleting it; it may stay until its decisions
have been migrated to `adr/{feature}.md`.

Only the PRD and spec below follow the spec's flat/hierarchical structure regardless of which design
source above was used.

**Upstream documents — flat structure**:

- Load `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md` (PRD, if exists)
- Load `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md` (if exists)

**Upstream documents — hierarchical structure** (when `feature-name` contains `/`):

- Load `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md` (parent feature PRD, if exists)
- Load `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md` (child feature PRD, if exists)
- Load `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md` (parent feature spec, if exists)
- Load `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md` (child feature spec, if exists)

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` suffix optional (`index_spec.md`, `{feature-name}_spec.md`, or no suffix)
- **Under task**: Design draft uses the fixed filename `design-draft.md`; when absent, the fallback
  design source under specification/ uses the `_design` suffix (`{feature-name}_design.md`), distinct from
  the `_spec` suffix above

**Hierarchical structure input example**:

- `/task-breakdown auth/user-login TICKET-123`

- If neither the design draft nor its fallback exists:
  - **CI Mode (`--ci`)**: Output error message and stop processing.
  - **Interactive**: Prompt creation with `/generate-spec <description> --ticket {ticket-number}` first.
- If PRD/spec exists, use to verify tasks cover requirements

### 2. Analyze Design Source

Extract the following information from the design draft:

| Extraction Item      | Description                 |
|:---------------------|:----------------------------|
| **Module Structure** | Files/directories to create |
| **Dependencies**     | Inter-module dependencies   |
| **Interfaces**       | Public API for each module  |
| **Technology Stack** | Libraries/frameworks to use |

### 3. Task Breakdown Principles

#### Independence

- Each task can be implemented without depending on other tasks
- Break down to granularity allowing parallel work

#### Testability

- Each task can be tested independently
- Clear completion criteria

#### Appropriate Granularity

- 1 task = completable in hours to 1 day
- Not too large, not too small

### 4. Task Classification

| Category        | Description                      | Examples                              |
|:----------------|:---------------------------------|:--------------------------------------|
| **Foundation**  | Work prerequisite to other tasks | Directory structure, type definitions |
| **Core**        | Main feature implementation      | Business logic, API                   |
| **Integration** | Inter-module coordination        | Service layer, event processing       |
| **Testing**     | Test creation                    | Unit tests, integration tests         |
| **Finishing**   | Final adjustments                | Documentation updates, refactoring    |

### 5. Organize Dependencies

Clarify dependencies between tasks. See `references/task_dependency_diagram.md` for an example Mermaid dependency diagram.

## Output Format

### Task List

**Reference**: `examples/task_list_format.md`

The example includes 5 phases (Foundation, Core Implementation, Integration, Testing, Finishing) with dependency diagrams and reference documents.

## Output

Use the `templates/${SDD_LANG:-en}/breakdown_output.md` template for output formatting. Save results to
`${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/tasks.md` — the same directory as
`design-draft.md`, so `task-cleanup` covers both with one ticket-scoped sweep.

## Requirement Coverage Verification

If PRD/spec exists, verify the following for generated task list:

### Check Items

| Check Item                                   | Verification Content                                                 |
|:---------------------------------------------|:---------------------------------------------------------------------|
| **Functional Requirement Coverage**          | Are PRD/spec functional requirements (FR-xxx) covered by tasks?      |
| **Non-Functional Requirement Consideration** | Are non-functional requirements (NFR-xxx) included in testing tasks? |
| **API Implementation Coverage**              | Are all spec APIs included in core tasks?                            |

### Requirement Coverage Table Output

Add the following to task list end (if PRD/spec exists):

**Reference**: `examples/requirement_coverage.md`

### Handling Insufficient Coverage

- If uncovered requirements exist, add tasks
- If tasks have no corresponding requirements, verify if out of scope

## Post-Generation Actions

1. **Save File**:
    - `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/tasks.md`

2. **Requirement Coverage Verification**:
    - If PRD/spec exists: Verify all requirements are covered by tasks
    - Add coverage table to task list

## Serena MCP Integration (Optional)

If Serena MCP is enabled, semantic code analysis can be leveraged to improve task breakdown precision.

### Usage Conditions

- `serena` is configured in `.mcp.json`
- Target language's Language Server is supported

### Additional Features When Serena is Enabled

#### Impact Scope Analysis

| Feature                    | Usage                                                 |
|:---------------------------|:------------------------------------------------------|
| `find_symbol`              | Identify symbols to be changed                        |
| `find_referencing_symbols` | Understand impact scope (dependent code) from changes |

#### Enhanced Task Breakdown Items

1. **Automatic Dependency Detection**: Analyze existing code dependencies to accurately define inter-task dependencies
2. **Impact Scope Identification**: Detect modules affected by changes and appropriately set integration tasks
3. **Existing Test Understanding**: Search related test code to improve testing task precision
4. **Refactoring Target Identification**: Detect existing code requiring modification due to changes

#### Additional Information in Task List

**Reference**: `examples/serena_analysis.md`

### Behavior When Serena is Not Configured

Even without Serena, task breakdown is performed based on the design draft.
If impact scope analysis is needed, recommend manual verification to user.

## Post-Generation Verification

### Automatic Verification (Performed)

The following verifications are automatically performed during generation:

- [x] **Requirement Coverage Check**: Verify PRD/spec requirements are covered by tasks
- [x] **Dependency Consistency Check**: Confirm no contradictions in inter-task dependencies
- [x] **Completion Criteria Specificity Check**: Verify each task has clear completion criteria


### Verification Commands

- `/check-spec {feature-name}` — Confirm consistency with related design documents
- `/clarify {feature-name}` — Verify any unclear points in specifications
- `/checklist {feature-name} {ticket-number}` — Generate checklist to clarify quality criteria

## Notes

- Avoid task breakdown without a design draft
- If tasks are too large, consider further breakdown
- Avoid implementation order that ignores dependencies
- Completion criteria should be specific and verifiable
