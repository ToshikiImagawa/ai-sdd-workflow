---
name: implement-cli
description: "CLI-enhanced TDD implementation. Execute TDD-based implementation using sdd-cli for document discovery."
argument-hint: "<feature-name> [ticket-number]"
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, TaskGet
---

# Implement (CLI) - TDD-Based Implementation Execution

CLI-enhanced version: Uses `sdd-cli search` to efficiently locate task and design documents,
reducing Glob/Grep overhead for prerequisite verification.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/cli_integration_guide.md` - CLI command reference
- `references/cli_error_handling.md` - Error handling and fallback strategies

### Required Prerequisites

Verify the following exist before execution:

| Prerequisite         | Verification                                    | Command to Generate          |
|:---------------------|:------------------------------------------------|:-----------------------------|
| **Task Breakdown**   | `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/tasks.md` exists            | `/task-breakdown {feature}`  |
| **Technical Design** | `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature}_design.md` exists | `/generate-spec {feature}`   |
| **Abstract Spec**    | `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature}_spec.md` exists   | `/generate-spec {feature}`   |

## Input

$ARGUMENTS

| Argument | Required | Description |
|:--|:--|:--|
| `feature-name` | Yes | Target feature name or path (e.g., `user-auth`, `auth/user-login`) |
| `ticket-number` | - | Task directory name. Uses feature-name if omitted |

Read `examples/input_format.md` for input format and usage examples.

## Front Matter Generation Rules

Same as non-CLI version. See `references/front_matter_impl.md` for full schema definition.

## Processing Flow

### 0. CLI - Prerequisite Verification & Document Discovery

Use `sdd-cli` to verify prerequisites and discover documents:

```bash
# Find all documents for the feature
sdd-cli search --feature-id <feature-name> --format json
```

**From CLI output, verify:**

1. Task breakdown file exists (type: `task`)
2. Design document exists (type: `design`)
3. Spec document exists (type: `spec`)

**Error Handling**: If CLI fails, fall back to manual path verification using Glob.

### 1. Pre-Implementation Verification

Read `templates/${SDD_LANG:-en}/pre_implementation_verification.md` for document loading and verification steps.

Use document paths from CLI output (Phase 0) instead of manual path construction.

**Check Task Completion Rate**:

Read `templates/${SDD_LANG:-en}/task_progress_analysis.md` for the progress analysis template.

### 2. Task Management Initialization

**Progress Management Using TaskList**:

At the start of implementation, create tasks corresponding to each phase.

Read `templates/${SDD_LANG:-en}/tasklist_patterns.md` for TaskCreate/TaskUpdate usage patterns.

Read `references/tasklist_error_handling.md` for error handling procedures.

### 3. Implementation Phases

Execute tasks in order following TDD principles:

Read `templates/${SDD_LANG:-en}/phase_execution_order.md` for phase execution order.

#### Phase 1: Foundation (Setup)

**Purpose**: Establish project structure and dependencies

**TDD Approach**: Setup test infrastructure first, verify test runner works, no production code yet

#### Phase 2: Core (TDD Loop)

**Purpose**: Implement main business logic

Read `templates/${SDD_LANG:-en}/tdd_cycle.md` for the TDD cycle procedure.

#### Phase Progress Tracking

Read `templates/${SDD_LANG:-en}/phase_progress_tracking.md` for auto-progress tracking.

### 4. Continuous Verification

After completing each task:

Read `templates/${SDD_LANG:-en}/continuous_verification.md` for verification steps.

### 5. Completion Verification

Read `templates/${SDD_LANG:-en}/final_verification_checklist.md` for the final checklist.

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

- Spec is ambiguous
- Multiple valid interpretations exist
- Non-functional requirements unclear
- External dependencies unavailable

## TDD Best Practices

Read `references/tdd_principles.md` for Red-Green-Refactor cycle.

## Error Handling

Read `templates/${SDD_LANG:-en}/error_test_failure.md` for test failure handling.
Read `templates/${SDD_LANG:-en}/error_spec_inconsistency.md` for spec inconsistency handling.

## Notes

- Always follow TDD approach: Red -> Green -> Refactor
- Don't skip tests to "save time"
- Mark task complete only when tests pass and match spec
- Document design decisions during implementation, not after
- Keep updating implementation log for knowledge transfer
- Run `/check-spec` at phase boundaries to detect drift early
