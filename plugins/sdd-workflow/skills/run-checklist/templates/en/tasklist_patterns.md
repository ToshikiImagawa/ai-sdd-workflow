# TaskList Patterns for Run Checklist

## Initial Task Creation

At the start of verification, create tasks for each category being verified:

```
TaskCreate:
  subject: "Verify Testing Review (CHK-5xx)"
  description: "Run tests and measure coverage for Testing Review checklist items"
  activeForm: "Running tests"
```

## Task Categories

| Category              | Subject Template                        | activeForm                    |
|:----------------------|:----------------------------------------|:------------------------------|
| Requirements (1xx)    | Verify Requirements Review (CHK-1xx)    | Checking requirements         |
| Specification (2xx)   | Verify Specification Review (CHK-2xx)   | Validating specifications     |
| Design (3xx)          | Verify Design Review (CHK-3xx)          | Analyzing architecture        |
| Implementation (4xx)  | Verify Implementation Review (CHK-4xx)  | Running linters               |
| Testing (5xx)         | Verify Testing Review (CHK-5xx)         | Running tests                 |
| Documentation (6xx)   | Verify Documentation Review (CHK-6xx)   | Checking documentation        |
| Security (7xx)        | Verify Security Review (CHK-7xx)        | Running security scanners     |
| Performance (8xx)     | Verify Performance Review (CHK-8xx)     | Running benchmarks            |
| Deployment (9xx)      | Verify Deployment Review (CHK-9xx)      | Validating configuration      |

## Status Updates

### Starting a Category

```
TaskUpdate:
  taskId: "{task-id}"
  status: "in_progress"
```

### Completing a Category

```
TaskUpdate:
  taskId: "{task-id}"
  status: "completed"
```

## Example Flow

1. Create all category tasks (pending)
2. For each category:
   - Set task to in_progress
   - Run verification commands
   - Record results
   - Set task to completed
3. Create final report task
4. Generate verification report
5. Mark report task completed
