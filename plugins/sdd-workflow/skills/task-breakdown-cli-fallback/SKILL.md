---
name: task-breakdown-cli-fallback
description: "Break down tasks from technical design document, generating a list of independently testable small tasks"
argument-hint: "<feature-name> [ticket-number]"
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Task Breakdown

Loads technical design document (`*_design.md`) and breaks it down into independently testable small tasks.

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

$ARGUMENTS

| Argument | Required | Description |
|:--|:--|:--|
| `feature-name` | Yes | Target feature name or path (e.g., `user-auth`, `auth/user-login`). Design doc path is resolved from this value |
| `ticket-number` | - | Used for output directory name (e.g., `TICKET-123`) |
| `--ci` | - | CI/non-interactive mode. Exits with error if design doc is missing instead of prompting |

### Input Examples

```
user-auth
task-management TICKET-123
```

## Front Matter Generation Rules

Generated task breakdown files must include YAML front matter at the top of the file.

See `references/front_matter_task.md` for full schema definition.

### Task-Specific Field Rules

| Field | Rule |
|:------|:-----|
| `id` | `"task-{feature-name}"`. For hierarchical: `"task-{parent}-{feature-name}"` |
| `status` | `"pending"` for new task breakdowns |
| `depends-on` | Design doc ID (e.g., `["design-user-auth"]`) |
| `ticket` | Ticket number from input argument (if provided) |
| `tags` | Inherit from design doc |
| `category` | Inherit from design doc |
| `priority` | Inherit from design doc |

## Processing Flow

### 1. Load Related Documents

Both flat and hierarchical structures are supported.

**For flat structure**:

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md (PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md (if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md (required)
```

**For hierarchical structure** (when argument contains `/`):

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md (parent feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md (child feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md (parent feature design, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md (child feature design, required)
```

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required

- If design document doesn't exist:
  - **CI Mode (`--ci`)**: Output error message and stop processing.
  - **Interactive**: Prompt creation with `/generate-spec` first.
- If PRD/spec exists, use to verify tasks cover requirements

### 2. Analyze Design Document

Extract the following information from design document:

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

Clarify dependencies between tasks.

## Output Format

### Task List

**Reference**: `examples/task_list_format.md`

## Output

Use the `templates/${SDD_LANG:-en}/breakdown_output.md` template for output formatting. Save results to ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket_number}/tasks.md or ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{feature}/tasks.md.

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

## Serena MCP Integration (Optional)

If Serena MCP is enabled, semantic code analysis can be leveraged to improve task breakdown precision.

### Additional Features When Serena is Enabled

#### Impact Scope Analysis

| Feature                    | Usage                                                 |
|:---------------------------|:------------------------------------------------------|
| `find_symbol`              | Identify symbols to be changed                        |
| `find_referencing_symbols` | Understand impact scope (dependent code) from changes |

**Reference**: `examples/serena_analysis.md`

### Behavior When Serena is Not Configured

Even without Serena, task breakdown is performed based on design document.

## Post-Generation Verification

### Automatic Verification (Performed)

- [x] **Requirement Coverage Check**: Verify PRD/spec requirements are covered by tasks
- [x] **Dependency Consistency Check**: Confirm no contradictions in inter-task dependencies
- [x] **Completion Criteria Specificity Check**: Verify each task has clear completion criteria

## Notes

- Avoid task breakdown without design document
- If tasks are too large, consider further breakdown
- Avoid implementation order that ignores dependencies
- Completion criteria should be specific and verifiable
