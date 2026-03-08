---
name: implement-cli-fallback
description: "Execute TDD-based implementation and progressively complete checklist in tasks.md"
argument-hint: "<feature-name> [ticket-number]"
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, TaskGet
---

# Implement - TDD-Based Implementation Execution

Execute implementation following TDD (Test-Driven Development) approach based on the checklist in `tasks.md`.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Required Prerequisites

Verify the following exist before execution:

| Prerequisite         | Verification                                    | Command to Generate          |
|:---------------------|:------------------------------------------------|:-----------------------------|
| **Task Breakdown**   | `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/tasks.md` exists            | `/task-breakdown {feature}`  |
| **Technical Design** | `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature}_design.md` exists | `/generate-spec {feature}`   |
| **Abstract Spec**    | `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature}_spec.md` exists   | `/generate-spec {feature}`   |

* For hierarchical structure: Add `[{path}/]` prefix (e.g., `auth/user-login_spec.md`).
* For parent features, use `index_spec.md`

## Input

$ARGUMENTS

| Argument | Required | Description |
|:--|:--|:--|
| `feature-name` | Yes | Target feature name or path (e.g., `user-auth`, `auth/user-login`) |
| `ticket-number` | - | Task directory name. Uses feature-name if omitted |

Read `examples/input_format.md` for input format and usage examples.

## Front Matter Generation Rules

Generated implementation log files must include YAML front matter at the top of the file.

See `references/front_matter_impl.md` for full schema definition.

### Implementation Log-Specific Field Rules

| Field | Rule |
|:------|:-----|
| `id` | `"impl-{feature-name}"`. For hierarchical: `"impl-{parent}-{feature-name}"` |
| `status` | `"in-progress"` when implementation starts |
| `depends-on` | Design doc ID (e.g., `["design-user-auth"]`) |
| `ticket` | Ticket number from input argument (if provided) |
| `tags` | Inherit from task/design doc |
| `completed` | Empty string when starting. Set to `"YYYY-MM-DD"` when implementation completes |
| `implementer` | Name of the implementer (if known) |

### Updating Front Matter

When resuming implementation (continue mode), update the `updated` field to the current date.
When implementation completes, set `status` to `"completed"` and `completed` to the completion date.

## TDD Implementation Flow

### 5 Phases

Implementation proceeds through 5 phases progressively:

Read `references/five_phases_overview.md` for the phase overview table.

### Execution Rules per Phase

Read `templates/${SDD_LANG:-en}/phase_rules.md` for detailed execution rules for each phase.

## Processing Flow

### 1. Pre-Implementation Verification

Read `templates/${SDD_LANG:-en}/pre_implementation_verification.md` for document loading and verification steps.

**Check Task Completion Rate**:

Read `templates/${SDD_LANG:-en}/task_progress_analysis.md` for the progress analysis template.

### 2. Task Management Initialization

**Progress Management Using TaskList**:

At the start of implementation, create tasks corresponding to each phase.

Read `templates/${SDD_LANG:-en}/tasklist_patterns.md` for TaskCreate/TaskUpdate usage patterns and examples.

**Notes**: In environments where TaskList is unavailable, display progress in traditional markdown format.

Read `references/tasklist_error_handling.md` for TaskList error handling procedures.

### 3. Implementation Phases

Execute tasks in order following TDD principles:

Read `templates/${SDD_LANG:-en}/phase_execution_order.md` for phase execution order and starting phase determination.

#### Phase 1: Foundation (Setup)

**Purpose**: Establish project structure and dependencies

**Tasks**: Directory structure creation, type definitions, dependency installation, configuration files

**TDD Approach**: Setup test infrastructure first, verify test runner works, no production code yet

#### Phase 2: Core (TDD Loop)

**Purpose**: Implement main business logic

Read `templates/${SDD_LANG:-en}/tdd_cycle.md` for the TDD cycle (RED-GREEN-REFACTOR) procedure.

#### Phase Progress Tracking

Read `templates/${SDD_LANG:-en}/phase_progress_tracking.md` for auto-progress tracking templates.

### 4. Continuous Verification

After completing each task:

Read `templates/${SDD_LANG:-en}/continuous_verification.md` for auto-checks, spec consistency checks, and progress update format.

**Progress Log** `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/implementation_progress.md`:

For an example progress log format, see: `examples/implementation_progress_log.md`

### 5. Completion Verification

When all tasks complete:

Read `templates/${SDD_LANG:-en}/final_verification_checklist.md` for the final verification checklist.

## Output Format

Read `templates/${SDD_LANG:-en}/output_format.md` for output format reference table.

## Implementation Options

### Continue Mode

Read `examples/option_continue.md` for continue mode usage.

### Phase Skip Mode

Read `examples/option_phase_skip.md` for phase skip mode usage.

### Dry Run Mode

Read `examples/option_dry_run.md` for dry run mode usage.

## Best Practices

### Commit Strategy

Read `references/commit_strategy.md` for commit patterns.

### When to Pause

Pause and ask for clarification when:

- Spec is ambiguous (use `/clarify`)
- Multiple valid interpretations exist
- Non-functional requirements unclear
- External dependencies unavailable

## TDD Best Practices

Read `references/tdd_principles.md` for Red-Green-Refactor cycle.

## Error Handling

### Test Failure

Read `templates/${SDD_LANG:-en}/error_test_failure.md` for test failure error template.

### Spec Inconsistency Detected

Read `templates/${SDD_LANG:-en}/error_spec_inconsistency.md` for spec inconsistency error template.

## Notes

- Always follow TDD approach: Red -> Green -> Refactor
- Don't skip tests to "save time"
- Mark task complete only when tests pass and match spec
- Document design decisions during implementation, not after
- Keep updating implementation log for knowledge transfer
- Run `/check-spec` at phase boundaries to detect drift early
