---
name: task-breakdown-cli
description: "CLI-enhanced task breakdown. Break down tasks from technical design document using sdd-cli for document discovery."
argument-hint: "<feature-name> [ticket-number]"
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
---

# Task Breakdown (CLI)

CLI-enhanced version: Uses `sdd-cli search` to efficiently locate design documents,
reducing Glob/Grep overhead.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/cli_integration_guide.md` - CLI command reference
- `references/cli_error_handling.md` - Error handling and fallback strategies

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.

## Input

$ARGUMENTS

| Argument | Required | Description |
|:--|:--|:--|
| `feature-name` | Yes | Target feature name or path (e.g., `user-auth`, `auth/user-login`) |
| `ticket-number` | - | Used for output directory name (e.g., `TICKET-123`) |
| `--ci` | - | CI/non-interactive mode |

### Input Examples

```
user-auth
task-management TICKET-123
```

## Front Matter Generation Rules

Same as non-CLI version. See `references/front_matter_task.md` for full schema definition.

## Processing Flow

### 1. CLI - Document Discovery

Use `sdd-cli` to find the design document and related documents:

```bash
# Find all documents for the feature
sdd-cli search --feature-id <feature-name> --dir specification --format json
```

**From CLI output, extract:**

1. Design document path (`*_design.md`) - required
2. Spec document path (`*_spec.md`) - optional
3. Front matter data

Also search for PRD:

```bash
sdd-cli search --feature-id <feature-name> --dir requirement --format json
```

**Error Handling**: If CLI fails, fall back to manual path resolution:

```
${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md
```

### 2. Load & Analyze Design Document

Read the design document identified by CLI. Extract:

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

**Reference**: `examples/task_list_format.md`

## Output

Use the `templates/${SDD_LANG:-en}/breakdown_output.md` template for output formatting.

## Requirement Coverage Verification

If PRD/spec exists (discovered via CLI), verify coverage.

**Reference**: `examples/requirement_coverage.md`

## Serena MCP Integration (Optional)

Same as non-CLI version. See `examples/serena_analysis.md`.

## Notes

- Avoid task breakdown without design document
- If tasks are too large, consider further breakdown
- Avoid implementation order that ignores dependencies
- Completion criteria should be specific and verifiable
