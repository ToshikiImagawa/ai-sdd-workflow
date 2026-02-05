# TaskList Patterns

## Creating Phase 1 Task

```
TaskCreate({
  subject: "Execute setup phase",
  description: "Create directory structure, create type definition files, define basic interfaces, setup test environment",
  activeForm: "Executing setup phase"
})
```

## Creating Phase 2 Task (depends on Phase 1)

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

## Updating Phase Status

**At Phase Start**:

```
TaskUpdate({
  taskId: "<target phase task ID>",
  status: "in_progress"
})
```

**At Phase Completion**:

```
TaskUpdate({
  taskId: "<target phase task ID>",
  status: "completed"
})
```

## Notes

- `subject` should be in imperative form, short and concise (e.g., "Execute setup", "Create tests")
- `activeForm` should use present continuous form (e.g., "Executing setup", "Creating tests")
- All tasks are created with `pending` status
- Dependencies are set using TaskUpdate after TaskCreate
