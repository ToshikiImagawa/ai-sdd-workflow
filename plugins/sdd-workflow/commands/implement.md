---
description: "Execute TDD-based implementation and progressively complete checklist in tasks.md"
argument-hint: "<task-file-path>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, TaskGet
---

# Implement - TDD-Based Implementation Execution

Execute implementation following TDD (Test-Driven Development) approach based on the checklist in `tasks.md`.

## Prerequisites

### Plugin Update Check

**Before execution, check if `.sdd/UPDATE_REQUIRED.md` exists.**

If this file exists, the AI-SDD plugin needs to be updated. Display a warning to the user and prompt them to run the following command:

```
/sdd_init
```

### AI-SDD Principles Document

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `.sdd/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles.

This command performs implementation following AI-SDD principles.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value        | Description                    |
|:-------------------------|:---------------------|:-------------------------------|
| `SDD_ROOT`               | `.sdd`               | Root directory                 |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | PRD/Requirements directory     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`          | Task log directory             |

**Path Resolution Priority:**

1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

This document uses default values for examples, but replace with custom values if environment variables or configuration file exists.

### Required Prerequisites

Verify the following exist before execution:

| Prerequisite         | Verification                                    | Command to Generate         |
|:---------------------|:------------------------------------------------|:----------------------------|
| **Task Breakdown**   | `.sdd/task/{ticket}/tasks.md` exists            | `/task_breakdown {feature}` |
| **Technical Design** | `.sdd/specification/{feature}_design.md` exists | `/generate_spec {feature}`  |
| **Abstract Spec**    | `.sdd/specification/{feature}_spec.md` exists   | `/generate_spec {feature}`  |

* For hierarchical structure: Add `[{path}/]` prefix (e.g., `auth/user-login_spec.md`). For parent features, use `index_spec.md`

## Input

$ARGUMENTS

### Input Format

```
/implement {feature-name} {ticket-number}
/implement {feature-name}  # Uses feature-name as ticket directory
```

### Input Examples

```
/implement user-auth TICKET-123
/implement task-management FEAT-456
/implement auth/user-login TICKET-789  # For hierarchical structure
```

## TDD Implementation Flow

### 5 Phases

Implementation proceeds through 5 phases progressively:

| Phase | Phase Name         | Purpose                                    | TDD Approach                          |
|:------|:-------------------|:-------------------------------------------|:--------------------------------------|
| **1** | Setup (Foundation) | Directory structure, type definitions      | Setup test environment                |
| **2** | Tests (Test-First) | Create test cases (Red)                    | Write failing tests first             |
| **3** | Core (Core Implementation) | Main functionality implementation (Green) | Implement to pass tests              |
| **4** | Integration        | Module integration (Green)                 | Write integration tests first, then implement |
| **5** | Polish (Finishing) | Refactoring, documentation (Refactor)      | Improve code while maintaining tests  |

### Execution Rules per Phase

#### Phase 1: Setup

```
1. Create directory structure
2. Create type definition files
3. Define basic interfaces
4. Setup test environment
```

**Completion Criteria**: All foundation files created and tests runnable

#### Phase 2: Tests

```
1. Check test tasks in tasks.md
2. Create failing tests for each feature
3. Run tests and confirm Red (failure)
4. Mark [x] in tasks.md
```

**Completion Criteria**: All test cases created and failing as expected

#### Phase 3: Core

```
1. Implement corresponding to tests created in Phase 2
2. Implement to make tests Green (pass)
3. Use minimum implementation (avoid over-implementation)
4. Mark [x] in tasks.md
```

**Completion Criteria**: All core tests passing

#### Phase 4: Integration

```
1. Write integration tests between modules first
2. Run integration tests and confirm Red
3. Implement integration parts to make them Green
4. Mark [x] in tasks.md
```

**Completion Criteria**: Integration tests passing

#### Phase 5: Polish

```
1. Remove code duplication (DRY principle)
2. Improve naming
3. Add documentation comments
4. Performance optimization
5. Mark [x] in tasks.md
```

**Completion Criteria**: All tests passing and code quality meets standards

## Processing Flow

### 1. Pre-Implementation Verification

**Load and Verify Documents**:

```
1. Load task breakdown: .sdd/task/{ticket}/tasks.md
2. Load design document: .sdd/specification/[{path}/]{feature}_design.md
3. Load abstract spec: .sdd/specification/[{path}/]{feature}_spec.md
4. Load PRD (if exists): .sdd/requirement/[{path}/]{feature}.md
```

**⚠️ Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

**Check Task Completion Rate**:

````markdown
## Task Progress Analysis

| Phase                | Total Tasks | Completed | Remaining | Completion |
|:---------------------|:------------|:----------|:----------|:-----------|
| Phase 1: Foundation  | 3           | 0         | 3         | 0%         |
| Phase 2: Core        | 5           | 0         | 5         | 0%         |
| Phase 3: Integration | 2           | 0         | 2         | 0%         |
| Phase 4: Testing     | 4           | 0         | 4         | 0%         |
| Phase 5: Finishing   | 2           | 0         | 2         | 0%         |
| **Total**            | **16**      | **0**     | **16**    | **0%**     |

### Current Status

- Ready to start Phase 1: Foundation
````

### 2. Task Management Initialization

**Progress Management Using TaskList**:

At the start of implementation, create tasks corresponding to each phase. This enables:
- Users can check progress using `/tasks` command or `Ctrl+T`
- Tasks appear in the terminal status area
- Visual indicators show pending, in_progress, or completed status

**Why Use TaskList**:

This command involves 5 phases of complex multi-step work, meeting these criteria:
- Complex tasks requiring 3+ steps
- Each phase has clear completion criteria
- Progress tracking provides value

**Steps**:

1. Create tasks for each phase using TaskCreate tool
2. TaskCreate returns the ID of the created task
3. If dependencies exist, use the previous task ID when creating subsequent tasks

**Example: Creating Phase 1 Task**:

```
TaskCreate({
  subject: "Execute setup phase",
  description: "Create directory structure, create type definition files, define basic interfaces, setup test environment",
  activeForm: "Executing setup phase"
})
```

**Example: Creating Phase 2 Task (depends on Phase 1)**:

After obtaining Phase 1's task ID, create Phase 2 task:

```
TaskCreate({
  subject: "Create test cases",
  description: "Create failing tests for each feature (TDD Red)",
  activeForm: "Creating test cases"
})
```

After creation, set dependency using TaskUpdate:

```
TaskUpdate({
  taskId: "<Phase 2 task ID>",
  addBlockedBy: ["<Phase 1 task ID>"]
})
```

**Notes**:

- `subject` should be in imperative form, short and concise (e.g., "Execute setup", "Create tests")
- `activeForm` should use present continuous form (e.g., "Executing setup", "Creating tests")
- All tasks are created with `pending` status
- Dependencies are set using TaskUpdate after TaskCreate

### 3. Implementation Phases

Execute tasks in order following TDD principles:

#### Phase Execution Order

```
Phase 1: Foundation (Setup)
   ↓
Phase 2: Core (TDD Loop)
   ↓
Phase 3: Integration
   ↓
Phase 4: Testing
   ↓
Phase 5: Finishing (Polish)
```

#### Phase Progress Management Using TaskList

**At Phase Start**:

Update task status to `in_progress` using TaskUpdate tool:

```
TaskUpdate({
  taskId: "<target phase task ID>",
  status: "in_progress"
})
```

**During Phase Execution**:

1. Execute phase tasks in order
2. Update tasks.md to complete checklist
3. Continuously run tests

**At Phase Completion**:

Update task status to `completed` using TaskUpdate tool:

```
TaskUpdate({
  taskId: "<target phase task ID>",
  status: "completed"
})
```

Then:
1. Run tests for verification
2. Proceed to next phase

**Notes**:

- In environments where TaskList is unavailable, progress will be displayed in traditional markdown format
- Command execution continues even if TaskList operations fail
- Users can check progress anytime using `/tasks` command or `Ctrl+T`
- Tasks persist across context compactions
- Status area displays up to 10 tasks at a time (5 phases fit comfortably)

#### Phase 1: Foundation (Setup)

**Purpose**: Establish project structure and dependencies

**Tasks**:

- Directory structure creation
- Type definitions
- Dependency installation
- Configuration files

**TDD Approach**:

- Setup test infrastructure first
- Verify test runner works
- No production code yet

**Auto-Progress Tracking**:

````markdown
### Phase 1: Foundation

| #   | Task            | Description              | Completion Criteria | Status |
|:----|:----------------|:-------------------------|:--------------------|:-------|
| 1.1 | Directory setup | Create module structure  | Directories exist   | [x]    |
| 1.2 | Type definitions | Define core types       | Types compile       | [x]    |
| 1.3 | Test setup      | Configure test framework | Tests can run       | [x]    |
````

#### Phase 2: Core (TDD Loop)

**Purpose**: Implement main business logic

**TDD Cycle for Each Task**:

```
1. RED: Write failing test
   - Define expected behavior
   - Test should fail (no implementation yet)
   - Commit: "test: add test for {feature}"

2. GREEN: Make test pass
   - Write minimum code to pass test
   - Confirm test succeeds
   - Commit: "feat: implement {feature}"

3. REFACTOR: Clean up code
   - Improve structure without changing behavior
   - Confirm all tests still pass
   - Commit: "refactor: clean up {feature}"
```

**Auto-Progress Tracking**:

````markdown
### Phase 2: Core Implementation

| #   | Task            | Description          | Completion Criteria | Status |
|:----|:----------------|:---------------------|:--------------------|:-------|
| 2.1 | User validation | Validate user input  | Tests pass          | [x]    |
| 2.2 | Data persistence | Save to database    | Tests pass          | [ ]    |
| 2.3 | Business logic  | Core feature logic   | Tests pass          | [ ]    |

### Phase 3: Integration

**Purpose**: Connect components

**Tasks**:

- Service layer integration
- API endpoint wiring
- Event handling
- Middleware integration

**Verification**:

- Integration tests pass
- End-to-end flows work
- Verify spec compliance

### Phase 4: Testing

**Purpose**: Comprehensive test coverage

**Test Types**:

| Test Type             | Purpose                       | Coverage Target     |
|:----------------------|:------------------------------|:--------------------|
| **Unit Tests**        | Individual component behavior | Core business logic |
| **Integration Tests** | Component interaction         | Service layer, APIs |
| **Edge Case Tests**   | Boundary conditions           | Error paths, limits |
| **Non-Functional Tests** | Performance, security      | NFR verification    |

**Auto-Verification**:

- Run test suite
- Check coverage metrics
- Verify all acceptance criteria met

### Phase 5: Finishing (Polish)

**Purpose**: Final improvements

**Tasks**:

- Code cleanup
- Documentation update
- Performance optimization
- Design document update
````

### 4. Continuous Verification

After completing each task:

**Auto-Checks**:

```
1. Run related tests → Must pass
   ↓
2. Check spec consistency → Must match
   ↓
3. Update tasks.md → Mark [x]
```

**Spec Consistency Check** (automatic):

````markdown
### Spec Consistency Check

| Verification Item               | Status | Notes                       |
|:--------------------------------|:-------|:----------------------------|
| API signatures match spec       | ✓      | All public APIs implemented |
| Data models match spec          | ✓      | Types align with spec       |
| Behavior matches sequence diagrams | ✓   | Flow verified               |
| Non-functional requirements met | ⚠      | Response time needs tuning  |
````

### 5. Progress Tracking

**Auto-Progress Update in tasks.md**:

```diff
### Phase 2: Core Implementation

| # | Task | Description | Completion Criteria | Status |
|:---|:---|:---|:---|:---|
- | 2.1 | User validation | Validate user input | [ ] |
+ | 2.1 | User validation | Validate user input | [x] |
```

**Progress Log** `.sdd/task/{ticket}/implementation_progress.md`:

````markdown
# Implementation Progress Log

## 2024-01-15 14:30 - Task 2.1 Complete

**Task**: User validation
**Approach**: Used Zod for schema validation
**Tests**: Added 8 tests, all passing
**Commits**:

- test: add user validation tests (abc123)
- feat: implement user validation (def456)

**Notes**: Chose Zod over Joi for better TypeScript integration
````

### 6. Completion Verification

When all tasks complete:

**Final Verification Checklist**:

````markdown
## Implementation Completion Verification

### Task Completion

- [x] All Phase 1 tasks complete (3/3)
- [x] All Phase 2 tasks complete (5/5)
- [x] All Phase 3 tasks complete (2/2)
- [x] All Phase 4 tasks complete (4/4)
- [x] All Phase 5 tasks complete (2/2)

### Test Verification

- [x] All tests passing
- [x] Code coverage ≥ 80%
- [x] Edge cases covered
- [x] Non-functional requirements tested

### Spec Consistency

- [x] All spec APIs implemented
- [x] Data models match spec
- [x] Behavior matches spec
- [x] Design doc updated with decisions

### Documentation

- [x] Code comments added
- [x] Design doc updated
- [x] Implementation log complete
- [x] Breaking changes documented (if any)

### Ready for Review

✓ All checks passed - Ready to create PR
```

### 7. Determine Starting Phase

```
- All Phase 1 tasks complete → Start from Phase 2
- All Phase 2 tasks complete → Start from Phase 3
- And so on...
```

**When --phase option specified**: Force start from specified phase

### 8. Execute Per Phase

```
For each phase:

1. Display task list for the phase
2. Execute each task in order
   a. Check task details
   b. Refer to design/spec docs for implementation
   c. Follow TDD approach
   d. Mark [x] in tasks.md after completion
3. Run tests after phase completion
4. Move to next phase if all tests pass
````

## Output Format

### Phase Start

````markdown
# Implementation: {feature-name}

## Phase {n}: {Phase Name}

### Tasks in This Phase

1. **Task {n.m}: {Task Name}**
    - Description: {Task description}
    - Completion Criteria: {Criteria}
    - Dependencies: {Dependent tasks}

### TDD Approach

**RED Phase**: {Tests to write first}
**GREEN Phase**: {Minimum implementation needed}
**REFACTOR Phase**: {Cleanup opportunities}

### Starting implementation...
````

### Task Completion

````markdown
## ✓ Task {n.m} Complete: {Task Name}

### Implementation Summary

- Approach: {Brief description}
- Files Changed: {File list}
- Tests Added: {Test count}
- Test Results: {Pass/fail status}

### Commits

- {commit-hash}: {commit-message}

### Spec Consistency

- [x] Matches API spec
- [x] Matches data model
- [x] Follows design decisions

### Progress Update

- Phase {n} Progress: {completed}/{total} tasks ({percent}%)
- Overall Progress: {completed}/{total} tasks ({percent}%)

### Next Task

Moving to Task {n.m+1}: {Next task name}
````

### Phase Completion

````markdown
## ✓ Phase {n} Complete: {Phase Name}

### Phase Summary

- Tasks Completed: {n} tasks
- Tests Added: {n} tests
- Commits: {n} commits
- Time Estimate: {time estimate}

### Key Achievements

- {Achievement 1}
- {Achievement 2}

### Design Decisions

- {Decision 1}: {Rationale}
- {Decision 2}: {Rationale}

### Next Phase

Ready to start Phase {n+1}: {Phase name}
````

### Implementation Complete

````markdown
# ✓ Implementation Complete: {feature-name}

## Summary

| Metric          | Value      |
|:----------------|:-----------|
| Total Tasks     | {n}        |
| Tasks Completed | {n}        |
| Tests Added     | {n}        |
| Test Pass Rate  | 100%       |
| Code Coverage   | {percent}% |
| Commits         | {n}        |

## Phase Breakdown

| Phase                | Tasks   | Status     |
|:---------------------|:--------|:-----------|
| Phase 1: Foundation  | {n}/{n} | ✓ Complete |
| Phase 2: Core        | {n}/{n} | ✓ Complete |
| Phase 3: Integration | {n}/{n} | ✓ Complete |
| Phase 4: Testing     | {n}/{n} | ✓ Complete |
| Phase 5: Finishing   | {n}/{n} | ✓ Complete |

## Spec Consistency

✓ All verification checks passed

## Design Decisions Documented

Key decisions integrated into `.sdd/specification/[{path}/]{feature}_design.md`

## Next Steps

1. Review implementation log: `.sdd/task/{ticket}/implementation_progress.md`
2. Run final spec check: `/check_spec {feature}`
3. Clean up task directory: `/task_cleanup {ticket}`
4. Create PR: Use standard PR workflow

````

## Implementation Options

### Continue Mode

Resume interrupted implementation:

```
/implement user-auth TICKET-123 --continue
```

Behavior:

- Load progress from tasks.md
- Resume from first incomplete task
- Preserve implementation log

### Phase Skip Mode

Skip to specific phase (use with caution):

```
/implement user-auth TICKET-123 --start-from phase-3
```

Requirements:

- Previous phases all marked complete
- Design doc exists
- Previous phase tests pass

### Dry Run Mode

Simulate implementation without changes:

```
/implement user-auth TICKET-123 --dry-run
```

Shows:

- Implementation plan
- Task execution order
- Estimated complexity

## Best Practices

### Commit Strategy

Follow this commit pattern:

| Phase          | Commit Prefix | Example                              |
|:---------------|:--------------|:-------------------------------------|
| Setup          | `chore`       | `chore: setup test infrastructure`   |
| Tests          | `test`        | `test: add user validation tests`    |
| Implementation | `feat`        | `feat: implement user validation`    |
| Refactoring    | `refactor`    | `refactor: extract validation logic` |
| Fix            | `fix`         | `fix: handle null user status`       |
| Documentation  | `docs`        | `docs: update design decisions`      |

### When to Pause

Pause and ask for clarification when:

- Spec is ambiguous (use `/clarify`)
- Multiple valid interpretations exist
- Non-functional requirements unclear
- External dependencies unavailable

### Integration with Other Commands

```
Before: /clarify → /task_breakdown → /implement
During: /implement (continuous /check_spec)
After: /implement → /check_spec → /task_cleanup → PR
```

## Implementation Log Recording

Auto-record decisions and issues during implementation in `.sdd/task/{ticket}/implementation_log.md`:

### Log Items

| Item                           | Content Recorded                          |
|:-------------------------------|:------------------------------------------|
| **Implementation Decisions**   | Implementation decisions not in design doc |
| **Issues & Solutions**         | Problems encountered and their solutions  |
| **Alternative Considerations** | Alternatives not chosen and reasons       |
| **Technical Discoveries**      | Insights gained during implementation     |
| **Test Results**               | Test execution result records             |

### Log Usage

After implementation complete, integrate important content into `*_design.md` (executed by `/task_cleanup`).

## TDD Best Practices

### Red-Green-Refactor Cycle

```
1. Red (Write failing test)
   ↓
2. Green (Minimum implementation to pass test)
   ↓
3. Refactor (Improve code while maintaining tests)
   ↓
   Repeat
```

### Test-First Principles

| Principle                  | Details                                  |
|:---------------------------|:-----------------------------------------|
| **Write Tests First**      | Create test cases before implementation  |
| **Small Steps**            | Implement only one feature at a time     |
| **Minimum Implementation** | Write minimum code to pass tests         |
| **Continuous Refactoring** | Always improve code while maintaining tests |

### Test Coverage Goals

| Target            | Coverage Goal |
|:------------------|:--------------|
| **Core Features** | 90% or above  |
| **Integration**   | 80% or above  |
| **Edge Cases**    | 100%          |

## Error Handling

### Test Failure

````markdown
⚠ Task {n.m} Test Failure

**Failed Tests**: {n} tests failed

**Required Actions**:

1. Review test failures
2. Fix implementation OR
3. Update tests if spec understanding was wrong

**Do not mark task complete until tests pass**
````

### Spec Inconsistency Detected

````markdown
⚠ Spec Inconsistency Detected

**Issue**: Implementation doesn't match specification

**Details**:

- Spec Description: {spec requirement}
- Implementation: {what was implemented}

**Required Actions**:

1. Update implementation to match spec OR
2. Update spec if requirements changed
3. Re-run verification

**Task remains incomplete**
````

## Notes

- Always follow TDD approach: Red → Green → Refactor
- Don't skip tests to "save time"
- Mark task complete only when tests pass and match spec
- Document design decisions during implementation, not after
- Keep updating implementation log for knowledge transfer
- Run `/check_spec` at phase boundaries to detect drift early
