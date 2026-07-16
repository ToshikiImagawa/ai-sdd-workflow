# Type-Specific Front Matter Fields

Additional fields to include based on the document `type` field.

**PRD** (`type: "prd"`):

```yaml
priority: "medium"
risk: "medium"
```

**Spec** (`type: "spec"`):

```yaml
sdd-phase: "specify"
```

**Design** (`type: "design"`):

```yaml
sdd-phase: "plan"
impl-status: "not-implemented"
```

**Task** (`type: "task"`):

```yaml
sdd-phase: "tasks"
ticket: ""
```

**Implementation Log** (`type: "implementation-log"`):

```yaml
sdd-phase: "implement"
ticket: ""
completed: ""
implementer: ""
```
