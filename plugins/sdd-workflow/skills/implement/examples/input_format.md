# Input Format

## Command Format

```
/implement {feature-name} {ticket-number}
/implement {feature-name} --ticket {ticket-number}
/implement {feature-name} --ticket={ticket-number}
/implement {feature-name}  # ticket-number omitted: reads task/{feature-name}/tasks.md
```

The ticket number can be given positionally or as a flag; `--ticket <number>` and `--ticket=<number>` are
accepted and mean the same thing. When it is omitted, `{feature-name}` is used as the task directory name, so
the task list is read from `${SDD_TASK_PATH}/{feature-name}/tasks.md`. State the resolved path in the output,
and if no `tasks.md` is there, report the path, that the omitted ticket-number caused it, and the two ways
forward (re-run with the ticket number, or run `/task-breakdown {feature-name} {ticket-number}` first).

## Input Examples

```
/implement user-auth TICKET-123
/implement task-management FEAT-456
/implement auth/user-login TICKET-789  # For hierarchical structure
/implement user-auth --ticket TICKET-123
/implement user-auth --ticket=TICKET-123
```
